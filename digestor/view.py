# Licensed under a MIT style license - see LICENSE.rst
# -*- coding: utf-8 -*-
"""
digestor.view
=============

Handle schema metadata for views.
"""
import os
import json
import sys
from argparse import ArgumentParser


def get_options():
    """Parse command-line options.

    Returns
    -------
    :class:`argparse.Namespace`
        The parsed options.
    """
    parser = ArgumentParser(description=__doc__.split("\n")[-2],
                            prog=os.path.basename(sys.argv[0]))
    # parser.add_argument('-c', '--configuration', dest='config', metavar='FILE',
    #                     default=resource_filename('digestor', 'data/sdss.yaml'),
    #                     help='Read table-specific configuration from FILE.')
    parser.add_argument('-d', '--description', dest='description',
                        metavar='TEXT',
                        help='Short description of the view.')
    # parser.add_argument('-E', '--no-ecliptic', dest='ecliptic', action='store_false',
    #                     help='Do not add ecliptic coordinates.')
    # parser.add_argument('-e', '--extension', dest='hdu', metavar='N',
    #                     type=int, default=1,
    #                     help='Read data from FITS HDU N (default %(default)s).')
    # parser.add_argument('-G', '--no-galactic', dest='galactic', action='store_false',
    #                     help='Do not add galactic coordinates.')
    # parser.add_argument('-j', '--output-json', dest='output_json', metavar='FILE',
    #                     help='Write table metadata to FILE.')
    # parser.add_argument('-k', '--keep', action='store_true',
    #                     help='Do not overwrite any existing intermediate files.')
    # parser.add_argument('-l', '--log', dest='log', metavar='FILE',
    #                     help='Log operations to FILE.')
    # parser.add_argument('-m', '--merge', dest='merge_json', metavar='FILE',
    #                     help='Merge metadata in FILE into final metadata output.')
    parser.add_argument('-o', '--output', dest='output', metavar='FILE',
                        help='Write metadata to FILE instead of overwriting input.')
    # parser.add_argument('-p', '--primary-key', dest='pkey', metavar='COLUMN',
    #                     default='objid',
    #                     help='COLUMN is primary key (default %(default)s).')
    # parser.add_argument('-r', '--ra', dest='ra', metavar='COLUMN', default='ra',
    #                     help='Right Ascension is in COLUMN (default %(default)s).')
    parser.add_argument('-s', '--schema', metavar='SCHEMA',
                        help='Override the schema name found in META.')
    # parser.add_argument('-t', '--table', metavar='TABLE',
    #                     help='Set the table name.')
    # parser.add_argument('-v', '--verbose', action='store_true',
    #                     help='Print extra information.')
    parser.add_argument('meta', metavar='META', help='Name of metadata file.')
    parser.add_argument('table', metavar='TABLE', help='Name of base table for view.')
    parser.add_argument('view', metavar='VIEW', help='Name of view.')
    return parser.parse_args()


def main():
    """Entry-point for command-line script.

    Returns
    -------
    :class:`int`
        An integer suitable for passing to :func:`sys.exit`.
    """
    options = get_options()
    with open(options.meta) as j:
        meta = json.load(j)
    if options.schema is None:
        schema = meta['schemas'][0]['schema_name']
    else:
        schema = options.schema
    try:
        table_meta = [t for t in meta['tables'] if t['schema_name'] == schema and t['table_name'] == options.table][0]
    except IndexError:
        print("ERROR: could not find {0}.{1} in the list of tables!".format(schema, options.table))
        return 1
    view_meta = table_meta.copy()
    view_meta['table_name'] = options.view
    view_meta['table_type'] = 'view'
    if options.description is None:
        view_meta['description'] = 'VIEW of {0}.{1}.'.format(schema, options.table)
    else:
        view_meta['description'] = options.description
    print(view_meta)
    return 0
