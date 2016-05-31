#!/usr/bin/env python3
# coding: utf-8

import re
from csv import DictWriter
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

receiver = {"time": [], "tx": [], "rx": []}
sender = {"time": [], "tx": [], "rx": []}

model_receiver = {"time": [], "tx": [], "rx": []}
model_sender = {"time": [], "tx": [], "rx": []}

counter = {"time": [], "count": []}


def bytes_to_times(n):
    """
    Take bytes and send back a time in seconds spent to send it
    in 802.15.4
    """
    return (992 + (n / 250000.0)) * 10 ** -6


def message_2_csv(f):
    """
    Extract from the serial logs all the message.

    IMPORTANT: We only extract the message received from the root or send by
    the root.

    186572 ID:2 DATA send to 1 'Hello 1'
    187124 ID:8 DATA recv 'Hello 1' from 2

    TODO: Pass all times to seconds.
    """

    # Departures from client
    departure = "^(?P<time>\d+)\s+ID:\d+\s+Client sending"
    ack_time = 352 * 10 ** -6
    fieldnames = ["time", "message_type"]

    with open(f) as serial_file, open("serial.csv", "w") as output_file:
        writer = DictWriter(output_file, fieldnames)
        writer.writeheader()
        # Counting packets to get an average rate
        match = 0
        for line in serial_file:

            if re.match(departure, line):
                d = re.match(departure, line).groupdict()
                d["message_type"] = "transmission"
                d["time"] = float(d["time"]) / (10 ** 6)
                counter["time"].append(d["time"])
                match += 1
                counter["count"].append(match)
                model_receiver["time"].append(d["time"])
                model_receiver["rx"].append(2* bytes_to_times(192))
                model_receiver["tx"].append(ack_time)

                model_sender["time"].append(d["time"])
                model_sender["rx"].append(ack_time)
                model_sender["tx"].append(2 * bytes_to_times(192))
        print("match %d lines" % match)
        for i in model_receiver["time"]:
            print(i)


def plot_receiver():
    f1 = plt.figure()
    ax1 = f1.add_subplot(111)

    # Energy

    ax1.plot(receiver["time"], receiver["rx"], "g", label="powertracker receiver rx")
    ax1.plot(receiver["time"], receiver["tx"], "r", label="powertracker receiver tx")

    # Model

    ax1.plot(model_receiver["time"], np.cumsum(model_receiver["rx"]), "g--", label="model receiver rx")
    ax1.plot(model_receiver["time"], np.cumsum(model_receiver["tx"]), "r--", label="model receiver tx")

    # Regression

    regression_to_do = {
        "model_receiver_rx": (model_receiver["time"], np.cumsum(model_receiver["rx"])),
        "receiver_rx": (receiver["time"], receiver["rx"]),
        #"model_receiver tx": (model_receiver["time"], np.cumsum(model_receiver["tx"])),
        #"receiver tx": (receiver["time"], receiver["tx"])

    }

    error = {}

    for name, (x, y) in regression_to_do.items():
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        error[name] = slope
        # plt.plot(xi, slope * xi + intercept, label=name)

    e = abs(error["model_receiver_rx"] - error["receiver_rx"]) / error["receiver_rx"]
    print("erreur receiver => ", e)

    ax1.set_xlabel("Time [s]")
    ax1.set_ylabel("Time spent in given state")
    ax1.legend(loc="upper left")

    f1.savefig("nullmac_calibration_receiver.pdf", format="pdf")


