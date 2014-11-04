# -*- coding: utf-8 -*-

"""
Useful functions for testing and sending traffic towards a node
"""

from contextlib import contextmanager
import fnmatch
import logging
import os
import shutil
import socket
import telnetlib

from . import PJ
from .settings import EXPERIMENTS_FOLDER, TEMPLATE_ENV


@contextmanager
def ignored(*exceptions):
    """
    Ignore certain class of exceptions
    """
    try:
        yield
    except exceptions:
        pass


def test_telnet_port(host, port):
    """
    Will test if a port is open for a telnet connection
    """
    log = logging.getLogger("test_telnet_port")
    try:
        telnetlib.Telnet(host, port)
        log.info("Port %s OK", str(port))
        return True
    except socket.error:
        return False


def node_address(node):
    """
    Return the default IPv6 address of a COOJA node
    """
    numbers = {
        "first": hex(29696 + node).lstrip("0x"),
        "second": hex(node).lstrip("0x"),
        "third": hex(257 * node).lstrip("0x")
    }
    return "aaaa::212:%(first)s:%(second)s:%(third)s" % numbers


def result_folders(target):
    """
    Generator for the results folder
    """
    for folder in os.listdir(target):
        if fnmatch.fnmatch(folder, ".random_seed_[0-9]*"):
            yield PJ(target, folder)


def new_experiment(name, exp_template=None):
    """
    Create a new experiment
    """
    log = logging.getLogger("new_experiment")
    log.info("Create %s", str(name))
    folder = PJ(EXPERIMENTS_FOLDER, name)
    settings = TEMPLATE_ENV.get_template("exp.json")

    if os.path.isdir(folder):
        raise OSError("The folder already exists. Aborting")

    if exp_template:
        template = PJ(EXPERIMENTS_FOLDER, exp_template)
        try:
            shutil.copytree(PJ(template, "nodes"), PJ(folder, "nodes"))
            shutil.copyfile(PJ(template, "exp.json"), PJ(folder, "exp.json"))
            return folder
        except OSError as err:
            log.warn(err)
    else:
        with ignored(OSError):
            os.mkdir(folder)
            os.mkdir(PJ(folder, "nodes"))
        with open(PJ(folder, "exp.json"), "w") as exp_settings_file:
            exp_settings_file.write(settings.render({"name": name}))
        return folder
