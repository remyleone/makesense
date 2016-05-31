#!/usr/bin/env python

from csv import DictReader
import matplotlib.pyplot as plt
from os.path import join as PJ


def repartition_protocol(csv_file):
        """
        Representation of protocol repartition (stacked histogram)

        Include UDP, CoAP, ping, RPL, other...
        """
        fig1 = plt.figure()
        ax1 = fig1.add_subplot(111)
        ax1.set_ylabel("Bytes")
        ax1.set_xlabel("Time (s)")

        color = {"coap": "red",
                 "rpl": "blue",
                 "ping": "green",
                 "total": "black",
                 "udp": "yellow",
                 "rplinfo": "cyan",
                 "battery": "magenta"}

        with open(csv_file) as f:
            reader = DictReader(f)

            # Hack to avoid duplicate label in legend
            label_first = {"total": True, "rpl": True, "ping": True,
                           "udp": True, "coap": True, "battery": True,
                           "rplinfo": True}
            for row in reader:
                row = {k: float(v) for k, v in row.iteritems()}
                width = (row["bin_end"] - row["bin_start"]) / 2
                bottom = 0.0

                # if row["total_bytes"]:
                #     ax1.bar(row["bin_start"], row['total_bytes'],
                #             color=color["total"], width=width,
                #             label="total" if label_first["total"] else "")
                #     label_first["total"] = False

                # rpl
                if row["rpl_bytes"]:
                    ax1.bar(row["bin_start"] + width, row["rpl_bytes"],
                            color=color["rpl"], width=width, bottom=bottom,
                            label="rpl" if label_first["rpl"] else "")
                    bottom += row["rpl_bytes"]
                    label_first["rpl"] = False

                # udp
                if row["udp_bytes"]:
                    ax1.bar(row["bin_start"] + width, row["udp_bytes"],
                            color=color["udp"], width=width, bottom=bottom,
                            label='application' if label_first["udp"] else "")
                    bottom += row["udp_bytes"]
                    label_first["udp"] = False

                # battery
                if row["battery_bytes"]:
                    ax1.bar(row["bin_start"] + width, row["battery_bytes"],
                            color=color["battery"], width=width, bottom=bottom,
                            label="battery" if label_first["battery"] else "")
                    bottom += row["battery_bytes"]
                    label_first["battery"] = False

                # rplinfo
                if row["rplinfo_bytes"]:
                    ax1.bar(row["bin_start"] + width, row["rplinfo_bytes"],
                            color=color["rplinfo"], width=width, bottom=bottom,
                            label="rplinfo" if label_first["rplinfo"] else "")
                    # Last value
                    #bottom += row["rplinfo_bytes"]
                    label_first["rplinfo"] = False

        key, value = [], []
        for k, v in color.items():
            key.append(k)
            value.append(v)
        #plt.legend(tuple(key), tuple(value))
        plt.legend()

        img_path = "/home/sieben/workspace/tee/img/repartition_protocol.pdf"
        plt.savefig(img_path, format="pdf")
