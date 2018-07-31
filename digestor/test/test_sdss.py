# Licensed under a MIT style license - see LICENSE.rst
# -*- coding: utf-8 -*-
"""Test digestor.sdss.
"""
import unittest
import unittest.mock as mock
import json
from tempfile import NamedTemporaryFile
from ..sdss import (init_metadata, get_options, parse_line,
                    parse_column_metadata, finish_table)


class TestSDSS(unittest.TestCase):
    """Test digestor.sdss.
    """

    @classmethod
    def setUpClass(cls):
        cls.schema = 'sdss_dr14'
        cls.table =  'specobjall'
        cls.description = 'Sloan Digital Sky Survey Data Relase 14'
        cls.merge_json = None

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.metadata = init_metadata(self)

    def tearDown(self):
        pass

    def test_init_metadata(self):
        """Test metadata initialization.
        """
        with mock.patch('sys.argv', ['sdss2dl', '-t', 'specobjall', 'specobjall.sql']):
            options = get_options()
        meta = init_metadata(options)
        self.assertEqual(meta['schemas'][0]['schema_name'], options.schema)
        self.assertEqual(meta['schemas'][0]['description'], options.description)
        self.assertEqual(meta['tables'][0]['schema_name'], options.schema)
        self.assertEqual(meta['tables'][0]['table_name'], options.table)
        with NamedTemporaryFile('w+') as f:
            json.dump({'schemas': [{'schema_name': 'sdss_dr13'}]}, f)
            f.seek(0)
            with mock.patch('sys.argv', ['sdss2dl', '-m', f.name, '-t', 'specobjall', 'specobjall.sql']):
                options = get_options()
            with self.assertRaises(ValueError) as e:
                meta = init_metadata(options)
            self.assertEqual(str(e.exception),
                             "You are attempting to merge schema=sdss_dr14 into schema=sdss_dr13!")
        with NamedTemporaryFile('w+') as f:
            json.dump({'schemas': [{'schema_name': 'sdss_dr14'}], 'tables': [{'table_name': 'specobjall'}]}, f)
            f.seek(0)
            with mock.patch('sys.argv', ['sdss2dl', '-m', f.name, '-t', 'specobjall', 'specobjall.sql']):
                options = get_options()
            with self.assertRaises(ValueError) as e:
                meta = init_metadata(options)
            self.assertEqual(str(e.exception),
                             "Table specobjall is already defined!")

    def test_get_options(self):
        """Test command-line arguments.
        """
        with mock.patch('sys.argv', ['sdss2dl', 'specobjall.sql']):
            options = get_options()
        self.assertEqual(options.sql, 'specobjall.sql')
        self.assertFalse(options.verbose)
        self.assertIsNone(options.table)
        self.assertEqual(options.schema, 'sdss_dr14')
        self.assertIsNone(options.output_sql)
        self.assertIsNone(options.output_json)
        self.assertIsNone(options.merge_json)

    def test_parse_column_metadata(self):
        """Test parsing metadata of individual columns.
        """
        d, r = parse_column_metadata('foo', '--/U mm --/D Random column.')
        self.assertIsNone(r)
        self.assertEqual(d['unit'], 'mm')
        self.assertEqual(d['description'], 'Random column.')
        d, r = parse_column_metadata('foo', '--/F bar --/K ID_CATALOG --/D Random column.')
        self.assertEqual(r, 'BAR')
        self.assertEqual(d['ucd'], 'ID_CATALOG')
        self.assertEqual(d['description'], 'Random column.')
        d, r = parse_column_metadata('mag_g', '--/F mag 1 --/D Random column.')
        self.assertEqual(r, 'MAG[1]')
        self.assertEqual(d['description'], 'Random column.')
        d, r = parse_column_metadata('extra', '--/F NOFITS --/D Random column. --/U arcsec')
        self.assertIsNone(r)
        self.assertEqual(d['unit'], 'arcsec')
        self.assertEqual(d['description'], 'Random column.')
        d, r = parse_column_metadata('flux_u', '--/U nanomaggies --/D Random column.')
        self.assertEqual(r, 'FLUX[0]')
        self.assertEqual(d['unit'], 'nanomaggies')
        self.assertEqual(d['description'], 'Random column.')

    def test_parse_line(self):
        """Test parsing single SQL lines.
        """
        with mock.patch('sys.argv', ['sdss2dl', '-s', 'foo', '-t', 'bar', 'specobjall.sql']):
            options = get_options()
        out, st = parse_line(r'CREATE TABLE specObjAll  (  ', options, self.metadata)
        self.assertEqual(out, r'CREATE TABLE foo.bar (')
        self.assertEqual(st, 'explodeall;')
        out, st = parse_line('--', options, self.metadata)
        self.assertIsNone(out)
        out, st = parse_line('--/H This is the short description', options, self.metadata)
        self.assertIsNone(out)
        self.assertEqual(self.metadata['tables'][0]['description'], 'This is the short description')
        out, st = parse_line('--/T This is the long description', options, self.metadata)
        out, st = parse_line('--/T This is the long description', options, self.metadata)
        self.assertIsNone(out)
        # self.assertEqual(self.metadata['description'], 'This is the long description\nThis is the long description\n')
        out, st = parse_line('   column int NOT NULL, --/U mm --/D Column description --/F MY_COLUMN', options, self.metadata)
        self.assertEqual(out, '    column integer NOT NULL,')
        self.assertEqual(self.metadata['columns'][0]['column_name'], 'column')
        self.assertEqual(self.metadata['columns'][0]['datatype'], 'integer')
        self.assertEqual(self.metadata['columns'][0]['unit'], 'mm')
        # self.assertEqual(self.metadata['columns']['column']['FITS'], 'MY_COLUMN')
        self.assertEqual(self.metadata['columns'][0]['description'], 'Column description')
        out, st = parse_line('   column2 real NOT NULL, --/U deg --/D Column description --/F RA', options, self.metadata)
        self.assertEqual(out, '    column2 real NOT NULL,')
        self.assertEqual(self.metadata['columns'][1]['column_name'], 'column2')
        self.assertEqual(self.metadata['columns'][1]['datatype'], 'real')
        self.assertEqual(self.metadata['columns'][1]['unit'], 'deg')
        # self.assertEqual(self.metadata['columns']['column2']['FITS'], 'RA')
        self.assertEqual(self.metadata['columns'][1]['description'], 'Column description')
        out, st = parse_line('   column3 varchar(16) NOT NULL, --/K UCD --/D Column description --/F RA', options, self.metadata)
        self.assertEqual(out, '    column3 varchar(16) NOT NULL,')
        self.assertEqual(self.metadata['columns'][2]['column_name'], 'column3')
        self.assertEqual(self.metadata['columns'][2]['datatype'], 'character')
        self.assertEqual(self.metadata['columns'][2]['size'], 16)
        self.assertEqual(self.metadata['columns'][2]['unit'], '')
        self.assertEqual(self.metadata['columns'][2]['ucd'], 'UCD')
        # self.assertEqual(self.metadata['columns']['column2']['FITS'], 'RA')
        self.assertEqual(self.metadata['columns'][2]['description'], 'Column description')
        out, st = parse_line('   column4 float NOT NULL, --/K UCD --/D Column description --/F DEC', options, self.metadata)
        self.assertEqual(out, '    column4 double precision NOT NULL,')
        self.assertEqual(self.metadata['columns'][3]['column_name'], 'column4')
        self.assertEqual(self.metadata['columns'][3]['datatype'], 'double')
        self.assertEqual(self.metadata['columns'][3]['size'], 1)
        self.assertEqual(self.metadata['columns'][3]['unit'], '')
        self.assertEqual(self.metadata['columns'][3]['ucd'], 'UCD')
        # self.assertEqual(self.metadata['columns']['column2']['FITS'], 'RA')
        out, st = parse_line('    loadVersion  int NOT NULL, --/D Load Version --/K ID_TRACER --/F NOFITS', options, self.metadata)
        self.assertEqual(self.metadata['columns'][3]['description'], 'Column description')
        out, st = parse_line('    z real NOT NULL, --/D Redshift', options, self.metadata)
        self.assertEqual(st, 'colmeta -name z Z;')
        out, st = parse_line('    snMedian_u real NOT NULL, --/D S/N --/F sn_median 0', options, self.metadata)
        self.assertEqual(st, 'colmeta -name snmedian_u SN_MEDIAN_1;')
        out, st = parse_line('  ); ', options, self.metadata)
        self.assertIsNone(out)

    def test_finish_table(self):
        """Test Data Lab-specific columns.
        """
        # with mock.patch('sys.argv', ['sdss2dl', '-s', 'foo', '-t', 'bar', 'specobjall.sql']):
        #     options = get_options()
        out = finish_table(self, self.metadata)
        self.assertListEqual(out, ["    htm9 integer NOT NULL,",
                                   "    ring256 integer NOT NULL,",
                                   "    nest4096 integer NOT NULL,",
                                   # "    random_id real NOT NULL,",
                                   "    glon double precision NOT NULL,",
                                   "    glat double precision NOT NULL,",
                                   "    elon double precision NOT NULL,",
                                   "    elat double precision NOT NULL",
                                   ");"])

def test_suite():
    """Allows testing of only this module with the command::

        python setup.py test -m <modulename>
    """
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
