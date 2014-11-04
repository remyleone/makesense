# -*- coding: utf-8 -*-

"""
Fabric file providing shortcuts to control the simulations series
"""

import pdb
import json
import logging
import os
from os.path import join as pj
from itertools import chain

from jinja2 import Environment, FileSystemLoader
from fabric.api import env, task, lcd, local
from fabric.api import get, hosts, put, roles, run

from makesense.run import run_experiment

from makesense.parser import message
from makesense.parser import powertracker2csv
from makesense.parser import pcap2csv
from makesense.parser import format_pcap_csv
from makesense.parser import parse_iotlab_energy

from makesense.graph import rpl_graph

from makesense.analyze import depth
from makesense.analyze import strobes
from makesense.analyze import strobes_depth
from makesense.analyze import dashboard
# from makesense.analyze import pdr_depth

from makesense.plot import plot_iotlab_energy
from makesense.plot import overhead
from makesense.plot import dashboard
from makesense.plot import protocol_repartition_depth
from makesense.plot import protocol_repartition_aggregated
from makesense.plot import protocol_repartition
from makesense.plot import pdr
from makesense.plot import pdr_depth
from makesense.plot import strobes
from makesense.plot import strobes_depth
from makesense.plot import energy
from makesense.plot import energy_depth

logging.basicConfig(level=logging.INFO)
env.hosts = ["localhost"]
env.use_ssh_config = True

logging.basicConfig(filename="fab.log", filemode="w", level=logging.DEBUG)

env.shell = "/usr/local/bin/bash -c "
env.roledefs.update({
    "web": ["perso", "galois"],
    "cluster": ["enst", "nexium"]
})


CONTIKI_FOLDER = os.path.abspath("contiki")
ROOT_DIR = os.path.dirname(__file__)
EXPERIMENT_FOLDER = pj(ROOT_DIR, "experiments")
TEMPLATE_FOLDER = pj(ROOT_DIR, "templates")
TEMPLATE_ENV = Environment(loader=FileSystemLoader(TEMPLATE_FOLDER))
COOJA_DIR = pj(CONTIKI_FOLDER, "tools", "cooja")


@task
def new(name):
    """
    Default experiment is a client and a server sending messages to each others.
    """
    path = pj(EXPERIMENT_FOLDER, name)
    if not os.path.exists(path):
        os.makedirs(path)

    client_template = TEMPLATE_ENV.get_template("dummy_client.c")
    with open(pj(path, "dummy-client.c"), "w") as f:
        f.write(client_template.render())

    server_template = TEMPLATE_ENV.get_template("dummy_server.c")
    with open(pj(path, "dummy-server.c"), "w") as f:
        f.write(server_template.render())

    makefile_template = TEMPLATE_ENV.get_template("dummy_makefile")
    with open(pj(path, "Makefile"), "w") as f:
        f.write(makefile_template.render(contiki=CONTIKI_FOLDER))

    main_csc_template = TEMPLATE_ENV.get_template("dummy_main.csc")
    script_template = TEMPLATE_ENV.get_template("dummy_script.js")
    script = script_template.render(
        timeout=100000,
        powertracker_frequency=10000,
    )
    with open(pj(path, "main.csc"), "w") as f:
        f.write(main_csc_template.render(
            title="Dummy Simulation",
            random_seed=12345,
            transmitting_range=42,
            interference_range=42,
            success_ratio_tx=1.0,
            success_ratio_rx=1.0,
            mote_types=[
                {"name": "server", "description": "server", "firmware": "dummy-server.wismote"},
                {"name": "client", "description": "client", "firmware": "dummy-client.wismote"}
            ],
            motes=[
                {"mote_id": 1, "x": 0, "y": 0, "mote_type": "server"},
                {"mote_id": 2, "x": 1, "y": 1, "mote_type": "client"},
            ],
            script=script))

    print("Think to rename otherwise if you do fab new:%s again dummy files will be overwritten" % name)

@task
def compile_nodes(name):
    """
    Fabric command to compile nodes
    """
    path = pj(EXPERIMENT_FOLDER, name)
    with lcd(path):
        local("make")
        local("make ihex")

