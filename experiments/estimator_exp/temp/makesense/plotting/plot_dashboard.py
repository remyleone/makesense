import pandas as pd
import matplotlib.pyplot as plt
from os.path import join as pj
import os


def plot_dashboard(folder):
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
        fig.savefig(pj(output_folder, 'dashboard_%d.pdf' % target), format="pdf")
