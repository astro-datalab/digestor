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
from datetime import datetime
from argparse import ArgumentParser

from pytz import utc

_SQLre = {'create': re.compile(r'\s*CREATE\s+TABLE\s+.*\s+\('),
          'comment': re.compile(r'\s*--/(H|T)\s+(.*)$'),
          'column': re.compile(r'\s*(\S+)\s+(\S+)\s*([^,]+),\s*(.*)$'),
          'finish': re.compile(r'\s*\);?')}

_server2post = {'float': 'double precision', 'int': 'integer'}

#
# Ignore columns that are specific to the SDSS CAS system.
#
_skip_columns = ('htmid', 'loadversion')

_stilts_header = """# {filename}
# {ts}
"""

_stilts_footer = """addcol htm9 "(int)htmIndex(9,{ra},{dec})";
addcol ring256 "(int)healpixRingIndex(8,{ra},{dec})";
addcol nest4096 "(int)healpixNestIndex(12,{ra},{dec})";
addskycoords -inunit deg -outunit deg icrs galactic {ra} {dec} glon glat;
addskycoords -inunit deg -outunit deg icrs ecliptic {ra} {dec} elon elat;
"""

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
    else:
        with open(options.merge_json) as f:
            metadata = json.load(f)
        if metadata['schemas'][0]['schema_name'] != options.schema:
            raise ValueError("You are attempting to merge schema={0} into schema={1}!".format(options.schema, metadata['schemas'][0]['schema_name']))
        for t in metadata['tables']:
            if t['table_name'] == options.table:
                raise ValueError("Table {0} is already defined!".format(options.table))
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
            if r == 'create':
                log.debug(r"CREATE TABLE IF NOT EXISTS %s.%s (", options.schema, options.table)
                return (r"CREATE TABLE IF NOT EXISTS %s.%s (" % (options.schema, options.table),
                        'explodeall;')
            elif r == 'comment':
                g = m.groups()
                if g[0] == 'H':
                    log.debug("metadata['tables'][0]['description'] += '%s'", g[1])
                    metadata['tables'][0]['description'] += g[1]
                if g[0] == 'T':
                    log.debug("metadata['tables'][0]['long_description'] += '%s'", g[1])
                    # metadata['description'] += g[1]+'\n'
                return (None, None)
            elif r == 'column':
                g = m.groups()
                col = g[0].lower()
                if col in _skip_columns:
                    log.debug("Skipping column %s.", col)
                    return (None, None)
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
                if r is not None:
                    try:
                        foo = r.split('[')
                        i = int(foo[1].strip(']')) + 1
                        log.debug('colmeta -name %s %s_%d;', col, foo[0], i)
                        stilts = 'colmeta -name %s %s_%d;' % (col, foo[0], i)
                    except IndexError:
                        log.debug('colmeta -name %s %s;', col, r)
                        stilts = 'colmeta -name %s %s;' % (col, r)
                else:
                    log.debug('colmeta -name %s %s;', col, col.upper())
                    stilts = 'colmeta -name %s %s;' % (col, col.upper())
                metadata['columns'].append(p)
                return ("    %s %s %s," % (col, post_type, g[2]),
                        stilts)
            elif r == 'finish':
                log.debug("End of table definition.")
                return (None, None)
    return (None, None)


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
    :func:`tuple`
        A tuple containing a dictionary containing the parsed metadata
        in TapSchema format, and the original name of the column in the
        FITS file, if detected.
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
                    log.debug("rename %s -> %s", r, column)
                    rename = r
            else:
                log.debug("p['%s'] = %s", tr[m], repr(r))
                p[tr[m]] = r
        except ValueError:
            if m == 'F' and any([column.endswith('_%s' % f) for f in 'ugriz']):
                foo = column.rsplit('_', 1)
                r = "{0}[{1:d}]".format(foo[0], 'ugriz'.index(foo[1])).upper()
                log.debug("rename %s -> %s", r, column)
                rename = r
    return (p, rename)


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
    parser.add_argument('-j', '--output-json', dest='output_json', metavar='FILE',
                        help='Write table metadata to FILE.')
    parser.add_argument('-m', '--merge', dest='merge_json', metavar='FILE',
                        help='Merge metadata in FILE into final metadata output.')
    parser.add_argument('-o', '--output-sql', dest='output_sql', metavar='FILE',
                        help='Write table definition to FILE.')
    parser.add_argument('-r', '--ra', dest='ra', metavar='COLUMN', default='ra',
                        help='Right Ascension is in COLUMN.')
    parser.add_argument('-S', '--output-stilts', dest='output_stilts', metavar='FILE',
                        help='Write stitls commands to FILE.')
    parser.add_argument('-s', '--schema', metavar='SCHEMA',
                        default='sdss_dr14',
                        help='Define table with this schema.')
    parser.add_argument('-t', '--table', metavar='TABLE',
                        help='Set the table name.')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Print extra information.')
    parser.add_argument('sql', help='SQL file to convert.')
    return parser.parse_args()


