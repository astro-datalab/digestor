# Licensed under a MIT style license - see LICENSE.rst
# -*- coding: utf-8 -*-
"""
digestor.test
=============

Used to initialize the unit test framework via ``python setup.py test``.
"""
import unittest


def digestor_test_suite():
    """Returns unittest.TestSuite of digestor tests.
    This is factored out separately from runtests() so that it can be used by
    ``python setup.py test``.
    """
    from os.path import dirname
    py_dir = dirname(dirname(__file__))
    return unittest.defaultTestLoader.discover(py_dir,
                                               top_level_dir=dirname(py_dir))


def runtests():
    """Run all tests in digestor.test.test_*.
    """
    # Load all TestCase classes from digestor/test/test_*.py
    tests = digestor_test_suite()
    # Run them
    unittest.TextTestRunner(verbosity=2).run(tests)
