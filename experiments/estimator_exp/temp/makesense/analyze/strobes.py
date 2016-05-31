#!/usr/bin/env python

from collections import defaultdict
import pdb
import pandas as pd
from os.path import join as pj
import re
import numpy as np
import os

BIN = 25


def strobes(folder):
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


# def strobes(folder):

#     sizes = [1, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 107]

#     time_regexp = "^(?P<time>\d+)"
#     mote_id_regexp = "ID:(?P<mote_id>\d+)"
#     reception_regexp = r" ".join([time_regexp, mote_id_regexp,
#                                   "contikimac: send \(strobes=(?P<strobes>\d+), len=(?P<len>\d+), ack, no collision\), done$"])

#     strobes = {size: [] for size in sizes}
#     frame_sizes = {size: [] for size in sizes}

#     for size in sizes:
#         with open(pj(folder, "%d/serial.log" % size)) as f:
#             for line in f:
#                 reception_match = re.match(reception_regexp, line, re.MULTILINE)
#                 if reception_match:
#                     d = reception_match.groupdict()
#                     frame_size = int(d["len"])
#                     if frame_size > 7:
#                         strobes[size].append(int(d["strobes"]) + 1)
#                         frame_sizes[size].append(int(d["len"]))

#     df = pd.DataFrame({
#         "sizes": [size + 7 for size in sorted(sizes)],
#         "mean": [np.mean(strobes[size]) for size in sorted(sizes)],
#         "avg": [np.std(strobes[size]) for size in sorted(sizes)]})
#     df.to_csv(pj(folder, "strobes.csv"), index=False)
