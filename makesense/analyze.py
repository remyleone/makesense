# -*- coding: utf-8 -*-

"""
This module contains all the classes used in order to analyze trace
of experiments.

For instance we analyze PCAP by defaults but it would be completely acceptable
to have some log analyzer code here.
"""

from collections import defaultdict
from csv import DictWriter
from math import sqrt
from os.path import join as pj
from scipy import stats
from scipy.interpolate import interp1d
import networkx as nx
import errno
import fnmatch
import json
import logging
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import pdb
import re
import subprocess


def depth(folder, root=1):
    """
    Build up the RPL representation at the gateway
    """
    rpl_graph = nx.DiGraph()

    message_df = pd.read_csv(pj(folder, "results", "messages.csv"))
    parent_df = message_df[message_df.message_type == "parent"][
        ["time", "mote_id", "node"]]

    for index, row in parent_df.iterrows():
        parent = int(row["node"])
        node = int(row["mote_id"])
        if parent and node:
            rpl_graph.add_edge(node, parent)

    route_path = {n: nx.shortest_path(rpl_graph, n, root)
                       for n in rpl_graph.nodes()
                       if nx.has_path(rpl_graph, n, root)}

    res = {node: len(route_path[node]) - 1
           for node in rpl_graph.nodes()}
    df = pd.DataFrame(list(res.items()), columns=["node", "depth"])
    df.to_csv(pj(folder, "results", "depth.csv"), index=False)


