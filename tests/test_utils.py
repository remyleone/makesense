#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_utils
------------

Tests for `makesense.utils` module.
"""

import os
import shutil
import sys
import unittest

from makesense import utils

class TestUtils(unittest.TestCase):

    def test_make_sure_path_exists(self):
        self.assertTrue(utils.make_sure_path_exists('/usr/'))
        self.assertTrue(utils.make_sure_path_exists('tests/blah'))
        self.assertTrue(utils.make_sure_path_exists('tests/trailingslash/'))
        self.assertFalse(
            utils.make_sure_path_exists(
                '/this-dir-does-not-exist-and-cant-be-created/'.replace("/", os.sep)
            )
        )
        shutil.rmtree('tests/blah/')
        shutil.rmtree('tests/trailingslash/')


    def test_workin(self):
        cwd = os.getcwd()
        self.assertTrue(utils.make_sure_path_exists('tests/files'))
        ch_to = 'tests/files'

        class TestException(Exception):
            pass

        def test_work_in():
            with utils.work_in(ch_to):
                test_dir = os.path.join(cwd, ch_to).replace("/", os.sep)
                self.assertEqual(test_dir, os.getcwd())
                raise TestException()

        # Make sure we return to the correct folder
        self.assertEqual(cwd, os.getcwd())

        # Make sure that exceptions are still bubbled up
        self.assertRaises(TestException, test_work_in)
        shutil.rmtree('tests/files')

if __name__ == '__main__':
    unittest.main()