def finish_table(options, metadata):
    """Add SQL column definitions of Data Lab-added columns.

    Parameters
    ----------
    options : :class:`argparse.Namespace`
        The command-line options.
    metadata : :class:`dict`
        A pre-initialized dictionary containing metadata.

    Returns
    -------
    :class:`list`
        List of SQL column definitions suitable for appending to an
        existing list.
    """

    _stilts_footer = """addcol htm9 "(int)htmIndex(9,{ra},{dec})";
    addcol ring256 "(int)healpixRingIndex(8,{ra},{dec})";
    addcol nest4096 "(int)healpixNestIndex(12,{ra},{dec})";
    addskycoords -inunit deg -outunit deg icrs galactic {ra} {dec} glon glat;
    addskycoords -inunit deg -outunit deg icrs ecliptic {ra} {dec} elon elat;
    # colmeta -name first_snr FIRST_SNR;
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
    metadata['columns'] += columns
    sql = list()
    for c in columns:
        n = c['column_name']
        t = c['datatype']
        if c['datatype'] == 'double':
            t = 'double precision'
        s = '    {0} {1} NOT NULL'.format(n, t)
        if n != 'elat':
            s += ','
        sql.append(s)
    sql.append(') WITH (fillfactor=100);')
    return sql


def main():
    """Entry-point for command-line script.

    Returns
    -------
    :class:`int`
        An integer suitable for passing to :func:`sys.exit`.
    """
    options = get_options()
    ts = datetime.utcnow().replace(tzinfo=utc).strftime('%Y-%m-%dT%H:%M:%S %Z')
    ch = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(levelname)s:%(lineno)s: %(message)s')
    ch.setFormatter(formatter)
    log = logging.getLogger(__name__)
    log.addHandler(ch)
    if options.verbose:
        log.setLevel(logging.DEBUG)
    else:
        log.setLevel(logging.INFO)
    log.debug("options.sql = '%s'", options.sql)
    if options.table is None:
        options.table = os.path.splitext(os.path.basename(options.sql))[0]
    log.debug("options.table = '%s'", options.table)
    output = list()
    metadata = init_metadata(options)
    stilts = list()
    with open(options.sql) as SQL:
        for line in SQL:
            out, st = parse_line(line, options, metadata)
            if out is not None:
                output.append(out)
            if st is not None:
                stilts.append(st)
    #
    # Finish SQL output.
    #
    output += finish_table(options, metadata)
    create_table = '\n'.join(output) + '\n'
    if options.output_sql is None:
        options.output_sql = os.path.join(os.path.dirname(options.sql),
                                          "%s.%s.sql" % (options.schema, options.table))
    log.debug("options.output_sql = '%s'", options.output_sql)
    with open(options.output_sql, 'w') as POST:
        POST.write(create_table)
    #
    # Finish JSON output.
    #
    if options.output_json is None:
        options.output_json = os.path.join(os.path.dirname(options.sql),
                                           "%s.%s.json" % (options.schema, options.table))
    log.debug("options.output_json = '%s'", options.output_json)
    with open(options.output_json, 'w') as JSON:
        json.dump(metadata, JSON, indent=4)
    #
    # Finish STILTS output.
    #
    st = ('\n'.join(stilts) + '\n' +
          _stilts_footer.format(ra=options.ra.lower(),
                                dec=options.ra.lower().replace('ra', 'dec')))
    if options.output_stilts is None:
        options.output_stilts = os.path.join(os.path.dirname(options.sql),
                                             "%s.%s.stilts" % (options.schema, options.table))
    log.debug("options.output_stilts = '%s'", options.output_stilts)
    with open(options.output_stilts, 'w') as STILTS:
        STILTS.write(st)
    return 0
