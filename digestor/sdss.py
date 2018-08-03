# Licensed under a MIT style license - see LICENSE.rst
# -*- coding: utf-8 -*-
"""
digestor.sdss
=============

Convert SDSS SQL (MS SQL Server) table definitions to Data Lab SQL (PostgreSQL).
"""
import json
import os
import re
import sys
import logging
import subprocess as sub
from datetime import datetime
from argparse import ArgumentParser

from pytz import utc
from astropy.io import fits
from astropy.table import Table

_SQLre = {'comment': re.compile(r'\s*--/(H|T)\s+(.*)$'),
          'column': re.compile(r'\s*(\S+)\s+(\S+)\s*([^,]+),\s*(.*)$')}

_server2post = {'float': 'double precision', 'int': 'integer'}

#
# Ignore columns that are specific to the SDSS CAS system.
#
_skip_columns = ('htmid', 'loadversion')

#
# Defer some pre-processing to STILTS.
#
_stilts_command = """addcol htm9 "(int)htmIndex(9,{ra},{dec})";
addcol ring256 "(int)healpixRingIndex(8,{ra},{dec})";
addcol nest4096 "(int)healpixNestIndex(12,{ra},{dec})";
addskycoords -inunit deg -outunit deg icrs galactic {ra} {dec} glon glat;
addskycoords -inunit deg -outunit deg icrs ecliptic {ra} {dec} elon elat;
"""


def get_options():
    """Parse command-line options.

    Returns
    -------
    :class:`argparse.Namespace`
        The parsed options.
    """
    parser = ArgumentParser(description=__doc__.split("\n")[-2],
                            prog=os.path.basename(sys.argv[0]))
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


def configure_log(options):
    """Set up logging for the module.

    Parameters
    ----------
    options : :class:`argparse.Namespace`
        The command-line options.
    """
    ch = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(levelname)s:%(name)s:%(lineno)s: %(message)s')
    ch.setFormatter(formatter)
    log = logging.getLogger(__name__)
    log.addHandler(ch)
    level = logging.INFO
    if options.verbose:
        level = logging.DEBUG
    log.setLevel(level)
    return


def add_dl_columns(options):
    """Add DL columns to FITS file prior to column reorganization.

    Parameters
    ----------
    options : :class:`argparse.Namespace`
        The command-line options.

    Returns
    -------
    :class:`str`
        The name of the processed file.
    """
    log = logging.getLogger(__name__+'.add_dl_columns')
    out = options.fits.replace('.fits', '.stilts.fits')
    if os.path.exists(out) and options.keep:
        log.info("Using existing file: %s.", out)
        return out
    if os.path.exists(out):
        log.info("Removing existing file: %s.", out)
        os.remove(out)
    cmd = _stilts_command.format(ra=options.ra.lower(),
                                 dec=options.ra.lower().replace('ra', 'dec')).replace('\n', ' ').strip()
    command = ['stilts', 'tpipe', 'in={0.fits}'.format(options),
               "cmd='{0}'".format(cmd), 'ofmt=fits-basic',
               'out={0}'.format(out)]
    log.debug(' '.join(command))
    proc = sub.Popen(command, stdout=sub.PIPE, stderr=sub.PIPE)
    o, e = proc.communicate()
    log.debug('STILTS STDOUT = %s', o)
    if proc.returncode != 0 or e:
        log.error('STILTS returncode = %d', proc.returncode)
        log.error('STILTS STDERR = %s', e)
    return out


