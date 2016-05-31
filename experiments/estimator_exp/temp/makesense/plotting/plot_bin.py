import pdb
import os
from csv import DictReader
from os.path import join as pj
from matplotlib import pyplot as plt
from . import format_axes
import pandas as pd
import numpy as np
from matplotlib.font_manager import FontProperties


BIN = 25


# def plot_bin(folder):
#     """
#     Will plot for every node side by side :
#         - The amount of TX estimated and real
#         - The amount of RX estimated and real
#     """
#     color = {"tx": "red", "rx": "blue",
#              "tx_estimated": "magenta", "rx_estimated": "cyan"}
#     hatch = {"tx": "\\", "tx_estimated": "\\\\",
#              "rx": "/", "rx_estimated": "//"}
#     name = {"tx": "tx (reality)", "rx": "rx (reality)",
#             "tx_estimated": "tx (estimated)", "rx_estimated": "rx (estimated)"}

#     width = BIN

#     for file_name in os.listdir(pj(folder, "results", "estimation")):
#         if file_name.startswith("bin_estimation") and file_name.endswith("csv"):

#             path = pj(folder, "results", "estimation", file_name)
#             output_path_png = path.replace(".csv", ".png")
#             output_path_pdf = path.replace(".csv", ".pdf")
#             kinds = ["tx", "tx_estimated", "rx", "rx_estimated"]
#             label_first = {kind: True for kind in kinds}
#             print(output_path_pdf)

#             fig = plt.figure()
#             ax = fig.add_subplot(111)

#             with open(path) as f:
#                 reader = DictReader(f)
#                 for row in reader:
#                     # We stack TX on top of RX for each bin
#                     for key, value in row.items():
#                         if value:
#                             row[key] = float(value)
#                         else:
#                             row[key] = 0.0

#                     # Real RX & TX

#                     shifts = [0, 0.25, 0.5, 0.75]
#                     for (kind, shift) in zip(kinds, shifts):
#                         ax.bar(row["bin_start"] + shift * width,
#                                row[kind],
#                                # bottom=bottom_powertracker,
#                                width=width / 4,
#                                color=color[kind],
#                                hatch=hatch[kind],
#                                label=name[kind] if label_first[kind] else "")
#                         label_first[kind] = False

#             ax.legend(ncol=2)
#             #ax.set_title("estimator %s" % file_name)
#             ax.set_xlabel("Time [s]")
#             ax.set_ylabel("Time [s]")
#             # if "global" in output_path_png:
#             ax.set_ylim(0, 2)
#             # else:
#             #     if "chaine" in folder:
#             #         ax.set_ylim(0, 4)
#             #     else:
#             #         ax.set_ylim(0, 1)

#             format_axes(ax)
#             fig.savefig(output_path_png, format="png")
#             fig.savefig(output_path_pdf, format="pdf")


def plot_bin(folder):
    output_folder = pj(folder, "results", "estimation")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    depth_df = pd.read_csv(pj(folder, "results", "depth.csv"))

    # depth_df.set_index("node", inplace=True)
    targets = depth_df.node.unique()

    fig, axes = plt.subplots(nrows=3, ncols=2)
    for i, target in enumerate([2, 3, 7]):
        df = pd.read_csv(pj(output_folder, "cost_%d.csv" % int(target)))
        df["bin_start"] = BIN * (df.time // BIN)
        bin_df = df.drop("time", 1).groupby("bin_start").sum()

        p_df = pd.read_csv(pj(folder, "results", "powertracker", "series_powertracker_%d.csv" % target))
        p_df["bin_start"] = BIN * (p_df.time // BIN)
        p_df.tx = p_df.tx.diff()
        p_df.rx = p_df.rx.diff()
        bin_p_df = p_df.groupby("bin_start").sum()[["tx", "rx"]]
        res = bin_p_df.join(bin_df).rename(columns={
            "tx_noinfo": "tx (noinfo)", "rx_noinfo": "rx (noinfo)",
            "tx_route": "tx (route)", "rx_route": "rx (route)"})
        res[["tx", "rx", "tx (noinfo)", "rx (noinfo)"]].plot(ax=axes[i, 0], kind="bar")
        res[["tx", "rx", "tx (route)", "rx (route)"]].plot(ax=axes[i, 1], kind="bar")
        axes[i, 0].set_xticklabels(res.index.map(int), rotation=0)
        axes[i, 1].set_xticklabels(res.index.map(int), rotation=0)
    fontP = FontProperties()
    fontP.set_size('small')
    axes[0, 0].legend(ncol=4, bbox_to_anchor=(1, 1), prop=fontP)
    axes[0, 0].set_title("Noinfo :: Node 2")
    axes[0, 1].legend().set_visible(False)
    axes[0, 1].set_title("Route :: Node 2")
    axes[1, 0].legend().set_visible(False)
    axes[1, 0].set_title("Noinfo :: Node 3")
    axes[1, 1].legend().set_visible(False)
    axes[1, 1].set_title("Route :: Node 3")
    axes[2, 0].legend().set_visible(False)
    axes[2, 0].set_title("Noinfo :: Node 7")
    axes[2, 1].legend().set_visible(False)
    axes[2, 1].set_title("Noinfo :: Node 7")


        # axes[i, 0].set_xticklabels(res.index.map(int), rotation=0)
        # axes[i, 0].set_xlabel("Time [s]")
        # axes[i, 0].set_ylabel("Time [s]")
        # axes[i, 1].set_xticklabels(res.index.map(int), rotation=0)
        # axes[i, 1].set_xlabel("Time [s]")
        # axes[i, 1].set_ylabel("Time [s]")

    # fig = plt.gcf()
    plt.tight_layout()
    # plt.legend(loc='best', ncol=4)
    # fig.set_size_inches(18.5, 10.5)
    fig.savefig(pj(output_folder, 'cost_bin_%d.pdf' % target), format="pdf")
    plt.close('all')
