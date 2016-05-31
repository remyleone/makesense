import logging
import pdb


from makesense.analyze.packet_loss import packet_loss
from makesense.analyze.pcap import pcap2csv, format_pcap_csv
from makesense.analyze.pcap import df_strobes
from makesense.analyze.pcap import dashboard
from makesense.parser.powertracker2csv import powertracker2csv
from makesense.parser.parse_serial import message
from makesense.estimators.estimators import Estimator
from makesense.analyze.strobes import strobes
from makesense.estimators.checker import check
from makesense.plotting.plot_bin import plot_bin
from makesense.plotting.plot_series import plot_series
from makesense.plotting.plot_packet_loss import plot_packet_loss
from makesense.plotting.plot_strobes import plot_strobes


from fabric.api import local, get, hosts, put, env, roles, run
from itertools import chain

logging.basicConfig(filename="fab.log", filemode="w", level=logging.DEBUG)

env.use_ssh_config = True
env.shell = "/usr/local/bin/bash -c "
env.roledefs.update({
    "web": ["perso", "erebor"],
    "cluster": ["enst", "nexium"]
})

traffic = {"low": 1, "medium": 5, "high": 10}

folder_chaine = [
    # "chaine/chaine_high/",
    # "chaine/chaine_high_calibration_75/",
    "chaine/chaine_high_calibration_75_8/",
    "chaine/chaine_high_calibration_75_16/",
    "chaine/chaine_high_calibration_75_4/",
    # "chaine/chaine_low/",
    # "chaine/chaine_low_calibration/",
    # "chaine/chaine_medium/",
    # "chaine/chaine_medium_calibration/"
]


folder_fleur = [
    # "fleur/fleur_high",
    # "fleur/fleur_high_calibration",
    # "fleur/fleur_low",
    # "fleur/fleur_low_calibration",
    # "fleur/fleur_medium",
    # "fleur/fleur_medium_calibration"
]


folder_arbre = [
    # "arbre_overhearing/arbre_high",
    # "arbre_overhearing/arbre_high_calibration",
    # "arbre_overhearing/arbre_low",
    # "arbre_overhearing/arbre_low_calibration",
    # "arbre_overhearing/arbre_medium",
    # "arbre_overhearing/arbre_medium_calibration",
    # "arbre/arbre_high",
    # "arbre/arbre_high_calibration",
    # "arbre/arbre_low",
    # "arbre/arbre_low_calibration",
    # "arbre/arbre_medium",
    # "arbre/arbre_medium_calibration"
]


all_folders = chain(folder_chaine, folder_fleur, folder_arbre)


def deploy_firmware():
    for folder in all_folders:
        local("cp udp-client.c udp-server.c %s" % folder)


def compile_firmware():
    for folder in all_folders:
        local("(cd %s; make nodes)" % folder)


def run_simulation():
    for folder in all_folders:
        local("(cd %s; make run)" % folder)


# def deploy_flower():
#     local("cp project-conf-high-calibration.h fleur/fleur_high_calibration/project-conf.h")
#     local("cp project-conf-high.h fleur/fleur_high/project-conf.h")
#     local("cp project-conf-low-calibration.h fleur/fleur_low_calibration/project-conf.h")
#     local("cp project-conf-low.h fleur/fleur_low/project-conf.h")
#     local("cp project-conf-medium-calibration.h fleur/fleur_medium_calibration/project-conf.h")
#     local("cp project-conf-medium.h fleur/fleur_medium/project-conf.h")
        

def analyze():
    print("Begin analyze")
    for folder in all_folders:
        print(folder)
        # powertracker2csv(folder)
        # packet_loss(folder)
        # message(folder)
        # pcap2csv(folder)
        # format_pcap_csv(folder)
        # dashboard(folder)
        df_strobes(folder)


def estimate():
    print("Begin estimation")
    for folder in all_folders:
        print(folder)
        e = Estimator(folder)
        e.estimate()
        check(e)
        e.save()


def plot():
    print("Begin plot")
    for folder in all_folders:
        print(folder)
        # plot_bin(folder)
        # plot_series(folder)
        plot_packet_loss(folder)
        plot_strobes(folder)


def calibration():
    print("Begin calibration (strobes)")
    strobes("packet_size.old/contikimac")


def deploy_web():
    for folder in all_folders:
        local("pandoc index.md > %s/index.html" % folder)

    local("pandoc packet_size_overview.md > packet_size/index.html")

    for i in range(10, 120, 10):
        local("pandoc packet_size.md > packet_size/contikimac/%d/index.html" % i)
        local("pandoc packet_size.md > packet_size/nullmac/%d/index.html" % i)


