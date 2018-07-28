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
from argparse import ArgumentParser


_SQLre = {'create': re.compile(r'\s*CREATE\s+TABLE\s+.*\s+\('),
          'comment': re.compile(r'\s*--/(H|T)\s+(.*)$'),
          'column': re.compile(r'\s*(\S+)\s+(\S+)\s*([^,]+),\s*(.*)$'),
          'finish': re.compile(r'\s*\);?')}

_server2post = {'float': 'double precision', 'int': 'integer'}


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
    """
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
    metadata['keys'] = list()
    metadata['key_columns'] = list()
    # metadata['short_description'] = ""
    # metadata['description'] = ""
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

    Returns
    -------
    :class:`str`
        A PostgreSQL-compatible string, or ``None`` if only metadata is detected.

    Notes
    -----
    * Currently, the long description is thrown out.
    """
    log = logging.getLogger(__name__+'.parse_line')
    l = line.strip()
    for r in _SQLre:
        m = _SQLre[r].match(l)
        if m is not None:
            if r == 'create':
                log.debug(r"CREATE TABLE %s.%s (", options.schema, options.table)
                return r"CREATE TABLE %s.%s (" % (options.schema, options.table)
            elif r == 'comment':
                g = m.groups()
                if g[0] == 'H':
                    log.debug("metadata['tables'][0]['description'] += '%s'", g[1])
                    metadata['tables'][0]['description'] += g[1]
                if g[0] == 'T':
                    log.debug("metadata['tables'][0]['long_description'] += '%s'", g[1])
                    # metadata['description'] += g[1]+'\n'
                return None
            elif r == 'column':
                g = m.groups()
                typ = g[1].strip('[]').lower()
                try:
                    post_type = _server2post[typ]
                except KeyError:
                    post_type = typ
                log.debug("    %s %s %s,", g[0].lower(), post_type, g[2])
                log.debug("metadata = '%s'", g[3])
                p, r = parse_column_metadata(g[0].lower(), g[3])
                p['table_name'] = options.table
                if post_type == 'double precision':
                    p['datatype'] = 'double'
                elif post_type.startswith('varchar'):
                    p['datatype'] = 'character'
                    p['size'] = int(post_type.split('(')[1].strip(')'))
                else:
                    p['datatype'] = post_type
                if r is not None:
                    log.debug("rename column %s -> %s", r, g[0].lower())
                metadata['columns'].append(p)
                return "    %s %s %s," % (g[0].lower(), post_type, g[2])
            elif r == 'finish':
                log.debug(");")
                return ');'
    return None


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
    parser = ArgumentParser(description=__doc__,
                            prog=os.path.basename(sys.argv[0]))
    parser.add_argument('-d', '--schema-description', dest='description',
                        metavar='TEXT',
                        default='Sloan Digital Sky Survey Data Relase 14',
                        help='Short description of the schema.')
    parser.add_argument('-j', '--output-json', dest='output_json', metavar='FILE',
                        help='Write table metadata to FILE.')
    parser.add_argument('-o', '--output-sql', dest='output_sql', metavar='FILE',
                        help='Write table definition to FILE.')
    parser.add_argument('-s', '--schema', metavar='SCHEMA',
                        default='sdss_dr14',
                        help='Define table with this schema.')
    parser.add_argument('-t', '--table', metavar='TABLE',
                        help='Set the table name.')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Print extra information.')
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
    with open(options.sql) as SQL:
        for line in SQL:
            out = parse_line(line, options, metadata)
            if out is not None:
                output.append(out)
    create_table = '\n'.join(output) + '\n'
    if options.output_sql is None:
        options.output_sql = os.path.join(os.path.dirname(options.sql),
                                          "%s.%s.sql" % (options.schema, options.table))
    log.debug("options.output_sql = '%s'", options.output_sql)
    with open(options.output_sql, 'w') as POST:
        POST.write(create_table)
    if options.output_json is None:
        options.output_json = os.path.join(os.path.dirname(options.sql),
                                           "%s.%s.json" % (options.schema, options.table))
    log.debug("options.output_json = '%s'", options.output_json)
    with open(options.output_json, 'w') as JSON:
        json.dump(metadata, JSON, indent=4)
    return 0