@task
def push_iotlab(name):
    experiment_path = pj(EXPERIMENT_FOLDER, name)
    results_folder = pj(experiment_path, "results", "iotlab")
    if not os.path.exists(results_folder):
        os.makedirs(results_folder)

    with lcd(experiment_path):
        settings = {
            "name": "dummy_experiment",
            "duration": 1,
            "nodes": [
                {"site": "grenoble",
                 "platform": "wsn430",
                 "mote_id": "1",
                 "firmware": "dummy-client.ihex",
                 "profile": "energy_monitoring"},

                {"site": "grenoble",
                 "platform": "wsn430",
                 "mote_id": "2",
                 "firmware": "dummy-server.ihex",
                 "profile": "energy_monitoring"},
            ]
        }
        settings["nodes_command"] = " -l ".join(["%(site)s,%(platform)s,%(mote_id)s,%(firmware)s,%(profile)s" % node for node in settings["nodes"]])
        json_output = local("experiment-cli submit "
              "-n %(name)s "
              "-d %(duration)d"
              " -l %(nodes_command)s" % settings,
              capture=True)
        with open(pj(results_folder, "iotlab.json"), "w") as f:
            f.write(json.dumps(json.loads(json_output)))

@task
@hosts("grenoble")
def pull_iotlab(name):
    iotlab_folder = pj(EXPERIMENT_FOLDER, name, "results", "iotlab")
    experiment_id = None
    with open(pj(iotlab_folder, "iotlab.json")) as f:
        exp_json = json.load(f)
        experiment_id = exp_json["id"]

    get(".iot-lab/%d" % experiment_id, local_path=iotlab_folder)

@task
def parse_iotlab(name):
    iotlab_folder = pj(EXPERIMENT_FOLDER, name, "results", "iotlab")
    experiment_id = None
    with open(pj(iotlab_folder, "iotlab.json")) as f:
        exp_json = json.load(f)
        experiment_id = exp_json["id"]
    parse_iotlab_energy(pj(iotlab_folder, str(experiment_id)))

@task
def plot_iotlab(name):
    iotlab_folder = pj(EXPERIMENT_FOLDER, name, "results", "iotlab")
    experiment_id = None
    with open(pj(iotlab_folder, "iotlab.json")) as f:
        exp_json = json.load(f)
        experiment_id = exp_json["id"]
    plot_iotlab_energy(pj(iotlab_folder, str(experiment_id)))


@task
def compile_cooja():
    with lcd(COOJA_DIR):
        local("ant jar")

@task
def clean_cooja():
    with lcd(COOJA_DIR):
        local("ant jar")

@task
def clean_nodes(name):
    path = pj(EXPERIMENT_FOLDER, name)
    with lcd(path):
        local("make clean")

@task
def make(name):
    """
    Fabric command to make all the folder structures and compile nodes
    """
    compile_nodes(name)
    compile_cooja()

@task
def launch(name):
    """
    Fabric command to run an experiment
    """
    path = pj(EXPERIMENT_FOLDER, name)
    with lcd(path):
        local("make run")

@task
def clean_results(name):
    """
    Fabric command to clean results
    """
    path = pj(EXPERIMENT_FOLDER, name)
    with lcd(path):
        local("rm -fr results")

@task
def parse(name):
    path = pj(EXPERIMENT_FOLDER, name)
    powertracker2csv(path)
    message(path)
    # pcap2csv(path)
    # format_pcap_csv(path)

@task
def analyze(name):
    """
    Fabric command to analyze trace
    """
    path = pj(EXPERIMENT_FOLDER, name)
    depth(path)
    rpl_graph(path)
    # dashboard(path)
    # strobes(path)
    # strobes_depth(path)

@task
@hosts("galois")
def push(name):
    path = pj(EXPERIMENT_FOLDER, name)
    put(path,
        remote_path="~/html/results/")

@task
@hosts("galois")
def pull(name):
    path = pj(EXPERIMENT_FOLDER, name)
    get(name, local_path=path)

@task
@hosts("galois")
def pull_results(name):
    path = pj(EXPERIMENT_FOLDER, name)
    get(pj(name, "results"), local_path=path)

@task
def plot(name):
    path = pj(EXPERIMENT_FOLDER, name)
    overhead(path)
    dashboard(path)
    protocol_repartition_depth(path)
    protocol_repartition_aggregated(path)
    protocol_repartition(path)
    pdr(path)
    pdr_depth(path)
    strobes(path)
    strobes_depth(path)
    energy(path)
    energy_depth(path)
