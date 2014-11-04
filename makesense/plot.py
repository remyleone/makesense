# -*- coding: utf-8 -*-

"""
Module building up the graph using mat plot lib
"""

import pdb
from csv import DictReader
from os.path import join as pj
import logging

import matplotlib

# matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd

log = logging.getLogger("plot")

def plot_iotlab_energy(folder):
    df = pd.read_csv(pj(folder, "energy.csv"))    
    df.set_index("time", inplace=True)
    targets = df.mote_id.unique()
    for target in targets:
        ax = df[df.mote_id == target].voltage.plot()
        ax.set_ylabel("Voltage [V]")
        ax.set_xlabel("Time [s]")
        fig = plt.gcf()

        # fig.set_size_inches(18.5, 10.5)
        fig.savefig(pj(folder, 'voltage_%s.png' % target))
        plt.close('all')

def overhead(folder):
    """
    Plot the overhead (RPL, ACK,...).

    This graph measures the amount of bytes sent by nodes that are not
    application oriented (UDP, ping or CoAP) therefore we can see the amount
    of bytes transmitted just to keep the network alive. This packets are
    usually RPL and ACK packets.)

    """
    fig = plt.figure()
    ax1 = fig.add_subplot(111)

    ax1.set_title('RPL traffic by time')
    ax1.set_xlabel('Time (s)')
    ax1.set_ylabel('RPL traffic (bytes)')

    with open(pj(folder, "results", "io.csv")) as io_csv_f:
        reader = DictReader(io_csv_f)
        time, overhead_bytes = [], []
        for row in reader:
            time.append(float(row["bin_end"]))
            overhead_bytes.append(float(row["total_bytes"])
                                  - float(row["udp_bytes"])
                                  - float(row["ping_bytes"])
                                  - float(row["coap_bytes"]))
        ax1.plot(time, overhead_bytes)

    img_path = pj(self.img_dir, "overhead.png")
    fig.savefig(img_path)
    plt.close('all')


def dashboard(folder):
    output_folder = pj(folder, "results", "dashboard")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    depth_df = pd.read_csv(pj(folder, "results", "depth.csv"))
    targets = depth_df.node

    for target in targets:
        df = pd.read_csv(pj(output_folder, "res_%d.csv" % int(target)))
        df.drop("tx", 1).drop("rx", 1).plot(kind="bar")

        fig = plt.gcf()
        fig.set_size_inches(18.5, 10.5)
        fig.savefig(pj(output_folder, 'dashboard_%d.png' % target))
        plt.close('all')

def protocol_repartition_depth(folder):
    output_folder = pj(folder, "results", "protocol_repartition")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    depth_df = pd.read_csv(pj(folder, "results", "depth.csv"))
    depth_df.set_index("node", inplace=True)

    pcap_df = pd.read_csv(pj(folder, "results", "pcap_relooked.csv"))
    pcap_df = pcap_df.join(depth_df, on="mac_src")

    res = pd.DataFrame()

    res["rpl"] = pcap_df[pcap_df.icmpv6_type == "rpl"].groupby("depth").sum().length
    res["udp"] = pcap_df[pcap_df.icmpv6_type == "udp"].groupby("depth").sum().length

    RATE = 250000
    res["rpl"] = 8.0 * res["rpl"] / RATE
    res["udp"] = 8.0 * res["udp"] / RATE

    ax = res.plot(kind="bar", stacked=True)
    ax.set_ylabel('Time [s]')
    ax.set_xlabel("Depth")
    ax.set_xticklabels(res.index.map(int), rotation=0)

    fig = plt.gcf()
    plt.tight_layout()

    # fig.set_size_inches(18.5, 10.5)
    fig.savefig(pj(output_folder, 'protocol_repartition_depth.png'))
    plt.close('all')


