# Licensed under a MIT style license - see LICENSE.rst
# -*- coding: utf-8 -*-
"""Test top-level digestor functions.
"""
import unittest
import re
import sys
from .. import __version__ as theVersion


class TestTopLevel(unittest.TestCase):
    """Test top-level digestor functions.
    """

    @classmethod
    def setUpClass(cls):
        cls.versionre = re.compile(
                r'([0-9]+!)?([0-9]+)(\.[0-9]+)*((a|b|rc|\.post|\.dev)[0-9]+)?')

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_version(self):
        """Ensure the version conforms to PEP386/PEP440.
        """
        self.assertRegex(theVersion, self.versionre)


def test_suite():
    """Allows testing of only this module with the command::

        python setup.py test -m <modulename>
    """
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
