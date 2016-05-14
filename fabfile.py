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

import iotlabcli
from iotlabcli import experiment
import requests
from jinja2 import Environment, FileSystemLoader
from fabric.api import env, task, lcd, local, parallel
from fabric.api import get, hosts, put, roles, run
import pandas as pd

# Simplify the makesense import to only have
# a package import and then we use function
# from the package

from makesense.run import run_experiment
from makesense import parser
from makesense.graph import rpl_graph
from makesense import analyze as anlz
from makesense import plot as pt

# Using iotlab

logging.basicConfig(level=logging.INFO)
env.hosts = ["localhost"]
env.use_ssh_config = True
env.shell = "/bin/bash -c"
env.roledefs.update({
    "web": ["perso", "galois"],
    "cluster": [],
    "iotlab": ["rennes", "strasbourg", "grenoble", "rocquencourt"]
})


ROOT_DIR = os.path.dirname(__file__)
CONTIKI_FOLDER = os.path.abspath(pj(ROOT_DIR, "contiki"))
EXPERIMENT_FOLDER = pj(ROOT_DIR, "experiments")
TEMPLATE_FOLDER = pj(ROOT_DIR, "templates")
TEMPLATE_ENV = Environment(loader=FileSystemLoader(TEMPLATE_FOLDER))
COOJA_DIR = pj(CONTIKI_FOLDER, "tools", "cooja")
TUNSLIP6 = pj(CONTIKI_FOLDER, "tools", "tunslip6")

settings = {
        "ROOT_DIR": ROOT_DIR,
        "CONTIKI_FOLDER": CONTIKI_FOLDER,
        "EXPERIMENT_FOLDER": EXPERIMENT_FOLDER,
        "TEMPLATE_FOLDER": TEMPLATE_FOLDER,
        "COOJA_DIR": COOJA_DIR,
        "TUNSLIP6": TUNSLIP6
}

@task
def new(name, notebook_template="Default Jupyter notebook.ipynb"):
    """
    Default experiment is a client and a server sending messages to each others.
    The default platform is wismote
    """
    path = pj(EXPERIMENT_FOLDER, name)
    if not os.path.exists(path):
        os.makedirs(path)

    # Copy of the settings file
    with open(pj(path, "settings.json"), "w") as f:
        f.write(json.dumps(settings,
                sort_keys=True,
                indent=4,
                separators=(',', ': ')))

    notebook_template = TEMPLATE_ENV.get_template(notebook_template)
    with open(pj(path, "%s.ipynb" % name), "w") as f:
        f.write(notebook_template.render())

@task
def new_iotlab(name):
    """
    Default experiment but using m3 as default platform
    """
    path = pj(EXPERIMENT_FOLDER, name)
    if not os.path.exists(path):
        os.makedirs(path)

    # client_template = TEMPLATE_ENV.get_template("dummy_client_iotlab.c")
    # with open(pj(path, "dummy-client.c"), "w") as f:
    #     f.write(client_template.render())

    # server_template = TEMPLATE_ENV.get_template("dummy_server_iotlab.c")
    # with open(pj(path, "dummy-server.c"), "w") as f:
    #     f.write(server_template.render())

    serial_template = TEMPLATE_ENV.get_template("dummy_serial.c")
    with open(pj(path, "dummy_serial.c"), "w") as f:
        f.write(serial_template.render())

    makefile_template = TEMPLATE_ENV.get_template("dummy_makefile")
    with open(pj(path, "Makefile"), "w") as f:
        f.write(makefile_template.render(contiki=CONTIKI_FOLDER,
                                         target="iotlab-m3"))

    config_template = TEMPLATE_ENV.get_template("dummy_iotlab.json")
    with open(pj(path, "iotlab.json"), "w") as f:
        f.write(config_template.render())

