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
# from datetime import datetime
from argparse import ArgumentParser

from pkg_resources import resource_filename
# from pytz import utc

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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
                    p['table_name'] = self.table
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
                        r = "{0}[{1}]".format(*(r.split(' ')))
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

    def mapColumns(self):
        """Complete mapping of FITS table columns to SQL columns.

        Raises
        ------
        :exc:`KeyError`
            If an expected mapping cannot be found.
        """
        log = self.logName('sdss.SDSS.mapColumns')
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
                                log.debug("FITS: %s -> SQL: %s", fc, sc)
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
                else:
                    msg = "Could not find a FITS column corresponding to %s!"
                    log.error(msg, sc)
                    raise KeyError(msg % sc)
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
    parser.add_argument('-e', '--extension', dest='hdu', metavar='N',
                        type=int, default=1,
                        help='Read data from FITS HDU N (default %(default)s).')
    parser.add_argument('-j', '--output-json', dest='output_json', metavar='FILE',
                        help='Write table metadata to FILE.')
    parser.add_argument('-k', '--keep', action='store_true',
                        help='Do not overwrite any existing intermediate files.')
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
    if options.table is None:
        options.table = os.path.splitext(os.path.basename(options.sql))[0]
    if options.output_sql is None:
        options.output_sql = os.path.join(os.path.dirname(options.sql),
                                          "%s.%s.sql" % (options.schema, options.table))
    if options.output_json is None:
        options.output_json = options.output_sql.replace('sql', 'json')
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
    sdss.configureLog(options.verbose)
    log = sdss.logName('sdss.main')
    # ts = datetime.utcnow().replace(tzinfo=utc).strftime('%Y-%m-%dT%H:%M:%S %Z')
    log.debug("options.fits = '%s'", options.fits)
    log.debug("options.sql = '%s'", options.sql)
    log.debug("options.schema = '%s'", options.schema)
    log.debug("options.table = '%s'", options.table)
    log.debug("options.output_sql = '%s'", options.output_sql)
    log.debug("options.output_json = '%s'", options.output_json)
    #
    # Preprocess the FITS file.
    #
    try:
        dlfits = sdss.addDLColumns(options.fits, ra=options.ra,
                                   overwrite=(not options.keep))
    except ValueError as e:
        log.error(str(e))
        return 1
    sdss.parseFITS(dlfits, hdu=options.extension)
    #
    # Read the SQL file.
    #
    sdss.parseSQL(options.sql)
    #
    # Map the FITS columns to table columns.
    #
    try:
        sdss.mapColumns()
    except KeyError as e:
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
        pgfits = sdss.processFITS(hdu=options.extension,
                                  overwrite=(not options.keep))
    except ValueError as e:
        return 1
    return 0