def plot_sender():
    f2 = plt.figure()
    ax2 = f2.add_subplot(111)

    # Energy

    ax2.plot(sender["time"], sender["rx"], "g", label="powertracker sender rx")
    ax2.plot(sender["time"], sender["tx"], "r", label="powertracker sender tx")

    # Model

    ax2.plot(model_sender["time"], np.cumsum(model_sender["rx"]), "g--", label="model sender rx")
    ax2.plot(model_sender["time"], np.cumsum(model_sender["tx"]), "r--", label="model sender tx")

    # Regression

    regression_to_do = {
        #"model_sender rx": (model_sender["time"], np.cumsum(model_sender["rx"])),
        #"sender rx": (sender["time"], sender["rx"]),
        "model_sender_tx": (model_sender["time"], np.cumsum(model_sender["tx"])),
        "sender_tx": (sender["time"], sender["tx"])

    }

    error = {}

    for name, (x, y) in regression_to_do.items():
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        error[name] = slope
        # plt.plot(xi, slope * xi + intercept, label=name)

    e = abs(error["model_sender_tx"] - error["sender_tx"]) / error["sender_tx"]
    print("erreur sender => ", e)

    ax2.set_xlabel("Time (s)")
    ax2.set_ylabel("Time spent in given state")
    ax2.legend(loc="upper left")
    f2.savefig("nullmac_calibration_sender.pdf", format="pdf")

def error(x, slope_reality=0, slope_model=0, intercept_model=0, intercept_reality=0):
    reality = slope_reality * x + intercept_reality
    model = slope_model * x + intercept_model
    return abs(reality - model) / reality

def plot_error():

    r = {
        "model_sender_tx": (0, 0),
        "sender_tx": (0, 0),
        "model_sender_rx": (0, 0),
        "sender_rx": (0, 0),
        "model_receiver_tx": (0, 0),
        "receiver_tx": (0, 0),
        "model_receiver_rx": (0, 0),
        "receiver_rx": (0, 0)
    }

    regression_to_do = {
        "model_sender_rx": (model_sender["time"], np.cumsum(model_sender["rx"])),
        "sender_rx": (sender["time"], sender["rx"]),
        "model_sender_tx": (model_sender["time"], np.cumsum(model_sender["tx"])),
        "sender_tx": (sender["time"], sender["tx"]),
        "model_receiver_rx": (model_receiver["time"], np.cumsum(model_receiver["rx"])),
        "receiver_rx": (receiver["time"], receiver["rx"]),
        "model_receiver_tx": (model_receiver["time"], np.cumsum(model_receiver["tx"])),
        "receiver_tx": (receiver["time"], receiver["tx"])
    }
    for name, (x, y) in regression_to_do.items():
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        r[name] = (slope, intercept)

    f2 = plt.figure()
    ax2 = f2.add_subplot(111)

    x = np.arange(0, 2000, 100)


    e_sender_rx = lambda x: error(x, slope_reality=r["sender_rx"][0], slope_model=r["model_sender_rx"][0], intercept_reality=r["sender_rx"][1], intercept_model=r["model_sender_rx"][1])
    e_sender_tx = lambda x: error(x, slope_reality=r["sender_tx"][0], slope_model=r["model_sender_tx"][0], intercept_reality=r["sender_tx"][1], intercept_model=r["model_sender_tx"][1])
    e_receiver_rx = lambda x: error(x, slope_reality=r["receiver_rx"][0], slope_model=r["model_receiver_rx"][0], intercept_reality=r["receiver_rx"][1], intercept_model=r["model_receiver_rx"][1])
    e_receiver_tx = lambda x: error(x, slope_reality=r["sender_tx"][0], slope_model=r["model_sender_tx"][0], intercept_reality=r["sender_tx"][1], intercept_model=r["model_sender_tx"][1])

    print("coucou")
    print(e_receiver_rx(x))

    ax2.plot(x, e_sender_rx(x), "go", linewidth=4, label=r"$\epsilon$ sender rx")
    ax2.plot(x, e_sender_tx(x), "ro", linewidth=4, label=r"$\epsilon$ sender tx")
    ax2.plot(x, e_receiver_rx(x), "g--", markersize=4, label=r"$\epsilon$ receiver rx")
    ax2.plot(x, e_receiver_tx(x), "r--", markersize=4, label=r"$\epsilon$ receiver tx")

    ax2.set_xlabel("Time [s]")
    ax2.set_ylabel("Error")
    ax2.legend(loc="upper right", mode="expand", ncol=2)
    f2.savefig("calibration_nullmac.pdf", format="pdf")
# Analyze

powertracker_to_csv("powertracker.log")
message_2_csv("serial.log")

xi = np.arange(0, 1000)

print("slope, intercept, r_value, p_value, std_err")
plot_receiver()
plot_sender()
plot_error()
plt.show()
