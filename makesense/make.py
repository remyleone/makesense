# coding: utf-8

"""
Make step

- Compilation of firmware
- Make simulation file
"""

import json
import logging
import os
import shutil
import time

import errno
from fabric.context_managers import lcd
from fabric.operations import local
from . import Step
from .settings import PJ, TEMPLATE_ENV, CONTIKI_DIR, COOJA_DIR
from .utils import ignored


class Make(Step):
    """
    Class implementation of the make step
    """

    def compile_nodes(self):
        """
        Compile all the nodes for the experiment
        """
        log = logging.getLogger("compile_nodes")
        log.info(self.exp_folder)
        exp_nodes_dirs = PJ(self.exp_folder, "nodes")
        for folder in os.listdir(exp_nodes_dirs):
            node_folder = PJ(exp_nodes_dirs, folder)
            with lcd(node_folder):
                log.info(node_folder)
                local("make")

    @staticmethod
    def compile_cooja():
        """
        Create the JAR file containing COOJA
        """
        with lcd(COOJA_DIR):
            local("ant jar")

    def compile_plugins(self):
        """
        Create the JAR file of the COOJA add-ons
        """
        log = logging.getLogger("compile_plugins")
        log.info("Will compile plugins %s", self.settings["plugins"])
        for plugin in self.settings["plugins"]:
            with lcd(PJ(COOJA_DIR, "apps", plugin)):
                local("ant jar")

    def make_simulation_file(self, random_seed):
        """
        Make the simulation file for a precise experiment
        """
        log = logging.getLogger("make_simulation_file")
        log.info(self.result_folder)
        with open(PJ(self.result_folder, "main.csc"), "w") as sim_file:
            log.info("[make csc] " + PJ(self.exp_folder, "main.csc"))

            csc_template = TEMPLATE_ENV.get_template("simulation.csc")
            csc_variables = {}
            script_settings = self.settings.get("script_settings", {})

            # Script rendering
            if "script_template" in script_settings:
                script_template = TEMPLATE_ENV.get_template(
                    script_settings["script_template"]
                )
            else:
                script_template = TEMPLATE_ENV.get_template(
                    "lambda_bootstrap.js"
                )
            csc_variables["script"] = script_template.render(script_settings)

            # Simulation file rendering
            csc_variables.update(self.settings)

            # Random seed
            csc_variables["random_seed"] = random_seed

            # Plug-ins
            csc_variables["plugins"] = [PJ(COOJA_DIR, "apps", plugin) for plugin in self.settings["plugins"]]

            # Mote binary code location compilation
            mote_types = self.settings["mote_types"]
            for mote in mote_types:
                if "firmware" in mote_types.get(mote, []):
                    continue
                mote_types[mote]["firmware"] = PJ(
                    self.exp_folder,
                    *mote_types[mote]["firmware_address"])
            csc_variables["mote_types"] = self.settings["mote_types"]
            sim_file.write(csc_template.render(csc_variables))

    def __init__(self, name):
        """
        Compile all the motes firmware that an experiment requires and make
        the simulation file defined in the experiment file.
        """
        log = logging.getLogger("make")
        Step.__init__(self, name)
        self.load_settings()

        # nodes firmware compilation
        self.compile_nodes()

        # random_seeds by default is "generated"
        if "random_seeds" in self.settings:
            self.random_seeds = self.settings["random_seeds"]
        else:
            self.random_seeds = ["generated"]

        for random_seed in self.random_seeds:
            log.info("Random seed " + str(random_seed))
            self.result_folder = PJ(self.exp_folder, "exp_" + str(time.time()))
            with ignored(OSError):
                log.info("Making the folder " + self.result_folder)
                os.mkdir(self.result_folder)
                link_path = PJ(self.exp_folder,
                               ".random_seed_" + str(random_seed))
                with open(PJ(self.result_folder, "exp.json"),
                          "wb") as exp_json:
                    exp_json.write(
                        json.dumps(
                            self.settings,
                            sort_keys=True, separators=(',', ': '), indent=2))
                os.mkdir(PJ(self.result_folder, "img"))
                os.mkdir(PJ(self.result_folder, "logs"))
                try:
                    os.symlink(self.result_folder, link_path)
                except OSError, err:
                    if err.errno == errno.EEXIST:
                        os.unlink(link_path)
                        os.symlink(self.result_folder, link_path)

            try:
                shutil.copytree(
                    PJ(self.exp_folder, "nodes"),
                    PJ(self.result_folder, "nodes"))
            except OSError as err:
                log.warn(err)

            # Makefile
            log.info("In folder " + self.result_folder)
            if "makefile_template" in self.settings:
                makefile_template = TEMPLATE_ENV.get_template(
                    self.settings["makefile_template"])
            else:
                makefile_template = TEMPLATE_ENV.get_template("simple_makefile")
            self.settings["contiki"] = CONTIKI_DIR
            with open(PJ(self.result_folder, "Makefile"), "w") as makefile:
                makefile.write(makefile_template.render(self.settings))

            # main.csc
            self.make_simulation_file(random_seed)
