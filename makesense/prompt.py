#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
makesense.prompt
---------------------

Functions for prompting the user for project info.
"""

from __future__ import unicode_literals
import sys

PY3 = sys.version > '3'
if PY3:
    iteritems = lambda d: iter(d.items())
else:
    input = raw_input
    iteritems = lambda d: d.iteritems()


def prompt_for_config(context):
    """
    Prompts the user to enter new config, using context as a source for the
    field names and sample values.
    """
    makesense_dict = {}

    for key, val in iteritems(context['makesense']):
        prompt = "{0} (default is \"{1}\")? ".format(key, val)

        if PY3:
            new_val = input(prompt.encode('utf-8'))
        else:
            new_val = input(prompt.encode('utf-8')).decode('utf-8')

        new_val = new_val.strip()

        if new_val == '':
            new_val = val

        makesense_dict[key] = new_val
    return makesense_dict


def query_yes_no(question, default="yes"):
    """
    Ask a yes/no question via `raw_input()` and return their answer.

    :param question: A string that is presented to the user.
    :param default: The presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is one of "yes" or "no".

    Adapted from
    http://stackoverflow.com/questions/3041986/python-command-line-yes-no-input
    http://code.activestate.com/recipes/577058/

    """
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()

        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")
