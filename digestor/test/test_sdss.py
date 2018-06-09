# Licensed under a MIT style license - see LICENSE.rst
# -*- coding: utf-8 -*-
"""Test digestor.sdss.
"""
import unittest
import unittest.mock as mock
from ..sdss import get_options, parse_line, parse_column_metadata


class TestSDSS(unittest.TestCase):
    """Test digestor.sdss.
    """

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        self.metadata = dict()
        self.metadata['short_description'] = ""
        self.metadata['description'] = ""
        self.metadata['columns'] = dict()

    def tearDown(self):
        pass

    def test_get_options(self):
        """Test command-line arguments.
        """
        with mock.patch('sys.argv', ['sdss2idl', 'specobjall.sql']):
            options = get_options()
        self.assertEqual(options.sql, 'specobjall.sql')
        self.assertFalse(options.verbose)
        self.assertIsNone(options.table)
        self.assertEqual(options.schema, 'sdss_dr14')
        self.assertIsNone(options.output_sql)
        self.assertIsNone(options.output_json)

    def test_parse_column_metadata(self):
        """Test parsing metadata of individual columns.
        """
        d = parse_column_metadata('foo', '--/U mm --/D Random column.')
        self.assertEqual(d['unit'], 'mm')
        self.assertEqual(d['description'], 'Random column.')
        d = parse_column_metadata('foo', '--/F bar --/K ID_CATALOG --/D Random column.')
        self.assertEqual(d['FITS'], 'BAR')
        self.assertEqual(d['ucd'], 'ID_CATALOG')
        self.assertEqual(d['description'], 'Random column.')
        d = parse_column_metadata('mag_g', '--/F mag 1 --/D Random column.')
        self.assertEqual(d['FITS'], 'MAG[1]')
        self.assertEqual(d['description'], 'Random column.')
        d = parse_column_metadata('extra', '--/F NOFITS --/D Random column. --/U arcsec')
        self.assertEqual(d['FITS'], 'NOFITS')
        self.assertEqual(d['unit'], 'arcsec')
        self.assertEqual(d['description'], 'Random column.')
        d = parse_column_metadata('flux_u', '--/U nanomaggies --/D Random column.')
        self.assertEqual(d['FITS'], 'FLUX[0]')
        self.assertEqual(d['unit'], 'nanomaggies')
        self.assertEqual(d['description'], 'Random column.')

    def test_parse_line(self):
        """Test parsing single SQL lines.
        """
        with mock.patch('sys.argv', ['sdss2idl', '-s', 'foo', '-t', 'bar', 'specobjall.sql']):
            options = get_options()
        out = parse_line(r'CREATE TABLE specObjAll  (  ', options, self.metadata)
        self.assertEqual(out, r'CREATE TABLE foo.bar (')
        out = parse_line('--', options, self.metadata)
        self.assertIsNone(out)
        out = parse_line('--/H This is the short description', options, self.metadata)
        self.assertIsNone(out)
        self.assertEqual(self.metadata['short_description'], 'This is the short description')
        out = parse_line('--/T This is the long description', options, self.metadata)
        out = parse_line('--/T This is the long description', options, self.metadata)
        self.assertIsNone(out)
        self.assertEqual(self.metadata['description'], 'This is the long description\nThis is the long description\n')
        out = parse_line('   column int NOT NULL, --/U mm --/D Column description --/F MY_COLUMN', options, self.metadata)
        self.assertEqual(out, '    column integer NOT NULL,')
        self.assertEqual(self.metadata['columns']['column']['unit'], 'mm')
        self.assertEqual(self.metadata['columns']['column']['FITS'], 'MY_COLUMN')
        self.assertEqual(self.metadata['columns']['column']['description'], 'Column description')
        out = parse_line('   column2 real NOT NULL, --/U deg --/D Column description --/F RA', options, self.metadata)
        self.assertEqual(out, '    column2 real NOT NULL,')
        self.assertEqual(self.metadata['columns']['column2']['unit'], 'deg')
        self.assertEqual(self.metadata['columns']['column2']['FITS'], 'RA')
        self.assertEqual(self.metadata['columns']['column2']['description'], 'Column description')
        out = parse_line('  ); ', options, self.metadata)
        self.assertEqual(out, ');')


def test_suite():
    """Allows testing of only this module with the command::

        python setup.py test -m <modulename>
    """
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
