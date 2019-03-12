# Licensed under a MIT style license - see LICENSE.rst
# -*- coding: utf-8 -*-
"""
digestor.sdss
=============

Convert SDSS SQL (MS SQL Server) table definitions to Data Lab SQL (PostgreSQL).
"""
import os
import re
import sys
import time
# from datetime import datetime
from argparse import ArgumentParser

from pkg_resources import resource_filename
# from pytz import utc
import numpy as np
from astropy.table import Table

from .base import Digestor


class SDSS(Digestor):
    """Convert SDSS FITS+SQL files into Data Lab-compatible forms.
    """
    #
    # Match lines in SQL definition files.
    #
    _SQLre = {'comment': re.compile(r'\s*--/(H|T)\s+(.*)$'),
              'column': re.compile(r'\s*(\S+)\s+(\S+)\s*([^,]+),\s*(.*)$')}
    #
    # Map SQL Server data types to PostgreSQL.
    #
    _server2post = {'float': 'double precision', 'int': 'integer',
                    'tinyint': 'smallint'}

    #
    # Ignore columns that are specific to the SDSS CAS system.
    #
    _skip_columns = ('htmid', 'loadversion')
    #
    # Identify columns that contain photometric flags
    #
    _flagre = re.compile(r'flags(|_[ugriz])$', re.I)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.NOFITS = dict()

    def parseSQL(self, filename):
        """Parse an entire SQL file.

        Parameters
        ----------
        filename : :class:`str`
            Name of the SQL file.
        """
        with open(filename) as SQL:
            for line in SQL:
                self.parseLine(line)

    def parseLine(self, line):
        """Parse a single line from a SQL file.

        Parameters
        ----------
        line : :class:`str`
            A single line from a SQL file.

        Notes
        -----
        * Currently, the long description (``--/T``) is thrown out.
        """
        log = self.logName('sdss.SDSS.parseLine')
        l = line.strip()
        for r in self._SQLre:
            m = self._SQLre[r].match(l)
            if m is not None:
                g = m.groups()
                if r == 'comment':
                    ti = self.tableIndex()
                    if g[0] == 'H':
                        log.debug("self.tapSchema['tables'][%d]['description'] += '%s'", ti, g[1])
                        self.tapSchema['tables'][ti]['description'] += g[1]
                    if g[0] == 'T':
                        log.debug("self.tapSchema['tables'][%d]['long_description'] += '%s'", ti, g[1])
                        # self.tapSchema['tables'][ti]['long_description'] += g[1]+'\n'
                    return
                elif r == 'column':
                    col = g[0].lower()
                    if col in self._skip_columns:
                        log.debug("Skipping column %s.", col)
                        return
                    typ = g[1].strip('[]').lower()
                    try:
                        post_type = self._server2post[typ]
                    except KeyError:
                        post_type = typ
                    log.debug("    %s %s %s,", col, post_type, g[2])
                    log.debug("metadata = '%s'", g[3])
                    p, r = self.parseColumnMetadata(col, g[3])
                    p['table_name'] = self.stable
                    if post_type == 'double precision':
                        p['datatype'] = 'double'
                    elif post_type.startswith('varchar'):
                        p['datatype'] = 'character'
                        p['size'] = int(post_type.split('(')[1].strip(')'))
                    else:
                        p['datatype'] = post_type
                    self.tapSchema['columns'].append(p)
                    if r is not None:
                        log.debug("self.mapping['%s'] = '%s'", col, r)
                        self.mapping[col] = r
                    return
        return

    def parseColumnMetadata(self, column, data):
        """Parse the metadata for an individual column.

        Parameters
        ----------
        column : :class:`str`
            Name of the column.
        data : :class:`str`
            Metadata string extracted from the SQL file.

        Returns
        -------
        :class:`tuple`
            A tuple containing a dictionary containing the parsed metadata
            in TapSchema format and a FITS column name, if found.
        """
        log = self.logName('sdss.SDSS.parseColumnMetadata')
        tr = {'D': 'description',
              'F': 'FITS',
              'K': 'ucd',
              'U': 'unit'}
        defaults = {'D': ('description', 'NO DESCRIPTION'),
                    'F': ('FITS', column.upper()),
                    'K': ('ucd', None),
                    'U': ('unit', None)}
        p = self.tapColumn(column)
        rename = None
        for m in 'DFKU':
            try:
                i = data.index('--/%s' % m)
                try:
                    j = data.index('--', i + 2)
                except ValueError:
                    j = len(data)
                r = data[i + 5:j].strip()
                if m == 'F':
                    if ' ' in r:
                        r = "{0}[{1}]".format(*(re.split(r'\s+', r)))
                    r = r.upper()
                    if r == 'NOFITS':
                        log.warning("Column %s is not defined in the corresponding FITS file!", column)
                    else:
                        rename = r
                else:
                    log.debug("p['%s'] = %s", tr[m], repr(r))
                    p[tr[m]] = r
            except ValueError:
                if m == 'F' and any([column.endswith('_%s' % f) for f in 'ugriz']):
                    foo = column.rsplit('_', 1)
                    r = "{0}[{1:d}]".format(foo[0], 'ugriz'.index(foo[1])).upper()
                    rename = r
        return (p, rename)

    def fixNOFITS(self, filename):
        """Fix any missing data designated by ``--/F NOFITS`` using
        the YAML configuration file `filename`.

        Parameters
        ----------
        filename : :class:`str`
            Name of the YAML configuration file.
        """
        log = self.logName('sdss.SDSS.fixNOFITS')
        config = self._getYAML(filename)
        if config is not None:
            try:
                self.NOFITS = config[self.schema][self.table]['NOFITS']
            except KeyError:
                log.debug("No instructions found.")
        return

    def fixMapping(self, filename):
        """Fix any FITS to SQL mapping problems using the YAML configuration
        file `filename`.

        Parameters
        ----------
        filename : :class:`str`
            Name of the YAML configuration file.
        """
        log = self.logName('sdss.SDSS.fixMapping')
        config = self._getYAML(filename)
        if config is not None:
            try:
                mapping = config[self.schema][self.table]['mapping']
            except KeyError:
                log.debug("No mappings found.")
                return
            for sc in mapping:
                log.debug("self.mapping['%s'] = '%s'", sc, mapping[sc])
                self.mapping[sc] = mapping[sc]
        return

    def mapColumns(self):
        """Complete mapping of FITS table columns to SQL columns.

        Raises
        ------
        :exc:`KeyError`
            If an expected mapping cannot be found.
        """
        log = self.logName('sdss.SDSS.mapColumns')
        drop = list()
        for sc in self.colNames:
            if sc in self.mapping:
                #
                # Make sure the column actually exists.
                #
                verify_mapping = False
                mc = self.mapping[sc]
                index = ''
                if '[' in mc:
                    foo = mc.split('[')
                    mc = foo[0]
                    index = '[' + foo[1]
                if mc in self.FITS:
                    log.debug("FITS: %s -> SQL: %s", self.mapping[sc], sc)
                    verify_mapping = True
                else:
                    #
                    # See if there is a column containing underscores that
                    # could correspond to this mapping.
                    #
                    for fc in self.FITS:
                        for fcl in (fc.lower(), fc.lower().replace('_', ''),):
                            if fcl == mc.lower():
                                log.debug("FITS: %s%s -> SQL: %s", fc, index, sc)
                                self.mapping[sc] = fc + index
                                verify_mapping = True
                if not verify_mapping:
                    msg = "Could not find a FITS column corresponding to %s!"
                    log.error(msg, sc)
                    raise KeyError(msg % sc)
            else:
                for fc in self.FITS:
                    for fcl in (fc.lower(), fc.lower().replace('_', ''),):
                        if fcl == sc:
                            log.debug("FITS: %s -> SQL: %s", fc, sc)
                            self.mapping[sc] = fc
                            break
                    if sc in self.mapping:
                        break
            if sc not in self.mapping:
                if sc == 'random_id':
                    log.info("Skipping %s which will be added by FITS2DB.",
                             sc)
                elif sc in self.NOFITS:
                    if self.NOFITS[sc] == 'drop':
                        log.info("Dropping %s as requested.", sc)
                        drop.append(sc)
                    elif self.NOFITS[sc] == 'defer':
                        log.info("Column %s will be added in post-processing.", sc)
                    else:
                        msg = "Unknown NOFITS instruction: %s!"
                        log.error(msg, sc)
                        raise KeyError(msg % sc)
                else:
                    msg = "Could not find a FITS column corresponding to %s!"
                    log.error(msg, sc)
                    raise KeyError(msg % sc)
        #
        # Remove SQL columns that were requested to be dropped.
        #
        for sc in drop:
            i = self.columnIndex(sc)
            log.debug("del self.tapSchema['columns'][%d]", i)
            del self.tapSchema['columns'][i]
        #
        # Check for FITS columns that are NOT mapped to the SQL file.
        #
        for col in self.FITS:
            if col in self.mapping.values():
                log.debug("FITS column %s will be transferred to SQL.", col)
            else:
                col_array = re.compile(col + r'\[\d+\]')
                if any([col_array.match(sc) is not None for sc in self.mapping.values()]):
                    log.debug("FITS column %s will be transferred to SQL.", col)
                else:
                    log.warning("FITS column %s will be dropped from SQL!", col)
        return

    def _photoFlag(self, column, table):
        """Handle photometric flags in SDSS data.

        Parameters
        ----------
        column : :class:`dict`
            A TapSchema column definition.
        table : :class:`astropy.table.Table`
            Table containing the input data.

        Returns
        -------
        :class:`numpy.ndarray`
            The combined flags and flags2 data, or ``None`` if the
            column did not match.

        Raises
        ------
        :exc:`AssertionError`
            If the required columns are not present in the FITS file.
        """
        log = self.logName('sdss.SDSS._photoFlag')
        m = self._flagre.match(column['column_name'])
        if m is not None:
            g = m.groups()[0].replace('_', '')
            if g:
                #
                # Ensure FLAGS and FLAGS2 are present.
                #
                band = 'ugriz'.index(g)
                assert column['datatype'] == 'bigint'
                assert self.mapping[column['column_name']].lower() == 'flags[{0:d}]'.format(band)
                assert 'FLAGS' in table.colnames
                assert 'FLAGS2' in table.colnames
                log.debug("np.left_shift(table['FLAGS2'][:, %d].astype(np.int64), 32) | table['FLAGS'][:, %d].astype(np.int64)", band, band)
                return (np.left_shift(table['FLAGS2'][:, band].astype(np.int64), 32) |
                        table['FLAGS'][:, band].astype(np.int64))
            else:
                #
                # Ensure OBJC_FLAGS and OBJC_FLAGS2 are present.
                #
                assert column['datatype'] == 'bigint'
                assert self.mapping[column['column_name']].lower() == 'objc_flags'
                assert 'OBJC_FLAGS' in table.colnames
                assert 'OBJC_FLAGS2' in table.colnames
                log.debug("np.left_shift(table['OBJC_FLAGS2'].astype(np.int64), 32) | table['OBJC_FLAGS'].astype(np.int64)")
                return (np.left_shift(table['OBJC_FLAGS2'].astype(np.int64), 32) |
                        table['OBJC_FLAGS'].astype(np.int64))
        return None

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
        log = self.logName('sdss.SDSS.processFITS')
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
        safe_conversion = {('J', 'smallint'): 2**15,
                           ('A', 'smallint'): 2**15,
                           ('A', 'integer'): 2**31,
                           ('A', 'bigint'): 2**63}
        rebase = re.compile(r'^(\d+)(\D+)')
        columns = [c for c in self.tapSchema['columns']
                   if c['table_name'] == self.stable]
        old = Table.read(self._inputFITS, hdu=hdu)
        new = Table()
        for col in columns:
            if col['column_name'] == 'random_id':
                log.info("Creating %s column using numpy.random.random().",
                         col['column_name'])
                stime = int(time.time())
                log.debug('np.random.seed(%s)', stime)
                np.random.seed(stime)
                log.debug("new['%s'] = np.random.random((%d,)).astype(%s)",
                          col['column_name'], len(old), str(np_map[col['datatype']]))
                new[col['column_name']] = 100.0*np.random.random((len(old),)).astype(np_map[col['datatype']])
                continue
            if col['column_name'] in self.NOFITS:
                log.info("Creating placeholder column %s for post-processing.",
                         col['column_name'])
                log.debug("new['%s'] = np.zeros((%d,), dtype=%s)",
                          col['column_name'], len(old), str(np_map[col['datatype']]))
                new[col['column_name']] = np.zeros((len(old),), dtype=np_map[col['datatype']])
                continue
            if 'flags' in col['column_name']:
                flags64 = self._photoFlag(col, old)
                if flags64 is not None:
                    log.info("Combining photo flags for %s", col['column_name'])
                    new[col['column_name']] = flags64
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
                    log.debug("new['%s'] = old['%s'][:, %d]",
                              col['column_name'], fcol, index)
                    new[col['column_name']] = old[fcol][:, index]
                else:
                    log.debug("new['%s'] = old['%s']", col['column_name'], fcol)
                    new[col['column_name']] = old[fcol]
            elif fbasetype in type_map[col['datatype']]:
                log.debug("Safe type conversion possible for %s (%s) -> %s (%s).",
                          fcol, fbasetype, col['column_name'], col['datatype'])
                if index is not None:
                    log.debug("new['%s'] = old['%s'][:, %d].astype(%s)",
                              col['column_name'], fcol, index,
                              str(np_map[col['datatype']]))
                    new[col['column_name']] = old[fcol][:, index].astype(np_map[col['datatype']])
                else:
                    log.debug("new['%s'] = old['%s'].astype(%s)",
                              col['column_name'], fcol,
                              str(np_map[col['datatype']]))
                    new[col['column_name']] = old[fcol].astype(np_map[col['datatype']])
            else:
                if (fbasetype, col['datatype']) in safe_conversion:
                    limit = safe_conversion[(fbasetype, col['datatype'])]
                    if fbasetype == 'A':
                        log.debug("String to integer conversion required for %s -> %s.", fcol, col['column_name'])
                        width = int(str(old[fcol].dtype).split(old[fcol].dtype.kind)[1])
                        blank = ' '*width
                        w = np.nonzero(old[fcol] == blank)[0]
                        if len(w) > 0:
                            log.debug("old['%s'][old['%s'] == blank] = blank[0:%d] + '0'",
                                      fcol, fcol, width - 1)
                            old[fcol][w] = blank[0:(width-1)] + '0'
                        log.debug("test_old = old['%s'].astype(np.int64)", fcol)
                        try:
                            test_old = old[fcol].astype(np.int64)
                        except OverflowError:
                            log.debug("Attempting string to quasi-unsigned integer conversion for %s -> %s.",
                                      fcol, col['column_name'])
                            uold = old[fcol].astype(np.uint64)
                            hi = np.nonzero(uold >= 2**63)[0]
                            lo = np.nonzero(uold < 2**63)[0]
                            test_old = np.zeros(uold.shape, dtype=np.int64)
                            test_old[lo] = uold[lo]
                            test_old[hi] = (uold[hi] - 2**63).astype(np.int64) - 2**63
                    else:
                        if index is not None:
                            test_old = old[fcol][:, index]
                        else:
                            test_old = old[fcol]
                    if ((test_old >= -limit) & (test_old <= limit - 1)).all():
                        if (fbasetype, col['datatype']) == ('A', 'bigint'):
                            log.debug("new['%s'] = test_old  # quasi-unsigned integer", col['column_name'])
                            new[col['column_name']] = test_old
                        else:
                            if index is not None:
                                log.debug("new['%s'] = old['%s'][:, %d].astype(%s)", col['column_name'], fcol, index, str(np_map[col['datatype']]))
                                new[col['column_name']] = old[fcol][:, index].astype(np_map[col['datatype']])
                            else:
                                log.debug("new['%s'] = old['%s'].astype(%s)", col['column_name'], fcol, str(np_map[col['datatype']]))
                                new[col['column_name']] = old[fcol].astype(np_map[col['datatype']])
                    else:
                        msg = "Values too large for safe data type conversion for %s (%s) -> %s (%s)!"
                        log.error(msg, fcol, fbasetype, col['column_name'], col['datatype'])
                        raise ValueError(msg % (fcol, fbasetype, col['column_name'], col['datatype']))
                else:
                    msg = "No safe data type conversion possible for %s (%s) -> %s (%s)!"
                    log.error(msg, fcol, fbasetype, col['column_name'], col['datatype'])
                    raise ValueError(msg % (fcol, fbasetype, col['column_name'], col['datatype']))
            if fbasetype in ('D', 'E'):
                new[col['column_name']][~np.isfinite(new[col['column_name']])] = -9999.0
        log.debug("new.write('%s')", out)
        new.write(out)
        return out


