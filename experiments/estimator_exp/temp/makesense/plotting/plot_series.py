import os
import pdb
from os.path import join as pj
from csv import DictReader
from matplotlib import pyplot as plt
# from . import format_axes
import pandas as pd
import numpy as np


# def plot_series(folder):
#     """
#     :param powertracker_csv:
#     :param output:
#     """
#     estimation_folder = pj(folder, "results", "estimation")
#     # powertracker values

#     for target in range(2, 8):
#         p_df = pd.read_csv(pj(folder, "results", "powertracker", "series_powertracker_%d.csv" % target),
#                            )

#         for estimator in ["noinfo", "route"]:
#             e_df = pd.read_csv(pj(estimation_folder, "series_estimation_%d_%s.csv" % (target, estimator)),
#                                )

#             p_df.tx.plot()
#             plt.savefig("mes_couilles.png")

#             fig = plt.figure()
#             ax = fig.add_subplot(111)

#             ax.plot(p_df.time, p_df.tx, color="red", label="tx (reality)")
#             ax.plot(p_df.time, p_df.rx, color="blue", label="rx (reality)")

#             ax.plot(e_df.time, e_df.tx, color="magenta", label="tx (estimated)")
#             ax.plot(e_df.time, e_df.rx, color="cyan", label="rx (estimated)")

#             ax.set_xlabel('Simulation Time (s)')
#             ax.set_ylabel('Time (s)')
#             ax.set_ylim(0, 4)
#             ax.legend(loc="upper left", ncol=2)

#             for f in ["png", "pdf"]:
#                 path = pj(estimation_folder, "series_estimation_%d_%s.%s" % (target, estimator, f))
#                 print(path)
#                 fig.savefig(path, format=f)


def plot_series_cost(folder):
    output_folder = pj(folder, "results", "estimation")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    depth_df = pd.read_csv(pj(folder, "results", "depth.csv"))

    # depth_df.set_index("node", inplace=True)
    targets = depth_df.node.unique()
    for target in targets:
        df = pd.read_csv(pj(output_folder, "cost_%d.csv" % int(target)))
        df.set_index("time", inplace=True)
        df = df.cumsum()
        
        p_df = pd.read_csv(pj(folder, "results", "powertracker", "series_powertracker_%d.csv" % target))
        p_df.set_index("time", inplace=True)
        p_df.join(df, how="outer").fillna(method="ffill").plot()

        fig = plt.gcf()
        fig.set_size_inches(18.5, 10.5)
        fig.savefig(pj(output_folder, 'series_cost_%d.pdf' % target), format="pdf")
        plt.close('all')


def plot_series_recalibration(folder):
    output_folder = pj(folder, "results", "estimation")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    depth_df = pd.read_csv(pj(folder, "results", "depth.csv"))

    # depth_df.set_index("node", inplace=True)
    targets = depth_df.node.unique()
    for target in targets:
        df = pd.read_csv(pj(output_folder, "estimation_%d.csv" % int(target)))
        df.set_index("time", inplace=True)

        # p_df = pd.read_csv(pj(folder, "results", "powertracker", "series_powertracker_%d.csv" % target))
        # p_df.set_index("time", inplace=True)
        # # p_df.join(df, how="outer").fillna(method="ffill").plot()

        # tx = df[df.kind == "tx"].reality.plot(label="tx")
        # rx = df[df.kind == "rx"].reality.plot(label="rx")
        # tx_route = df[(df.kind == "tx") & (df.estimator == "route")].estimation.plot(label="tx_route")
        # rx_route = df[(df.kind == "rx") & (df.estimator == "route")].estimation.plot(label="rx_route")
        # tx_noinfo = df[(df.kind == "tx") & (df.estimator == "noinfo")].estimation.plot(label="tx_noinfo")
        # rx_noinfo = df[(df.kind == "rx") & (df.estimator == "noinfo")].estimation.plot(label="rx_noinfo")
        # plt.legend()

        df[["estimation_tx_route", "estimation_rx_route", "tx", "rx", "estimation_tx_noinfo", "estimation_rx_noinfo"]].plot()

        fig = plt.gcf()
        # fig.set_size_inches(18.5, 10.5)
        fig.savefig(pj(output_folder, 'series_recalibration_%d.pdf' % target), format="pdf")
        plt.close('all')
