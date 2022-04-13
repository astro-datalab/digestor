# Licensed under a MIT style license - see LICENSE.rst
# -*- coding: utf-8 -*-
"""Test digestor.sdss.
"""
import os
import unittest
import unittest.mock as mock
from tempfile import NamedTemporaryFile, TemporaryDirectory

import numpy as np

from ..sdss import SDSS, get_options
from .utils import DigestorCase


class TestSDSS(DigestorCase):
    """Test digestor.sdss.
    """

    def setUp(self):
        super().setUp()
        self.schema = 'sdss'
        self.table = 'spectra'
        self.stable = "{0.schema}.{0.table}".format(self)
        self.description = 'sdss spectra'
        self.sdss = SDSS(self.schema, self.table,
                         description=self.description)

    def test_get_options(self):
        """Test command-line arguments.
        """
        with mock.patch('sys.argv', ['sdss2dl', '-r', 'plug_ra', '-t', 'specobjall',
                                     'specObj-dr14.fits', 'specobjall.sql']):
            self.options = get_options()
        self.assertEqual(self.options.sql, 'specobjall.sql')
        self.assertFalse(self.options.verbose)
        self.assertEqual(self.options.table, 'specobjall')
        self.assertEqual(self.options.schema, 'sdss_dr14')
        self.assertIsNone(self.options.output_sql)
        self.assertIsNone(self.options.output_json)
        self.assertIsNone(self.options.merge_json)

    def test_sdss_joinid(self):
        """Test sdss_joinid option.
        """
        self.assertFalse(self.sdss.join)
        s = SDSS(self.schema, self.table,
                 description=self.description, join=True)
        self.assertTrue(s.join)
        self.assertEqual(s.tapSchema['columns'][-1]['column_name'], 'sdss_joinid')

    def test_parse_sql(self):
        """Test parsing a whole SQL file.
        """
        sql = r"""CREATE TABLE specObjAll(
--/H This is a description.
  foo real NOT NULL, --/D this is a column
)
"""
        with NamedTemporaryFile('w+') as f:
            f.write(sql)
            f.seek(0)
            self.sdss.parseSQL(f.name)

    def test_parse_line(self):
        """Test parsing single SQL lines.
        """
        self.sdss.parseLine(r'CREATE TABLE specObjAll  (  ')
        self.sdss.parseLine('--')
        self.sdss.parseLine('--/H This is the short description')
        self.assertEqual(self.sdss.tapSchema['tables'][0]['description'], 'This is the short description')
        self.sdss.parseLine('--/T This is the long description')
        # self.assertEqual(self.sdss.tapSchema['tables'][0]['description'], 'This is the long description\nThis is the long description\n')
        self.sdss.parseLine('   column int NOT NULL, --/U mm --/D Column description --/F MY_COLUMN')
        self.assertEqual(self.sdss.tapSchema['columns'][-1]['column_name'], 'column')
        self.assertEqual(self.sdss.tapSchema['columns'][-1]['datatype'], 'integer')
        self.assertEqual(self.sdss.tapSchema['columns'][-1]['unit'], 'mm')
        self.assertEqual(self.sdss.tapSchema['columns'][-1]['description'], 'Column description')
        self.assertEqual(self.sdss.mapping['column'], 'MY_COLUMN')
        self.sdss.parseLine('   column2 real NOT NULL, --/U deg --/D Column description --/F RA')
        self.assertEqual(self.sdss.tapSchema['columns'][-1]['column_name'], 'column2')
        self.assertEqual(self.sdss.tapSchema['columns'][-1]['datatype'], 'real')
        self.assertEqual(self.sdss.tapSchema['columns'][-1]['unit'], 'deg')
        self.assertEqual(self.sdss.tapSchema['columns'][-1]['description'], 'Column description')
        self.assertEqual(self.sdss.mapping['column2'], 'RA')
        self.sdss.parseLine('   column3 varchar(16) NOT NULL, --/K UCD --/D Column description --/F RA')
        self.assertEqual(self.sdss.tapSchema['columns'][-1]['column_name'], 'column3')
        self.assertEqual(self.sdss.tapSchema['columns'][-1]['datatype'], 'character')
        self.assertEqual(self.sdss.tapSchema['columns'][-1]['size'], 16)
        self.assertEqual(self.sdss.tapSchema['columns'][-1]['unit'], '')
        self.assertEqual(self.sdss.tapSchema['columns'][-1]['ucd'], 'UCD')
        self.assertEqual(self.sdss.tapSchema['columns'][-1]['description'], 'Column description')
        self.sdss.parseLine('   column4 float NOT NULL, --/K UCD --/D Column description --/F DEC')
        self.assertEqual(self.sdss.tapSchema['columns'][-1]['column_name'], 'column4')
        self.assertEqual(self.sdss.tapSchema['columns'][-1]['datatype'], 'double')
        self.assertEqual(self.sdss.tapSchema['columns'][-1]['size'], 1)
        self.assertEqual(self.sdss.tapSchema['columns'][-1]['unit'], '')
        self.assertEqual(self.sdss.tapSchema['columns'][-1]['ucd'], 'UCD')
        self.assertEqual(self.sdss.tapSchema['columns'][-1]['description'], 'Column description')
        self.sdss.parseLine('    loadVersion  int NOT NULL, --/D Load Version --/K ID_TRACER --/F NOFITS')
        # self.sdss.parseLine('    z real NOT NULL, --/D Redshift')
        self.sdss.parseLine('    snMedian_u real NOT NULL --/D S/N --/F sn_median 0')
        self.assertEqual(self.sdss.mapping['snmedian_u'], 'SN_MEDIAN[0]')
        self.sdss.parseLine('  ); ')

    def test_parse_column_metadata(self):
        """Test parsing metadata of individual columns.
        """
        d, r = self.sdss.parseColumnMetadata('foo', '--/U mm --/D Random column.')
        self.assertEqual(d['unit'], 'mm')
        self.assertEqual(d['description'], 'Random column.')
        d, r = self.sdss.parseColumnMetadata('foo', '--/F bar --/K ID_CATALOG --/D Random column.')
        self.assertEqual(d['ucd'], 'ID_CATALOG')
        self.assertEqual(d['description'], 'Random column.')
        self.assertEqual(r, 'BAR')
        d, r = self.sdss.parseColumnMetadata('mag_g', '--/F mag 1 --/D Random column.')
        self.assertEqual(d['description'], 'Random column.')
        self.assertEqual(r, 'MAG[1]')
        d, r = self.sdss.parseColumnMetadata('extra', '--/F NOFITS --/D Random column. --/U arcsec')
        self.assertEqual(d['unit'], 'arcsec')
        self.assertEqual(d['description'], 'Random column.')
        d, r = self.sdss.parseColumnMetadata('flux_u', '--/U nanomaggies --/D Random column.')
        self.assertEqual(d['unit'], 'nanomaggies')
        self.assertEqual(d['description'], 'Random column.')

    def test_fix_nofits(self):
        """Test adjustment of missing columns with YAML configuration.
        """
        yaml = """sdss:
    spectra:
        NOFITS:
            glon: drop
            glat: drop
        """
        self.assertEqual(len(self.sdss.NOFITS), 0)
        with NamedTemporaryFile('w+') as f:
            f.write(yaml)
            f.seek(0)
            self.sdss.fixNOFITS(f.name)
        self.assertEqual(self.sdss.NOFITS['glon'], 'drop')
        self.assertEqual(self.sdss.NOFITS['glat'], 'drop')
        self.sdss.table = 'foo'
        self.sdss.fixNOFITS(f.name)

    def test_fix_mapping(self):
        """Test adjustment of column mapping with YAML configuration.
        """
        yaml = """sdss:
    spectra:
        mapping:
            glon: L
            glat: B
        """
        with NamedTemporaryFile('w+') as f:
            f.write(yaml)
            f.seek(0)
            self.sdss.fixMapping(f.name)
        self.assertEqual(self.sdss.mapping['glon'], 'L')
        self.assertEqual(self.sdss.mapping['glat'], 'B')
        self.sdss.table = 'foo'
        self.sdss.fixMapping(f.name)

    def test_map_columns(self):
        """Test mapping of FITS columns to SQL columns.
        """
        self.sdss.tapSchema['columns'] += [{"table_name": "{0.table}".format(self),
                                            "column_name": "mag_u",
                                            "description": "u Magnitude",
                                            "unit": "", "ucd": "", "utype": "",
                                            "datatype": "real", "size": 1,
                                            "principal": 0, "indexed": 0, "std": 0},
                                           {"table_name": "{0.table}".format(self),
                                            "column_name": "mag_g",
                                            "description": "g Magnitude",
                                            "unit": "", "ucd": "", "utype": "",
                                            "datatype": "real", "size": 1,
                                            "principal": 0, "indexed": 0, "std": 0},
                                           {"table_name": "{0.table}".format(self),
                                            "column_name": "magivar_u",
                                            "description": "u ivar",
                                            "unit": "", "ucd": "", "utype": "",
                                            "datatype": "real", "size": 1,
                                            "principal": 0, "indexed": 0, "std": 0},
                                           {"table_name": "{0.table}".format(self),
                                            "column_name": "magivar_g",
                                            "description": "g ivar",
                                            "unit": "", "ucd": "", "utype": "",
                                            "datatype": "real", "size": 1,
                                            "principal": 0, "indexed": 0, "std": 0},
                                           {"table_name": "{0.table}".format(self),
                                            "column_name": "no_fits_keep",
                                            "description": "keeper",
                                            "unit": "", "ucd": "", "utype": "",
                                            "datatype": "real", "size": 1,
                                            "principal": 0, "indexed": 0, "std": 0},
                                           {"table_name": "{0.table}".format(self),
                                            "column_name": "no_fits_drop",
                                            "description": "dropper",
                                            "unit": "", "ucd": "", "utype": "",
                                            "datatype": "real", "size": 1,
                                            "principal": 0, "indexed": 0, "std": 0}]
        self.sdss.mapping = {'mag_u': 'MAG[0]', 'mag_g': 'MAG[1]',
                             'magivar_u': 'MAGIVAR[0]', 'magivar_g': 'MAGIVAR[1]'}
        self.sdss.FITS = {'e_lon': 'D', 'e_lat': 'D',
                          'g_lon': 'D', 'g_lat': 'D',
                          'HTM9': 'J', 'ring256': 'J',
                          'nest4096': 'J', 'MAG': '2E',
                          'MAG_IVAR': '2E',
                          'FOOBAR': '16A'}
        self.sdss.NOFITS = {'no_fits_keep': 'defer', 'no_fits_drop': 'drop'}
        self.sdss.mapColumns()
        final_mapping = {'mag_u': 'MAG[0]', 'mag_g': 'MAG[1]',
                         'magivar_u': 'MAG_IVAR[0]', 'magivar_g': 'MAG_IVAR[1]',
                         'htm9': 'HTM9', 'ring256': 'ring256', 'nest4096': 'nest4096',
                         'glon': 'g_lon', 'glat': 'g_lat',
                         'elon': 'e_lon', 'elat': 'e_lat'}
        self.assertDictEqual(self.sdss.mapping, final_mapping)
        self.assertLog(-1, 'FITS column FOOBAR will be dropped from SQL!')

    def test_map_columns_no_random(self):
        """Test turning off random column.
        """
        self.sdss.random = False
        del self.sdss.tapSchema['columns'][3]
        self.sdss.tapSchema['columns'] += [{"table_name": "{0.table}".format(self),
                                            "column_name": "mag_u",
                                            "description": "u Magnitude",
                                            "unit": "", "ucd": "", "utype": "",
                                            "datatype": "real", "size": 1,
                                            "principal": 0, "indexed": 0, "std": 0},
                                           {"table_name": "{0.table}".format(self),
                                            "column_name": "mag_g",
                                            "description": "g Magnitude",
                                            "unit": "", "ucd": "", "utype": "",
                                            "datatype": "real", "size": 1,
                                            "principal": 0, "indexed": 0, "std": 0},
                                           {"table_name": "{0.table}".format(self),
                                            "column_name": "magivar_u",
                                            "description": "u ivar",
                                            "unit": "", "ucd": "", "utype": "",
                                            "datatype": "real", "size": 1,
                                            "principal": 0, "indexed": 0, "std": 0},
                                           {"table_name": "{0.table}".format(self),
                                            "column_name": "magivar_g",
                                            "description": "g ivar",
                                            "unit": "", "ucd": "", "utype": "",
                                            "datatype": "real", "size": 1,
                                            "principal": 0, "indexed": 0, "std": 0},
                                           {"table_name": "{0.table}".format(self),
                                            "column_name": "no_fits_keep",
                                            "description": "keeper",
                                            "unit": "", "ucd": "", "utype": "",
                                            "datatype": "real", "size": 1,
                                            "principal": 0, "indexed": 0, "std": 0},
                                           {"table_name": "{0.table}".format(self),
                                            "column_name": "no_fits_drop",
                                            "description": "dropper",
                                            "unit": "", "ucd": "", "utype": "",
                                            "datatype": "real", "size": 1,
                                            "principal": 0, "indexed": 0, "std": 0}]
        self.sdss.mapping = {'mag_u': 'MAG[0]', 'mag_g': 'MAG[1]',
                             'magivar_u': 'MAGIVAR[0]', 'magivar_g': 'MAGIVAR[1]'}
        self.sdss.FITS = {'e_lon': 'D', 'e_lat': 'D',
                          'g_lon': 'D', 'g_lat': 'D',
                          'HTM9': 'J', 'ring256': 'J',
                          'nest4096': 'J', 'MAG': '2E',
                          'MAG_IVAR': '2E',
                          'FOOBAR': '16A'}
        self.sdss.NOFITS = {'no_fits_keep': 'defer', 'no_fits_drop': 'drop'}
        self.sdss.mapColumns()
        final_mapping = {'mag_u': 'MAG[0]', 'mag_g': 'MAG[1]',
                         'magivar_u': 'MAG_IVAR[0]', 'magivar_g': 'MAG_IVAR[1]',
                         'htm9': 'HTM9', 'ring256': 'ring256', 'nest4096': 'nest4096',
                         'glon': 'g_lon', 'glat': 'g_lat',
                         'elon': 'e_lon', 'elat': 'e_lat'}
        self.assertDictEqual(self.sdss.mapping, final_mapping)
        self.assertNotIn('random_id', self.sdss.colNames)

    def test_map_columns_missing_fits_array_column(self):
        """Test mapColumns with a missing, array-valued column.
        """
        self.sdss.tapSchema['columns'] += [{"table_name": "{0.table}".format(self),
                                            "column_name": "mag_u",
                                            "description": "u Magnitude",
                                            "unit": "", "ucd": "", "utype": "",
                                            "datatype": "real", "size": 1,
                                            "principal": 0, "indexed": 0, "std": 0},
                                           {"table_name": "{0.table}".format(self),
                                            "column_name": "mag_g",
                                            "description": "g Magnitude",
                                            "unit": "", "ucd": "", "utype": "",
                                            "datatype": "real", "size": 1,
                                            "principal": 0, "indexed": 0, "std": 0},
                                           {"table_name": "{0.table}".format(self),
                                            "column_name": "magivar_u",
                                            "description": "u ivar",
                                            "unit": "", "ucd": "", "utype": "",
                                            "datatype": "real", "size": 1,
                                            "principal": 0, "indexed": 0, "std": 0},
                                           {"table_name": "{0.table}".format(self),
                                            "column_name": "magivar_g",
                                            "description": "g ivar",
                                            "unit": "", "ucd": "", "utype": "",
                                            "datatype": "real", "size": 1,
                                            "principal": 0, "indexed": 0, "std": 0},
                                           {"table_name": "{0.table}".format(self),
                                            "column_name": "no_fits_keep",
                                            "description": "keeper",
                                            "unit": "", "ucd": "", "utype": "",
                                            "datatype": "real", "size": 1,
                                            "principal": 0, "indexed": 0, "std": 0},
                                           {"table_name": "{0.table}".format(self),
                                            "column_name": "no_fits_drop",
                                            "description": "dropper",
                                            "unit": "", "ucd": "", "utype": "",
                                            "datatype": "real", "size": 1,
                                            "principal": 0, "indexed": 0, "std": 0}]
        self.sdss.tapSchema['columns'] += [{"table_name": "{0.table}".format(self),
                                            "column_name": "flux_u",
                                            "description": "u flux",
                                            "unit": "", "ucd": "", "utype": "",
                                            "datatype": "real", "size": 1,
                                            "principal": 0, "indexed": 0, "std": 0},
                                           {"table_name": "{0.table}".format(self),
                                            "column_name": "flux_g",
                                            "description": "g flux",
                                            "unit": "", "ucd": "", "utype": "",
                                            "datatype": "real", "size": 1,
                                            "principal": 0, "indexed": 0, "std": 0}]
        self.sdss.mapping = {'mag_u': 'MAG[0]', 'mag_g': 'MAG[1]',
                             'magivar_u': 'MAGIVAR[0]', 'magivar_g': 'MAGIVAR[1]',
                             'flux_u': 'FLUX[0]', 'flux_g': 'FLUX[1]'}
        self.sdss.FITS = {'e_lon': 'D', 'e_lat': 'D',
                          'g_lon': 'D', 'g_lat': 'D',
                          'HTM9': 'J', 'ring256': 'J',
                          'nest4096': 'J', 'MAG': '2E',
                          'MAG_IVAR': '2E',
                          'FOOBAR': '16A'}
        self.sdss.NOFITS = {'no_fits_keep': 'defer', 'no_fits_drop': 'drop'}
        with self.assertRaises(KeyError) as e:
            self.sdss.mapColumns()
        self.assertEqual(e.exception.args[0], 'Could not find a FITS column corresponding to flux_u!')

    def test_map_columns_missing_fits_column(self):
        """Test mapColumns with a missing column.
        """
        self.sdss.tapSchema['columns'] += [{"table_name": "{0.table}".format(self),
                                            "column_name": "mag_u",
                                            "description": "u Magnitude",
                                            "unit": "", "ucd": "", "utype": "",
                                            "datatype": "real", "size": 1,
                                            "principal": 0, "indexed": 0, "std": 0},
                                           {"table_name": "{0.table}".format(self),
                                            "column_name": "mag_g",
                                            "description": "g Magnitude",
                                            "unit": "", "ucd": "", "utype": "",
                                            "datatype": "real", "size": 1,
                                            "principal": 0, "indexed": 0, "std": 0},
                                           {"table_name": "{0.table}".format(self),
                                            "column_name": "magivar_u",
                                            "description": "u ivar",
                                            "unit": "", "ucd": "", "utype": "",
                                            "datatype": "real", "size": 1,
                                            "principal": 0, "indexed": 0, "std": 0},
                                           {"table_name": "{0.table}".format(self),
                                            "column_name": "magivar_g",
                                            "description": "g ivar",
                                            "unit": "", "ucd": "", "utype": "",
                                            "datatype": "real", "size": 1,
                                            "principal": 0, "indexed": 0, "std": 0},
                                           {"table_name": "{0.table}".format(self),
                                            "column_name": "no_fits_keep",
                                            "description": "keeper",
                                            "unit": "", "ucd": "", "utype": "",
                                            "datatype": "real", "size": 1,
                                            "principal": 0, "indexed": 0, "std": 0},
                                           {"table_name": "{0.table}".format(self),
                                            "column_name": "no_fits_drop",
                                            "description": "dropper",
                                            "unit": "", "ucd": "", "utype": "",
                                            "datatype": "real", "size": 1,
                                            "principal": 0, "indexed": 0, "std": 0}]
        self.sdss.tapSchema['columns'] += [{"table_name": "{0.table}".format(self),
                                            "column_name": "flux_u",
                                            "description": "u flux",
                                            "unit": "", "ucd": "", "utype": "",
                                            "datatype": "real", "size": 1,
                                            "principal": 0, "indexed": 0, "std": 0},
                                           {"table_name": "{0.table}".format(self),
                                            "column_name": "flux_g",
                                            "description": "g flux",
                                            "unit": "", "ucd": "", "utype": "",
                                            "datatype": "real", "size": 1,
                                            "principal": 0, "indexed": 0, "std": 0}]
        self.sdss.mapping = {'mag_u': 'MAG[0]', 'mag_g': 'MAG[1]',
                             'magivar_u': 'MAGIVAR[0]', 'magivar_g': 'MAGIVAR[1]',
                             'flux_u': 'FLUX[0]', 'flux_g': 'FLUX[1]'}
        self.sdss.FITS = {'e_lon': 'D', 'e_lat': 'D',
                          'g_lon': 'D', 'g_lat': 'D',
                          'HTM9': 'J', 'ring256': 'J',
                          'nest4096': 'J', 'MAG': '2E',
                          'MAG_IVAR': '2E',
                          'FOOBAR': '16A'}
        self.sdss.NOFITS = {'no_fits_keep': 'defer', 'no_fits_drop': 'drop'}
        self.sdss.FITS['FLUX'] = '2E'
        self.sdss.tapSchema['columns'] += [{"table_name": "{0.table}".format(self),
                                            "column_name": "z",
                                            "description": "z",
                                            "unit": "", "ucd": "", "utype": "",
                                            "datatype": "real", "size": 1,
                                            "principal": 0, "indexed": 0, "std": 0}]
        self.sdss.mapping = {'mag_u': 'MAG[0]', 'mag_g': 'MAG[1]',
                             'magivar_u': 'MAGIVAR[0]', 'magivar_g': 'MAGIVAR[1]',
                             'flux_u': 'FLUX[0]', 'flux_g': 'FLUX[1]'}
        with self.assertRaises(KeyError) as e:
            self.sdss.mapColumns()
        self.assertEqual(e.exception.args[0], 'Could not find a FITS column corresponding to z!')

    def test_map_columns_missing_nofits_instruction(self):
        """Test a missing NOFITS instruction.
        """
        self.sdss.tapSchema['columns'] += [{"table_name": "{0.table}".format(self),
                                            "column_name": "mag_u",
                                            "description": "u Magnitude",
                                            "unit": "", "ucd": "", "utype": "",
                                            "datatype": "real", "size": 1,
                                            "principal": 0, "indexed": 0, "std": 0},
                                           {"table_name": "{0.table}".format(self),
                                            "column_name": "mag_g",
                                            "description": "g Magnitude",
                                            "unit": "", "ucd": "", "utype": "",
                                            "datatype": "real", "size": 1,
                                            "principal": 0, "indexed": 0, "std": 0},
                                           {"table_name": "{0.table}".format(self),
                                            "column_name": "magivar_u",
                                            "description": "u ivar",
                                            "unit": "", "ucd": "", "utype": "",
                                            "datatype": "real", "size": 1,
                                            "principal": 0, "indexed": 0, "std": 0},
                                           {"table_name": "{0.table}".format(self),
                                            "column_name": "magivar_g",
                                            "description": "g ivar",
                                            "unit": "", "ucd": "", "utype": "",
                                            "datatype": "real", "size": 1,
                                            "principal": 0, "indexed": 0, "std": 0},
                                           {"table_name": "{0.table}".format(self),
                                            "column_name": "no_fits_keep",
                                            "description": "keeper",
                                            "unit": "", "ucd": "", "utype": "",
                                            "datatype": "real", "size": 1,
                                            "principal": 0, "indexed": 0, "std": 0},
                                           {"table_name": "{0.table}".format(self),
                                            "column_name": "no_fits_drop",
                                            "description": "dropper",
                                            "unit": "", "ucd": "", "utype": "",
                                            "datatype": "real", "size": 1,
                                            "principal": 0, "indexed": 0, "std": 0}]
        self.sdss.tapSchema['columns'] += [{"table_name": "{0.table}".format(self),
                                            "column_name": "flux_u",
                                            "description": "u flux",
                                            "unit": "", "ucd": "", "utype": "",
                                            "datatype": "real", "size": 1,
                                            "principal": 0, "indexed": 0, "std": 0},
                                           {"table_name": "{0.table}".format(self),
                                            "column_name": "flux_g",
                                            "description": "g flux",
                                            "unit": "", "ucd": "", "utype": "",
                                            "datatype": "real", "size": 1,
                                            "principal": 0, "indexed": 0, "std": 0}]
        self.sdss.FITS = {'e_lon': 'D', 'e_lat': 'D',
                          'g_lon': 'D', 'g_lat': 'D',
                          'HTM9': 'J', 'ring256': 'J',
                          'nest4096': 'J', 'MAG': '2E',
                          'MAG_IVAR': '2E',
                          'FOOBAR': '16A'}
        self.sdss.NOFITS = {'no_fits_keep': 'defer', 'no_fits_drop': 'drop'}
        self.sdss.FITS['FLUX'] = '2E'
        self.sdss.tapSchema['columns'] += [{"table_name": "{0.table}".format(self),
                                            "column_name": "z",
                                            "description": "z",
                                            "unit": "", "ucd": "", "utype": "",
                                            "datatype": "real", "size": 1,
                                            "principal": 0, "indexed": 0, "std": 0}]
        self.sdss.mapping = {'mag_u': 'MAG[0]', 'mag_g': 'MAG[1]',
                             'magivar_u': 'MAGIVAR[0]', 'magivar_g': 'MAGIVAR[1]',
                             'flux_u': 'FLUX[0]', 'flux_g': 'FLUX[1]'}
        self.sdss.tapSchema['columns'] += [{"table_name": "{0.table}".format(self),
                                            "column_name": "no_fits_error",
                                            "description": "error",
                                            "unit": "", "ucd": "", "utype": "",
                                            "datatype": "real", "size": 1,
                                            "principal": 0, "indexed": 0, "std": 0}]
        self.sdss.FITS['Z'] = 'E'
        self.sdss.NOFITS = {'no_fits_keep': 'defer', 'no_fits_drop': 'drop', 'no_fits_error': 'foobar'}
        with self.assertRaises(KeyError) as e:
            self.sdss.mapColumns()
        self.assertEqual(e.exception.args[0], 'Unknown NOFITS instruction: no_fits_error!')

    def test_process_fits(self):
        """Test processing of SDSS-specific FITS file for loading.
        """
        self.sdss.tapSchema['columns'] += [{"table_name": "{0.table}".format(self),
                                            "column_name": "mag_u",
                                            "description": "u Magnitude",
                                            "unit": "", "ucd": "", "utype": "",
                                            "datatype": "real", "size": 1,
                                            "principal": 0, "indexed": 0, "std": 0},
                                           {"table_name": "{0.table}".format(self),
                                            "column_name": "mag_g",
                                            "description": "g Magnitude",
                                            "unit": "", "ucd": "", "utype": "",
                                            "datatype": "real", "size": 1,
                                            "principal": 0, "indexed": 0, "std": 0},
                                           {"table_name": "{0.table}".format(self),
                                            "column_name": "magivar_u",
                                            "description": "u ivar",
                                            "unit": "", "ucd": "", "utype": "",
                                            "datatype": "double", "size": 1,
                                            "principal": 0, "indexed": 0, "std": 0},
                                           {"table_name": "{0.table}".format(self),
                                            "column_name": "magivar_g",
                                            "description": "g ivar",
                                            "unit": "", "ucd": "", "utype": "",
                                            "datatype": "double", "size": 1,
                                            "principal": 0, "indexed": 0, "std": 0},
                                           {"table_name": "{0.table}".format(self),
                                            "column_name": "objid",
                                            "description": "id",
                                            "unit": "", "ucd": "", "utype": "",
                                            "datatype": "bigint", "size": 1,
                                            "principal": 0, "indexed": 0, "std": 0},
                                           {"table_name": "{0.table}".format(self),
                                            "column_name": "bigobjid",
                                            "description": "id",
                                            "unit": "", "ucd": "", "utype": "",
                                            "datatype": "bigint", "size": 1,
                                            "principal": 0, "indexed": 0, "std": 0},
                                           {"table_name": "{0.table}".format(self),
                                            "column_name": "smallid",
                                            "description": "id",
                                            "unit": "", "ucd": "", "utype": "",
                                            "datatype": "smallint", "size": 1,
                                            "principal": 0, "indexed": 0, "std": 0},
                                           {"table_name": "{0.table}".format(self),
                                            "column_name": "unsafe",
                                            "description": "unsafe",
                                            "unit": "", "ucd": "", "utype": "",
                                            "datatype": "integer", "size": 1,
                                            "principal": 0, "indexed": 0, "std": 0},
                                           {"table_name": "{0.table}".format(self),
                                            "column_name": "unsafe2",
                                            "description": "unsafe",
                                            "unit": "", "ucd": "", "utype": "",
                                            "datatype": "smallint", "size": 1,
                                            "principal": 0, "indexed": 0, "std": 0},
                                           {"table_name": "{0.table}".format(self),
                                            "column_name": "small_bit",
                                            "description": "unsafe",
                                            "unit": "", "ucd": "", "utype": "",
                                            "datatype": "smallint", "size": 1,
                                            "principal": 0, "indexed": 0, "std": 0},
                                           {"table_name": "{0.table}".format(self),
                                            "column_name": "small_flags_u",
                                            "description": "unsafe",
                                            "unit": "", "ucd": "", "utype": "",
                                            "datatype": "smallint", "size": 1,
                                            "principal": 0, "indexed": 0, "std": 0},
                                           {"table_name": "{0.table}".format(self),
                                            "column_name": "flags",
                                            "description": "unsafe",
                                            "unit": "", "ucd": "", "utype": "",
                                            "datatype": "bigint", "size": 1,
                                            "principal": 0, "indexed": 0, "std": 0},
                                           {"table_name": "{0.table}".format(self),
                                            "column_name": "flags_u",
                                            "description": "unsafe",
                                            "unit": "", "ucd": "", "utype": "",
                                            "datatype": "bigint", "size": 1,
                                            "principal": 0, "indexed": 0, "std": 0},
                                           {"table_name": "{0.table}".format(self),
                                            "column_name": "no_fits_keep",
                                            "description": "unsafe",
                                            "unit": "", "ucd": "", "utype": "",
                                            "datatype": "integer", "size": 1,
                                            "principal": 0, "indexed": 0, "std": 0},
                                           {"table_name": "{0.table}".format(self),
                                            "column_name": "no_fits_drop",
                                            "description": "unsafe",
                                            "unit": "", "ucd": "", "utype": "",
                                            "datatype": "integer", "size": 1,
                                            "principal": 0, "indexed": 0, "std": 0}]
        i = self.sdss.columnIndex('nest4096')
        u = self.sdss.columnIndex('unsafe')
        self.sdss.tapSchema['columns'][i]['datatype'] = 'smallint'
        self.sdss.FITS = {'elon': 'D', 'elat': 'D',
                          'glon': 'E', 'glat': 'E',
                          'htm9': 'J', 'ring256': 'J',
                          'nest4096': 'J',
                          'random_id': 'E',
                          'mag': '2E', 'magivar': '2E',
                          'objid': '16A',
                          'bigobjid': '20A',
                          'smallid': '3A',
                          'foobar': '16A',
                          'small_bit': 'J',
                          'small_bits': '5J',
                          'objc_flags': 'J',
                          'objc_flags2': 'J',
                          'flags': '5J',
                          'flags2': '5J',
                          'unsafe': 'K',
                          'unsafe2': 'J'}
        self.sdss.NOFITS = {'no_fits_keep': 'defer', 'no_fits_drop': 'drop'}
        for k in self.sdss.FITS:
            self.sdss.mapping[k] = k
        self.sdss.mapping['mag_u'] = 'mag[0]'
        self.sdss.mapping['mag_g'] = 'mag[1]'
        self.sdss.mapping['magivar_u'] = 'magivar[0]'
        self.sdss.mapping['magivar_g'] = 'magivar[1]'
        self.sdss.mapping['small_flags_u'] = 'small_bits[0]'
        self.sdss.mapping['flags'] = 'objc_flags'
        self.sdss.mapping['flags_u'] = 'flags[0]'
        self.sdss._inputFITS = 'foo.fits'
        dummy_values = {'elon': np.ones((5,), dtype=np.float64),
                        'elat': np.ones((5,), dtype=np.float64),
                        'glon': np.ones((5,), dtype=np.float32),
                        'glat': np.ones((5,), dtype=np.float32),
                        'htm9': np.ones((5,), dtype=np.int32),
                        'ring256': np.ones((5,), dtype=np.int32),
                        'nest4096': np.ones((5,), dtype=np.int32),
                        'random_id': np.ones((5,), dtype=np.float32),
                        'mag': np.ones((5, 2), dtype=np.float32),
                        'magivar': np.ones((5, 2), dtype=np.float32),
                        'objid': np.array([' '*15 + '1']*4 + [' '*16], dtype='U16'),
                        'bigobjid': np.array(['9223372036854775808']*3 + ['18446744073709551615']*2, dtype='U20'),
                        'smallid': np.array(['123']*3 + ['   ']*2, dtype='U3'),
                        'foobar': np.array([' '*16]*5, dtype='U16'),
                        'small_bit': np.ones((5,), dtype=np.int32),
                        'small_bits': np.ones((5, 5), dtype=np.int32),
                        'objc_flags': np.ones((5,), dtype=np.int32),
                        'objc_flags2': np.ones((5,), dtype=np.int32),
                        'flags': np.ones((5, 5), dtype=np.int32),
                        'flags2': np.ones((5, 5), dtype=np.int32),
                        'unsafe': np.ones((5,), dtype=np.int64),
                        'unsafe2': np.ones((5,), dtype=np.int32) + 2**15}
        #
        # Raise an unsafe error.
        #
        with mock.patch('digestor.sdss.Table') as T:
            t = T.read.return_value = mock.MagicMock()
            t.__getitem__.side_effect = lambda key: dummy_values[key.lower()]
            t.colnames = [k.upper() for k in dummy_values.keys()]
            with self.assertRaises(ValueError) as e:
                self.sdss.processFITS()
            self.assertEqual(e.exception.args[0], 'No safe data type conversion possible for unsafe (K) -> unsafe (integer)!')
        del dummy_values['unsafe']
        del self.sdss.FITS['unsafe']
        del self.sdss.mapping['unsafe']
        del self.sdss.tapSchema['columns'][u]
        u2 = self.sdss.columnIndex('unsafe2')
        #
        # Try again.
        #
        with mock.patch('digestor.sdss.Table') as T:
            t = T.read.return_value = mock.MagicMock()
            t.__getitem__.side_effect = lambda key: dummy_values[key.lower()]
            t.colnames = [k.upper() for k in dummy_values.keys()]
            with self.assertRaises(ValueError) as e:
                self.sdss.processFITS()
            self.assertEqual(e.exception.args[0], 'Values too large for safe data type conversion for unsafe2 (J) -> unsafe2 (smallint)!')
        del dummy_values['unsafe2']
        del self.sdss.FITS['unsafe2']
        del self.sdss.mapping['unsafe2']
        del self.sdss.tapSchema['columns'][u2]
        #
        # Try again.
        #
        with mock.patch('digestor.sdss.Table') as T:
            t = T.read.return_value = mock.MagicMock()
            t.__getitem__.side_effect = lambda key: dummy_values[key.lower()]
            t.colnames = [k.upper() for k in dummy_values.keys()]
            out = self.sdss.processFITS()
        self.assertEqual(out, '{0.schema}.{0.table}.fits'.format(self))
        #
        # Check overwrite
        #
        with mock.patch('os.path.exists') as ex:
            ex.return_value = True
            out = self.sdss.processFITS()
            ex.assert_called_with(out)
        with mock.patch('os.path.exists') as ex:
            with mock.patch('os.remove') as rm:
                with mock.patch('digestor.sdss.Table') as T:
                    t = T.read.return_value = mock.MagicMock()
                    t.__getitem__.side_effect = lambda key: dummy_values[key.lower()]
                    t.colnames = [k.upper() for k in dummy_values.keys()]
                    ex.return_value = True
                    out = self.sdss.processFITS(overwrite=True)
            rm.assert_called_with(out)
            ex.assert_called_with(out)

    def test_writeSQL(self):
        """Test writing SQL preload file.
        """
        with TemporaryDirectory() as d:
            f = os.path.join(d, 'foo.sql')
            self.sdss.writeSQL(f)
            with open(f) as ff:
                l = ff.readlines()
        self.assertEqual(l[3], 'CREATE SCHEMA IF NOT EXISTS sdss;\n')

    def test_writePOSTSQL(self):
        """Test writing SQL postload file.
        """
        with TemporaryDirectory() as d:
            f = os.path.join(d, 'foo.sql')
            self.sdss.writePOSTSQL(f, pkey='foo_id')
            with open(f) as ff:
                l = ff.readlines()
        self.assertEqual(l[4], 'CREATE INDEX spectra_q3c_ang2ipix ON sdss.spectra (q3c_ang2ipix(ra, "dec")) WITH (fillfactor=100);\n')
        self.assertEqual(l[8], 'ALTER TABLE sdss.spectra ADD PRIMARY KEY (foo_id);\n')


def test_suite():
    """Allows testing of only this module with the command::

        python setup.py test -m <modulename>
    """
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