def init_metadata(options):
    """Create a dictionary compatible with TapSchema.

    Parameters
    ----------
    options : :class:`argparse.Namespace`
        The command-line options.

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
    if options.merge_json is None:
        metadata = dict()
        metadata['schemas'] = [{'schema_name': options.schema,
                                'description': options.description,
                                'utype': ''},]
        metadata['tables'] = [{'schema_name': options.schema,
                               'table_name': options.table,
                               'table_type': 'table',
                               'utype': '',
                               'description': ''},]
        metadata['columns'] = list()
        metadata['keys'] = [{"key_id": "",
                             "from_table": "",
                             "target_table": "",
                             "description": "",
                             "utype": ""}]
        metadata['key_columns'] = [{"key_id": "",
                                    "from_column": "",
                                    "target_column": ""}]
        metadata['mapping'] = dict()
    else:
        with open(options.merge_json) as f:
            metadata = json.load(f)
        if metadata['schemas'][0]['schema_name'] != options.schema:
            raise ValueError("You are attempting to merge schema={0} into schema={1}!".format(options.schema, metadata['schemas'][0]['schema_name']))
        for t in metadata['tables']:
            if t['table_name'] == options.table:
                raise ValueError("Table {0} is already defined!".format(options.table))
        if 'mapping' not in metadata:
            metadata['mapping'] = dict()
    return metadata


def parse_line(line, options, metadata):
    """Parse a single line from a SQL file.

    Parameters
    ----------
    line : :class:`str`
        A single line from a SQL file.
    options : :class:`argparse.Namespace`
        The command-line options.
    metadata : :class:`dict`
        A pre-initialized dictionary containing metadata.

    Notes
    -----
    * Currently, the long description (``--/T``) is thrown out.
    """
    log = logging.getLogger(__name__+'.parse_line')
    l = line.strip()
    for r in _SQLre:
        m = _SQLre[r].match(l)
        if m is not None:
            if r == 'comment':
                g = m.groups()
                if g[0] == 'H':
                    log.debug("metadata['tables'][0]['description'] += '%s'", g[1])
                    metadata['tables'][0]['description'] += g[1]
                if g[0] == 'T':
                    log.debug("metadata['tables'][0]['long_description'] += '%s'", g[1])
                    # metadata['description'] += g[1]+'\n'
                return
            elif r == 'column':
                g = m.groups()
                col = g[0].lower()
                if col in _skip_columns:
                    log.debug("Skipping column %s.", col)
                    return
                typ = g[1].strip('[]').lower()
                try:
                    post_type = _server2post[typ]
                except KeyError:
                    post_type = typ
                log.debug("    %s %s %s,", col, post_type, g[2])
                log.debug("metadata = '%s'", g[3])
                p, r = parse_column_metadata(col, g[3])
                p['table_name'] = options.table
                if post_type == 'double precision':
                    p['datatype'] = 'double'
                elif post_type.startswith('varchar'):
                    p['datatype'] = 'character'
                    p['size'] = int(post_type.split('(')[1].strip(')'))
                else:
                    p['datatype'] = post_type
                metadata['columns'].append(p)
                if r is not None:
                    metadata['mapping'][col] = r
                return
    return


def parse_column_metadata(column, data):
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
    log = logging.getLogger(__name__+'.parse_column_metadata')
    tr = {'D': 'description',
          'F': 'FITS',
          'K': 'ucd',
          'U': 'unit'}
    defaults = {'D': ('description', 'NO DESCRIPTION'),
                'F': ('FITS', column.upper()),
                'K': ('ucd', None),
                'U': ('unit', None)}
    p = {'table_name': '',  # fill in later
         'column_name': column,
         'description': '',
         'unit': '',
         'ucd': '',
         'utype': '',
         'datatype': '',  # fill in later
         'size': 1,
         'principal': 0,
         'indexed': 0,
         'std': 0,
         }
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
                    log.debug("metadata['mapping']['%s'] = '%s'", column, r)
                    rename = r
            else:
                log.debug("p['%s'] = %s", tr[m], repr(r))
                p[tr[m]] = r
        except ValueError:
            if m == 'F' and any([column.endswith('_%s' % f) for f in 'ugriz']):
                foo = column.rsplit('_', 1)
                r = "{0}[{1:d}]".format(foo[0], 'ugriz'.index(foo[1])).upper()
                log.debug("metadata['mapping']['%s'] = '%s'", column, r)
                rename = r
    return (p, rename)


def finish_table(options):
    """Add SQL column definitions of Data Lab-added columns.

    Parameters
    ----------
    options : :class:`argparse.Namespace`
        The command-line options.

    Returns
    -------
    :class:`list`
        A list suitable for appending to an existing list of columns.
    """
    columns = [{"table_name": options.table,
                "column_name": "htm9",
                "description": "HTM index (order 9 => ~10 arcmin size)",
                "unit": "", "ucd": "", "utype": "",
                "datatype": "integer", "size": 1,
                "principal": 0, "indexed": 1, "std": 0},
               {"table_name": options.table,
                "column_name": "ring256",
                "description": "HEALPIX index (Nsides 256, Ring scheme => ~14 arcmin size)",
                "unit": "", "ucd": "", "utype": "",
                "datatype": "integer", "size": 1,
                "principal": 0, "indexed": 1, "std": 0},
               {"table_name": options.table,
                "column_name": "nest4096",
                "description": "HEALPIX index (Nsides 4096, Nest scheme => ~52 arcsec size",
                "unit": "", "ucd": "", "utype": "",
                "datatype": "integer", "size": 1,
                "principal": 0, "indexed": 1, "std": 0},
               # {"table_name": options.table,
               #  "column_name": "random_id",
               #  "description": "Random ID in the range 0.0 => 100.0",
               #  "unit": "", "ucd": "", "utype": "",
               #  "datatype": "real", "size": 1,
               #  "principal": 0, "indexed": 1, "std": 0},
               {"table_name" : options.table,
                "column_name": "glon",
                "description": "Galactic Longitude",
                "unit": "deg", "ucd": "", "utype": "",
                "datatype": "double", "size": 1,
                "principal": 0, "indexed": 1, "std": 0},
               {"table_name" : options.table,
                "column_name": "glat",
                "description": "Galactic Latitude",
                "unit": "deg", "ucd": "", "utype": "",
                "datatype": "double", "size": 1,
                "principal": 0, "indexed": 1, "std": 0},
               {"table_name": options.table,
                "column_name": "elon",
                "description": "Ecliptic Longitude",
                "unit": "deg", "ucd": "", "utype": "",
                "datatype": "double", "size": 1,
                "principal": 0, "indexed": 0, "std": 0},
               {"table_name": options.table,
                "column_name": "elat",
                "description": "Ecliptic Latitude",
                "unit": "deg", "ucd": "", "utype": "",
                "datatype": "double", "size": 1,
                "principal": 0, "indexed": 0, "std": 0},]
    return columns


def map_columns(options, metadata):
    """Complete mapping of FITS table columns to SQL columns.

    Parameters
    ----------
    options : :class:`argparse.Namespace`
        The command-line options.
    metadata : :class:`dict`
        A pre-initialized dictionary containing metadata.

    Raises
    ------
    :exc:`KeyError`
        If an expected mapping cannot be found.
    """
    log = logging.getLogger(__name__+'.map_columns')
    sql_columns = [c['column_name'] for c in metadata['columns']
                   if c['table_name'] == options.table]
    colnames = list(metadata['fits'].keys())
    del colnames[colnames.index('__filename')]
    for sc in sql_columns:
        if sc in metadata['mapping']:
            #
            # Make sure the column actually exists.
            #
            verify_mapping = False
            mc = metadata['mapping'][sc]
            index = ''
            if '[' in mc:
                foo = mc.split('[')
                mc = foo[0]
                index = '[' + foo[1]
            if mc in colnames:
                log.debug("FITS: %s -> SQL: %s", metadata['mapping'][sc], sc)
                verify_mapping = True
            else:
                #
                # See if there is a column containing underscores that
                # could correspond to this mapping.
                #
                for fc in colnames:
                    for fcl in (fc.lower(), fc.lower().replace('_', ''),):
                        if fcl == mc.lower():
                            log.debug("FITS: %s -> SQL: %s", fc, sc)
                            metadata['mapping'][sc] = fc + index
                            verify_mapping = True
            if not verify_mapping:
                msg = "Could not find a FITS column corresponding to %s!"
                log.error(msg, sc)
                raise KeyError(msg % sc)
        else:
            for fc in colnames:
                for fcl in (fc.lower(), fc.lower().replace('_', ''),):
                    if fcl == sc:
                        log.debug("FITS: %s -> SQL: %s", fc, sc)
                        metadata['mapping'][sc] = fc
                        break
                if sc in metadata['mapping']:
                    break
        if sc not in metadata['mapping']:
            msg = "Could not find a FITS column corresponding to %s!"
            log.error(msg, sc)
            raise KeyError(msg % sc)
    #
    # Check for FITS columns that are NOT mapped to the SQL file.
    #
    for col in colnames:
        if col in metadata['mapping'].values():
            log.debug("FITS column %s will be transferred to SQL.", col)
        else:
            col_array = re.compile(col + r'\[\d+\]')
            if any([col_array.match(sc) is not None for sc in metadata['mapping'].values()]):
                log.debug("FITS column %s will be transferred to SQL.", col)
            else:
                log.warning("FITS column %s will be dropped from SQL!", col)
    return


def sort_columns(options, metadata):
    """Sort the SQL columns for best performance.

    Parameters
    ----------
    options : :class:`argparse.Namespace`
        The command-line options.
    metadata : :class:`dict`
        A pre-initialized dictionary containing metadata.
    """
    ordered = ('bigint', 'double', 'integer', 'real', 'smallint', 'character')
    new_columns = list()
    for o in ordered:
        for c in metadata['columns']:
            if c['table_name'] == options.table and c['datatype'] == o:
                new_columns.append(c)
    assert len(new_columns) == len([c['column_name'] for c in metadata['columns']
                                                     if c['table_name'] == options.table])
    for i, c in enumerate(metadata['columns']):
        if c['table_name'] == options.table:
            metadata['columns'][i] = new_columns.pop(0)
    return


def process_fits(options, metadata):
    """Convert a pre-processed FITS file into one ready for database loading.

    Parameters
    ----------
    options : :class:`argparse.Namespace`
        The command-line options.
    metadata : :class:`dict`
        A pre-initialized dictionary containing metadata.

    Raises
    ------
    :exc:`ValueError`
        If the FITS data type cannot be converted to SQL.
    """
    log = logging.getLogger(__name__+'.process_fits')
    type_map = {'bigint': ('K', 'J', 'I', 'B'),
                'integer': ('J', 'I', 'B'),
                'smallint': ('I', 'B'),
                'double': ('D', 'E'),
                'real': ('E',),
                'character': ('A',)}
    rebase = re.compile(r'^(\d+)(\D+)')
    columns = [c for c in metadata['columns']
               if c['table_name'] == options.table]
    for col in columns:
        fcol = metadata['mapping'][col['column_name']]
        try:
            ftype = metadata['fits'][fcol]
        except KeyError:
            ftype = metadata['fits'][fcol.split('[')[0]]
        fbasetype = rebase.sub(r'\2', ftype)
        if fbasetype == type_map[col['datatype']][0]:
            log.debug("Type match for %s -> %s.", fcol, col['column_name'])
        elif fbasetype in type_map[col['datatype']]:
            log.debug("Safe type conversion possible for %s (%s) -> %s (%s).",
                      fcol, fbasetype, col['column_name'], col['datatype'])
        elif fbasetype == 'A' and col['datatype'] == 'bigint':
            log.debug("String to integer conversion required for %s -> %s.", fcol, col['column_name'])
        else:
            msg = "No safe data type conversion possible for %s (%s) -> %s (%s)!"
            log.error(msg, fcol, fbasetype, col['column_name'], col['datatype'])
            # raise ValueError(msg % (fcol, fbasetype, col['column_name'], col['datatype']))
    return


def construct_sql(options, metadata):
    """Construct a CREATE TABLE statement from the `metadata`.

    Parameters
    ----------
    options : :class:`argparse.Namespace`
        The command-line options.
    metadata : :class:`dict`
        A pre-initialized dictionary containing metadata.

    Returns
    -------
    :class:`str`
        A SQL table definition.
    """
    log = logging.getLogger(__name__+'.parse_column_metadata')
    if options.output_sql is None:
        options.output_sql = os.path.join(os.path.dirname(options.sql),
                                          "%s.%s.sql" % (options.schema, options.table))
    log.debug("options.output_sql = '%s'", options.output_sql)
    sql = [r"CREATE TABLE IF EXISTS {0.schema}.{0.table} (".format(options)]
    for c in metadata['columns']:
        if c['table_name'] == options.table:
            typ = c['datatype']
            if typ == 'double':
                typ = 'double precision'
            if typ == 'character':
                typ = 'varchar({size})'.format(**c)
            sql.append("    {0} {1} NOT NULL,".format(c['column_name'], typ))
    sql[-1] = sql[-1].replace(',', '')
    sql.append(r") WITH (fillfactor=100);")
    return '\n'.join(sql) + '\n'


def main():
    """Entry-point for command-line script.

    Returns
    -------
    :class:`int`
        An integer suitable for passing to :func:`sys.exit`.
    """
    options = get_options()
    configure_log(options)
    log = logging.getLogger(__name__+'.main')
    # ts = datetime.utcnow().replace(tzinfo=utc).strftime('%Y-%m-%dT%H:%M:%S %Z')
    log.debug("options.fits = '%s'", options.fits)
    log.debug("options.sql = '%s'", options.sql)
    if options.table is None:
        options.table = os.path.splitext(os.path.basename(options.sql))[0]
    log.debug("options.table = '%s'", options.table)
    #
    # Preprocess the FITS file.
    #
    dlfits = add_dl_columns(options)
    #
    # Process the metadata.
    #
    metadata = init_metadata(options)
    with open(options.sql) as SQL:
        for line in SQL:
            parse_line(line, options, metadata)
    #
    # Finish SQL output.
    #
    metadata['columns'] += finish_table(options)
    #
    # Map the FITS columns to table columns.
    #
    # log.debug("t = Table.read('%s', hdu=%d)", dlfits, options.hdu)
    # t = Table.read(dlfits, hdu=options.hdu)
    with fits.open(dlfits) as hdulist:
        fits_names = hdulist[options.hdu].columns.names
        fits_types = hdulist[options.hdu].columns.formats
    metadata['fits'] = {'__filename': dlfits}
    for i, f in enumerate(fits_names):
        metadata['fits'][f] = fits_types[i]
    map_columns(options, metadata)
    #
    # Sort the columns.
    #
    sort_columns(options, metadata)
    #
    # Sort the FITS data table to match the columns.
    #
    process_fits(options, metadata)
    #
    # Write the SQL file.
    #
    create_table = construct_sql(options, metadata)
    with open(options.output_sql, 'w') as POST:
        POST.write(create_table)
    #
    # Finish JSON output.
    #
    if options.output_json is None:
        options.output_json = os.path.join(os.path.dirname(options.sql),
                                           "%s.%s.json" % (options.schema, options.table))
    log.debug("options.output_json = '%s'", options.output_json)
    del metadata['mapping']
    del metadata['fits']
    with open(options.output_json, 'w') as JSON:
        json.dump(metadata, JSON, indent=4)
    return 0
