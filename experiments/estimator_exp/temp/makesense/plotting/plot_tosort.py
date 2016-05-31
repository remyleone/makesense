# -*- coding: utf-8 -*-

"""
Module building up the graph using mat plot lib
"""

from multiprocessing.pool import Pool
import re
from itertools import product
from collections import defaultdict
from csv import DictReader

from networkx.readwrite import json_graph
import matplotlib


matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import os

from . import Step
from .settings import RESULTS_DIR, PJ, log
from .utils import sim_to_do_in, distance
from .report import update_report


class Plot(Step):
    """
    Graph function implementing the strategy pattern
    """

    def __init__(self, simulation):
        """
        Initialize a plot
        """
        Step.__init__(self)
        self.load_settings()
        self.result_dir = simulation
        self.img_dir = PJ(self.result_dir, "img")
        if not os.path.exists(self.img_dir):
            os.makedirs(self.img_dir)

        # Graph loading
        self.rpl_tree, self.radio_json = None, None
        with open(PJ(self.result_dir, "rpl_tree.json")) as f:
            self.rpl_tree = json_graph.loads(f.read())
        with open(PJ(self.result_dir, "radio.json")) as f:
            self.radio_tree = json_graph.loads(f.read())
        self.nodes = self.rpl_tree.nodes(data=True)

        # Powertracker
        self.powertracker_csv = PJ(self.result_dir, "powertracker.csv")
        self.energy_csv = PJ(self.result_dir, "energy.csv")

        # PCAP
        self.io_csv = PJ(self.result_dir, "io.csv")

    def __call__(self):
        """
        Run the plot
        """
        log.info("Starting plots for %s" % self.result_dir)

        tasks_to_do = []

        plot_to_do = [self.energy, self.repartition_protocol, self.overhead, self.packet_loss, self.depth_energy]

        graph_to_do = [
            # self.plot_rpl_tree,
            # self.plot_radio_tree,
            # self.plot_graph
        ]
        estimator_graph_to_do = [
            self.divergence,
            # self.estimator_energy,
            self.estimator_overhead
        ]

        advanced_plot_to_do = [
            # Traffic impact on difference
            self.traffic_impact,
            # Recalibration impact on difference
            self.recalibration_impact,
            self.cost_calibration
        ]

        tasks_to_do.extend(plot_to_do)
        tasks_to_do.extend(graph_to_do)
        tasks_to_do.extend(estimator_graph_to_do)
        tasks_to_do.extend(advanced_plot_to_do)

        for task in tasks_to_do:
            try:
                log.info("Starting with %s" % task)
                task()
                log.info("Done with %s" % task)
            except IOError as e:
                log.warning(e)
                raise e
        log.info("All plot done for %s" % self.result_dir)

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

    def energy(self):
        """
        format :
        Sky_2 MONITORED 9898083 us
        Sky_2 ON 180565 us 1,82 %
        Sky_2 TX 83860 us 0,85 %
        Sky_2 RX 2595 us 0,03 %
        Sky_2 INT 907 us 0,01 %

        tx_cost: Transmitting during 1 us
        rx_cost: Reception during 1 us
        on_cost: Only CPU on during 1 us
        int_cost: Idle mode during 1 us
        """
        fig = plt.figure()
        ax1 = fig.add_subplot(111)

        ax1.set_title('Energy measured by Powertracker')
        ax1.set_xlabel('Time (s)')
        ax1.set_ylabel('Energy (Ah)')

        results = defaultdict(dict)
        with open(self.powertracker_csv) as f:
            reader = DictReader(f)
            for row in reader:
                results[row["mote_id"]].setdefault(
                    "time", []).append(row["monitored_time"])
                results[row["mote_id"]].setdefault(
                    "energy", []).append(row["energy_consumed"])

        for node, values in results.items():
            ax1.plot(values["time"], values["energy"], label=node)

        ax1.legend(loc="upper left")
        img_path = PJ(self.img_dir, "energy.pdf")
        fig.savefig(img_path, format="pdf")
        update_report(self.result_dir, "energy",
                      {"img_src": "img/energy.pdf",
                       "comment": "Several group to observe here.",
                       "text": """
             Powertracker analyze the energy consumption by using the amount of
             time that every node spend in a transmitting reception, interference
             or on mode."""})

    def plot_rpl_tree(self):
        fig = plt.figure()
        ax1 = fig.add_subplot(111)
        ax1.set_title("RPL tree")
        ax1.axis("off")

        with open(PJ(self.result_dir, "rpl_tree.json")) as rpl_tree_file:
            rpl_net = json_graph.loads(rpl_tree_file.read())
            # Drawing the nodes
            nx.draw_networkx(rpl_net, ax=ax1,
                             edge_color='r', arrows=True)
        img_path = PJ(self.img_dir, "rpl_tree.pdf")
        fig.savefig(img_path, format="pdf")

    def plot_radio_tree(self):
        fig = plt.figure()
        ax1 = fig.add_subplot(111)
        ax1.set_title("Radio tree")
        ax1.axis("off")
        radio_net = nx.Graph()

        for node in self.nodes:
            radio_net.add_node(node["mote_id"], mote_type=node["mote_type"],
                               x=node["x"], y=node["y"])

        for (a, d_a), (b, d_b) in product(radio_net.nodes(data=True), radio_net.nodes(data=True)):
            d = distance(d_a["x"], d_b["x"], d_a["y"], d_b["y"])
            if d < 42:
                radio_net.add_edge(a, b)

        nx.draw_networkx(radio_net, ax=ax1,
                         edge_color='r', arrows=True)

        img_path = PJ(self.img_dir, "radio_tree.pdf")
        fig.savefig(img_path, format="pdf")

    def plot_graph(self):
        """
        Plot the transmission graph of the simulation.

        TODO: Draw arrows and have a directed graph.
        http://goo.gl/Z697dH

        TODO: Graph with big nodes for big transmissions
        """
        fig = plt.figure()
        ax1 = fig.add_subplot(111)
        ax1.set_title("Transmission / RPL tree")
        ax1.axis("off")

        val_color = {"udp_server": 0.5714285714285714}

        pos = {node: data["pos"]
               for node, data in self.radio_tree.nodes(data=True)}

        # color for all nodes
        node_color = [val_color.get(data["mote_type"], 0.25)
                      for node, data in self.radio_tree.nodes(data=True)]
        # Drawing the nodes
        nx.draw_networkx_nodes(self.radio_tree, pos, node_color=node_color, ax=ax1)
        nx.draw_networkx_labels(self.radio_tree, pos, ax=ax1)

        # Drawing radio edges
        nx.draw_networkx_edges(self.radio_tree, pos, edgelist=self.radio_tree.edges(),
                               width=8, alpha=0.5, ax=ax1)

        # Adding the depth of each node.
        with open(PJ(self.result_dir, "depth.csv")) as depth_f:
            reader = DictReader(depth_f)
            for row in reader:
                node = int(row["node"])
                depth = row["depth"]

                ax1.text(pos[node][0] + 5, pos[node][1] + 5, depth,
                         bbox=dict(facecolor='red', alpha=0.5),
                         horizontalalignment='center')

        # Drawing RPL edges
        nx.draw_networkx_edges(
            self.rpl_tree, pos, edge_color='r', nodelist=[], arrows=True, ax=ax1)

        img_path = PJ(self.img_dir, "graph.pdf")
        fig.savefig(img_path, format="pdf")
        update_report(self.result_dir, "plot_graph", {
            "img_src": "img/graph.pdf",
            "comment": """
            When the edge is thick it means edges are in an RPL instance.
            Otherwise it means that the two nodes can see each others.
            """,
            "text": """
            We generate a random geometric graph then use information coming
            to the RPL root to construct the gateway representation of the RPL
            tree. We add into this tree representation the traffic generated.
            """})

    def energy_by_rate(self):
        """
        The higher lambda rate is, the higher the energy usage is going to be.
        """
        plt.title("Protocol repartition")
        plt.ylabel("Bytes")
        plt.xlabel("Time (s)")
        img_path = PJ(self.img_dir, "energy_by_rate.pdf")
        plt.savefig(img_path, format="pdf")
        update_report(self.result_dir, "energy_by_rate", {
            "img_src": "img/energy_by_rate.pdf",
            "text": """
            Energy used in average by nodes that are sending at a fixed rate."""})

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

    def repartition_protocol(self):
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

        with open(self.io_csv) as f:
            reader = DictReader(f)

            # Hack to avoid duplicate label in legend
            label_first = {"total": True, "rpl": True, "ping": True,
                           "udp": True, "coap": True, "battery": True,
                           "rplinfo": True}
            for row in reader:
                row = {k: float(v) for k, v in row.iteritems()}
                width = (row["bin_end"] - row["bin_start"]) / 2
                bottom = 0.0

                # if row["total_bytes"]:
                #     ax1.bar(row["bin_start"], row['total_bytes'],
                #             color=color["total"], width=width,
                #             label="total" if label_first["total"] else "")
                #     label_first["total"] = False

                # rpl
                if row["rpl_bytes"]:
                    ax1.bar(row["bin_start"] + width, row["rpl_bytes"],
                            color=color["rpl"], width=width, bottom=bottom,
                            label="rpl" if label_first["rpl"] else "")
                    bottom += row["rpl_bytes"]
                    label_first["rpl"] = False

                # ping_bytes
                if row["ping_bytes"]:
                    ax1.bar(row["bin_start"] + width, row["ping_bytes"],
                            color=color["ping"], width=width, bottom=bottom,
                            label="ping" if label_first["ping"] else "")
                    bottom += row["ping_bytes"]
                    label_first["ping"] = False

                # udp
                if row["udp_bytes"]:
                    ax1.bar(row["bin_start"] + width, row["udp_bytes"],
                            color=color["udp"], width=width, bottom=bottom,
                            label='application' if label_first["udp"] else "")
                    bottom += row["udp_bytes"]
                    label_first["udp"] = False

                # coap
                if row["coap_bytes"]:
                    ax1.bar(row["bin_start"] + width, row["coap_bytes"],
                            color=color["coap"], width=width, bottom=bottom,
                            label="coap" if label_first["coap"] else "")
                    bottom += row["coap_bytes"]
                    label_first["coap"] = False

                # battery
                if row["battery_bytes"]:
                    ax1.bar(row["bin_start"] + width, row["battery_bytes"],
                            color=color["battery"], width=width, bottom=bottom,
                            label="battery" if label_first["battery"] else "")
                    bottom += row["battery_bytes"]
                    label_first["battery"] = False

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

        img_path = PJ(self.img_dir, "repartition_protocol.pdf")
        plt.savefig(img_path, format="pdf")

        update_report(self.result_dir, "repartition_protocol", {
            "img_src": "img/repartition_protocol.pdf",
            "text": """
            This graph represents through time the repartition of the protocol
            usage. We obtain this graph by analyzing through the PCAP produced by
            our simulator. As we can see the amount of packets produced by the
            routing protocol is very high at the beginning of the simulation then
            come down to a relatively stable rate. The trickle mechanism in RPL
            cause the periodic reconstruction of the route.
            """})

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

    # def time_delta(self):
    #     """
    #     Delta between the energy estimated and reality
    #
    #     delta between reality and estimated values
    #     """
    #
    #     fig, ax = plt.subplots()
    #     ax.set_xlabel('Time')
    #     ax.set_ylabel('Delta')
    #     ax.set_title('Delta between energy and estimation')
    #
    #     nodes = set()
    #     powertracker_time, powertracker_energy = defaultdict(
    #         list), defaultdict(list)
    #
    #     with open(self.powertracker_csv) as f:
    #         reader = DictReader(f)
    #         for row in reader:
    #             mote = row["mote_id"]
    #             monitored_time = float(row["monitored_time"])
    #             energy_consumed = float(row["energy_consumed"])
    #             nodes.add(row["mote_id"])
    #             # This is the reality.
    #             powertracker_time[mote].append(monitored_time)
    #             powertracker_energy[mote].append(energy_consumed)
    #
    #     estimated = defaultdict(list)
    #     # Extraction of the estimated values.
    #     with open(self.estimator_csv) as f:
    #         reader = DictReader(f)
    #
    #         for row in reader:
    #             time_transaction = float(row["time"]) / 10 ** 6
    #             energy_transaction = float(
    #                 row["transmit"]) + float(row["received"])
    #             node_transaction = row["node"]
    #             for time in powertracker_time[node_transaction]:
    #                 if time_transaction < time:
    #                     estimated[node_transaction] = [(t, e + energy_transaction)
    #                                                    for (t, e) in estimated[node_transaction]
    #                                                    if time_transaction <= t]
    #
    #     diff = {node: [] for node in nodes}
    #     for node in nodes:
    #         ax.plot(powertracker_time[node],
    #                 diff[node], label=node)
    #     name = "Hello!"
    #     ax.legend(loc='bottom right', shadow=True)
    #     img_path = PJ(self.img_dir, "%s_time_delta.pdf" % name)
    #     fig.savefig(img_path, format="pdf")
    #     update_report(self.result_dir, "%s_time_delta" % name, {
    #         "img_src": "img/%s_time_delta.pdf" % name,
    #         "text": """
    #         Delta between reality and %s estimator
    #         """ % name})

    def packet_loss(self):
        """
        Plot packet loss through time.
        """
        fig = plt.figure()
        ax1 = fig.add_subplot(111)

        ax1.set_title('Packet delivery ratio through time')
        ax1.set_xlabel('Time (s)')
        ax1.set_ylabel('Packet delivery ratio (%)')
        ax1.set_ylim([0, 101])

        with open(PJ(self.result_dir, "packet_loss.csv")) as packet_loss_f:
            reader = DictReader(packet_loss_f)
            time, avg, nodes, rows = [], [], set(), {}
            for row in reader:
                time.append(float(row["time"]) / 10 ** 6)
                avg.append(100.0 * float(row["avg"]))
                nodes.add(int(row["node"]))
                rows[int(row["time"])] = row

            for node in nodes:
                t = [int(t) / 10 ** 6
                     for t, values in sorted(rows.items())
                     if int(values["node"]) == node]
                r = [100.0 * float(values["ratio"])
                     for _, values in sorted(rows.items())
                     if int(values["node"]) == node]
                ax1.plot(t, r, label=node)

            ax1.plot(time, avg, label="Average")
            # Now add the legend with some customizations.
            ax1.legend(loc='upper right', shadow=True)

        img_path = PJ(self.img_dir, "packet_delivery_ratio.pdf")
        fig.savefig(img_path, format="pdf")
        update_report(self.result_dir, "packet_delivery_ratio", {
            "img_src": "img/packet_delivery_ratio.pdf",
            "text": """
            packet_delivery_ratio measured through the serial output.
            """})

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

    def divergence(self):
        """
        TODO: Make them share some axis.
        """

        nodes = [node for node, data in self.nodes
                 if "root" not in data]

        # Energy that is constant for all nodes.
        energy = {n: {"time": [], "energy": []}
                  for n, d in self.nodes}

        result = {"noinfo": {n: {"time": [], "estimation": []}
                             for n in nodes},
                  "route": {n: {"time": [], "estimation": []}
                            for n in nodes},
                  "radio": {n: {"time": [], "estimation": []}
                            for n in nodes}}

        # We only load energy records once
        with open(self.powertracker_csv) as f:
            reader = DictReader(f)
            for row in reader:
                node = int(row["mote_id"])
                energy[node]["time"].append(float(row["monitored_time"]))
                energy[node]["energy"].append(float(row["energy_consumed"]))

        for key, d in result.items():
            for node, records in d.items():
                try:
                    with open(PJ(self.result_dir, "%s_%s.csv" % (node, key))) as f:
                        reader = DictReader(f)
                        for row in reader:
                            d[node]["time"].append(float(row["time"]))
                            d[node]["estimation"].append(float(row["estimation"]))
                except IOError as e:
                    log.warning(e)
                    raise e

        estimator_name = ["noinfo", "route", "radio"]
        estimator = range(len(estimator_name))
        f, axarr = plt.subplots(len(nodes), len(estimator_name))
        for (node, estimator) in product(nodes, estimator):
            axarr[node - 1, estimator].plot(result[estimator_name[estimator]][node]["time"],
                                            result[estimator_name[estimator]][node]["estimation"])
            axarr[node - 1, estimator].plot(energy[node]["time"],
                                            energy[node]["energy"])
            if node == max(nodes):
                axarr[node - 1, estimator].set_xlabel('T (s)')
            if not estimator:
                axarr[node - 1, estimator].set_ylabel('E (Ah)')
                axarr[node - 1, estimator].set_ylabel('E (Ah)')
            if node == 1:
                axarr[node - 1, estimator].set_title(estimator_name[estimator])

        for ax in plt.gcf().axes:
            try:
                ax.label_outer()
            except Exception as e:
                log.warning(e)
                raise e
        img_path = PJ(self.img_dir, "divergence.pdf")
        f.savefig(img_path, format="pdf")


def run(sim_folder):
    step = Plot(sim_folder)
    step()


if __name__ == '__main__':
    p = Pool(5)
    p.map(run, [PJ(RESULTS_DIR, sim) for sim in sim_to_do_in(RESULTS_DIR)])
