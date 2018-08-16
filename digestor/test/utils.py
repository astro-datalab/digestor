# Licensed under a MIT style license - see LICENSE.rst
# -*- coding: utf-8 -*-
"""
digestor.test.utils
===================

Basic functionality shared by all tests.
"""
import unittest
import logging
from logging.handlers import MemoryHandler


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


class DigestorCase(unittest.TestCase):
    """Base class for Digestor tests.
    """

    @classmethod
    def setUpClass(cls):
        cls.maxDiff = None

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        root_logger = logging.getLogger('digestor')
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
        root_logger = logging.getLogger('digestor')
        while len(root_logger.handlers) > 0:
            h = root_logger.handlers[0]
            h.flush()
            h.close()
            root_logger.removeHandler(h)
        if self.cache_handler is not None:
            root_logger.addHandler(self.cache_handler)
            self.cache_handler = None

    def assertLog(self, order=-1, message=''):
        """Examine the log messages.
        """
        root_logger = logging.getLogger('digestor')
        handler = root_logger.handlers[0]
        record = handler.buffer[order]
        self.assertEqual(record.getMessage(), message)