def run_all():
    for folder in all_folders:
        deploy_firmware(folder)
        compile_firmware(folder)
        run_simulation(folder)
        powertracker2csv(folder)
        message(folder)
        e = Estimator(folder)
        e.estimate()
        check(e)
        e.save()
        plot_bin(folder)
        plot_series(folder)


# def deploy_chaine():
#     print("Deploy project-conf to chaine")

#     local("cp project-conf-high-calibration.h chaine/chaine_high_calibration/project-conf.h")
#     local("cp project-conf-high.h chaine/chaine_high/project-conf.h")
#     local("cp project-conf-low-calibration.h chaine/chaine_low_calibration/project-conf.h")
#     local("cp project-conf-low.h chaine/chaine_low/project-conf.h")
#     local("cp project-conf-medium-calibration.h chaine/chaine_medium_calibration/project-conf.h")
#     local("cp project-conf-medium.h chaine/chaine_medium/project-conf.h")


# def deploy_arbre():
#     print("Deploy project-conf to arbre")

#     local("cp project-conf-high-calibration.h arbre_overhearing/arbre_high_calibration/project-conf.h")
#     local("cp project-conf-high.h arbre_overhearing/arbre_high/project-conf.h")
#     local("cp project-conf-low-calibration.h arbre_overhearing/arbre_low_calibration/project-conf.h")
#     local("cp project-conf-low.h arbre_overhearing/arbre_low/project-conf.h")
#     local("cp project-conf-medium-calibration.h arbre_overhearing/arbre_medium_calibration/project-conf.h")
#     local("cp project-conf-medium.h arbre_overhearing/arbre_medium/project-conf.h")
#     local("cp project-conf-high-calibration.h arbre/arbre_high_calibration/project-conf.h")
#     local("cp project-conf-high.h arbre/arbre_high/project-conf.h")
#     local("cp project-conf-low-calibration.h arbre/arbre_low_calibration/project-conf.h")
#     local("cp project-conf-low.h arbre/arbre_low/project-conf.h")
#     local("cp project-conf-medium-calibration.h arbre/arbre_medium_calibration/project-conf.h")
#     local("cp project-conf-medium.h arbre/arbre_medium/project-conf.h")


# def deploy_packet_size():
#     print("Deploy project-conf to packet_size")

#     for size in range(10, 100, 10):
#         local("cp udp-server.c udp-client.c packet_size/contikimac/%d/" % size)


@hosts("enst")
def fetch_results_from_enst():
    for folder in all_folders:
        get("~/results_estimators/%s/serial.log" % folder,
            "~/Dropbox/results_estimators/%s/serial.log" % folder)
        get("~/results_estimators/%s/powertracker.log" % folder,
            "~/Dropbox/results_estimators/%s/powertracker.log" % folder)


@hosts("erebor")
def sync_web():
    for folder in all_folders:
        run("mkdir -p ~/html/results/%s" % folder)
        local("rsync -Pizav %s/results/ erebor:~/html/results/%s" % (folder, folder))
        print("See results at http://results.sieben.fr/%s" % folder)


@hosts("nexium")
def fetch_results_from_nexium():
    for folder in all_folders:
        get("~/results_estimators/%s/serial.log" % folder,
            "~/Dropbox/results_estimators/%s/serial.log" % folder)
        get("~/results_estimators/%s/powertracker.log" % folder,
            "~/Dropbox/results_estimators/%s/powertracker.log" % folder)


@roles("cluster")
def upload_sim():
    for folder in all_folders:

        put("~/Dropbox/results_estimators/%s/main.csc" % folder,
            "~/results_estimators/%s/main.csc" % folder)

        put("~/Dropbox/results_estimators/%s/project-conf.h" % folder,
            "~/results_estimators/%s/project-conf.h" % folder)
        put("~/Dropbox/results_estimators/%s/project-conf.h" % folder,
            "~/results_estimators/%s/project-conf.h" % folder)

        put("~/Dropbox/results_estimators/%s/udp-client.c" % folder,
            "~/results_estimators/%s/udp-client.c" % folder)
        put("~/Dropbox/results_estimators/%s/udp-server.c" % folder,
            "~/results_estimators/%s/udp-server.c" % folder)

        put("~/Dropbox/results_estimators/%s/udp-client.sky" % folder,
            "~/results_estimators/%s/udp-client.sky" % folder)
        put("~/Dropbox/results_estimators/%s/udp-server.sky" % folder,
            "~/results_estimators/%s/udp-server.sky" % folder)

        # put("~/Dropbox/results_estimators/%s/udp-client.wismote" % folder,
        #     "~/results_estimators/%s/udp-client.wismote" % folder)
        # put("~/Dropbox/results_estimators/%s/udp-server.wismote" % folder,
        #     "~/results_estimators/%s/udp-server.wismote" % folder)


@hosts("enst")
def launch_lame():
    run("cat /proc/cpuinfo | grep processor")
