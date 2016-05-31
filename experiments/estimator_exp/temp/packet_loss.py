#!/usr/bin/env python

import re
from os.path import join as PJ
from matplotlib import pyplot as plt
from csv import DictWriter, DictReader


def packet_loss(folder):
    """
    Extract from the serial logs all the message.

    IMPORTANT: We only extract the message received from the root or send by
    the root.

    186572 ID:2 DATA send to 1 'Hello 1'
    187124 ID:8 DATA recv 'Hello 1' from 2
    197379 ID:8 REPLY send to 7 'Reply 1'
    197702 ID:7 REPLY recv 'Reply 1' from 8

    TODO: Pass all times to seconds.
    """
    # Arrivals to root
    arrival = "^(?P<time>\d+)\s+ID:(?P<mote_id>\d+)\s+DATA recv '(?P<message>.*)' from (?P<source>\d+)"
    departure = "^(?P<time>\d+)\s+ID:(?P<mote_id>\d+)\s+D1 '(?P<message>.*)'"
    fieldnames = ["time", "mote_id",
            "node_sent", "node_received",
            "global_sent", "global_received",
            "node_packet_loss", "global_packet_loss"]

    with open(PJ(folder, "serial.log")) as serial_file:
        lines = serial_file.read()

        with open(PJ(folder, "packet_loss.csv"), "w") as output_file:
            writer = DictWriter(output_file, fieldnames)
            writer.writeheader()

            nodes = range(42)
            node_packet_loss = {node: {"received": 0.0, "sent": 0.0} for node in nodes}
            global_sent, global_received = 0.0, 0.0
            for match in re.finditer(departure, lines, re.MULTILINE):
                d = match.groupdict()
                row = {}
                row["time"] = float(d["time"]) / (10 ** 6)
                row["mote_id"] = int(d["mote_id"])

                global_sent += 1.0
                node_packet_loss[row["mote_id"]]["sent"] += 1.0
                row["global_sent"] = global_sent
                row["global_received"] = global_received

                row["node_sent"] = node_packet_loss[row["mote_id"]]["sent"]
                row["node_received"] = node_packet_loss[row["mote_id"]]["received"]

                if row["node_sent"]:
                    row["node_packet_loss"] = row["node_received"] / row["node_sent"]
                else:
                    row["node_packet_loss"] = None
                if row["global_sent"]:
                    row["global_packet_loss"] = row["global_received"] / row["global_sent"]
                else:
                    row["global_packet_loss"] = None

                writer.writerow(row)

            for match in re.finditer(arrival, lines, re.MULTILINE):
                d = match.groupdict()
                row = {}
                row["time"] = float(d["time"]) / (10 ** 6)
                row["mote_id"] = int(d["mote_id"])

                global_received += 1.0
                node_packet_loss[row["mote_id"]]["received"] += 1.0

                row["global_sent"] = global_sent
                row["global_received"] = global_received

                row["node_sent"] = node_packet_loss[row["mote_id"]]["sent"]
                row["node_received"] = node_packet_loss[row["mote_id"]]["received"]

                if row["node_sent"]:
                    row["node_packet_loss"] = row["node_received"] / row["node_sent"]
                else:
                    row["node_packet_loss"] = None
                if row["global_sent"]:
                    row["global_packet_loss"] = row["global_received"] / row["global_sent"]
                else:
                    row["global_packet_loss"] = None

                writer.writerow(row)

        return nodes

def plot_packet_loss(folder, data=None):
    with open(PJ(folder, "packet_loss.csv")) as f:

        # Doing packet loss for every nodes
        # nodes = data["nodes"]
        #for node in nodes:

        #    fig = plt.figure()
        #    ax1 = fig.add_subplot(111)
        #    ax1.set_title("Packet loss")

        #    fig.savefig(PJ(folder, "%d_packet_loss.png" % node), format="png")
        #    fig.savefig(PJ(folder, "%d_packet_loss.pdf" % node), format="pdf")


        # Doing packet loss for the whole network
        time, global_packet_loss = [], []
        reader = DictReader(f)
        for row in reader:
            time.append(row["time"])
            global_packet_loss.append(100 * float(row["global_packet_loss"]))

        fig = plt.figure()
        ax1 = fig.add_subplot(111)
        ax1.set_title("Global packet loss")
        ax1.set_xlabel("Time [s]")
        ax1.set_ylabel("Packet loss [%]")
        ax1.plot(time, global_packet_loss)
        fig.savefig(PJ(folder, "packet_loss.png"), format="png")
        fig.savefig(PJ(folder, "packet_loss.pdf"), format="pdf")

folders = ["./chaine/chaine_high/", "./chaine/chaine_high_calibration/",
        "./chaine/chaine_medium/", "./chaine/chaine_medium_calibration/",
        "./chaine/chaine_low/", "./chaine/chaine_low_calibration/",

        "./fleur/fleur_high/", "./fleur/fleur_high_calibration/",
        "./fleur/fleur_medium/", "./fleur/fleur_medium_calibration/",
        "./fleur/fleur_low/", "./fleur/fleur_low_calibration/",

        "./arbre/arbre_high/", "./arbre/arbre_high_calibration/",
        "./arbre/arbre_medium/", "./arbre/arbre_medium_calibration/",
        "./arbre/arbre_low/", "./arbre/arbre_low_calibration/",

        "./arbre_overhearing/arbre_high/", "./arbre_overhearing/arbre_high_calibration/",
        "./arbre_overhearing/arbre_medium/", "./arbre_overhearing/arbre_medium_calibration/",
        "./arbre_overhearing/arbre_low/", "./arbre_overhearing/arbre_low_calibration/"

        ]


for folder in folders:
    print(folder)
    summary = packet_loss(folder)
    plot_packet_loss(folder, data=summary)
