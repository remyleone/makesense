#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module building up the graph using mat plot lib
"""

import re
from itertools import product
from csv import DictReader
import json
from networkx.readwrite import json_graph
import matplotlib
from scipy.interpolate import UnivariateSpline
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import os
from math import sqrt
import logging
from matplotlib.ticker import MaxNLocator


log = logging.getLogger("plot")


def damier():
    """
    TODO: Make them share some axis.
    """

    nodes = range(1, 16)

    # Energy that is constant for all nodes.
    raw_energy = {n: {"time": [], "energy": []}
                  for n in nodes}

    raw_result = {"noinfo": {n: {"time": [], "estimation": []}
                             for n in nodes},
                  "route": {n: {"time": [], "estimation": []}
                            for n in nodes},
                  "radio": {n: {"time": [], "estimation": []}
                            for n in nodes}}

    node_depth = {
        1: [1, 2],
        2: [3, 4, 5],
        3: [6, 7, 9, 10],
        4: [11, 12, 13, 14, 15]
    }

    # We only load energy records once
    with open("powertracker.csv") as f:
        reader = DictReader(f)
        for row in reader:
            node = int(row["mote_id"])
            raw_energy[node]["time"].append(float(row["monitored_time"]))
            raw_energy[node]["energy"].append(float(row["energy_consumed"]))

    for key, d in raw_result.items():
        for node, records in d.items():
            try:
                with open("%s_%s.csv" % (node, key)) as f:
                    reader = DictReader(f)
                    for row in reader:
                        d[node]["time"].append(float(row["time"]))
                        d[node]["estimation"].append(float(row["estimation"]))
            except IOError as e:
                log.warning(e)
                raise e

    # Creating a spline for each values

    energy_spline = {node: UnivariateSpline(data["time"], data["energy"], k=1)
                     for node, data in raw_energy.items()}

    estimator_spline = {
        "route": {n: UnivariateSpline(data["time"],
                                      data["estimation"])
                  for n, data in raw_result["route"].items()},
        "noinfo": {n: UnivariateSpline(data["time"], data["estimation"])
                   for n, data in raw_result["noinfo"].items()},
        "radio": {n: UnivariateSpline(data["time"], data["estimation"])
                  for n, data in raw_result["radio"].items()}
    }

    x = np.arange(200)

    # Averaging all spline

    mean_estimator_spline = {
        "route": {depth: np.mean([estimator_spline["route"][node](x)
                                  for node in node_list],
                                 axis=0)
                  for depth, node_list in node_depth.items()},

        "noinfo": {depth: np.mean([estimator_spline["noinfo"][node](x)
                                   for node in node_list],
                                  axis=0)
                   for depth, node_list in node_depth.items()},

        "radio": {depth: np.mean([estimator_spline["radio"][node](x)
                                  for node in node_list],
                                 axis=0)
                  for depth, node_list in node_depth.items()}}

    mean_energy_spline = {
        depth: np.mean([energy_spline[node](x)
                        for node in node_list], axis=0)
        for depth, node_list in node_depth.items()}

    # We got 4 levels of depth
    f, axarr = plt.subplots(4, 3)

    # Noinfo
    for depth in node_depth:

        axarr[depth - 1, 0].plot(x, mean_estimator_spline["noinfo"][depth], '--', linewidth=2)
        axarr[depth - 1, 0].plot(x, mean_energy_spline[depth], linewidth=2)
	axarr[depth - 1, 0].yaxis.set_major_locator(MaxNLocator(5))

        if depth == min(node_depth):
            axarr[depth - 1, 0].set_title("noinfo")

    # Route
    for depth in node_depth:

        axarr[depth - 1, 1].plot(x, mean_estimator_spline["route"][depth], "--", linewidth=2)
        axarr[depth - 1, 1].plot(x, mean_energy_spline[depth], linewidth=2)

        if depth == min(node_depth):
            axarr[depth - 1, 1].set_title("route")

    # Radio
    for depth in node_depth:

        axarr[depth - 1, 2].plot(x, mean_estimator_spline["radio"][depth], "--", linewidth=2)
        axarr[depth - 1, 2].plot(x, mean_energy_spline[depth], linewidth=2)

        if depth == min(node_depth):
            axarr[depth - 1, 2].set_title("radio")

    for depth in node_depth:
        axarr[depth - 1, 2].yaxis.set_label_position("right")
        axarr[depth - 1, 2].set_ylabel("Depth %d" % depth, rotation="vertical")




    for ax in plt.gcf().axes:
        try:
            ax.label_outer()
        except Exception as e:
            log.warning(e)
            raise e

    f.savefig("damier.pdf", format="pdf")


def distance(x1, x2, y1, y2):
    return sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def plot_rpl_tree():
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    ax1.set_title("RPL tree")
    ax1.axis("off")

    with open("rpl_tree.json") as rpl_tree_file:
        rpl_net = json_graph.loads(rpl_tree_file.read())
        # Drawing the nodes
        nx.draw_networkx(rpl_net, ax=ax1,
                         edge_color='r', arrows=True)
    fig.savefig("rpl_tree.pdf", format="pdf")


def plot_radio_tree():
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    ax1.set_title("Radio tree")
    ax1.axis("off")
    radio_net = nx.Graph()

    with open("graph.json") as f:
        g = json.loads(f.read())
        for node in g:
            radio_net.add_node(node["mote_id"], mote_type=node["mote_type"],
                               x=node["x"], y=node["y"])

        for (a, d_a), (b, d_b) in product(radio_net.nodes(data=True), radio_net.nodes(data=True)):
            d = distance(d_a["x"], d_b["x"], d_a["y"], d_b["y"])
            if d < 42:
                radio_net.add_edge(a, b)

        nx.draw_networkx(radio_net, ax=ax1,
                         edge_color='r', arrows=True)

        fig.savefig("radio_tree.pdf", format="pdf")


def repartition_protocol():
    """
    Representation of protocol repartition (stacked histogram)

    Include UDP, CoAP, ping, RPL, other...
    """
    fig1 = plt.figure()
    ax1 = fig1.add_subplot(111)
    ax1.set_title("Protocol repartition")
    ax1.set_ylabel("Bytes")
    ax1.set_xlabel("Time (s)")

    color = {"coap": "red",
             "rpl": "blue",
             "ping": "green",
             "total": "black",
             "udp": "yellow",
             "rplinfo": "cyan",
             "battery": "magenta"}

    with open("io.csv") as f:
        reader = DictReader(f)

        # Hack to avoid duplicate label in legend
        label_first = {"total": True, "rpl": True, "ping": True,
                       "udp": True, "coap": True, "battery": True,
                       "rplinfo": True}
        for row in reader:
            row = {k: float(v) for k, v in row.iteritems()}
            width = (row["bin_end"] - row["bin_start"]) / 2
            bottom = 0.0

            # rpl
            if row["rpl_bytes"]:
                ax1.bar(row["bin_start"] + width, row["rpl_bytes"],
                        color=color["rpl"], width=width, bottom=bottom,
                        label="rpl" if label_first["rpl"] else "")
                bottom += row["rpl_bytes"]
                label_first["rpl"] = False

            # udp
            if row["udp_bytes"]:
                ax1.bar(row["bin_start"] + width, row["udp_bytes"],
                        color=color["udp"], width=width, bottom=bottom,
                        label='application' if label_first["udp"] else "")
                bottom += row["udp_bytes"]
                label_first["udp"] = False

            # rplinfo
            if row["rplinfo_bytes"]:
                ax1.bar(row["bin_start"] + width, row["rplinfo_bytes"],
                        color=color["rplinfo"], width=width, bottom=bottom,
                        label="rplinfo" if label_first["rplinfo"] else "")
                # Last value
                #bottom += row["rplinfo_bytes"]
                label_first["rplinfo"] = False

    key, value = [], []
    for k, v in color.items():
        key.append(k)
        value.append(v)
    #plt.legend(tuple(key), tuple(value))
    plt.legend()
    plt.savefig("repartition_protocol.pdf", format="pdf")




class Plot():
    """
    Graph function implementing the strategy pattern
    """

    def traffic_impact(self):
        """
        3 curves. One for each traffic.
        """
        nodes = [node for node, data in self.nodes
                 if "root" not in data]

        low = {"noinfo": {n: {"time": [], "difference": []}
                          for n in nodes},
               "route": {n: {"time": [], "difference": []}
                         for n in nodes},
               "radio": {n: {"time": [], "difference": []}
                         for n in nodes}}
        medium = {"noinfo": {n: {"time": [], "difference": []}
                             for n in nodes},
                  "route": {n: {"time": [], "difference": []}
                            for n in nodes},
                  "radio": {n: {"time": [], "difference": []}
                            for n in nodes}}
        high = {"noinfo": {n: {"time": [], "difference": []}
                           for n in nodes},
                "route": {n: {"time": [], "difference": []}
                          for n in nodes},
                "radio": {n: {"time": [], "difference": []}
                          for n in nodes}}

        for key, d in high.items():
            for node, records in d.items():
                try:
                    with open(PJ(RESULTS_DIR, "sim_10_100_100_123456", "%s_%s.csv" % (node, key))) as f:
                        reader = DictReader(f)
                        for row in reader:
                            d[node]["time"].append(float(row["time"]))
                            d[node]["difference"].append(float(row["difference"]))
                except IOError as e:
                    log.warning(e)
                    raise e

        for key, d in medium.items():
            for node, records in d.items():
                try:
                    with open(PJ(RESULTS_DIR, "sim_25_100_100_123456", "%s_%s.csv" % (node, key))) as f:
                        reader = DictReader(f)
                        for row in reader:
                            d[node]["time"].append(float(row["time"]))
                            d[node]["difference"].append(float(row["difference"]))
                except IOError as e:
                    log.warning(e)
                    raise e

        for key, d in low.items():
            for node, records in d.items():
                try:
                    with open(PJ(RESULTS_DIR, "sim_50_100_100_123456", "%s_%s.csv" % (node, key))) as f:
                        reader = DictReader(f)
                        for row in reader:
                            d[node]["time"].append(float(row["time"]))
                            d[node]["difference"].append(float(row["difference"]))
                except IOError as e:
                    log.warning(e)
                    raise e

        estimator_name = ["noinfo", "route", "radio"]
        estimator = range(len(estimator_name))
        f, axarr = plt.subplots(len(nodes), len(estimator_name))
        for (node, estimator) in product(nodes, estimator):
            axarr[node - 1, estimator].plot(low[estimator_name[estimator]][node]["time"],
                                            low[estimator_name[estimator]][node]["difference"], label="low",
                                            color="green")
            axarr[node - 1, estimator].plot(medium[estimator_name[estimator]][node]["time"],
                                            medium[estimator_name[estimator]][node]["difference"], label="medium",
                                            color="orange")
            axarr[node - 1, estimator].plot(high[estimator_name[estimator]][node]["time"],
                                            high[estimator_name[estimator]][node]["difference"], label="high",
                                            color="red")

            if node == max(nodes):
                axarr[node - 1, estimator].set_xlabel('T (s)')
            if not estimator:
                axarr[node - 1, estimator].set_ylabel('E (Ah)')
            if node == 1:
                axarr[node - 1, estimator].set_title(estimator_name[estimator])

        for ax in plt.gcf().axes:
            try:
                ax.label_outer()
            except Exception as e:
                log.warning(e)
                raise e
        img_path = PJ(self.img_dir, "traffic_impact.pdf")
        f.savefig(img_path, format="pdf")

    def recalibration_impact(self):
        nodes = [node for node, data in self.nodes
                 if "root" not in data]

        low = {"noinfo": {n: {"time": [], "difference": []}
                          for n in nodes},
               "route": {n: {"time": [], "difference": []}
                         for n in nodes},
               "radio": {n: {"time": [], "difference": []}
                         for n in nodes}}
        medium = {"noinfo": {n: {"time": [], "difference": []}
                             for n in nodes},
                  "route": {n: {"time": [], "difference": []}
                            for n in nodes},
                  "radio": {n: {"time": [], "difference": []}
                            for n in nodes}}
        high = {"noinfo": {n: {"time": [], "difference": []}
                           for n in nodes},
                "route": {n: {"time": [], "difference": []}
                          for n in nodes},
                "radio": {n: {"time": [], "difference": []}
                          for n in nodes}}

        for key, d in low.items():
            for node, records in d.items():
                try:
                    with open(PJ(RESULTS_DIR, "sim_10_500_100_123456", "%s_%s.csv" % (node, key))) as f:
                        reader = DictReader(f)
                        for row in reader:
                            d[node]["time"].append(float(row["time"]))
                            d[node]["difference"].append(float(row["difference"]))
                except IOError as e:
                    log.warning(e)
                    raise e

        for key, d in medium.items():
            for node, records in d.items():
                try:
                    with open(PJ(RESULTS_DIR, "sim_10_250_100_123456", "%s_%s.csv" % (node, key))) as f:
                        reader = DictReader(f)
                        for row in reader:
                            d[node]["time"].append(float(row["time"]))
                            d[node]["difference"].append(float(row["difference"]))
                except IOError as e:
                    log.warning(e)
                    raise e

        for key, d in high.items():
            for node, records in d.items():
                try:
                    with open(PJ(RESULTS_DIR, "sim_10_100_100_123456", "%s_%s.csv" % (node, key))) as f:
                        reader = DictReader(f)
                        for row in reader:
                            d[node]["time"].append(float(row["time"]))
                            d[node]["difference"].append(float(row["difference"]))
                except IOError as e:
                    log.warning(e)
                    raise e

        estimator_name = ["noinfo", "route", "radio"]
        estimator = range(len(estimator_name))
        f, axarr = plt.subplots(len(nodes), len(estimator_name))
        for (node, estimator) in product(nodes, estimator):
            axarr[node - 1, estimator].plot(low[estimator_name[estimator]][node]["time"],
                                            low[estimator_name[estimator]][node]["difference"], label="low",
                                            color="green")
            axarr[node - 1, estimator].plot(medium[estimator_name[estimator]][node]["time"],
                                            medium[estimator_name[estimator]][node]["difference"], label="medium",
                                            color="orange")
            axarr[node - 1, estimator].plot(high[estimator_name[estimator]][node]["time"],
                                            high[estimator_name[estimator]][node]["difference"], label="high",
                                            color="red")

            if node == max(nodes):
                axarr[node - 1, estimator].set_xlabel('T (s)')
            if not estimator:
                axarr[node - 1, estimator].set_ylabel('E (Ah)')
            if node == 1:
                axarr[node - 1, estimator].set_title(estimator_name[estimator])

        for ax in plt.gcf().axes:
            try:
                ax.label_outer()
            except Exception as e:
                log.warning(e)
                raise e
        img_path = PJ(self.img_dir, "recalibration_impact.pdf")
        f.savefig(img_path, format="pdf")


    def overhead(self):
        """
        Plot the overhead (RPL, ACK,...).

        """
        fig = plt.figure()
        ax1 = fig.add_subplot(111)

        ax1.set_title('RPL traffic by time')
        ax1.set_xlabel('Time (s)')
        ax1.set_ylabel('RPL traffic (bytes)')

        with open(PJ(self.result_dir, "io.csv")) as io_csv_f:
            reader = DictReader(io_csv_f)
            time, overhead_bytes = [], []
            for row in reader:
                time.append(float(row["bin_end"]))
                overhead_bytes.append(float(row["total_bytes"])
                                      - float(row["udp_bytes"])
                                      - float(row["ping_bytes"])
                                      - float(row["coap_bytes"]))
            ax1.plot(time, overhead_bytes)

        img_path = PJ(self.img_dir, "overhead.pdf")
        fig.savefig(img_path, format="pdf")
        update_report(self.result_dir, "overhead", {"img_src": "img/overhead.pdf", "text": """

                    This graph measures the amount of bytes sent by nodes that
                    are not application oriented (UDP, ping or CoAP) therefore
                    we can see the amount of bytes transmitted just to keep
                    the network alive. This packets are usually RPL and ACK
                    packets.)"""})


    def depth_energy(self):
        """
        Energy used by depth of a node in the RPL tree.
        """
        fig1 = plt.figure()
        ax1 = fig1.add_subplot(111)

        ax1.set_title('Energy by depth')
        ax1.set_ylabel('Energy (Ah)')
        ax1.set_xlabel('Depth')

        with open(PJ(self.result_dir, "depth_energy.csv")) as f:
            reader = DictReader(f)
            depth, mean, std = [], [], []
            for row in reader:
                depth.append(row["depth"])
                mean.append(float(row["mean_energy"]))
                std.append(float(row["std_energy"]))

            n_groups = len(depth)
            index = np.arange(n_groups)

            bar_width = 0.35
            opacity = 0.4
            error_config = {'ecolor': '0.3'}

            ax1.bar(index, mean, bar_width,
                    alpha=opacity,
                    yerr=std,
                    error_kw=error_config,
                    label='Depth')

            plt.xticks(index + bar_width, depth)

        plt.legend()
        plt.tight_layout()
        img_path = PJ(self.img_dir, "energy_depth.pdf")
        plt.savefig(img_path, format="pdf")
        update_report(self.result_dir, "depth_energy", {
            "img_src": "img/energy_depth.pdf",
            "text": """

            Energy used by nodes that are a fixed depth from the root."""})


    def estimator_overhead(self):
        """
        Plotting the overhead in packet send of an estimator.

        We get this by doing a calculating how many bytes are
        used by the estimators. Then because we know the cost of
        one byte to be transmitted we can know the amount of energy spent.
        """
        time, battery, rplinfo, other = [], [], [], []
        fig = plt.figure()
        ax1 = fig.add_subplot(111)

        ax1.set_title('Estimator Overhead')
        ax1.set_xlabel('Time (s)')
        ax1.set_ylabel('Packets')

        with open(PJ(self.result_dir, "estimator_overhead.csv")) as estimator_overhead_csv_f:
            reader = DictReader(estimator_overhead_csv_f)

            for row in reader:
                time.append(float(row["time"]))
                battery.append(float(row["battery"]))
                rplinfo.append(float(row["rplinfo"]))
                other.append(float(row["other"]))

            ax1.plot(time, battery, label="battery")
            ax1.plot(time, rplinfo, label="rplinfo")
            ax1.plot(time, other, label="Other")

        plt.legend(loc='upper left', shadow=True)
        img_path = PJ(self.img_dir, "estimator_overhead.pdf")
        fig.savefig(img_path, format="pdf")
        update_report(self.result_dir, "estimator_overhead", {
            "img_src": "img/estimator_overhead.pdf",
            "text": """
            Estimator overhead
            """})

    def estimator_energy(self):
        """
        TODO: Make them share some axis.
        """
        for estimator in os.listdir(self.result_dir):
            m = re.match("estimator_(?P<estimator_type>dumb|route|radio)_(?P<mote_id>\d+).csv", estimator)
            if m:
                fig = plt.figure()
                ax1 = fig.add_subplot(111)

                estimator_type = m.groupdict()["estimator_type"]
                mote_id = m.groupdict()["mote_id"]
                #ax1.set_title('Estimator Energy for %s' % m.groupdict()["estimator_type"])
                ax1.set_xlabel('Time (s)')
                ax1.set_ylabel('Energy (Ah)')
                time, energy, estimation = [], [], []

                with open(PJ(self.result_dir, estimator)) as estimator_csv_f:
                    reader = DictReader(estimator_csv_f)

                    for row in reader:
                        time.append(float(row["time"]))
                        estimation.append(float(row["estimation"]))
                        energy.append(float(row["energy"]))

                ax1.plot(time, energy, label="energy")
                ax1.plot(time, estimation, label="estimation")
                ax1.legend(loc='lower right')

                img_path = PJ(self.img_dir, "%s_%s_estimator.pdf" % (mote_id, estimator_type))
                fig.savefig(img_path, format="pdf")
                update_report(self.result_dir, "%s_estimator_energy" % estimator, {
                    "img_src": "img/%s_%s_estimator.pdf" % (mote_id, estimator_type),
                    "text": """
                    Estimator energy for %s
                    """ % estimator})