@task
@hosts("grenoble")
def push_iotlab(name):
    experiment_path = pj(EXPERIMENT_FOLDER, name)
    results_folder = pj(experiment_path, "results", "iotlab")
    if not os.path.exists(results_folder):
        os.makedirs(results_folder)

    # gets user password from credentials file None, None
    user, passwd = iotlabcli.get_user_credentials()
    api = iotlabcli.Api(user, passwd)

    # describe the resources
    resources = None
    with open(pj(experiment_path, "iotlab.json")) as f:
        config = json.loads(f.read())
        resources = [experiment.exp_resources(**c) for c in config]

    print(resources)
    # actually submit the experiment
    exp_id = None
    # We move to the folder to have a portable iotlab.json
    with lcd(experiment_path):
        exp_res = experiment.submit_experiment(
            api, 'dummy_experiment', 1, resources)
        exp_id = exp_wres["id"]
        with open("results/iotlab/iotlab.json", "w") as f:
            f.write(json.dumps({"id": exp_id}))

    # get the content
    print("Exp submited with id: %u" % exp_id)

    run("experiment-cli wait -i %d" % exp_id)

    with open(pj(results_folder, "serial.log"), 'w') as f:
        run("./iot-lab/tools_and_scripts/serial_aggregator.py -i %d" % exp_id,
            stdout=f)
    print("Written serial logs to %s" % pj(results_folder, "serial.log"))


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
    parse.parse_iotlab_energy(pj(iotlab_folder, str(experiment_id)))


@task
def plot_iotlab(name):
    iotlab_folder = pj(EXPERIMENT_FOLDER, name, "results", "iotlab")
    experiment_id = None
    with open(pj(iotlab_folder, "iotlab.json")) as f:
        exp_json = json.load(f)
        experiment_id = exp_json["id"]
    plot_iotlab_energy(pj(iotlab_folder, str(experiment_id)))


@task
def ewsn_analyze():
    experiment_list = ["rpl_udp_10", "rpl_udp_20", "rpl_udp_30", "rpl_udp_40"]
    res = {exp: {"dao": 0, "dio": 0} for exp in experiment_list}

    for exp in experiment_list:
        with open(pj(EXPERIMENT_FOLDER, exp, "results", "iotlab", "serial.log")) as f:
            for line in f:
                if "RPL: Sending a multicast-DIO" in line or "RPL: Sending unicast-DIO" in line:
                    res[exp]["dio"] += 1
                if "Sending DAO" in line:
                    res[exp]["dao"] += 1
    res = {int(key.strip("rpl_udp_")): value for key, value in res.items()}
    df = pd.DataFrame(res)

    pt.latexify()
    import matplotlib.pyplot as plt

    ax = df.T.plot(kind='bar')
    ax.set_xlabel("Nodes")
    ax.set_ylabel("RPL packets sent")
    ax.set_xticklabels(range(10, 50, 10), rotation=0)

    fig = plt.gcf()
    plt.tight_layout()

    # fig.set_size_inches(18.5, 10.5)
    fig.savefig("burnes.pdf", format="pdf")
    plt.close('all')

@task
def forge_simfile_from_iotlab(name):

    main_file = pj(EXPERIMENT_FOLDER, name, 'main.csc')
    iotlab_resources, motes, mote_types = None, None, None

    # Little tool to gather a potential node_id
    find_id = lambda x: int(x.split(".")[0].split("-")[1])

    with open(pj(EXPERIMENT_FOLDER, name, "results", 'iotlab', "resources_iotlab.json")) as f:
        iotlab_resources = json.load(f)
        motes = {find_id(elem["network_address"]): {"x": float(elem["x"]),
                                                    "y": float(elem["y"]),
                                                    "z": float(elem["z"]),
                                                    "mote_id": find_id(elem["network_address"])}
                 for elem in iotlab_resources["items"]}

    with open(pj(EXPERIMENT_FOLDER, name, "iotlab.json")) as f:
        reserved_resources = json.load(f)
        res = [{elem["firmware_path"].split(".")[0]:
                [find_id(node) for node in elem["nodes"]]}
               for elem in reserved_resources]
        mote_types = [
            {"name": elem["firmware_path"].split(".")[0],
             "firmware": elem["firmware_path"].replace("iotlab-m3", "wismote")}
            for elem in reserved_resources]

        new_dict = {}
        for r in res:
            for key, values in r.items():
                new_dict.update({value: key for value in values})
        for node_id, node_type in new_dict.items():
            motes[node_id]["mote_type"] = node_type

    with open(pj(EXPERIMENT_FOLDER, name, "iotlab.csc"), "w") as f:
        sim_template = TEMPLATE_ENV.get_template("dummy_main.csc")
        f.write(sim_template.render(
            title=name, random_seed=12345,
            transmitting_range=100, interference_range=100,
            success_ratio_rx=1.0, success_ratio_tx=1.0,
            mote_types=mote_types,
            motes=motes.values()))


