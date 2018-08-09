# Licensed under a MIT style license - see LICENSE.rst
# -*- coding: utf-8 -*-
"""
digestor.base
=============

Base class containing common functionality.
"""
import os
import sys
import re
import json
import logging
import subprocess as sub

import yaml
import numpy as np
from astropy.io import fits
from astropy.table import Table


class Digestor(object):
    """Base class for FITS+SQL to FITS+SQL conversion.

    Parameters
    ----------
    schema : :class:`str`
        Name of the PostgreSQL schema containing `table`.
    table : :class:`str`
        Name of the PostgreSQL table.
    description : :class:`str`, optional
        A short description of `schema`.
    merge : :class:`str`, optional
        Name of a JSON file containing existing TapSchema metadata.
    """
    #
    # Name of the root logger provided by Digestor.
    #
    rootLogger = 'digestor'
    #
    # Order columns for disk efficiency.
    #
    ordered = ('bigint', 'double', 'integer', 'real', 'smallint', 'character')
    #
    # Defer some pre-processing to STILTS.
    #
    _stilts_command = ['cmd=addcol htm9 (int)htmIndex(9,{ra},{dec})',
                       'cmd=addcol ring256 (int)healpixRingIndex(8,{ra},{dec})',
                       'cmd=addcol nest4096 (int)healpixNestIndex(12,{ra},{dec})',
                       'cmd=addskycoords -inunit deg -outunit deg icrs galactic {ra} {dec} glon glat',
                       'cmd=addskycoords -inunit deg -outunit deg icrs ecliptic {ra} {dec} elon elat']

    def __init__(self, schema, table, description=None, merge=None):
        self.schema = schema
        self.table = table
        self.tapSchema = self._initTapSchema(description, merge)
        self.mapping = dict()
        self.FITS = dict()
        self._tableIndexCache = dict()
        self._columnIndexCache = dict()
        self._inputFITS = None

    @classmethod
    def configureLog(cls, debug=False):
        """Set up logging for the module.

        Parameters
        ----------
        debug : :class:`bool`, optional
            If ``True``, set log level to DEBUG.
        """
        ch = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(levelname)s:%(name)s:%(lineno)s: %(message)s')
        ch.setFormatter(formatter)
        log = logging.getLogger(cls.rootLogger)
        log.addHandler(ch)
        level = logging.INFO
        if debug:
            level = logging.DEBUG
        log.setLevel(level)
        return

    def logName(self, method):
        """Get a logger with name `method`.

        Parameters
        ----------
        method : :class:`str`
            Name of the log object.  Will be appended to the root name.

        Returns
        -------
        :class:`logging.Logger`
            A configured log object.
        """
        return logging.getLogger(self.rootLogger + '.' + method)

    def _initTapSchema(self, description='', merge=None):
        """Create a dictionary compatible with TapSchema.

        Parameters
        ----------
        description : :class:`str`, optional
            A short description of `schema`.
        merge : :class:`str`, optional
            Name of a JSON file containing existing TapSchema metadata.

        Returns
        -------
        :class:`dict`
            A dictionary compatible with TapSchema.

        Raises
        ------
        :exc:`ValueError`
            When merging, if the schema names don't match, or if the table is
            already loaded.
        """
        if merge is None:
            metadata = dict()
            metadata['schemas'] = [{'schema_name': self.schema,
                                    'description': description,
                                    'utype': ''},]
            metadata['tables'] = [{'schema_name': self.schema,
                                   'table_name': self.table,
                                   'table_type': 'table',
                                   'utype': '',
                                   'description': ''},]
            metadata['columns'] = self._dlColumns()
            metadata['keys'] = [{"key_id": "",
                                 "from_table": "",
                                 "target_table": "",
                                 "description": "",
                                 "utype": ""}]
            metadata['key_columns'] = [{"key_id": "",
                                        "from_column": "",
                                        "target_column": ""}]
        else:
            with open(merge) as f:
                metadata = json.load(f)
            if metadata['schemas'][0]['schema_name'] != self.schema:
                raise ValueError("You are attempting to merge schema={0} into schema={1}!".format(self.schema, metadata['schemas'][0]['schema_name']))
            for t in metadata['tables']:
                if t['table_name'] == self.table:
                    raise ValueError("Table {0} is already defined!".format(self.table))
            metadata['tables'].append({'schema_name': self.schema,
                                       'table_name': self.table,
                                       'table_type': 'table',
                                       'utype': '',
                                       'description': ''})
            metadata['columns'] += self._dlColumns()
        return metadata

    def _dlColumns(self):
        """Add SQL column definitions of Data Lab-added columns.

        Returns
        -------
        :class:`list`
            A list suitable for appending to an existing list of columns.
        """
        return [self.tapColumn('htm9',
                               description="HTM index (order 9 => ~10 arcmin size)",
                               datatype='integer', indexed=1),
                self.tapColumn('ring256',
                               description="HEALPIX index (Nsides 256, Ring scheme => ~14 arcmin size)",
                               datatype='integer', indexed=1),
                self.tapColumn('nest4096',
                               description="HEALPIX index (Nsides 4096, Nest scheme => ~52 arcsec size",
                               datatype='integer', indexed=1),
                self.tapColumn('random_id',
                               description="Random ID in the range 0.0 => 100.0",
                               datatype='real', indexed=1),
                self.tapColumn('glon',
                               description="Galactic Longitude",
                               datatype='double', unit='deg', indexed=1),
                self.tapColumn('glat',
                               description="Galactic Latitude",
                               datatype='double', unit='deg', indexed=1),
                self.tapColumn('elon',
                               description="Ecliptic Longitude",
                               datatype='double', unit='deg', indexed=1),
                self.tapColumn('elat',
                               description="Ecliptic Longitude",
                               datatype='double', unit='deg', indexed=1)]

    def tapColumn(self, column, **kwargs):
        """Create a TapSchema-compatible column definition.

        Parameters
        ----------
        column : :class:`str`
            Name of the column.

        Returns
        -------
        :class:`dict`
            A column definition in TapSchema format.
        """
        p = {'table_name': self.table,
             'column_name': column,
             'description': '',
             'unit': '',
             'ucd': '',
             'utype': '',
             'datatype': '',
             'size': 1,
             'principal': 0,
             'indexed': 0,
             'std': 0,
             }
        for k in kwargs:
            if k in p:
                p[k] = kwargs[k]
        return p

    def tableIndex(self):
        """Find the index of the table in the list of tables.

        Raises
        ------
        :exc:`ValueError`
            If the table is not found.
        """
        try:
            return self._tableIndexCache[(self.schema, self.table)]
        except KeyError:
            for i, t in enumerate(self.tapSchema['tables']):
                if t['schema_name'] == self.schema and t['table_name'] == self.table:
                    self._tableIndexCache[(self.schema, self.table)] = i
                    return i
        raise ValueError("Table {0.table} was not found in schema {0.schema}!".format(self))

    def columnIndex(self, column):
        """Find the index of the column in the list of columns.

        Raises
        ------
        :exc:`ValueError`
            If the column is not found.
        """
        try:
            return self._columnIndexCache[(self.schema, self.table, column)]
        except KeyError:
            for i, c in enumerate(self.tapSchema['columns']):
                if c['table_name'] == self.table and c['column_name'] == column:
                    self._columnIndexCache[(self.schema, self.table, column)] = i
                    return i
        raise ValueError("Column {0} was not found in {1.schema}.{1.table}!".format(column, self))

    @property
    def colNames(self):
        """List of columns in the table.
        """
        return [c['column_name'] for c in self.tapSchema['columns']
                if c['table_name'] == self.table]

    @property
    def nColumns(self):
        """Number of columns in the table.
        """
        return len(self.colNames)

    def mapColumns(self):
        """Complete mapping of FITS table columns to SQL columns.

        This method may need to be overridden by a subclass.

        Raises
        ------
        :exc:`KeyError`
            If an expected mapping cannot be found.
        """
        log = self.logName('base.Digestor.mapColumns')
        for sc in self.colNames:
            if sc in self.mapping:
                if self.mapping[sc] in self.FITS:
                    log.debug("FITS: %s -> SQL: %s", self.mapping[sc], sc)
                else:
                    msg = "Could not find a FITS column corresponding to %s!"
                    log.error(msg, sc)
                    raise KeyError(msg % sc)
            else:
                log.debug("FITS: %s -> SQL: %s", sc, sc)
                self.mapping[sc] = sc
        return

    def fixColumns(self, filename):
        """Fix any table definition oddities "by hand".

        Parameters
        ----------
        filename : :class:`str`
            Name of the YAML configuration file.

        Raises
        ------
        :exc:`ValueError`
            If the configuration file contains an unknown column.
        """
        log = self.logName('base.Digestor.fixColumns')
        if os.path.exists(filename):
            log.debug("Opening %s.", filename)
            with open(filename) as f:
                conf = yaml.load(f)
            try:
                col_fix = conf[self.schema][self.table]['columns']
            except KeyError:
                return
            for col in col_fix:
                i = self.columnIndex(col)
                for k in col_fix[col]:
                    log.debug("self.tapSchema['columns'][%d]['%s'] = col_fix['%s']['%s'] = '%s'",
                              i, k, col, k, col_fix[col][k])
                self.tapSchema['columns'][i][k] = col_fix[col][k]
        return

    def sortColumns(self):
        """Sort the SQL columns for best performance.

        Raises
        ------
        :exc:`AssertionError`
            If not all columns are sorted into the new order.
        """
        new_columns = list()
        for o in self.ordered:
            for c in self.tapSchema['columns']:
                if c['table_name'] == self.table and c['datatype'] == o:
                    new_columns.append(c)
        assert len(new_columns) == self.nColumns
        for i, c in enumerate(self.tapSchema['columns']):
            if c['table_name'] == self.table:
                self.tapSchema['columns'][i] = new_columns.pop(0)
        return

    def addDLColumns(self, filename, ra='ra', overwrite=False):
        """Add DL columns to FITS file prior to column reorganization.

        Parameters
        ----------
        filename : :class:`str`
            Name of the FITS file.
        ra : :class:`str`, optional
            Look for Right Ascension in this column (default 'ra').
        overwrite : :class:`bool`, optional
            If ``True``, remove any existing file.

        Returns
        -------
        :class:`str`
            The name of the processed file.

        Raises
        ------
        :exc:`ValueError`
            If a problem with :command:`stilts` is detected.
        """
        log = self.logName('base.Digestor.addDLColumns')
        out = filename.replace('.fits', '.stilts.fits')
        if os.path.exists(out) and not overwrite:
            log.info("Using existing file: %s.", out)
            return out
        if os.path.exists(out):
            log.info("Removing existing file: %s.", out)
            os.remove(out)
        fra = ra.lower()
        fdec = ra.lower().replace('ra', 'dec')
        command = ['stilts', 'tpipe', 'in={0}'.format(filename)]
        command += [cmd.format(ra=fra, dec=fdec) for cmd in self._stilts_command]
        command += ['ofmt=fits-basic', 'out={0}'.format(out)]
        log.debug(' '.join(command))
        proc = sub.Popen(command, stdout=sub.PIPE, stderr=sub.PIPE)
        o, e = proc.communicate()
        if o:
            log.debug('STILTS STDOUT = %s', o.decode('utf-8'))
        if proc.returncode != 0 or e:
            log.error('STILTS returncode = %d', proc.returncode)
            log.error('STILTS STDERR = %s', e.decode('utf-8'))
            raise ValueError("STILTS error detected!")
        return out

    def parseFITS(self, filename, hdu=1):
        """Read FITS metadata from `filename`.

        Parameters
        ----------
        filename : :class:`str`
            Name of the FITS file.
        hdu : :class:`int`, optional
            Read data from this HDU (default 1).
        """
        with fits.open(filename) as hdulist:
            fits_names = hdulist[hdu].columns.names
            fits_types = hdulist[hdu].columns.formats
        self._inputFITS = filename
        for i, f in enumerate(fits_names):
            self.FITS[f] = fits_types[i]

    def processFITS(self, hdu=1, overwrite=False):
        """Convert a pre-processed FITS file into one ready for database loading.

        Parameters
        ----------
        hdu : :class:`int`, optional
            Read data from this HDU (default 1).
        overwrite : :class:`bool`, optional
            If ``True``, remove any existing file.

        Returns
        -------
        :class:`str`
            The name of the file written.

        Raises
        ------
        :exc:`ValueError`
            If the FITS data type cannot be converted to SQL.
        """
        log = self.logName('base.Digestor.processFITS')
        out = "{0.schema}.{0.table}.fits".format(self)
        if os.path.exists(out) and not overwrite:
            log.info("Using existing file: %s.", out)
            return out
        if os.path.exists(out):
            log.info("Removing existing file: %s.", out)
            os.remove(out)
        type_map = {'bigint': ('K', 'J', 'I', 'B'),
                    'integer': ('J', 'I', 'B'),
                    'smallint': ('I', 'B'),
                    'double': ('D', 'E'),
                    'real': ('E',),
                    'character': ('A',)}
        np_map = {'bigint': np.int64,
                  'integer': np.int32,
                  'smallint': np.int16,
                  'double': np.float64,
                  'real': np.float32}
        safe_conversion = {('J', 'smallint'): 2**15}
        rebase = re.compile(r'^(\d+)(\D+)')
        columns = [c for c in self.tapSchema['columns']
                   if c['table_name'] == self.table]
        old = Table.read(self._inputFITS, hdu=hdu)
        new = Table()
        for col in columns:
            if col['column_name'] == 'random_id':
                log.info("Skipping %s which will be added by FITS2DB.",
                         col['column_name'])
                continue
            fcol = self.mapping[col['column_name']]
            index = None
            if '[' in fcol:
                foo = fcol.split('[')
                fcol = foo[0]
                index = int(foo[1].strip(']'))
            ftype = self.FITS[fcol]
            fbasetype = rebase.sub(r'\2', ftype)
            if fbasetype == type_map[col['datatype']][0]:
                log.debug("Type match for %s -> %s.", fcol, col['column_name'])
                if index is not None:
                    log.debug("new['%s'] = old['%s'][:,%d]",
                              col['column_name'], fcol, index)
                    new[col['column_name']] = old[fcol][:,index]
                else:
                    log.debug("new['%s'] = old['%s']", col['column_name'], fcol)
                    new[col['column_name']] = old[fcol]
            elif fbasetype in type_map[col['datatype']]:
                log.debug("Safe type conversion possible for %s (%s) -> %s (%s).",
                          fcol, fbasetype, col['column_name'], col['datatype'])
                if index is not None:
                    log.debug("new['%s'] = old['%s'][:,%d].astype(%s)",
                              col['column_name'], fcol, index,
                              str(np_map[col['datatype']]))
                    new[col['column_name']] = old[fcol][:,index].astype(np_map[col['datatype']])
                else:
                    log.debug("new['%s'] = old['%s'].astype(%s)",
                              col['column_name'], fcol,
                              str(np_map[col['datatype']]))
                    new[col['column_name']] = old[fcol].astype(np_map[col['datatype']])
            elif fbasetype == 'A' and col['datatype'] == 'bigint':
                log.debug("String to integer conversion required for %s -> %s.", fcol, col['column_name'])
                width = int(str(old[fcol].dtype).split(old[fcol].dtype.kind)[1])
                blank = ' '*width
                w = np.nonzero(old[fcol] == blank)[0]
                if len(w) > 0:
                    log.debug("old['%s'][old['%s'] == blank] = blank[0:%d] + '0'",
                              fcol, fcol, width - 1)
                    old[fcol][w] = blank[0:(width-1)] + '0'
                log.debug("new['%s'] = old['%s'].astype(np.int64)", col['column_name'], fcol)
                try:
                    new[col['column_name']] = old[fcol].astype(np.int64)
                except OverflowError:
                    uold = old[fcol].astype(np.uint64)
                    hi = np.nonzero(uold >= 2**63)[0]
                    lo = np.nonzero(uold < 2**63)[0]
                    inew = np.zeros(uold.shape, dtype=np.int64)
                    inew[lo] = uold[lo]
                    inew[hi] = (uold[hi] - 2**63).astype(np.int64) - 2**63
                    new[col['column_name']] = inew
            else:
                if (fbasetype, col['datatype']) in safe_conversion:
                    limit = safe_conversion[(fbasetype, col['datatype'])]
                    if ((old[fcol] >= -limit) & (old[fcol] <= limit - 1)).all():
                        if index is not None:
                            log.debug("new['%s'] = old['%s'][:,%d].astype(%s)", col['column_name'], fcol, index, str(np_map[col['datatype']]))
                            new[col['column_name']] = old[fcol][:,index].astype(np_map[col['datatype']])
                        else:
                            log.debug("new['%s'] = old['%s'].astype(%s)", col['column_name'], fcol, str(np_map[col['datatype']]))
                            new[col['column_name']] = old[fcol].astype(np_map[col['datatype']])
                else:
                    msg = "No safe data type conversion possible for %s (%s) -> %s (%s)!"
                    log.error(msg, fcol, fbasetype, col['column_name'], col['datatype'])
                    raise ValueError(msg % (fcol, fbasetype, col['column_name'], col['datatype']))
            if fbasetype in ('D', 'E'):
                new[col['column_name']][~np.isfinite(new[col['column_name']])] = -9999.0
        log.debug("new.write('%s')", out)
        new.write(out)
        return out

    def writeTapSchema(self, filename):
        """Write the TapSchema metadata to a JSON file.

        Parameters
        ----------
        filename : :class:`str`
            Name of the JSON file.
        """
        with open(filename, 'w') as JSON:
            json.dump(self.tapSchema, JSON, indent=4)

    def createSQL(self):
        """Construct a CREATE TABLE statement from the TapSchema metadata.

        Returns
        -------
        :class:`str`
            A SQL table definition.
        """
        # log = self.logName('base.Digestor.createSQL')
        sql = [r"CREATE TABLE IF NOT EXISTS {0.schema}.{0.table} (".format(self)]
        for c in self.tapSchema['columns']:
            if c['table_name'] == self.table:
                typ = c['datatype']
                if typ == 'double':
                    typ = 'double precision'
                if typ == 'character':
                    typ = 'varchar({size})'.format(**c)
                sql.append("    {0} {1} NOT NULL,".format(c['column_name'], typ))
        sql[-1] = sql[-1].replace(',', '')
        sql.append(r") WITH (fillfactor=100);")
        return '\n'.join(sql) + '\n'

    def writeSQL(self, filename):
        """Write the CREATE TABLE statement to `filename`.

        Parameters
        ----------
        filename : :class:`str`
            Name of the SQL file.
        """
        with open(filename, 'w') as POST:
            POST.write(self.createSQL())