def get_options():
    """Parse command-line options.

    Returns
    -------
    :class:`argparse.Namespace`
        The parsed options.
    """
    parser = ArgumentParser(description=__doc__.split("\n")[-2],
                            prog=os.path.basename(sys.argv[0]))
    parser.add_argument('-c', '--configuration', dest='config', metavar='FILE',
                        default=resource_filename('digestor', 'data/sdss.yaml'),
                        help='Read table-specific configuration from FILE.')
    parser.add_argument('-d', '--schema-description', dest='description',
                        metavar='TEXT',
                        default='Sloan Digital Sky Survey Data Relase 14',
                        help='Short description of the schema.')
    parser.add_argument('-E', '--no-ecliptic', dest='ecliptic', action='store_false',
                        help='Do not add ecliptic coordinates.')
    parser.add_argument('-e', '--extension', dest='hdu', metavar='N',
                        type=int, default=1,
                        help='Read data from FITS HDU N (default %(default)s).')
    parser.add_argument('-G', '--no-galactic', dest='galactic', action='store_false',
                        help='Do not add galactic coordinates.')
    parser.add_argument('-j', '--output-json', dest='output_json', metavar='FILE',
                        help='Write table metadata to FILE.')
    parser.add_argument('-k', '--keep', action='store_true',
                        help='Do not overwrite any existing intermediate files.')
    parser.add_argument('-l', '--log', dest='log', metavar='FILE',
                        help='Log operations to FILE.')
    parser.add_argument('-m', '--merge', dest='merge_json', metavar='FILE',
                        help='Merge metadata in FILE into final metadata output.')
    parser.add_argument('-o', '--output-sql', dest='output_sql', metavar='FILE',
                        help='Write table definition to FILE.')
    parser.add_argument('-r', '--ra', dest='ra', metavar='COLUMN', default='ra',
                        help='Right Ascension is in COLUMN.')
    parser.add_argument('-s', '--schema', metavar='SCHEMA',
                        default='sdss_dr14',
                        help='Define table with this schema.')
    parser.add_argument('-t', '--table', metavar='TABLE',
                        help='Set the table name.')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Print extra information.')
    parser.add_argument('fits', help='FITS file to convert.')
    parser.add_argument('sql', help='SQL file to convert.')
    return parser.parse_args()