@task
def compile_cooja():
    with lcd(COOJA_DIR):
        local("ant jar")


@task
def clean_cooja():
    with lcd(COOJA_DIR):
        local("ant clean")


@task
def clean_nodes(name):
    path = pj(EXPERIMENT_FOLDER, name)
    with lcd(path):
        local("make clean")

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
    parser.powertracker2csv(path)
    parser.message(path)
    parser.parse_iotlab_energy(path)
    # pcap2csv(path)
    # format_pcap_csv(path)


@task
def analyze(name):
    """
    Fabric command to analyze trace
    """
    path = pj(EXPERIMENT_FOLDER, name)
    anlz.depth(path)
    anlz.rpl_graph(path)
    # anlz.dashboard(path)
    # anlz.strobes(path)
    # anlz.strobes_depth(path)


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
def plot(name):
    path = pj(EXPERIMENT_FOLDER, name)
    pt.overhead(path)
    pt.dashboard(path)
    pt.protocol_repartition_depth(path)
    pt.protocol_repartition_aggregated(path)
    pt.protocol_repartition(path)
    pt.pdr(path)
    pt.pdr_depth(path)
    pt.strobes(path)
    pt.strobes_depth(path)
    pt.energy(path)
    pt.energy_depth(path)

@task
@parallel
@roles("iotlab")
def update_iotlab():
    run("cd iot-lab; git pull")
    run("cd .oh-my-zsh; git pull")
    put("~/.iotlabrc", remote_path="~")
    put("~/.gitconfig", remote_path="~")
    put("~/.ssh/config", remote_path="~/.ssh/config")


@task
def make_iotlab(name):
    """
    Fabric command to make all the folder structures and compile nodes
    """
    compile_nodes(name, target="iotlab-m3")
    compile_cooja()


@task
def web(name):
    """
    Fabric command to launch a web server with ipython
    """
    path = pj(EXPERIMENT_FOLDER, name)
    local("jupyter-notebook %(path)s/%(name)s.ipynb" %
          {"path": path, "name": name})

import nbformat
from nbconvert import PythonExporter

def update_script(name):
    python_exporter = PythonExporter()
    with open("experiments/{name}/{name}.ipynb".format(name=name)) as f:
        notebook = nbformat.reads(f.read(), 4)
        test = python_exporter.from_notebook_node(notebook)
        path = "experiments/{name}/{name}.py".format(name=name)
        with open(path, "w") as f_out:
            f_out.write(test[0])
        return path

@task
def make(name):
    """
    Fabric command to make all the folder structures and compile nodes
    """
    # In python 3.5
    #import importlib.util
    #spec = importlib.util.spec_from_file_location("module.name", "/path/to/file.py")
    #foo = importlib.util.module_from_spec(spec)
    #spec.loader.exec_module(foo)
    #foo.MyClass()

    path = update_script(name)
    from importlib.machinery import SourceFileLoader
    SourceFileLoader(name, path).load_module().make()

@task
def launch_cooja(name):
    """
    Fabric command to launch an experiment
    """
    path = update_script(name)
    from importlib.machinery import SourceFileLoader
    SourceFileLoader(name, path).load_module().launch_cooja()
