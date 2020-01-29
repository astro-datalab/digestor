# Licensed under a MIT style license - see LICENSE.rst
# -*- coding: utf-8 -*-
"""Test digestor.view.
"""
import unittest
import unittest.mock as mock

from .utils import DigestorCase
from ..view import get_options


class TestView(DigestorCase):
    """Test digestor.view.
    """

    def setUp(self):
        super().setUp()

    def test_get_options(self):
        """Test command-line arguments.
        """
        with mock.patch('sys.argv', ['add_view_metdata', '-d', 'Test', '-s', 'sdss',
                                     'sdss_dr14.json', 'specobjall', 'specobj']):
            self.options = get_options()
        self.assertEqual(self.options.meta, 'sdss_dr14.json')
        self.assertEqual(self.options.table, 'specobjall')
        self.assertEqual(self.options.view, 'specobj')
        self.assertEqual(self.options.schema, 'sdss')
        self.assertEqual(self.options.description, 'Test')
        self.assertIsNone(self.options.output)


def test_suite():
    """Allows testing of only this module with the command::

        python setup.py test -m <modulename>
    """
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
