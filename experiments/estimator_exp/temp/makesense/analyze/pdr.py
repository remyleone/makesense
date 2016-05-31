import pandas as pd
from os.path import join as pj
from collections import defaultdict
import numpy as np
import pdb
import os


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
