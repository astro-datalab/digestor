# Licensed under a MIT style license - see LICENSE.rst
# -*- coding: utf-8 -*-
"""Test digestor.base.
"""
import unittest
import unittest.mock as mock
import logging
import json
from tempfile import NamedTemporaryFile

from ..base import Digestor
from .utils import DigestorCase


class TestBase(DigestorCase):
    """Test digestor.base.
    """

    def setUp(self):
        super().setUp()
        self.schema = 'sdss'
        self.table = 'spectra'
        self.description = 'sdss schema'
        self.base = Digestor(self.schema, self.table,
                             description=self.description)

    def test_configure_log(self):
        """Test the logging configuration.
        """
        Digestor.configureLog(True)
        root_logger = logging.getLogger('digestor')
        self.assertEqual(len(root_logger.handlers), 2)
        self.assertIsInstance(root_logger.handlers[1], logging.StreamHandler)

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
                             "Table {0.table} is already defined!".format(self))
        with NamedTemporaryFile('w+') as f:
            json.dump({'schemas': [{'schema_name': self.schema}],
                       'tables': [{'table_name': 'foobar'}],
                       'columns': [{'table_name': 'foobar', 'column_name': 'baz'}]}, f)
            f.seek(0)
            base = Digestor(self.schema, self.table,
                            description=self.description,
                            merge=f.name)
            self.assertEqual(base.tapSchema['tables'][1]['table_name'], self.table)

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
                                     'cmd=\'addcol htm9 "(int)htmIndex(9,plug_ra,plug_dec)"; addcol ring256 "(int)healpixRingIndex(8,plug_ra,plug_dec)"; addcol nest4096 "(int)healpixNestIndex(12,plug_ra,plug_dec)"; addskycoords -inunit deg -outunit deg icrs galactic plug_ra plug_dec glon glat; addskycoords -inunit deg -outunit deg icrs ecliptic plug_ra plug_dec elon elat;\'',
                                     'ofmt=fits-basic',
                                     'out=specObj-dr14.stilts.fits'],
                                     stderr=-1, stdout=-1)
        self.assertEqual(out, 'specObj-dr14.stilts.fits')
        with mock.patch('subprocess.Popen') as proc:
            p = proc.return_value = mock.MagicMock()
            p.returncode = 0
            p.communicate.return_value = (b'', b'foobar')
            with mock.patch('os.path.exists') as e:
                e.return_value = True
                with mock.patch('os.remove') as rm:
                    with self.assertRaises(ValueError) as exc:
                        out = self.base.addDLColumns('specObj-dr14.fits',
                                                     ra='plug_ra', overwrite=True)
                    self.assertEqual(str(exc.exception), "STILTS error detected!")
                    rm.assert_called_with(out)
            proc.assert_called_with(['stilts', 'tpipe',
                                     'in=specObj-dr14.fits',
                                     'cmd=\'addcol htm9 "(int)htmIndex(9,plug_ra,plug_dec)"; addcol ring256 "(int)healpixRingIndex(8,plug_ra,plug_dec)"; addcol nest4096 "(int)healpixNestIndex(12,plug_ra,plug_dec)"; addskycoords -inunit deg -outunit deg icrs galactic plug_ra plug_dec glon glat; addskycoords -inunit deg -outunit deg icrs ecliptic plug_ra plug_dec elon elat;\'',
                                     'ofmt=fits-basic',
                                     'out=specObj-dr14.stilts.fits'],
                                     stderr=-1, stdout=-1)
        self.assertLog(-1, 'STILTS STDERR = foobar')

    # def test_fix_columns(self):
    #     """Test "by hand" fixes to table definition.
    #     """
    #     self.metadata['columns'] += [{"table_name": self.options.table,
    #                                   "column_name": "veldispnpix",
    #                                   "description": "number of pixels",
    #                                   "unit": "", "ucd": "", "utype": "",
    #                                   "datatype": "integer", "size": 1,
    #                                   "principal": 0, "indexed": 0, "std": 0},]
    #     fix_columns(self.options, self.metadata)
    #     self.assertEqual(self.metadata['columns'][0]['datatype'], 'real')
    #     self.options.table = 'foobar'
    #     fix_columns(self.options, self.metadata)

    def test_sort_columns(self):
        """Test sorting columns by size.
        """
        self.base.sortColumns()
        types = [c['datatype'] for c in self.base.tapSchema['columns']]
        self.assertListEqual(types, ['double', 'double', 'double', 'double',
                                     'integer', 'integer', 'integer', 'real'])

    # def test_process_fits(self):
    #     """Test processing of FITS file for loading.
    #     """
    #     self.metadata['columns'] += finish_table(self.options)
    #     self.metadata['columns'] += [{"table_name": self.options.table,
    #                                   "column_name": "mag_u",
    #                                   "description": "u Magnitude",
    #                                   "unit": "", "ucd": "", "utype": "",
    #                                   "datatype": "real", "size": 1,
    #                                   "principal": 0, "indexed": 0, "std": 0},
    #                                  {"table_name": self.options.table,
    #                                   "column_name": "mag_g",
    #                                   "description": "g Magnitude",
    #                                   "unit": "", "ucd": "", "utype": "",
    #                                   "datatype": "real", "size": 1,
    #                                   "principal": 0, "indexed": 0, "std": 0},
    #                                  {"table_name": self.options.table,
    #                                   "column_name": "magivar_u",
    #                                   "description": "u ivar",
    #                                   "unit": "", "ucd": "", "utype": "",
    #                                   "datatype": "double", "size": 1,
    #                                   "principal": 0, "indexed": 0, "std": 0},
    #                                  {"table_name": self.options.table,
    #                                   "column_name": "magivar_g",
    #                                   "description": "g ivar",
    #                                   "unit": "", "ucd": "", "utype": "",
    #                                   "datatype": "double", "size": 1,
    #                                   "principal": 0, "indexed": 0, "std": 0},
    #                                  {"table_name": self.options.table,
    #                                   "column_name": "objid",
    #                                   "description": "id",
    #                                   "unit": "", "ucd": "", "utype": "",
    #                                   "datatype": "bigint", "size": 1,
    #                                   "principal": 0, "indexed": 0, "std": 0},
    #                                  {"table_name": self.options.table,
    #                                   "column_name": "unsafe",
    #                                   "description": "unsafe",
    #                                   "unit": "", "ucd": "", "utype": "",
    #                                   "datatype": "integer", "size": 1,
    #                                   "principal": 0, "indexed": 0, "std": 0},
    #                                  {"table_name": self.options.table,
    #                                   "column_name": "flags_0",
    #                                   "description": "unsafe",
    #                                   "unit": "", "ucd": "", "utype": "",
    #                                   "datatype": "smallint", "size": 1,
    #                                   "principal": 0, "indexed": 0, "std": 0}]
    #     self.metadata['columns'][0]['datatype'] = 'smallint'
    #     self.metadata['mapping'] = {'mag_u': 'MAG[0]', 'mag_g': 'MAG[1]',
    #                                 'magivar_u': 'MAGIVAR[0]', 'magivar_g': 'MAGIVAR[1]',
    #                                 'flags_0': 'FLAGS[0]'}
    #     self.metadata['fits'] = {'e_lon': 'D', 'e_lat': 'D',
    #                              'g_lon': 'E', 'g_lat': 'E',
    #                              'HTM9': 'J', 'ring256': 'J',
    #                              'nest4096': 'J', 'MAG': '2E',
    #                              'MAG_IVAR': '2E',
    #                              'OBJID': '16A',
    #                              'FOOBAR': '16A',
    #                              'flags': '2J',
    #                              'unsafe': 'K',
    #                              '__filename': 'foo'}
    #     dummy_values = {'e_lon': np.ones((5,), dtype=np.float64),
    #                     'e_lat': np.ones((5,), dtype=np.float64),
    #                     'g_lon': np.ones((5,), dtype=np.float32),
    #                     'g_lat': np.ones((5,), dtype=np.float32),
    #                     'HTM9': np.ones((5,), dtype=np.int32),
    #                     'ring256': np.ones((5,), dtype=np.int32),
    #                     'nest4096': np.ones((5,), dtype=np.int32),
    #                     'MAG': np.ones((5, 2), dtype=np.float32),
    #                     'MAG_IVAR': np.ones((5, 2), dtype=np.float32),
    #                     'OBJID': np.array([' '*15 + '1']*4 + [' '*16], dtype='U16'),
    #                     'FOOBAR': np.array([' '*16]*5, dtype='U16'),
    #                     'flags': np.ones((5, 2), dtype=np.int32),
    #                     'unsafe': np.ones((5,), dtype=np.int64),}
    #     map_columns(self.options, self.metadata)
    #     # self.assertLog(-1, 'FITS column FOOBAR will be dropped from SQL!')
    #     with mock.patch('digestor.sdss.Table') as T:
    #         t = T.read.return_value = mock.MagicMock()
    #         # t.__getitem__.side_effect = lambda key: np.ones((5,2), dtype=np.int32)
    #         t.__getitem__.side_effect = lambda key: dummy_values[key]
    #         process_fits(self.options, self.metadata)
    #     # self.assertLog(-1, 'No safe data type conversion possible for unsafe (K) -> unsafe (integer)!')

    def test_create_sql(self):
        """Test SQL output.
        """
        self.base.tapSchema['columns'] = [{"table_name": self.base.table,
                                           "column_name": "htm9",
                                           "description": "",
                                           "unit": "", "ucd": "", "utype": "",
                                           "datatype": "integer", "size": 1,
                                           "principal": 0, "indexed": 1, "std": 0},
                                          {"table_name": self.base.table,
                                           "column_name": "foo",
                                           "description": "",
                                           "unit": "", "ucd": "", "utype": "",
                                           "datatype": "double", "size": 1,
                                           "principal": 0, "indexed": 1, "std": 0},
                                          {"table_name": self.base.table,
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


def test_suite():
    """Allows testing of only this module with the command::

        python setup.py test -m <modulename>
    """
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