def dashboard(folder, BIN=25):
    df = pd.read_csv(pj(folder, "results", "pcap_relooked.csv"))

    df["bin_start"] = BIN * (df.time // BIN)

    bin_df = pd.DataFrame()
    bin_df["total"] = df.groupby("bin_start").length.sum()
    bin_df["udp"] = df[df.icmpv6_type == "udp"].groupby("bin_start").length.sum()
    bin_df["rpl"] = df[df.icmpv6_type == "rpl"].groupby("bin_start").length.sum()
    bin_df["forwarding"] = df[df.forwarding].groupby("bin_start").length.sum()
    bin_df.to_csv(pj(folder, "results", "bin_global.csv"))

    for target in pd.Series(df.mac_src.values.ravel()).unique():
        if target > 1:
            node_df = df[df.mac_src == target]
            bin_df = pd.DataFrame()
            bin_df["total"] = node_df.groupby("bin_start").length.sum()
            bin_df["udp"] = node_df[node_df.icmpv6_type == "udp"].groupby("bin_start").length.sum()
            bin_df["rpl"] = node_df[node_df.icmpv6_type == "rpl"].groupby("bin_start").length.sum()
            bin_df["forwarding"] = node_df[node_df.forwarding].groupby("bin_start").length.sum()

            # Conversion from bytes to time
            RATE = 250000
            bin_df = 8.0 * bin_df / RATE

            output_folder = pj(folder, "results", "protocol_repartition")
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
            bin_df.to_csv(pj(output_folder, "protocol_repartition_%d.csv" % int(target)))

            output_folder = pj(folder, "results", "powertracker")
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
            powertracker = pd.read_csv(pj(folder, "results", "powertracker", "series_powertracker_%.d.csv" % target))
            powertracker["bin_start"] = BIN * (powertracker.time // BIN)

            bin_powertracker = powertracker.groupby("bin_start").max()[["tx", "rx"]]
            for kind in ["tx", "rx"]:
                bin_powertracker["diff_%s" % kind] = bin_powertracker[kind].diff()

            res = res.join(bin_powertracker)
            output_folder = pj(folder, "results", "dashboard")
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)

            res.to_csv(pj(output_folder, "res_%d.csv" % int(target)))

def pdr_depth(folder, data=None):
    output_folder = pj(folder, "results", "pdr")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    depth_df = pd.read_csv(pj(folder, "results", "depth.csv"))
    targets = depth_df.node
    res = defaultdict(list)

    depths = depth_df.depth.unique()

    for target in targets:
        depth = depth_df[depth_df.node == target].depth
        df_pdr = pd.read_csv(pj(output_folder, "pdr_%d.csv" % target))
        res[int(depth)].append(float(df_pdr.arrival_time.count()) / float(df_pdr.departure_time.count()))

    avg = [np.mean(res[depth]) for depth in depths]
    std = [np.std(res[depth]) for depth in depths]
    res_df = pd.DataFrame({"depth": depths, "avg": avg, "std": std})
    res_df.to_csv(pj(output_folder, "pdr_depth.csv"), index=False)

# for size in sizes:
#     df = pd.read_csv("%d/powertracker.csv" % size)

#     # Interpolation Sender

#     sender_df = df[df.mote_id == 2]
#     tx_sender = interp1d(sender_df.monitored_time, sender_df.tx_time)
#     rx_sender = interp1d(sender_df.monitored_time, sender_df.rx_time)

#     # Interpolation receiver

#     receiver_df = df[df.mote_id == 1]
#     tx_receiver = interp1d(receiver_df.monitored_time, receiver_df.tx_time)
#     rx_receiver = interp1d(receiver_df.monitored_time, receiver_df.rx_time)

#     # Linear regression receiver
#     slope, intercept, r_value, p_value, std_err = stats.linregress(receiver_df.monitored_time, receiver_df.tx_time)
#     line = slope * receiver_df.monitored_time + intercept
#     plt.plot(receiver_df.monitored_time, line, 'r-',
#              receiver_df.monitored_time, receiver_df.tx_time, 'o', label="receiver_tx")

#     slope, intercept, r_value, p_value, std_err = stats.linregress(receiver_df.monitored_time, receiver_df.rx_time)
#     line = slope * receiver_df.monitored_time + intercept
#     plt.plot(receiver_df.monitored_time, line, 'r-',
#              receiver_df.monitored_time, receiver_df.rx_time, 'o', label="receiver rx")

#     # Linear regression sender
#     slope, intercept, r_value, p_value, std_err = stats.linregress(receiver_df.monitored_time, sender_df.tx_time)
#     line = slope * sender_df.monitored_time + intercept
#     plt.plot(sender_df.monitored_time, line, 'r-',
#              sender_df.monitored_time, sender_df.tx_time, 'o', label="sender tx")

#     slope, intercept, r_value, p_value, std_err = stats.linregress(sender_df.monitored_time, sender_df.rx_time)
#     line = slope * sender_df.monitored_time + intercept
#     plt.plot(sender_df.monitored_time, line, 'r-',
#              sender_df.monitored_time, sender_df.rx_time, 'o', label="sender rx")
    
#     plt.legend()
#     plt.show()

#     time_regexp = "^(?P<time>\d+)"
#     mote_id_regexp = "ID:(?P<mote_id>\d+)"
#     reception_regexp = r" ".join([time_regexp, mote_id_regexp,
#                                   "DATA recv \'(?P<message>(.)*)\' from (?P<node>\d+)$"])

#     sending_regexp = r" ".join([time_regexp, mote_id_regexp,
#                                 "DATA send to root \'(?P<message>(.)*)\'$"])

#     message_table = defaultdict(dict)

#     with open("%d/serial.log" % size) as f:
#         for line in f:
#             reception_match = re.match(reception_regexp, line, re.MULTILINE)
#             if reception_match:
#                 d = reception_match.groupdict()

#                 node = int(d["node"])
#                 message_id = int(d["message"])
#                 message_table[message_id]["received"] = float(d["time"]) / 10 ** 6

#                 message_table[message_id]["status"] = (message_table[message_id]["received"]
#                                                        - message_table[message_id]["sent"] < 2)

#             sending_match = re.match(sending_regexp, line, re.MULTILINE)
#             if sending_match:
#                 d = sending_match.groupdict()

#                 message_id = int(d["message"])
#                 node = int(d["mote_id"])
#                 message_table[message_id]["sent"] = float(d["time"]) / 10 ** 6

#     # We filter only to have the one that got received
#     message_table = {key: value
#                      for key, value in message_table.items()
#                      if "received" in value and "sent" in value}
#     with open("%d/message_table.json" % size, "w") as f:
#         f.write(json.dumps(message_table, sort_keys=True, indent=4,
#                            separators=(',', ': ')))

#     repo = defaultdict(list)
#     init_interval = {"begin": 0.0, "end": 0.0, "messages": 0}
#     current_interval = {"begin": 0.0, "end": 0.0, "messages": 0}

#     # AGGREGATIOn
#     # for key, value in message_table.items():

#     #     # Init case
#     #     if value["status"]:
#     #         if not current_interval["begin"]:
#     #             current_interval["begin"] = value["sent"]
#     #         else:
#     #             current_interval["end"] = value["received"]

#     #         current_interval["messages"] += 1
#     #     else:
#     #         # We archive the current interval
#     #         if current_interval["begin"]:
#     #             res[size]["intervals"].append(current_interval)
#     #         current_interval = {"begin": 0.0, "end": 0.0, "messages": 0}

#     # # Finalize if we finish with a good interval
#     # if current_interval["begin"]:
#     #     res[size]["intervals"].append(current_interval)

#     # NO aggregation
#     for key, value in message_table.items():

#         if value["status"]:
#             res[size]["intervals"].append({
#                 "begin": value["sent"],
#                 "end": value["received"],
#                 "messages": 1})

# # Now we try to deduce the cost per packet
# for size, intervals_data in res.items():
#     print("SIZE: %d" % size)
#     intervals = intervals_data["intervals"]
#     tasks = {
#         "tx_sender": tx_sender,
#         "rx_sender": rx_sender,
#         "tx_receiver": tx_receiver,
#         "rx_receiver": rx_receiver
#     }

#     for task, interpolation in tasks.items():
#         for interval in intervals:

#             try:
#                 diff = (interpolation(interval["end"])
#                         - interpolation(interval["begin"])) / interval["messages"]
#                 if diff:
#                     res[size][task].append(diff)
#                 else:
#                     res[size][task].append(diff)
#                     print("0.0 diff increase powertracker resolution")
#             except ValueError:
#                 #pdb.set_trace()
#                 print("interpolation FAIL")
#     print("--------------------")

# mean = {kind: [] for kind in kinds}
# err = {kind: [] for kind in kinds}

# for kind in kinds:
#     for size, data in res.items():

#         avg = np.mean(res[size][kind])
#         print(avg)
#         if np.isnan(avg):
#             pdb.set_trace()
#         mean[kind].append(avg)
#         res[size]["mean_%s" % kind] = avg

#         std = np.std(res[size][kind])
#         err[kind].append(std)
#         res[size]["std_%s" % kind] = std


# with open("res.json", "w") as f:
#     f.write(json.dumps(res, sort_keys=True, indent=4, separators=(',', ': ')))

# for kind in kinds:
#     plt.errorbar(sizes, mean[kind], fmt="o-", yerr=err[kind], label=kind)


def strobes(folder, BIN=25):
    output_folder = pj(folder, "results", "strobes")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    depth_df = pd.read_csv(pj(folder, "results", "depth.csv"))
    targets = depth_df.node
    
    for target in targets:
        mac_df = pd.read_csv(pj(folder, "results", "estimation", "series_mac_%.d.csv" % target))
        mac_df["bin_start"] = BIN * (mac_df.time // BIN)
        mac_df.set_index("bin_start")

        df = mac_df[mac_df.size == 32].groupby("bin_start").mean().strobes.reset_index().set_index("bin_start")
        df.to_csv(pj(output_folder, "strobes_%d.csv" % target))


def strobes_depth(folder):
    output_folder = pj(folder, "results", "strobes")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    depth_df = pd.read_csv(pj(folder, "results", "depth.csv"))
    targets = depth_df.node
    res = defaultdict(list)

    depths = depth_df.depth.unique()

    for target in targets:
        depth = depth_df[depth_df.node == target].depth
        df_strobes = pd.read_csv(pj(folder, "results", "estimation", "series_mac_%d.csv" % target))
        res[int(depth)] += list(df_strobes[df_strobes.size == 32].strobes)

    avg = [np.mean(res[depth]) for depth in depths]
    std = [np.std(res[depth]) for depth in depths]

    res_df = pd.DataFrame({"depth": depths, "avg": avg, "std": std})
    res_df.set_index("depth", inplace=True)
    res_df.to_csv(pj(output_folder, "strobes_depth.csv"))
