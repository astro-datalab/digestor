# Licensed under a MIT style license - see LICENSE.rst
# -*- coding: utf-8 -*-
"""Test digestor.sdss.
"""
import unittest
import unittest.mock as mock
import json
import logging
from logging.handlers import MemoryHandler
from tempfile import NamedTemporaryFile
from ..sdss import (get_options, configure_log, add_dl_columns, init_metadata, parse_line,
                    parse_column_metadata, finish_table, map_columns,
                    fix_columns, sort_columns, process_fits, construct_sql)

import numpy as np


class TestHandler(MemoryHandler):
    """Capture log messages in memory.
    """
    def __init__(self, capacity=1000000, flushLevel=logging.CRITICAL):
        nh = logging.NullHandler()
        MemoryHandler.__init__(self, capacity,
                               flushLevel=flushLevel, target=nh)

    def shouldFlush(self, record):
        """Never flush, except manually.
        """
        return False


class TestSDSS(unittest.TestCase):
    """Test digestor.sdss.
    """

    @classmethod
    def setUpClass(cls):
        cls.maxDiff = None

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        with mock.patch('sys.argv', ['sdss2dl', '-r', 'plug_ra', '-t', 'specobjall',
                                     'specObj-dr14.fits', 'specobjall.sql']):
            self.options = get_options()
        self.metadata = init_metadata(self.options)
        root_logger = logging.getLogger('digestor.sdss')
        if len(root_logger.handlers) == 0:
            self.cache_handler = None
            fmt = logging.Formatter()
        else:
            while len(root_logger.handlers) > 0:
                h = root_logger.handlers[0]
                h.flush()
                self.cache_handler = h
                fmt = h.formatter
                root_logger.removeHandler(h)
        mh = TestHandler()
        mh.setFormatter(fmt)
        root_logger.addHandler(mh)
        root_logger.setLevel(logging.DEBUG)

    def tearDown(self):
        root_logger = logging.getLogger('digestor.sdss')
        while len(root_logger.handlers) > 0:
            h = root_logger.handlers[0]
            h.flush()
            root_logger.removeHandler(h)
        if self.cache_handler is not None:
            root_logger.addHandler(self.cache_handler)
            self.cache_handler = None

    def assertLog(self, order=-1, message=''):
        """Examine the log messages.
        """
        root_logger = logging.getLogger('digestor.sdss')
        handler = root_logger.handlers[0]
        record = handler.buffer[order]
        self.assertEqual(record.getMessage(), message)

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

    def test_configure_log(self):
        """Test the logging configuration.
        """
        self.options.verbose = True
        configure_log(self.options)
        root_logger = logging.getLogger('digestor.sdss')
        self.assertEqual(len(root_logger.handlers), 2)
        self.assertIsInstance(root_logger.handlers[1], logging.StreamHandler)

    def test_add_dl_columns(self):
        """Test adding STILTS columns.
        """
        self.options.keep = True
        with mock.patch('os.path.exists') as e:
            e.return_value = True
            out = add_dl_columns(self.options)
        self.assertEqual(out, 'specObj-dr14.stilts.fits')
        self.options.keep = False
        with mock.patch('subprocess.Popen') as proc:
            p = proc.return_value = mock.MagicMock()
            p.returncode = 0
            p.communicate.return_value = ('', '')
            with mock.patch('os.path.exists') as e:
                e.return_value = True
                with mock.patch('os.remove') as rm:
                    out = add_dl_columns(self.options)
                    rm.assert_called_with(out)
            proc.assert_called_with(['stilts', 'tpipe',
                                     'in=specObj-dr14.fits',
                                     'cmd=\'addcol htm9 "(int)htmIndex(9,plug_ra,plug_dec)"; addcol ring256 "(int)healpixRingIndex(8,plug_ra,plug_dec)"; addcol nest4096 "(int)healpixNestIndex(12,plug_ra,plug_dec)"; addskycoords -inunit deg -outunit deg icrs galactic plug_ra plug_dec glon glat; addskycoords -inunit deg -outunit deg icrs ecliptic plug_ra plug_dec elon elat;\'',
                                     'ofmt=fits-basic',
                                     'out=specObj-dr14.stilts.fits'],
                                     stderr=-1, stdout=-1)
        self.assertEqual(out, 'specObj-dr14.stilts.fits')
        with mock.patch('subprocess.Popen') as proc:
            p = proc.return_value = mock.MagicMock()
            p.returncode = 0
            p.communicate.return_value = ('', 'foobar')
            with mock.patch('os.path.exists') as e:
                e.return_value = True
                with mock.patch('os.remove') as rm:
                    out = add_dl_columns(self.options)
                    rm.assert_called_with(out)
            proc.assert_called_with(['stilts', 'tpipe',
                                     'in=specObj-dr14.fits',
                                     'cmd=\'addcol htm9 "(int)htmIndex(9,plug_ra,plug_dec)"; addcol ring256 "(int)healpixRingIndex(8,plug_ra,plug_dec)"; addcol nest4096 "(int)healpixNestIndex(12,plug_ra,plug_dec)"; addskycoords -inunit deg -outunit deg icrs galactic plug_ra plug_dec glon glat; addskycoords -inunit deg -outunit deg icrs ecliptic plug_ra plug_dec elon elat;\'',
                                     'ofmt=fits-basic',
                                     'out=specObj-dr14.stilts.fits'],
                                     stderr=-1, stdout=-1)
        self.assertLog(-1, 'STILTS STDERR = foobar')

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

    def test_finish_table(self):
        """Test Data Lab-specific columns.
        """
        columns = finish_table(self.options)
        self.assertEqual(columns[-1]['table_name'], 'specobjall')
        self.assertEqual(columns[-1]['column_name'], 'elat')

    def test_map_columns(self):
        """Test mapping of FITS columns to SQL columns.
        """
        self.metadata['columns'] += finish_table(self.options)
        self.metadata['columns'] += [{"table_name": self.options.table,
                                      "column_name": "mag_u",
                                      "description": "u Magnitude",
                                      "unit": "", "ucd": "", "utype": "",
                                      "datatype": "real", "size": 1,
                                      "principal": 0, "indexed": 0, "std": 0},
                                     {"table_name": self.options.table,
                                      "column_name": "mag_g",
                                      "description": "g Magnitude",
                                      "unit": "", "ucd": "", "utype": "",
                                      "datatype": "real", "size": 1,
                                      "principal": 0, "indexed": 0, "std": 0},
                                     {"table_name": self.options.table,
                                      "column_name": "magivar_u",
                                      "description": "u ivar",
                                      "unit": "", "ucd": "", "utype": "",
                                      "datatype": "real", "size": 1,
                                      "principal": 0, "indexed": 0, "std": 0},
                                     {"table_name": self.options.table,
                                      "column_name": "magivar_g",
                                      "description": "g ivar",
                                      "unit": "", "ucd": "", "utype": "",
                                      "datatype": "real", "size": 1,
                                      "principal": 0, "indexed": 0, "std": 0}]
        self.metadata['mapping'] = {'mag_u': 'MAG[0]', 'mag_g': 'MAG[1]',
                                    'magivar_u': 'MAGIVAR[0]', 'magivar_g': 'MAGIVAR[1]'}
        self.metadata['fits'] = {'e_lon': 'D', 'e_lat': 'D',
                                 'g_lon': 'D', 'g_lat': 'D',
                                 'HTM9': 'J', 'ring256': 'J',
                                 'nest4096': 'J', 'MAG': '2E',
                                 'MAG_IVAR': '2E',
                                 'FOOBAR': '16A',
                                 '__filename': 'foo'}
        map_columns(self.options, self.metadata)
        self.assertLog(-1, 'FITS column FOOBAR will be dropped from SQL!')
        self.metadata['columns'] += [{"table_name": self.options.table,
                                      "column_name": "flux_u",
                                      "description": "u flux",
                                      "unit": "", "ucd": "", "utype": "",
                                      "datatype": "real", "size": 1,
                                      "principal": 0, "indexed": 0, "std": 0},]
        self.metadata['mapping'] = {'mag_u': 'MAG[0]', 'mag_g': 'MAG[1]',
                                    'magivar_u': 'MAGIVAR[0]', 'magivar_g': 'MAGIVAR[1]',
                                    'flux_u': 'FLUX[0]'}
        with self.assertRaises(KeyError) as e:
            map_columns(self.options, self.metadata)
        self.assertEqual(e.exception.args[0], 'Could not find a FITS column corresponding to flux_u!')
        self.metadata['fits']['FLUX'] = '2E'
        self.metadata['columns'] += [{"table_name": self.options.table,
                                      "column_name": "z",
                                      "description": "z",
                                      "unit": "", "ucd": "", "utype": "",
                                      "datatype": "real", "size": 1,
                                      "principal": 0, "indexed": 0, "std": 0},]
        self.metadata['mapping'] = {'mag_u': 'MAG[0]', 'mag_g': 'MAG[1]',
                                    'magivar_u': 'MAGIVAR[0]', 'magivar_g': 'MAGIVAR[1]',
                                    'flux_u': 'FLUX[0]'}
        with self.assertRaises(KeyError) as e:
            map_columns(self.options, self.metadata)
        self.assertEqual(e.exception.args[0], 'Could not find a FITS column corresponding to z!')

    def test_fix_columns(self):
        """Test "by hand" fixes to table definition.
        """
        self.metadata['columns'] += [{"table_name": self.options.table,
                                      "column_name": "veldispnpix",
                                      "description": "number of pixels",
                                      "unit": "", "ucd": "", "utype": "",
                                      "datatype": "integer", "size": 1,
                                      "principal": 0, "indexed": 0, "std": 0},]
        fix_columns(self.options, self.metadata)
        self.assertEqual(self.metadata['columns'][0]['datatype'], 'real')
        self.options.table = 'foobar'
        fix_columns(self.options, self.metadata)

    def test_sort_columns(self):
        """Test sorting columns by size.
        """
        self.metadata['columns'] += finish_table(self.options)
        sort_columns(self.options, self.metadata)
        types = [c['datatype'] for c in self.metadata['columns']]
        self.assertListEqual(types, ['double', 'double', 'double', 'double',
                                     'integer', 'integer', 'integer', 'real'])

    def test_process_fits(self):
        """Test processing of FITS file for loading.
        """
        self.metadata['columns'] += finish_table(self.options)
        self.metadata['columns'] += [{"table_name": self.options.table,
                                      "column_name": "mag_u",
                                      "description": "u Magnitude",
                                      "unit": "", "ucd": "", "utype": "",
                                      "datatype": "real", "size": 1,
                                      "principal": 0, "indexed": 0, "std": 0},
                                     {"table_name": self.options.table,
                                      "column_name": "mag_g",
                                      "description": "g Magnitude",
                                      "unit": "", "ucd": "", "utype": "",
                                      "datatype": "real", "size": 1,
                                      "principal": 0, "indexed": 0, "std": 0},
                                     {"table_name": self.options.table,
                                      "column_name": "magivar_u",
                                      "description": "u ivar",
                                      "unit": "", "ucd": "", "utype": "",
                                      "datatype": "double", "size": 1,
                                      "principal": 0, "indexed": 0, "std": 0},
                                     {"table_name": self.options.table,
                                      "column_name": "magivar_g",
                                      "description": "g ivar",
                                      "unit": "", "ucd": "", "utype": "",
                                      "datatype": "double", "size": 1,
                                      "principal": 0, "indexed": 0, "std": 0},
                                     {"table_name": self.options.table,
                                      "column_name": "objid",
                                      "description": "id",
                                      "unit": "", "ucd": "", "utype": "",
                                      "datatype": "bigint", "size": 1,
                                      "principal": 0, "indexed": 0, "std": 0},
                                     {"table_name": self.options.table,
                                      "column_name": "unsafe",
                                      "description": "unsafe",
                                      "unit": "", "ucd": "", "utype": "",
                                      "datatype": "integer", "size": 1,
                                      "principal": 0, "indexed": 0, "std": 0},
                                     {"table_name": self.options.table,
                                      "column_name": "flags_0",
                                      "description": "unsafe",
                                      "unit": "", "ucd": "", "utype": "",
                                      "datatype": "smallint", "size": 1,
                                      "principal": 0, "indexed": 0, "std": 0}]
        self.metadata['columns'][0]['datatype'] = 'smallint'
        self.metadata['mapping'] = {'mag_u': 'MAG[0]', 'mag_g': 'MAG[1]',
                                    'magivar_u': 'MAGIVAR[0]', 'magivar_g': 'MAGIVAR[1]',
                                    'flags_0': 'FLAGS[0]'}
        self.metadata['fits'] = {'e_lon': 'D', 'e_lat': 'D',
                                 'g_lon': 'E', 'g_lat': 'E',
                                 'HTM9': 'J', 'ring256': 'J',
                                 'nest4096': 'J', 'MAG': '2E',
                                 'MAG_IVAR': '2E',
                                 'OBJID': '16A',
                                 'FOOBAR': '16A',
                                 'flags': '2J',
                                 'unsafe': 'K',
                                 '__filename': 'foo'}
        dummy_values = {'e_lon': np.ones((5,), dtype=np.float64),
                        'e_lat': np.ones((5,), dtype=np.float64),
                        'g_lon': np.ones((5,), dtype=np.float32),
                        'g_lat': np.ones((5,), dtype=np.float32),
                        'HTM9': np.ones((5,), dtype=np.int32),
                        'ring256': np.ones((5,), dtype=np.int32),
                        'nest4096': np.ones((5,), dtype=np.int32),
                        'MAG': np.ones((5, 2), dtype=np.float32),
                        'MAG_IVAR': np.ones((5, 2), dtype=np.float32),
                        'OBJID': np.array([' '*15 + '1']*4 + [' '*16], dtype='U16'),
                        'FOOBAR': np.array([' '*16]*5, dtype='U16'),
                        'flags': np.ones((5, 2), dtype=np.int32),
                        'unsafe': np.ones((5,), dtype=np.int64),}
        map_columns(self.options, self.metadata)
        # self.assertLog(-1, 'FITS column FOOBAR will be dropped from SQL!')
        with mock.patch('digestor.sdss.Table') as T:
            t = T.read.return_value = mock.MagicMock()
            # t.__getitem__.side_effect = lambda key: np.ones((5,2), dtype=np.int32)
            t.__getitem__.side_effect = lambda key: dummy_values[key]
            process_fits(self.options, self.metadata)
        # self.assertLog(-1, 'No safe data type conversion possible for unsafe (K) -> unsafe (integer)!')

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
        expected = """CREATE TABLE IF NOT EXISTS {0.schema}.{0.table} (
    htm9 integer NOT NULL,
    foo double precision NOT NULL,
    bar varchar(10) NOT NULL
) WITH (fillfactor=100);
""".format(self.options)
        sql = construct_sql(self.options, self.metadata)
        self.assertEqual(sql, expected)


def test_suite():
    """Allows testing of only this module with the command::

        python setup.py test -m <modulename>
    """
    return unittest.defaultTestLoader.loadTestsFromName(__name__)