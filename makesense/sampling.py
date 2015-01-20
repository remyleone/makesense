#!/usr/bin/env python

import pdb
import json
from collections import defaultdict
import re

from scipy.interpolate import interp1d
from scipy import stats
import pandas as pd
import numpy as np


import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from powertracker2csv import powertracker2csv


# BEWARE OF SIZES

sizes = [
    1, 10, 100, 107, 20, 30, 40,
    50,
    60, 70, 80, 90
    ]

powertracker2csv(sizes)

kinds = ["tx_sender", "rx_sender", "tx_receiver", "rx_receiver"]

res = {size: {"intervals": [],
              "tx_sender": [],
              "rx_sender": [],
              "tx_receiver": [],
              "rx_receiver": []}
       for size in sizes}

for size in sizes:

    # First step we must compute the function to have the same API
    df = pd.read_csv("contikimac/%d/powertracker_stripped.csv" % size)
    receiver_df = df[df.mote_id == 1]
    sender_df = df[df.mote_id == 2]

    functions = {
        "tx_sender": {"time": sender_df.monitored_time,
                      "value": sender_df.tx_time,
                      "function": None},
        "rx_sender": {"time": sender_df.monitored_time,
                      "value": sender_df.rx_time,
                      "function": None},
        "tx_receiver": {"time": receiver_df.monitored_time,
                        "value": receiver_df.tx_time,
                        "function": None},
        "rx_receiver": {"time": receiver_df.monitored_time,
                        "value": receiver_df.rx_time,
                        "function": None},
    }

    # Interpolation Sender
    interpolation = False

    if interpolation:

        for kind in kinds:
            time = functions[kind]["time"]
            value = functions[kind]["value"]
            functions[kind]["function"] = interp1d(time, value)

    regression = True

    if regression:

        regression_debug = False

        for kind in kinds:
            time = functions[kind]["time"]
            value = functions[kind]["value"]
            slope, intercept, r_value, p_value, std_err = stats.linregress(time, value)
            functions[kind]["function"] = lambda x: slope * x + intercept

            if regression_debug:
                line = slope * time + intercept
                plt.plot(time, line, '-', time, value, 'o', label=kind)
                plt.title("size %d" % size)

        if regression_debug:
            plt.legend()
            plt.show()

    time_regexp = "^(?P<time>\d+)"
    mote_id_regexp = "ID:(?P<mote_id>\d+)"
    reception_regexp = r" ".join([time_regexp, mote_id_regexp,
                                  "DATA recv \'(?P<message>(.)*)\'$"])

    sending_regexp = r" ".join([time_regexp, mote_id_regexp,
                                "DATA send to root \'(?P<message>(.)*)\'$"])

    message_table = defaultdict(dict)

    with open("contikimac/%d/serial.log" % size) as f:
        for line in f:
            reception_match = re.match(reception_regexp, line, re.MULTILINE)
            if reception_match:
                d = reception_match.groupdict()

                # TODO HACK DEGEU
                message_id = int(d["message"].split()[0])
                message_table[message_id]["received"] = float(d["time"]) / 10 ** 6

                message_table[message_id]["status"] = (message_table[message_id]["received"]
                                                       - message_table[message_id]["sent"] < 2)

            sending_match = re.match(sending_regexp, line, re.MULTILINE)
            if sending_match:
                d = sending_match.groupdict()

                message_id = int(d["message"])
                message_table[message_id]["sent"] = float(d["time"]) / 10 ** 6

    # We filter only to have the one that got received
    message_table = {key: value
                     for key, value in message_table.items()
                     if "received" in value and "sent" in value}
    with open("contikimac/%d/message_table.json" % size, "w") as f:
        f.write(json.dumps(message_table, sort_keys=True, indent=4,
                           separators=(',', ': ')))

    repo = defaultdict(list)
    init_interval = {"begin": 0.0, "end": 0.0, "messages": 0}
    current_interval = {"begin": 0.0, "end": 0.0, "messages": 0}

    # AGGREGATIOn
    # for key, value in message_table.items():

    #     # Init case
    #     if value["status"]:
    #         if not current_interval["begin"]:
    #             current_interval["begin"] = value["sent"]
    #         else:
    #             current_interval["end"] = value["received"]

    #         current_interval["messages"] += 1
    #     else:
    #         # We archive the current interval
    #         if current_interval["begin"]:
    #             res[size]["intervals"].append(current_interval)
    #         current_interval = {"begin": 0.0, "end": 0.0, "messages": 0}

    # # Finalize if we finish with a good interval
    # if current_interval["begin"]:
    #     res[size]["intervals"].append(current_interval)

    # NO aggregation
    for key, value in message_table.items():

        if value["status"]:
            res[size]["intervals"].append({
                "begin": value["sent"],
                "end": value["received"],
                "messages": 1})

# Now we try to deduce the cost per packet
for size, intervals_data in res.items():
    print("SIZE: %d" % size)
    intervals = intervals_data["intervals"]
    tasks = {
        "tx_sender": functions["tx_sender"]["function"],
        "rx_sender": functions["rx_sender"]["function"],
        "tx_receiver": functions["tx_receiver"]["function"],
        "rx_receiver": functions["rx_receiver"]["function"]
    }

    for task, interpolation in tasks.items():
        for interval in intervals:

            try:
                diff = (interpolation(interval["end"])
                        - interpolation(interval["begin"])) / interval["messages"]
                if diff:
                    res[size][task].append(diff)
                else:
                    res[size][task].append(diff)
                    print("0.0 diff increase powertracker resolution")
            except ValueError:
                #pdb.set_trace()
                print("interpolation FAIL")
    print("--------------------")

mean = {kind: [] for kind in kinds}
err = {kind: [] for kind in kinds}

for kind in kinds:
    for size, data in res.items():

        avg = np.mean(res[size][kind])
        print(avg)
        if np.isnan(avg):
            pdb.set_trace()
        mean[kind].append(avg)
        res[size]["mean_%s" % kind] = avg

        std = np.std(res[size][kind])
        err[kind].append(std)
        res[size]["std_%s" % kind] = std


with open("res.json", "w") as f:
    f.write(json.dumps(res, sort_keys=True, indent=4, separators=(',', ': ')))

for kind in kinds:
    plt.errorbar(sizes, mean[kind], fmt="o-", yerr=err[kind], label=kind)

plt.xlim([min(sizes) - 1, 50])
plt.ylim([0, 0.0002])
plt.legend()
plt.show()
