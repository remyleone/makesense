import pdb
from matplotlib import pyplot as plt
from os.path import join as pj
import pandas as pd
import os

BIN = 25

# def plot_pdr(folder, data=None):

#     for target in targets:

#         df_16 = pd.read_csv("chaine/chaine_high_calibration_75_16/results/pdr/pdr_%d.csv" % target)
#         df_4 = pd.read_csv("chaine/chaine_high_calibration_75_4/results/pdr/pdr_%d.csv" % target)
#         df_8 = pd.read_csv("chaine/chaine_high_calibration_75_8/results/pdr/pdr_%d.csv" % target)

#         df_16["bin_start"] = BIN * (df_16.departure_time // BIN)
#         df_4["bin_start"] = BIN * (df_4.departure_time // BIN)
#         df_8["bin_start"] = BIN * (df_8.departure_time // BIN)

#         g16 = df_16.groupby("bin_start").count()
#         g4 = df_4.groupby("bin_start").count()
#         g8 = df_8.groupby("bin_start").count()

#         g16.reset_index(inplace=True)
#         g4.reset_index(inplace=True)
#         g8.reset_index(inplace=True)

#         g16["ratio_16"] = g16.arrival_time / g16.departure_time
#         g4["ratio_4"] = g4.arrival_time / g4.departure_time
#         g8["ratio_8"] = g8.arrival_time / g8.departure_time

#         res = pd.merge(g4, g16, on="bin_start", how="outer")[["bin_start", "ratio_4", "ratio_16"]]
#         res2 = pd.merge(res, g8, on="bin_start", how="outer")[["bin_start", "ratio_4", "ratio_8", "ratio_16"]]

#         res2.set_index("bin_start", inplace=True)
#         res2.plot(kind="bar")

#         fig = plt.gcf()
#         fig.set_size_inches(18.5, 10.5)
#         fig.savefig(pj(folder, "results", "pdr", 'pdr_%d.pdf' % target), format="pdf")


def plot_pdr(folder):
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
        fig.savefig(pj(output_folder, 'pdr_%d.pdf' % target),
                    format="pdf")
        plt.close('all')


def plot_pdr_depth(folder):
    output_folder = pj(folder, "results", "pdr")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    pdr_df = pd.read_csv(pj(output_folder, "pdr_depth.csv"))
    pdr_df.set_index("depth", inplace=True)
    ax = pdr_df["avg"].plot(kind="bar", yerr=pdr_df["std"])
    ax.set_ylabel('Average PDR')
    ax.set_xlabel("Depth")
    ax.set_xticklabels(pdr_df.index, rotation=0)

    fig = plt.gcf()
    plt.tight_layout()

    # fig.set_size_inches(18.5, 10.5)
    fig.savefig(pj(output_folder, 'pdr_depth.pdf'), format="pdf")
    plt.close('all')
