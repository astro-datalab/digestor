#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Convert SDSS SQL (MS SQL Server) table definitions to Data Lab SQL (PostgreSQL).
"""
import json
import os
import re
import sys
import logging
from argparse import ArgumentParser


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
    :class:`dict`
        A dictionary containing the parsed metadata, and suitable for
        writing to *e.g.* a JSON file.
    """
    log = logging.getLogger(__name__+'.parse_column_metadata')
    defaults = {'D': ('description', 'NO DESCRIPTION'),
                'F': ('FITS', column.upper()),
                'K': ('ucd', None),
                'U': ('unit', None)}
    p = dict()
    for m in 'DFKU':
        try:
            i = data.index('--/%s' % m)
            try:
                j = data.index('--', i + 2)
            except ValueError:
                j = len(data)
            r = data[i + 5:j].strip()
            if m == 'F':
                # log.debug(r)
                if ' ' in r:
                    r = "{0}[{1}]".format(*(r.split(' ')))
                r = r.upper()
            log.debug("metadata['%s']['%s'] = %s", column, defaults[m][0], repr(r))
            p[defaults[m][0]] = r
            if r == 'NOFITS':
                log.warning("Column %s is not defined in the corresponding FITS file!", column)
        except ValueError:
            if m == 'F' and any([column.endswith('_%s' % f) for f in 'ugriz']):
                foo = column.rsplit('_', 1)
                r = "{0}[{1:d}]".format(foo[0], 'ugriz'.index(foo[1])).upper()
                log.debug("metadata['%s']['%s'] = %s", column, defaults[m][0], repr(r))
                p[defaults[m][0]] = r
            else:
                log.debug("metadata['%s']['%s'] = %s", column, defaults[m][0], repr(defaults[m][1]))
                p[defaults[m][0]] = defaults[m][1]
    return p


def main():
    """Entry-point for command-line script.

    Returns
    -------
    :class:`int`
        An integer suitable for passing to :func:`sys.exit`.
    """
    parser = ArgumentParser(description=__doc__,
                            prog=os.path.basename(sys.argv[0]))
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
    options = parser.parse_args()
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
    metadata = dict()
    metadata['short_description'] = ""
    metadata['description'] = ""
    metadata['columns'] = dict()
    server2post = {'float': 'double precision', 'int': 'integer'}
    create = re.compile(r'\s*CREATE\s+TABLE\s+.*\s+\(')
    comment = re.compile(r'\s*--/(H|T)\s+(.*)$')
    column = re.compile(r'\s*(\S+)\s+(\S+)\s*([^,]+),\s*(.*)$')
    finish = re.compile(r'\s*\);?')
    with open(options.sql) as SQL:
        for line in SQL:
            l = line.strip()
            m = create.match(l)
            if m is not None:
                log.debug("CREATE TABLE %s.%s (", options.schema, options.table)
                output.append("CREATE TABLE %s.%s (" % (options.schema, options.table))
                continue
            m = comment.match(l)
            if m is not None:
                g = m.groups()
                if g[0] == 'H':
                    log.debug("metadata['short_description'] += '%s'", g[1])
                    metadata['short_description'] += g[1]
                if g[0] == 'T':
                    log.debug("metadata['description'] += '%s'", g[1])
                    metadata['description'] += g[1]+'\n'
                continue
            m = column.match(l)
            if m is not None:
                g = m.groups()
                typ = g[1].strip('[]').lower()
                try:
                    post_type = server2post[typ]
                except KeyError:
                    post_type = typ
                log.debug("    %s %s %s,", g[0].lower(), post_type, g[2])
                log.debug("metadata = '%s'", g[3])
                output.append("    %s %s %s," % (g[0].lower(), post_type, g[2]))
                metadata['columns'][g[0].lower()] = parse_column_metadata(g[0].lower(), g[3])
                continue
            m = finish.match(l)
            if m is not None:
                log.debug(");")
                output.append(');')
                continue
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


if __name__ == '__main__':
    sys.exit(main())
