import pdb
import os
import pandas as pd
from os.path import join as pj
from itertools import product
import numpy as np

rates = [10, 25, 50, 75, 100]


def plot_error():
    res = pd.DataFrame()

    for rate in rates:
        df = pd.read_csv(pj("new_arbre", "arbre_high_calibration_%d" % rate, "results", "estimation", "recalibration_global.csv"))

        rate_record = {"rate": rate}
        rate_record["tx_noinfo_error_mean"] = df.error_tx_noinfo.mean()
        rate_record["rx_noinfo_error_mean"] = df.error_rx_noinfo.mean()
        rate_record["tx_route_error_mean"] = df.error_tx_route.mean()
        rate_record["rx_route_error_mean"] = df.error_rx_route.mean()

        rate_record["tx_noinfo_error_std"] = df.error_tx_noinfo.std()
        rate_record["rx_noinfo_error_std"] = df.error_rx_noinfo.std()
        rate_record["tx_route_error_std"] = df.error_tx_route.std()
        rate_record["rx_route_error_std"] = df.error_rx_route.std()
        res = res.append(pd.DataFrame(rate_record, index=["rate"]))

    pdb.set_trace()