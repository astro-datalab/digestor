# Licensed under a MIT style license - see LICENSE.rst
# -*- coding: utf-8 -*-
"""Test digestor.base.
"""
import unittest
import unittest.mock as mock
import os
import logging
import json
from tempfile import NamedTemporaryFile

import numpy as np

from ..base import Digestor
from .utils import DigestorCase


class TestBase(DigestorCase):
    """Test digestor.base.
    """

    def setUp(self):
        super().setUp()
        self.schema = 'sdss'
        self.table = 'spectra'
        self.stable = "{0.schema}.{0.table}".format(self)
        self.description = 'sdss schema'
        self.base = Digestor(self.schema, self.table,
                             description=self.description)

    def test_configure_log(self):
        """Test the logging configuration.
        """
        Digestor.configureLog('test.log', True)
        root_logger = logging.getLogger('digestor')
        self.assertEqual(len(root_logger.handlers), 2)
        self.assertIsInstance(root_logger.handlers[1], logging.FileHandler)
        os.remove('test.log')

    def test_init_metadata(self):
        """Test metadata initialization.
        """
        self.assertEqual(self.base.tapSchema['schemas'][0]['schema_name'], self.schema)
        self.assertEqual(self.base.tapSchema['schemas'][0]['description'], self.description)
        self.assertEqual(self.base.tapSchema['tables'][0]['table_name'], self.table)
        with NamedTemporaryFile('w+') as f:
            json.dump({'schemas': [{'schema_name': 'sdss_dr13'}]}, f)
            f.seek(0)
            with self.assertRaises(ValueError) as e:
                base = Digestor(self.schema, self.table,
                                description=self.description,
                                merge=f.name)
            self.assertEqual(str(e.exception),
                             "You are attempting to merge schema={0.schema} into schema=sdss_dr13!".format(self))
        with NamedTemporaryFile('w+') as f:
            json.dump({'schemas': [{'schema_name': self.schema}], 'tables': [{'table_name': self.table}]}, f)
            f.seek(0)
            with self.assertRaises(ValueError) as e:
                base = Digestor(self.schema, self.table,
                                description=self.description,
                                merge=f.name)
            self.assertEqual(str(e.exception),
                             "Table {0.stable} is already defined!".format(self))
        with NamedTemporaryFile('w+') as f:
            json.dump({'schemas': [{'schema_name': self.schema}], 'tables': [{'table_name': 'foobar'}]}, f)
            f.seek(0)
            base = Digestor(self.schema, self.table,
                            description=self.description,
                            merge=f.name)
            self.assertEqual(base.tapSchema['columns'][0]['column_name'], 'htm9')
        with NamedTemporaryFile('w+') as f:
            json.dump({'schemas': [{'schema_name': self.schema}],
                       'tables': [{'table_name': 'foobar'}],
                       'columns': [{'table_name': 'foobar', 'column_name': 'baz'}]}, f)
            f.seek(0)
            base = Digestor(self.schema, self.table,
                            description=self.description,
                            merge=f.name)
            self.assertEqual(base.tapSchema['tables'][1]['table_name'], self.table)

    def test_get_yaml(self):
        """Test grabbing and caching YAML configuration.
        """
        yaml = """sdss:
    spectra:
        columns:
            veldispnpix:
                datatype: real
        """
        with NamedTemporaryFile('w+') as f:
            f.write(yaml)
            f.seek(0)
            foo = self.base._getYAML(f.name)
            self.assertIn('sdss', foo)
        bar = self.base._getYAML(f.name)
        self.assertIn('sdss', foo)

    def test_table_index(self):
        """Test the table index search function.
        """
        self.assertEqual(self.base.tableIndex(), 0)
        self.base.table = 'foobar'
        with self.assertRaises(ValueError) as e:
            i = self.base.tableIndex()
        self.assertEqual(e.exception.args[0],
                         "Table {0.table} was not found in schema {0.schema}!".format(self.base))

    def test_column_index(self):
        """Test the column index search function.
        """
        self.assertEqual(self.base.columnIndex('htm9'), 0)
        with self.assertRaises(ValueError) as e:
            i = self.base.columnIndex('foobar')
        self.assertEqual(e.exception.args[0],
                         "Column {0} was not found in {1.schema}.{1.table}!".format('foobar', self.base))

    def test_fix_columns(self):
        """Test "by hand" fixes to table definition.
        """
        self.base.tapSchema['columns'] += [{"table_name": "{0.table}".format(self),
                                            "column_name": "veldispnpix",
                                            "description": "number of pixels",
                                            "unit": "", "ucd": "", "utype": "",
                                            "datatype": "integer", "size": 1,
                                            "principal": 0, "indexed": 0, "std": 0}]
        self.base.fixColumns('no_such_file.yaml')
        yaml = """sdss:
    spectra:
        columns:
            veldispnpix:
                datatype: real
"""
        with NamedTemporaryFile('w+') as f:
            f.write(yaml)
            f.seek(0)
            self.base.fixColumns(f.name)
            self.assertEqual(self.base.tapSchema['columns'][-1]['datatype'], 'real')
        self.base.table = 'foobar'
        with NamedTemporaryFile('w+') as f:
            f.write(yaml)
            f.seek(0)
            self.base.fixColumns(f.name)

    def test_sort_columns(self):
        """Test sorting columns by size.
        """
        self.base.sortColumns()
        types = [c['datatype'] for c in self.base.tapSchema['columns']]
        self.assertListEqual(types, ['double', 'double', 'double', 'double',
                                     'integer', 'integer', 'integer', 'real'])

    def test_custom_stilts(self):
        """Test adding custom STILTS commands.
        """
        yaml = """sdss:
    spectra:
        STILTS:
            - cmd=select skyversion==2
"""
        with NamedTemporaryFile('w+') as f:
            f.write(yaml)
            f.seek(0)
            self.base.customSTILTS(f.name)
            self.assertListEqual(self.base._custom_stilts_command, ['cmd=select skyversion==2'])
        self.base._custom_stilts_command = []
        self.base.table = 'photo'
        with NamedTemporaryFile('w+') as f:
            f.write(yaml)
            f.seek(0)
            self.base.customSTILTS(f.name)
            self.assertListEqual(self.base._custom_stilts_command, [])

    def test_add_dl_columns(self):
        """Test adding STILTS columns.
        """
        with mock.patch('os.path.exists') as e:
            e.return_value = True
            out = self.base.addDLColumns('specObj-dr14.fits')
        self.assertEqual(out, 'specObj-dr14.stilts.fits')
        with mock.patch('subprocess.Popen') as proc:
            p = proc.return_value = mock.MagicMock()
            p.returncode = 0
            p.communicate.return_value = ('', '')
            with mock.patch('os.path.exists') as e:
                e.return_value = True
                with mock.patch('os.remove') as rm:
                    out = self.base.addDLColumns('specObj-dr14.fits',
                                                 ra='plug_ra', overwrite=True)
                    rm.assert_called_with(out)
            proc.assert_called_with(['stilts', 'tpipe',
                                     'in=specObj-dr14.fits',
                                     'cmd=addcol htm9 (int)htmIndex(9,plug_ra,plug_dec)',
                                     'cmd=addcol ring256 (int)healpixRingIndex(8,plug_ra,plug_dec)',
                                     'cmd=addcol nest4096 (int)healpixNestIndex(12,plug_ra,plug_dec)',
                                     'cmd=addskycoords -inunit deg -outunit deg icrs ecliptic plug_ra plug_dec elon elat',
                                     'cmd=addskycoords -inunit deg -outunit deg icrs galactic plug_ra plug_dec glon glat',
                                     'ofmt=fits-basic',
                                     'out=specObj-dr14.stilts.fits'],
                                    stderr=-1, stdout=-1)
        self.assertEqual(out, 'specObj-dr14.stilts.fits')
        with mock.patch('subprocess.Popen') as proc:
            p = proc.return_value = mock.MagicMock()
            p.returncode = 0
            p.communicate.return_value = (b'fail', b'foobar')
            with mock.patch('os.path.exists') as e:
                e.return_value = True
                with mock.patch('os.remove') as rm:
                    with self.assertRaises(ValueError) as exc:
                        out = self.base.addDLColumns('specObj-dr14.fits',
                                                     ra='racen', overwrite=True)
                    self.assertEqual(str(exc.exception), "STILTS error detected!")
                    rm.assert_called_with(out)
            proc.assert_called_with(['stilts', 'tpipe',
                                     'in=specObj-dr14.fits',
                                     'cmd=addcol htm9 (int)htmIndex(9,racen,deccen)',
                                     'cmd=addcol ring256 (int)healpixRingIndex(8,racen,deccen)',
                                     'cmd=addcol nest4096 (int)healpixNestIndex(12,racen,deccen)',
                                     'cmd=addskycoords -inunit deg -outunit deg icrs ecliptic racen deccen elon elat',
                                     'cmd=addskycoords -inunit deg -outunit deg icrs galactic racen deccen glon glat',
                                     'ofmt=fits-basic',
                                     'out=specObj-dr14.stilts.fits'],
                                    stderr=-1, stdout=-1)
        self.assertLog(-1, 'STILTS STDERR = foobar')

    def test_map_columns(self):
        """Test mapping of FITS columns to SQL columns.
        """
        self.base.FITS = {'elon': 'D', 'elat': 'D',
                          'glon': 'D', 'glat': 'D',
                          'htm9': 'J', 'ring256': 'J',
                          'nest4096': 'J', 'random_id': 'E'}
        self.base.mapColumns()
        final_mapping = {'htm9': 'htm9', 'ring256': 'ring256', 'nest4096': 'nest4096',
                         'glon': 'glon', 'glat': 'glat',
                         'elon': 'elon', 'elat': 'elat',
                         'random_id': 'random_id'}
        self.assertDictEqual(self.base.mapping, final_mapping)
        self.base.tapSchema['columns'] += [{"table_name": "{0.table}".format(self),
                                            "column_name": "z",
                                            "description": "z",
                                            "unit": "", "ucd": "", "utype": "",
                                            "datatype": "real", "size": 1,
                                            "principal": 0, "indexed": 0, "std": 0}]
        self.base.mapping = {'random_id': 'random_id', 'z': 'z'}
        with self.assertRaises(KeyError) as e:
            self.base.mapColumns()
        self.assertEqual(e.exception.args[0], 'Could not find a FITS column corresponding to z!')

    def test_parse_fits(self):
        """Test reading metadata from FITS file.
        """
        with mock.patch('astropy.io.fits.open', mock.mock_open()) as mo:
            columns = mock.MagicMock()
            columns.columns.names = ['foo', 'bar']
            columns.columns.formats = ['D', 'J']
            mo.return_value.__enter__.return_value = [None, columns]
            self.base.parseFITS('foo.fits')
        self.assertEqual(self.base._inputFITS, 'foo.fits')
        self.assertDictEqual(self.base.FITS, {'foo': 'D', 'bar': 'J'})

    def test_process_fits(self):
        """Test processing of FITS file for loading.
        """
        self.base.tapSchema['columns'] += [{"table_name": "{0.table}".format(self),
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
                                            "column_name": "unsafe",
                                            "description": "unsafe",
                                            "unit": "", "ucd": "", "utype": "",
                                            "datatype": "integer", "size": 1,
                                            "principal": 0, "indexed": 0, "std": 0},
                                           {"table_name": "{0.table}".format(self),
                                            "column_name": "flags_0",
                                            "description": "unsafe",
                                            "unit": "", "ucd": "", "utype": "",
                                            "datatype": "smallint", "size": 1,
                                            "principal": 0, "indexed": 0, "std": 0}]
        i = self.base.columnIndex('nest4096')
        self.base.tapSchema['columns'][i]['datatype'] = 'smallint'
        self.base.FITS = {'elon': 'D', 'elat': 'D',
                          'glon': 'E', 'glat': 'E',
                          'htm9': 'J', 'ring256': 'J',
                          'nest4096': 'J',
                          'random_id': 'E',
                          'mag': '2E', 'magivar': '2E',
                          'foobar': '16A',
                          'flags': '2J',
                          'unsafe': 'K'}
        for k in self.base.FITS:
            self.base.mapping[k] = k
        self.base.mapping['mag_u'] = 'mag[0]'
        self.base.mapping['mag_g'] = 'mag[1]'
        self.base.mapping['magivar_u'] = 'magivar[0]'
        self.base.mapping['magivar_g'] = 'magivar[1]'
        self.base.mapping['flags_0'] = 'flags[0]'
        self.base._inputFITS = 'foo.fits'
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
                        'foobar': np.array([' '*16]*5, dtype='U16'),
                        'flags': np.ones((5, 2), dtype=np.int32),
                        'unsafe': np.ones((5,), dtype=np.int64)}
        #
        # Raise an unsafe error.
        #
        with mock.patch('digestor.base.Table') as T:
            t = T.read.return_value = mock.MagicMock()
            t.__getitem__.side_effect = lambda key: dummy_values[key]
            with self.assertRaises(ValueError) as e:
                self.base.processFITS()
            self.assertEqual(e.exception.args[0], 'No safe data type conversion possible for unsafe (K) -> unsafe (integer)!')
        del dummy_values['unsafe']
        del self.base.FITS['unsafe']
        del self.base.mapping['unsafe']
        del self.base.tapSchema['columns'][-2]
        #
        # Try again.
        #
        with mock.patch('digestor.base.Table') as T:
            t = T.read.return_value = mock.MagicMock()
            t.__getitem__.side_effect = lambda key: dummy_values[key]
            out = self.base.processFITS()
        self.assertEqual(out, '{0.schema}.{0.table}.fits'.format(self))
        #
        # Check overwrite
        #
        with mock.patch('os.path.exists') as ex:
            ex.return_value = True
            out = self.base.processFITS()
            ex.assert_called_with(out)
        with mock.patch('os.path.exists') as ex:
            with mock.patch('os.remove') as rm:
                with mock.patch('digestor.base.Table') as T:
                    t = T.read.return_value = mock.MagicMock()
                    t.__getitem__.side_effect = lambda key: dummy_values[key]
                    ex.return_value = True
                    out = self.base.processFITS(overwrite=True)
            rm.assert_called_with(out)
            ex.assert_called_with(out)

    def test_write_schema(self):
        """Test writing TapSchema metadata to file.
        """
        with NamedTemporaryFile('w+') as f:
            self.base.writeTapSchema(f.name)

    def test_create_sql(self):
        """Test SQL output.
        """
        self.base.tapSchema['columns'] = [{"table_name": "{0.table}".format(self),
                                           "column_name": "htm9",
                                           "description": "",
                                           "unit": "", "ucd": "", "utype": "",
                                           "datatype": "integer", "size": 1,
                                           "principal": 0, "indexed": 1, "std": 0},
                                          {"table_name": "{0.table}".format(self),
                                           "column_name": "foo",
                                           "description": "",
                                           "unit": "", "ucd": "", "utype": "",
                                           "datatype": "double", "size": 1,
                                           "principal": 0, "indexed": 1, "std": 0},
                                          {"table_name": "{0.table}".format(self),
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
""".format(self.base)
        sql = self.base.createSQL()
        self.assertEqual(sql, expected)

    def test_write_sql(self):
        """Test writing SQL to file.
        """
        with NamedTemporaryFile('w+') as f:
            self.base.writeSQL(f.name)


def test_suite():
    """Allows testing of only this module with the command::

        python setup.py test -m <modulename>
    """
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