def main():
    """Entry-point for command-line script.

    Returns
    -------
    :class:`int`
        An integer suitable for passing to :func:`sys.exit`.
    """
    options = get_options()
    if not os.path.exists(options.fits):
        print("%s does not exist!" % options.fits, file=sys.stderr)
        return 1
    if not os.path.exists(options.sql):
        p = resource_filename('digestor', 'data/' + options.sql)
        if os.path.exists(p):
            options.sql = p
        else:
            print("%s does not exist!" % options.sql, file=sys.stderr)
            return 1
    if options.table is None:
        options.table = os.path.splitext(os.path.basename(options.fits))[0]
    if options.output_sql is None:
        options.output_sql = os.path.join(os.path.dirname(options.fits),
                                          "%s.%s.sql" % (options.schema, options.table))
    if options.output_json is None:
        options.output_json = options.output_sql.replace('sql', 'json')
    if options.log is None:
        options.log = options.output_sql.replace('sql', 'log')
    try:
        sdss = SDSS(options.schema, options.table,
                    description=options.description,
                    merge=options.merge_json)
    except ValueError as e:
        #
        # ValueError indicates failure to process a merge file.
        #
        print(str(e))
        return 1
    sdss.configureLog(options.log, options.verbose)
    log = sdss.logName('sdss.main')
    # ts = datetime.utcnow().replace(tzinfo=utc).strftime('%Y-%m-%dT%H:%M:%S %Z')
    log.debug("options.fits = '%s'", options.fits)
    log.debug("options.sql = '%s'", options.sql)
    log.debug("options.schema = '%s'", options.schema)
    log.debug("options.table = '%s'", options.table)
    log.debug("options.output_sql = '%s'", options.output_sql)
    log.debug("options.output_json = '%s'", options.output_json)
    log.debug("options.log = '%s'", options.log)
    #
    # Preprocess the FITS file.
    #
    sdss.customSTILTS(options.config)
    try:
        dlfits = sdss.addDLColumns(options.fits, ra=options.ra,
                                   overwrite=(not options.keep),
                                   ecliptic=options.ecliptic,
                                   galactic=options.galactic)
    except ValueError as e:
        log.error(str(e))
        return 1
    sdss.parseFITS(dlfits, hdu=options.hdu)
    #
    # Read the SQL file.
    #
    sdss.parseSQL(options.sql)
    #
    # Map the FITS columns to table columns.
    #
    sdss.fixNOFITS(options.config)
    sdss.fixMapping(options.config)
    try:
        sdss.mapColumns()
    except KeyError as k:
        return 1
    #
    # Fix any table definition problems and sort the columns.
    #
    sdss.fixColumns(options.config)
    try:
        sdss.sortColumns()
    except AssertionError as e:
        log.error(str(e))
        return 1
    #
    # Write the SQL file.
    #
    sdss.writeSQL(options.output_sql)
    #
    # Write the JSON file.
    #
    sdss.writeTapSchema(options.output_json)
    #
    # Sort the FITS data table to match the columns.  Do this last so that
    # if it crashes, we at least have the SQL and JSON files.
    #
    try:
        pgfits = sdss.processFITS(hdu=options.hdu,
                                  overwrite=(not options.keep))
    except ValueError as e:
        return 1
    # except Exception as e:
    #     log.error(str(e))
    #     return 2
    return 0
