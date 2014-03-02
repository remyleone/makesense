#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Makesense.exceptions
-----------------------

All exceptions used in the Makesense code base are defined here.
"""


class MakesenseException(Exception):
    """
    Base exception class. All Makesense-specific exceptions should subclass
    this class.
    """


class NonTemplatedInputDirException(MakesenseException):
    """
    Raised when a project's input dir is not templated.
    The name of the input directory should always contain a string that is
    rendered to something else, so that input_dir != output_dir.
    """

class UnknownTemplateDirException(MakesenseException):
    """
    Raised when Makesense cannot determine which directory is the project
    template, e.g. more than one dir appears to be a template dir.
    """

class MissingProjectDir(MakesenseException):
    """
    Raised during cleanup when remove_repo() can't find a generated project
    directory inside of a repo.
    """

class ConfigDoesNotExistException(MakesenseException):
    """
    Raised when get_config() is passed a path to a config file, but no file
    is found at that path.
    """

class InvalidConfiguration(MakesenseException):
    """
    Raised if the global configuration file is not valid YAML or is
    badly contructed.
    """

class UnknownRepoType(MakesenseException):
    """
    Raised if a repo's type cannot be determined.
    """