def protocol_repartition_aggregated(folder, BIN=25):
    output_folder = pj(folder, "results", "protocol_repartition")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # depth_df = pd.read_csv(pj(folder, "results", "depth.csv"))
    # depth_df.set_index("node", inplace=True)

    pcap_df = pd.read_csv(pj(folder, "results", "pcap_relooked.csv"))
    pcap_df["bin_start"] = BIN * (pcap_df.time // BIN)

    res = pd.DataFrame()

    RATE = 250000
    res["udp"] = pcap_df[(pcap_df.icmpv6_type == "udp") & (pcap_df.time < 200)].groupby("bin_start").sum().length
    res["rpl"] = pcap_df[(pcap_df.icmpv6_type == "rpl") & (pcap_df.time < 200)].groupby("bin_start").sum().length

    res["rpl"] = 8.0 * res["rpl"] / RATE
    res["udp"] = 8.0 * res["udp"] / RATE

    ax = res[["rpl", "udp"]].plot(kind="bar", stacked=True)
    ax.set_ylabel('Time [s]')
    ax.set_xlabel("Time [s]")
    ax.set_ylim(0, 4.5)
    ax.set_xticklabels(res.index.map(int), rotation=0)

    fig = plt.gcf()
    plt.tight_layout()

    # fig.set_size_inches(18.5, 10.5)
    fig.savefig(pj(output_folder, 'protocol_repartition_aggregated.png'))
    plt.close('all')


def protocol_repartition(folder):
    """
    Representation of protocol repartition (stacked histogram)

    Include UDP, CoAP, ping, RPL, other...

    This graph represents through time the repartition of the protocol
    usage. We obtain this graph by analyzing through the PCAP produced by
    our simulator. As we can see the amount of packets produced by the
    routing protocol is very high at the beginning of the simulation then
    come down to a relatively stable rate. The trickle mechanism in RPL
    cause the periodic reconstruction of the route.
    """
    output_folder = pj(folder, "results", "protocol_repartition")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    depth_df = pd.read_csv(pj(folder, "results", "depth.csv"))
    targets = depth_df.node.unique()

    for target in targets:
        df = pd.read_csv(pj(output_folder, 'protocol_repartition_%d.csv' % target))
        df = df[df["bin_start"] < 200]
        df.set_index("bin_start", inplace=True)
        df["udp"] = df["udp"] - df["forwarding"]
        ax = df[["rpl", "udp", "forwarding"]].plot(kind="bar", stacked=True)
        ax.set_ylabel('Time [s]')
        ax.set_xlabel("Time [s]")
        ax.set_ylim([0.0, df.max().max() * 1.5])
        ax.set_xticklabels(df.index.map(int), rotation=0)
        # pdb.set_trace()

        fig = plt.gcf()
        plt.legend(ncol=3)
        plt.tight_layout()
        # fig.set_size_inches(18.5, 10.5)
        fig.savefig(pj(output_folder, "protocol_repartition_%d.png" % target))
        plt.close('all')

def pdr(folder, BIN=25):
    output_folder = pj(folder, "results", "pdr")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    depth_df = pd.read_csv(pj(folder, "results", "depth.csv"))
    
    # depth_df.set_index("node", inplace=True)
    targets = depth_df.node.unique()

    for target in targets:
        pdr_df = pd.read_csv(pj(output_folder, "pdr_%d.csv" % target))
        pdr_df["bin_start"] = BIN * (pdr_df.departure_time // BIN)
        pdr_df.groupby("bin_start").count()
        res = pdr_df.groupby("bin_start").count().arrival_time / pdr_df.groupby("bin_start").count().departure_time
        res.plot(kind='bar')

        fig = plt.gcf()
        fig.set_size_inches(18.5, 10.5)
        fig.savefig(pj(output_folder, 'pdr_%d.png' % target))
        plt.close('all')


def pdr_depth(folder):
    output_folder = pj(folder, "results", "pdr")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    pdr_df = pd.read_csv(pj(output_folder, "pdr_depth.csv"))
    pdr_df.set_index("depth", inplace=True)
    ax = pdr_df["avg"].plot(kind="bar", yerr=pdr_df["std"])
    ax.set_ylabel('avg PDR')
    ax.set_xlabel("Depth")
    ax.set_xticklabels(pdr_df.index, rotation=0)

    fig = plt.gcf()
    plt.tight_layout()

    # fig.set_size_inches(18.5, 10.5)
    fig.savefig(pj(output_folder, 'pdr_depth.png'))
    plt.close('all')


def strobes(folder):
    output_folder = pj(folder, "results", "strobes")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    depth_df = pd.read_csv(pj(folder, "results", "depth.csv"))

    # depth_df.set_index("node", inplace=True)
    targets = depth_df.node.unique()

    for target in targets:
        strobes_df = pd.read_csv(pj(folder, "results", "strobes", "strobes_%d.csv" % target))
        strobes_df.set_index("bin_start", inplace=True)
        strobes_df.plot(kind='bar')

        fig = plt.gcf()
        fig.set_size_inches(18.5, 10.5)
        fig.savefig(pj(folder, "results", "strobes", 'strobes_%d.png' % target),
                  )
        plt.close('all')


def strobes_depth(folder):
    latexify()
    plt.xticks(rotation=90)
    output_folder = pj(folder, "results", "strobes")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    strobes_df = pd.read_csv(pj(output_folder, "strobes_depth.csv"))
    strobes_df.set_index("depth", inplace=True)
    ax = strobes_df["avg"].plot(kind="bar", yerr=strobes_df["std"])
    ax.set_xticklabels(strobes_df.index, rotation=0)
    ax.set_ylabel('Packet strobing')
    ax.set_xlabel("Depth")
    fig = plt.gcf()
    plt.tight_layout()
    fig.savefig(pj(output_folder, 'strobes_depth.png'))
    plt.close('all')

def energy(self):
    """
    Powertracker analyze the energy consumption by using the amount of
    time that every node spend in a transmitting reception, interference
    or on mode.
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
    img_path = PJ(self.img_dir, "energy.png")
    fig.savefig(img_path)
    plt.close('all')

def energy_depth(self):
    """
    Energy used by depth of a node in the RPL tree.
    Energy used by nodes that are a fixed depth from the root.
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
    img_path = PJ(self.img_dir, "energy_depth.png")
    plt.savefig(img_path)

from math import sqrt

import matplotlib


def latexify(fig_width=None, fig_height=None, columns=1):
    """Set up matplotlib's RC params for LaTeX plotting.
    Call this before plotting a figure.

    Parameters
    ----------
    fig_width : float, optional, inches
    fig_height : float,  optional, inches
    columns : {1, 2}
    """

    # code adapted from http://www.scipy.org/Cookbook/Matplotlib/LaTeX_Examples

    # Width and max height in inches for IEEE journals taken from
    # computer.org/cms/Computer.org/Journal%20templates/transactions_art_guide.pdf

    assert(columns in [1, 2])

    if fig_width is None:
        fig_width = 3.39 if columns == 1 else 6.9  # width in inches

    if fig_height is None:
        golden_mean = (sqrt(5)-1.0)/2.0    # Aesthetic ratio
        fig_height = fig_width*golden_mean  # height in inches

    MAX_HEIGHT_INCHES = 8.0
    if fig_height > MAX_HEIGHT_INCHES:
        print("WARNING: fig_height too large:" + fig_height +
              "so will reduce to" + MAX_HEIGHT_INCHES + "inches.")
        fig_height = MAX_HEIGHT_INCHES

    params = {'backend': 'ps',
              'text.latex.preamble': ['\usepackage{gensymb}'],
              'axes.labelsize': 9,  # fontsize for x and y labels (was 12)
              'axes.titlesize': 9,
              'font.size': 9,  # was 12
              'legend.fontsize': 9,  # was 12
              'xtick.labelsize': 9,
              'ytick.labelsize': 9,
              'text.usetex': True,
              'figure.figsize': [fig_width, fig_height],
              'font.family': 'serif'
    }

    matplotlib.rcParams.update(params)


def format_axes(ax):

    SPINE_COLOR = 'gray'

    for spine in ['top', 'right']:
        ax.spines[spine].set_visible(False)

    for spine in ['left', 'bottom']:
        ax.spines[spine].set_color(SPINE_COLOR)
        ax.spines[spine].set_linewidth(0.5)

    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')

    for axis in [ax.xaxis, ax.yaxis]:
        axis.set_tick_params(direction='out', color=SPINE_COLOR)

    return ax
