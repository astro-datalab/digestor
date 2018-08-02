# Licensed under a MIT style license - see LICENSE.rst
# -*- coding: utf-8 -*-
"""Test digestor.sdss.
"""
import unittest
import unittest.mock as mock
import json
from tempfile import NamedTemporaryFile
from ..sdss import (add_dl_columns, init_metadata, get_options, parse_line,
                    parse_column_metadata, finish_table, construct_sql,
                    fits_names)


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
        with mock.patch('sys.argv', ['sdss2dl', '-r', 'plug_ra', '-t', 'specobjall',
                                     'specObj-dr14.fits', 'specobjall.sql']):
            self.options = get_options()
        self.metadata = init_metadata(self.options)

    def tearDown(self):
        pass

    def test_add_dl_columns(self):
        """Test adding STILTS columns.
        """
        with mock.patch('subprocess.Popen') as proc:
            p = proc.return_value = mock.MagicMock()
            p.returncode = 0
            p.communicate.return_value = ('', '')
            out = add_dl_columns(self.options)
            proc.assert_called_with(['stilts', 'tpipe',
                                     'in=specObj-dr14.fits',
                                     'cmd=\'addcol htm9 "(int)htmIndex(9,plug_ra,plug_dec)"; addcol ring256 "(int)healpixRingIndex(8,plug_ra,plug_dec)"; addcol nest4096 "(int)healpixNestIndex(12,plug_ra,plug_dec)"; addskycoords -inunit deg -outunit deg icrs galactic plug_ra plug_dec glon glat; addskycoords -inunit deg -outunit deg icrs ecliptic plug_ra plug_dec elon elat;\'',
                                     'ofmt=fits-basic',
                                     'out=specObj-dr14.stilts.fits'],
                                     stderr=-1, stdout=-1)
        self.assertEqual(out, 'specObj-dr14.stilts.fits')

    def test_init_metadata(self):
        """Test metadata initialization.
        """
        meta = init_metadata(self.options)
        self.assertEqual(meta['schemas'][0]['schema_name'], self.options.schema)
        self.assertEqual(meta['schemas'][0]['description'], self.options.description)
        self.assertEqual(meta['tables'][0]['schema_name'], self.options.schema)
        self.assertEqual(meta['tables'][0]['table_name'], self.options.table)
        with NamedTemporaryFile('w+') as f:
            json.dump({'schemas': [{'schema_name': 'sdss_dr13'}]}, f)
            f.seek(0)
            with mock.patch('sys.argv', ['sdss2dl', '-m', f.name, '-t', 'specobjall',
                                         'specObj-dr14.fits', 'specobjall.sql']):
                options = get_options()
            with self.assertRaises(ValueError) as e:
                meta = init_metadata(options)
            self.assertEqual(str(e.exception),
                             "You are attempting to merge schema=sdss_dr14 into schema=sdss_dr13!")
        with NamedTemporaryFile('w+') as f:
            json.dump({'schemas': [{'schema_name': 'sdss_dr14'}], 'tables': [{'table_name': 'specobjall'}]}, f)
            f.seek(0)
            with mock.patch('sys.argv', ['sdss2dl', '-m', f.name, '-t', 'specobjall',
                                         'specObj-dr14.fits', 'specobjall.sql']):
                options = get_options()
            with self.assertRaises(ValueError) as e:
                meta = init_metadata(options)
            self.assertEqual(str(e.exception),
                             "Table specobjall is already defined!")
        with NamedTemporaryFile('w+') as f:
            json.dump({'schemas': [{'schema_name': 'sdss_dr14'}], 'tables': [{'table_name': 'foobar'}]}, f)
            f.seek(0)
            with mock.patch('sys.argv', ['sdss2dl', '-m', f.name, '-t', 'specobjall',
                                         'specObj-dr14.fits', 'specobjall.sql']):
                options = get_options()
            meta = init_metadata(options)
            self.assertIn('mapping', meta)

    def test_get_options(self):
        """Test command-line arguments.
        """
        self.assertEqual(self.options.sql, 'specobjall.sql')
        self.assertFalse(self.options.verbose)
        self.assertEqual(self.options.table, 'specobjall')
        self.assertEqual(self.options.schema, 'sdss_dr14')
        self.assertIsNone(self.options.output_sql)
        self.assertIsNone(self.options.output_json)
        self.assertIsNone(self.options.merge_json)

    def test_parse_column_metadata(self):
        """Test parsing metadata of individual columns.
        """
        d, r = parse_column_metadata('foo', '--/U mm --/D Random column.')
        self.assertEqual(d['unit'], 'mm')
        self.assertEqual(d['description'], 'Random column.')
        d, r = parse_column_metadata('foo', '--/F bar --/K ID_CATALOG --/D Random column.')
        self.assertEqual(d['ucd'], 'ID_CATALOG')
        self.assertEqual(d['description'], 'Random column.')
        self.assertEqual(r, 'BAR')
        d, r = parse_column_metadata('mag_g', '--/F mag 1 --/D Random column.')
        self.assertEqual(d['description'], 'Random column.')
        self.assertEqual(r, 'MAG[1]')
        d, r = parse_column_metadata('extra', '--/F NOFITS --/D Random column. --/U arcsec')
        self.assertEqual(d['unit'], 'arcsec')
        self.assertEqual(d['description'], 'Random column.')
        d, r = parse_column_metadata('flux_u', '--/U nanomaggies --/D Random column.')
        self.assertEqual(d['unit'], 'nanomaggies')
        self.assertEqual(d['description'], 'Random column.')

    def test_parse_line(self):
        """Test parsing single SQL lines.
        """
        parse_line(r'CREATE TABLE specObjAll  (  ', self.options, self.metadata)
        parse_line('--', self.options, self.metadata)
        parse_line('--/H This is the short description', self.options, self.metadata)
        self.assertEqual(self.metadata['tables'][0]['description'], 'This is the short description')
        parse_line('--/T This is the long description', self.options, self.metadata)
        # self.assertEqual(self.metadata['description'], 'This is the long description\nThis is the long description\n')
        parse_line('   column int NOT NULL, --/U mm --/D Column description --/F MY_COLUMN', self.options, self.metadata)
        self.assertEqual(self.metadata['columns'][0]['column_name'], 'column')
        self.assertEqual(self.metadata['columns'][0]['datatype'], 'integer')
        self.assertEqual(self.metadata['columns'][0]['unit'], 'mm')
        self.assertEqual(self.metadata['columns'][0]['description'], 'Column description')
        self.assertEqual(self.metadata['mapping']['column'], 'MY_COLUMN')
        parse_line('   column2 real NOT NULL, --/U deg --/D Column description --/F RA', self.options, self.metadata)
        self.assertEqual(self.metadata['columns'][1]['column_name'], 'column2')
        self.assertEqual(self.metadata['columns'][1]['datatype'], 'real')
        self.assertEqual(self.metadata['columns'][1]['unit'], 'deg')
        self.assertEqual(self.metadata['columns'][1]['description'], 'Column description')
        self.assertEqual(self.metadata['mapping']['column2'], 'RA')
        parse_line('   column3 varchar(16) NOT NULL, --/K UCD --/D Column description --/F RA', self.options, self.metadata)
        self.assertEqual(self.metadata['columns'][2]['column_name'], 'column3')
        self.assertEqual(self.metadata['columns'][2]['datatype'], 'character')
        self.assertEqual(self.metadata['columns'][2]['size'], 16)
        self.assertEqual(self.metadata['columns'][2]['unit'], '')
        self.assertEqual(self.metadata['columns'][2]['ucd'], 'UCD')
        self.assertEqual(self.metadata['columns'][2]['description'], 'Column description')
        parse_line('   column4 float NOT NULL, --/K UCD --/D Column description --/F DEC', self.options, self.metadata)
        self.assertEqual(self.metadata['columns'][3]['column_name'], 'column4')
        self.assertEqual(self.metadata['columns'][3]['datatype'], 'double')
        self.assertEqual(self.metadata['columns'][3]['size'], 1)
        self.assertEqual(self.metadata['columns'][3]['unit'], '')
        self.assertEqual(self.metadata['columns'][3]['ucd'], 'UCD')
        self.assertEqual(self.metadata['columns'][3]['description'], 'Column description')
        parse_line('    loadVersion  int NOT NULL, --/D Load Version --/K ID_TRACER --/F NOFITS', self.options, self.metadata)
        # parse_line('    z real NOT NULL, --/D Redshift', self.options, self.metadata)
        parse_line('    snMedian_u real NOT NULL, --/D S/N --/F sn_median 0', self.options, self.metadata)
        self.assertEqual(self.metadata['mapping']['snmedian_u'], 'SN_MEDIAN[0]')
        parse_line('  ); ', self.options, self.metadata)

    def test_finish_table(self):
        """Test Data Lab-specific columns.
        """
        columns = finish_table(self.options)
        self.assertEqual(columns[-1]['table_name'], 'specobjall')
        self.assertEqual(columns[-1]['column_name'], 'elat')

    def test_construct_sql(self):
        """Test SQL output.
        """
        self.metadata['columns'] = [{"table_name": self.options.table,
                                     "column_name": "htm9",
                                     "description": "",
                                     "unit": "", "ucd": "", "utype": "",
                                     "datatype": "integer", "size": 1,
                                     "principal": 0, "indexed": 1, "std": 0},
                                    {"table_name": self.options.table,
                                     "column_name": "foo",
                                     "description": "",
                                     "unit": "", "ucd": "", "utype": "",
                                     "datatype": "double", "size": 1,
                                     "principal": 0, "indexed": 1, "std": 0},
                                    {"table_name": self.options.table,
                                     "column_name": "bar",
                                     "description": "",
                                     "unit": "", "ucd": "", "utype": "",
                                     "datatype": "character", "size": 10,
                                     "principal": 0, "indexed": 1, "std": 0}]
        expected = """CREATE TABLE IF EXISTS {0.schema}.{0.table} (
    htm9 integer NOT NULL,
    foo double precision NOT NULL,
    bar varchar(10) NOT NULL
) WITH (fillfactor=100);
""".format(self.options)
        sql = construct_sql(self.options, self.metadata)
        self.assertEqual(sql, expected)

    def test_fits_names(self):
        """Test the conversion of column names.
        """
        foo = fits_names('sn_median_u')
        self.assertEqual(foo, ('sn_median_u', 'SN_MEDIAN_U',
                               'snmedianu', 'SNMEDIANU',
                               'sn_median', 'SN_MEDIAN',
                               'snmedian', 'SNMEDIAN'))


def test_suite():
    """Allows testing of only this module with the command::

        python setup.py test -m <modulename>
    """
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
