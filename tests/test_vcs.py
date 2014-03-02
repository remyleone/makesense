#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_vcs
------------

Tests for `makesense.vcs` module.
"""

import locale
import logging
import os
import shutil
import subprocess
import sys
import unittest

PY3 = sys.version > '3'
if PY3:
    from unittest.mock import patch
    input_str = 'builtins.input'
else:
    import __builtin__
    from mock import patch
    input_str = '__builtin__.raw_input'
    from cStringIO import StringIO

from makesense import utils, vcs


# Log debug and above to console
logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)
encoding = locale.getdefaultlocale()[1]


class TestIdentifyRepo(unittest.TestCase):

    def test_identify_git_github(self):
        repo_url = "https://github.com/sieben/makesense.git"
        self.assertEqual(vcs.identify_repo(repo_url), "git")

    def test_identify_git_github_no_extension(self):
        repo_url = "https://github.com/sieben/makesense"
        self.assertEqual(vcs.identify_repo(repo_url), "git")


class TestVCS(unittest.TestCase):

    def test_git_clone(self):
        repo_dir = vcs.clone(
            'https://github.com/sieben/score.git'
        )
        self.assertEqual(repo_dir, 'score')
        self.assertTrue(os.path.isfile('score/README.md'))
        if os.path.isdir('score'):
            shutil.rmtree('score')

    def test_git_clone_checkout(self):
        repo_dir = vcs.clone(
            'https://github.com/sieben/score.git',
            'gh-pages'
        )
        git_dir = 'score'
        self.assertEqual(repo_dir, git_dir)
        self.assertTrue(os.path.isfile(os.path.join('score', 'README.md')))

        proc = subprocess.Popen(
            ['git', 'symbolic-ref', 'HEAD'],
            cwd=git_dir,
            stdout=subprocess.PIPE
        )
        symbolic_ref = proc.communicate()[0]
        branch = symbolic_ref.decode(encoding).strip().split('/')[-1]
        self.assertEqual('gh-pages', branch)

        if os.path.isdir(git_dir):
            shutil.rmtree(git_dir)

    def test_git_clone_custom_dir(self):
        os.makedirs("tests/custom_dir1/custom_dir2/")
        repo_dir = vcs.clone(
            repo_url='https://github.com/sieben/score.git',
            checkout=None,
            clone_to_dir="tests/custom_dir1/custom_dir2/"
        )
        with utils.work_in("tests/custom_dir1/custom_dir2/"):
            test_dir = 'tests/custom_dir1/custom_dir2/score'.replace("/", os.sep)
            self.assertEqual(repo_dir, test_dir)
            self.assertTrue(os.path.isfile('score/README.md'))
            if os.path.isdir('score'):
                shutil.rmtree('score')
        if os.path.isdir('tests/custom_dir1'):
            shutil.rmtree('tests/custom_dir1')


class TestVCSPrompt(unittest.TestCase):

    def setUp(self):
        if os.path.isdir('score'):
            shutil.rmtree('score')
        os.mkdir('score/')

    @patch(input_str, lambda: 'y')
    def test_git_clone_overwrite(self):
        if not PY3:
            sys.stdin = StringIO('y\n\n')
        repo_dir = vcs.clone(
            'https://github.com/sieben/score.git'
        )
        self.assertEqual(repo_dir, 'score')
        self.assertTrue(os.path.isfile('score/README.md'))

    @patch(input_str, lambda: 'n')
    def test_git_clone_cancel(self):
        if not PY3:
            sys.stdin = StringIO('n\n\n')
        self.assertRaises(
            SystemExit,
            vcs.clone,
            'https://github.com/sieben/score.git'
        )

    def tearDown(self):
        if os.path.isdir('score'):
            shutil.rmtree('score')

if __name__ == '__main__':
    unittest.main()
