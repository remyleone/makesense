import os
import pdb
from os.path import join as pj
from matplotlib import pyplot as plt
import pandas as pd


def plot_recalibration(folder):
    output_folder = pj(folder, "results", "estimation")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    depth_df = pd.read_csv(pj(folder, "results", "depth.csv"))

    # depth_df.set_index("node", inplace=True)
    targets = depth_df.node.unique()
    for target in targets:
        df = pd.read_csv(pj(output_folder, "recalibration_%d.csv" % int(target)))
        df.set_index("time", inplace=True)
        df[["real_tx", "real_rx", "estimation_rx_noinfo", "estimation_rx_route", "estimation_tx_noinfo", "estimation_tx_route"]].plot()

        fig = plt.gcf()
        fig.set_size_inches(18.5, 10.5)
        fig.savefig(pj(output_folder, 'recalibration_%d.pdf' % target), format="pdf")
        plt.close('all')

