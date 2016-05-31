import pdb
import pandas as pd
import matplotlib.pyplot as plt
from os.path import join as pj
import os
from . import latexify

BIN = 25


# def plot_strobes(folder):

#     for target in targets:

#         df_16 = pd.read_csv("chaine/chaine_high_calibration_75_16/results/strobes/strobes_%d.csv" % target)
#         df_8 = pd.read_csv("chaine/chaine_high_calibration_75_8/results/strobes/strobes_%d.csv" % target)
#         df_4 = pd.read_csv("chaine/chaine_high_calibration_75_4/results/strobes/strobes_%d.csv" % target)

#         df_16.rename(columns={"strobes": "strobes_16"}, inplace=True)
#         df_8.rename(columns={"strobes": "strobes_8"}, inplace=True)
#         df_4.rename(columns={"strobes": "strobes_4"}, inplace=True)

#         res = pd.merge(df_4, df_8, on="bin_start", how="outer")
#         res2 = pd.merge(res, df_16, on="bin_start", how="outer")

#         res2.set_index("bin_start", inplace=True)
#         res2.plot(kind="bar")

#         fig = plt.gcf()
#         fig.set_size_inches(18.5, 10.5)
#         fig.savefig(pj(folder, "results", 'strobes_%d.pdf') % target, format="pdf")

def plot_strobes(folder):
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
        fig.savefig(pj(folder, "results", "strobes", 'strobes_%d.pdf' % target),
                    format="pdf")
        plt.close('all')


def plot_strobes_depth(folder):
    latexify()
    plt.xticks(rotation=90)
    output_folder = pj(folder, "results", "strobes")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    strobes_df = pd.read_csv(pj(output_folder, "strobes_depth.csv"))
    strobes_df.set_index("depth", inplace=True)
    ax = strobes_df["avg"].plot(kind="bar", yerr=strobes_df["std"])
    ax.set_xticklabels(strobes_df.index, rotation=0)
    ax.set_ylabel('Average Strobing')
    ax.set_xlabel("Depth")
    fig = plt.gcf()
    plt.tight_layout()
    # fig.set_size_inches(18.5, 10.5)
    fig.savefig(pj(output_folder, 'strobes_depth.pdf'), format="pdf")
    plt.close('all')
