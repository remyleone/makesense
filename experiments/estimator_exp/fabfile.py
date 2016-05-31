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
from makesense import estimators as estmt

# Using iotlab

logging.basicConfig(level=logging.INFO)
env.hosts = ["localhost"]
env.use_ssh_config = True
env.shell = "/bin/bash -c"
env.roledefs.update({
    "web": ["perso", "galois"],
    "cluster": ["enst", "nexium"],
    "iotlab": ["rennes", "strasbourg", 
    #"euratech", # Too much problems
    "grenoble", "rocquencourt", "paris"]
})


ROOT_DIR = os.path.dirname(__file__)
CONTIKI_FOLDER = os.path.abspath(pj("/home/sieben/code/iot-lab/parts/", "contiki"))
EXPERIMENT_FOLDER = pj(CONTIKI_FOLDER, "examples")
TEMPLATE_FOLDER = pj(ROOT_DIR, "templates")
TEMPLATE_ENV = Environment(loader=FileSystemLoader(TEMPLATE_FOLDER))
COOJA_DIR = pj(CONTIKI_FOLDER, "tools", "cooja")


@task
def new(name):
    """
    Default experiment is a client and a server sending messages to each others.
    The default platform is wismote
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
        f.write(makefile_template.render(contiki=CONTIKI_FOLDER,
                                         target="wismote"))

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
                {"name": "server", "description": "server",
                    "firmware": "dummy-server.wismote"},
                {"name": "client", "description": "client",
                    "firmware": "dummy-client.wismote"}
            ],
            motes=[
                {"mote_id": 1, "x": 0, "y": 0, "z": 0, "mote_type": "server"},
                {"mote_id": 2, "x": 1, "y": 1, "z": 0, "mote_type": "client"},
            ],
            script=script))

    print(
        "Think to rename otherwise if you do fab new:%s again dummy files will be overwritten" % name)


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
def compile_nodes(name, target="wismote"):
    """
    Fabric command to compile nodes
    """
    path = pj(EXPERIMENT_FOLDER, name)
    with lcd(path):
        local("make -j TARGET=%s" % target)


# @task
# @hosts("grenoble")
# def push_iotlab(name):
#     experiment_path = pj(EXPERIMENT_FOLDER, name)
#     results_folder = pj(experiment_path, "results", "iotlab")
#     if not os.path.exists(results_folder):
#         os.makedirs(results_folder)

#     # gets user password from credentials file None, None
#     user, passwd = iotlabcli.get_user_credentials()
#     api = iotlabcli.Api(user, passwd)

#     # describe the resources
#     resources = None
#     with open(pj(experiment_path, "iotlab.json")) as f:
#         config = json.loads(f.read())
#         resources = [experiment.exp_resources(**c) for c in config]

#     print(resources)
#     # actually submit the experiment
#     exp_id = None
#     # We move to the folder to have a portable iotlab.json
#     with lcd(experiment_path):
#         exp_res = experiment.submit_experiment(
#             api, 'dummy_experiment', 1, resources)
#         exp_id = exp_wres["id"]
#         with open("results/iotlab/iotlab.json", "w") as f:
#             f.write(json.dumps({"id": exp_id}))

#     # get the content
#     print "Exp submited with id: %u" % exp_id

#     run("experiment-cli wait -i %d" % exp_id)

#     with open(pj(results_folder, "serial.log"), 'w') as f:
#         run("./iot-lab/tools_and_scripts/serial_aggregator.py -i %d" % exp_id,
#             stdout=f)
#     print("Written serial logs to %s" % pj(results_folder, "serial.log"))


@task
@hosts("grenoble")
def pull_iotlab(name, experiment_id=None):
    iotlab_folder = pj(EXPERIMENT_FOLDER, name, "results", "iotlab")
    # with open(pj(iotlab_folder, "iotlab.json")) as f:
    #     exp_json = json.load(f)
    #     experiment_id = exp_json["id"]

    get(".iot-lab/%d" % int(experiment_id), local_path=iotlab_folder)


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

    # Parsing serials
    # parser.iotlabserial2message(pj(path, "results", "iotlab", "15161", "log"))

    # Parsing PCAP
    parser.pcap2csv(
        pj(path, "results", "iotlab", "15161", "sniffer")
    )

    # Parsing Energy
    # parser.parse_iotlab_energy(pj(path, "results", "iotlab", "15161"))
    # parser.parse_iotlab_m3_energy(pj(path, "results", "iotlab", "15161", "consumption"))


@task
def analyze(name="iotlab_estimators", exp_id=15161):
    """
    Fabric command to analyze trace
    """
    path = pj(EXPERIMENT_FOLDER, name, "results", "iotlab", str(exp_id))
    output_path = pj(path, "analysis")

    if not os.path.exists(output_path):
        os.mkdir(output_path)

    df_pcap = pd.read_csv(pj(path, "sniffer", "pretty_pcap.csv"), parse_dates=True, index_col="Unnamed: 0")
    df_physical = pd.read_csv(pj(path, "consumption", "consumption.csv"), parse_dates=True, index_col="Unnamed: 0")
    df_serial = pd.read_csv(pj(path, "log", "serial.csv"))
    
    anlz.revision(df_pcap=df_pcap, df_serial=df_serial, output=(output_path, "revision.csv"))

    #anlz.packet_cost(df_physical, df_pcap, output=pj(output_path, "packet_cost"))
    #anlz.protocol_depth(df_serial, df_pcap, output=pj(output_path, "protocol_depth"))
    #anlz.protocol_time(df_pcap, output=pj(output_path, "protocol_time"))

    # df_estimation = pd.read_csv()
    # anlz.error_estimator(df_estimator)


@task
def estimate(name="iotlab_estimators", exp_id=15161):
    """
    Fabric command to produce estimation
    """
    path = pj(EXPERIMENT_FOLDER, name, "results", "iotlab", str(exp_id))
    output_path = pj(path, "analysis")

    if not os.path.exists(output_path):
        os.mkdir(output_path)

    df_pcap = pd.read_csv(pj(path, "sniffer", "pretty_pcap.csv"), parse_dates=True, index_col="Unnamed: 0")
    df_serial = pd.read_csv(pj(path, "log", "serial.csv"), parse_dates=True, index_col="time")

    #estmt.packets(df_pcap)
    estmt.revisions(df_pcap, df_serial)

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
def notebook(name):
    notebook_template = TEMPLATE_ENV.get_template("dummy.ipynb")
    path = pj(EXPERIMENT_FOLDER, name)
    with open(pj(path, "%s.ipynb" % name), "w") as f:
        f.write(notebook_template.render())
    print("Run with fab web:%(name)s (ipython notebook %(path)s/%(name)s.ipynb)" %
          {"path": path, "name": name})


@task
@parallel
@roles("iotlab")
def update_iotlab():
    run("cd iot-lab; git pull")
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
    local("ipython notebook %(path)s/%(name)s.ipynb" %
          {"path": path, "name": name})

@task
def generate_firmware(name, num):
    path = pj(EXPERIMENT_FOLDER, name)
    main_csc_template = TEMPLATE_ENV.get_template("dummy_main.csc")
    script_template = TEMPLATE_ENV.get_template("dummy_script.js")
    script = script_template.render(
        timeout=100000,
        powertracker_frequency=10000,
    )

    import random
    nodes_id = range(2, int(num))

    client_template = TEMPLATE_ENV.get_template("iotlab_client.c")
    server_template = TEMPLATE_ENV.get_template("iotlab_server.c")
    mote_server = [{"name": "server", "description": "server",
                        "firmware": "iotlab_server.wismote"}]

    position_server = [{"mote_id": 1, "x": 0, "y": 0, "z": 0, "mote_type": "server"}]

    mote_client = [{"name": "iotlab_client_%d" % node_id, 
                     "description": "iotlab_client_%d" % node_id,
                     "firmware": "iotlab_client_%d.wismote" % node_id}
                     for node_id in nodes_id]

    position_client = [
        {"mote_id": node_id, 
        "x": 100 * random.random(),
        "y": 100 * random.random(), "z": 0, 
        "mote_type": "iotlab_client_%d" % node_id}
        for node_id in nodes_id
    ]

    mote_types = mote_server + mote_client
    motes = position_client + position_server

    with open(pj(path, "main.csc"), "w") as f:
        f.write(main_csc_template.render(
            title="Iotlab estimators",
            random_seed=12345,
            transmitting_range=50,
            interference_range=50,
            success_ratio_tx=1.0,
            success_ratio_rx=1.0,
            mote_types=mote_types,
            motes=motes,
            script=script))

    with open(pj(path, "iotlab_server.c"), "w") as f:
        f.write(server_template.render())


    for node_id in nodes_id:

        with open(pj(path, "iotlab_client_%d.c" % node_id), "w") as f:
            f.write(client_template.render(node_id=node_id))

@task
def compile(name="iotlab_estimators"):
    for platform in ["wismote", "iotlab-m3", "sky"]:
        compile_nodes(name, platform)

@task
@hosts("")

@task
@hosts("grenoble")
def push_iotlab_estimator(name="udp_00"):
    from iotlabcli import experiment
    experiment_path = pj(EXPERIMENT_FOLDER, name)

    testbed_results_folder = pj(experiment_path, "results", "iotlab")
    testbed_results = pj(experiment_path, "results", "iotlab")

    # Name to give to our run
    testbed_name = "estimators_experiment"

    # Testbed
    env.host_string = "grenoble"

    # Simulation duration in minutes
    testbed_duration = 20

    # Experiment id
    testbed_experiment_id = None

    # Grenoble settings
    testbed_client_nodes = ["m3-%d" % i for i in range(101, 121)]
    testbed_server_nodes = ["m3-100"]

    # Paris settings
    # testbed_client_nodes = ["m3-%d" % i for i in range(2, 69)]
    # testbed_server_nodes = ["m3-1"]


    testbed_all_nodes = testbed_client_nodes + testbed_server_nodes

    # describe the resources
    resources = [
      {
        "nodes": [
          "%s.%s.iot-lab.info" % (node, env.host_string) for node in testbed_client_nodes
        ],
        "firmware_path": pj(experiment_path, "client.iotlab-m3"),
        "profile_name": "m3_energy_monitoring"
      },
      {
        "nodes": [
          "%s.%s.iot-lab.info" % (node, env.host_string) for node in testbed_server_nodes
        ],
        "firmware_path": pj(experiment_path, "server.iotlab-m3"),
        "profile_name": "m3_packet_energy_monitoring"
      }
    ]

    resources = [experiment.exp_resources(**c) for c in resources]

    # Let's save all this configuration in the results folder to keep track of what we ran
    with open(pj(testbed_results_folder, "nodes.json"), "w") as f:
        f.write(json.dumps(resources,
                           sort_keys=True, indent=4, separators=(',', ': ')) )

    experiment_finished = False
    
    # gets user password from credentials file None, None
    # actually submit the experiment
    # We move to the folder to have a portable iotlab.json
    with lcd(experiment_path):
        user, pwd = iotlabcli.get_user_credentials()
        api = iotlabcli.Api(user, pwd)
        exp_res = experiment.submit_experiment(
            api, testbed_name, testbed_duration, resources)
        testbed_experiment_id = exp_res["id"]
        with open(pj(testbed_results_folder, "experiment.json"), "w") as f:
            f.write(json.dumps({"id": testbed_experiment_id}))

    # get the content
    print "Exp submited with id: %u" % testbed_experiment_id
    
    # We wait till the experiment is completed
    # note that this step requieres you to have experiment-cli installed on the command line.
    # TODO: Replace with a full pythonic way
    run("experiment-cli wait -i %d" % testbed_experiment_id)

    with open(pj(testbed_results_folder, "serial.log"), 'w') as f:
        run("./sniffer.sh %d" % testbed_experiment_id)

    get(".iot-lab/%d" % testbed_experiment_id, local_path=testbed_results)

@task
@hosts("grenoble")
def full_push_iotlab_estimator():
    """
    Déploiement d'une serie d'expériences
    """
    for exp in ["udp_0", "udp_1", "udp_5", "udp_10", "udp_15", "udp_20"]:
        push_iotlab_estimator(name=exp)