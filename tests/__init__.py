#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
__init__
---------

Contains testing helpers.
"""

import os
import shutil
import stat
import sys
if sys.version_info[:2] < (2, 7):
    import unittest2 as unittest
else:
    import unittest


def force_delete(func, path, exc_info):
    """
    Error handler for `shutil.rmtree()` equivalent to `rm -rf`
    Usage: `shutil.rmtree(path, onerror=force_delete)`
    From stackoverflow.com/questions/2656322
    """

    if not os.access(path, os.W_OK):
        # Is the error an access error?
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise


class MakesenseCleanSystemTestCase(unittest.TestCase):
    """
    Test case that simulates a clean system with no config/cloned repositories.

    During setUp:

    * Back up the `~/.makesenserc` config file to `~/.makesenserc.backup`
    * Back up the `~/.makesense/` dir to `~/.makesense.backup/`
    * Starts off a test case with no pre-existing `~/.makesenserc` or
      `~/.makesense/`

    During tearDown:

    * Delete `~/.makesense/` only if a backup is present at
      `~/.makesense.backup/`
    * Restore the `~/.makesenserc` config file from `~/.makesenserc.backup`
    * Restore the `~/.makesense/` dir from `~/.makesense.backup/`

    """

    def setUp(self):
        # If ~/.makesenserc is pre-existing, move it to a temp location
        self.user_config_path = os.path.expanduser('~/.makesenserc')
        self.user_config_path_backup = os.path.expanduser(
            '~/.makesenserc.backup'
        )
        if os.path.exists(self.user_config_path):
            self.user_config_found = True
            shutil.copy(self.user_config_path, self.user_config_path_backup)
            os.remove(self.user_config_path)
        else:
            self.user_config_found = False

        # If the default makesense_dir is pre-existing, move it to a
        # temp location
        self.makesense_dir = os.path.expanduser('~/.makesense')
        self.makesense_dir_backup = os.path.expanduser('~/.makesense.backup')
        if os.path.isdir(self.makesense_dir):
            self.makesense_dir_found = True

            # Remove existing backups before backing up. If they exist, they're stale.
            if os.path.isdir(self.makesense_dir_backup):
                shutil.rmtree(self.makesense_dir_backup)

            shutil.copytree(self.makesense_dir, self.makesense_dir_backup)
        else:
            self.makesense_dir_found = False

    def tearDown(self):
        # If it existed, restore ~/.makesenserc
        # We never write to ~/.makesenserc, so this logic is simpler.
        if self.user_config_found and os.path.exists(self.user_config_path_backup):
            shutil.copy(self.user_config_path_backup, self.user_config_path)
            os.remove(self.user_config_path_backup)

        # Carefully delete the created ~/.makesense dir only in certain
        # conditions.
        if self.makesense_dir_found:
            # Delete the created ~/.makesense dir as long as a backup exists
            if os.path.isdir(self.makesense_dir) and os.path.isdir(self.makesense_dir_backup):
                shutil.rmtree(self.makesense_dir)
        else:
            # Delete the created ~/.makesense dir.
            # There's no backup because it never existed
            if os.path.isdir(self.makesense_dir):
                shutil.rmtree(self.makesense_dir)

        # Restore the user's default makesense_dir contents
        if os.path.isdir(self.makesense_dir_backup):
            shutil.copytree(self.makesense_dir_backup, self.makesense_dir)
        if os.path.isdir(self.makesense_dir):
            shutil.rmtree(self.makesense_dir_backup)
