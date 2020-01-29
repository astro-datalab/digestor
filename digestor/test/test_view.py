# Licensed under a MIT style license - see LICENSE.rst
# -*- coding: utf-8 -*-
"""Test digestor.view.
"""
import unittest
import unittest.mock as mock


class TestView(DigestorCase):
    """Test digestor.view.
    """

    def setUp(self):
        super().setUp()


def test_suite():
    """Allows testing of only this module with the command::

        python setup.py test -m <modulename>
    """
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
