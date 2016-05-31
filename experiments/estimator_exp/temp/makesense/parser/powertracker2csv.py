#!/usr/bin/env python3
# -*- coding: utf8 -*-

import os
from os.path import join as pj
import re
from csv import DictWriter
from itertools import product

"""
format :
Sky_2 MONITORED 9898083 us
Sky_2 ON 180565 us 1,82 %
Sky_2 TX 83860 us 0,85 %
Sky_2 RX 2595 us 0,03 %
Sky_2 INT 907 us 0,01 %

NO GARANTY IF FORMAT IS DIFFERENT
"""

# [10, 20, 30, 40, 50]
# sizes = range(10, 60, 10)
# shift = 90
# kinds = ["contikimac", "nullmac"]

# We have the result from powertracker in us
# (mA * µs) => (A * h) to fit Claude Chaudet slides
# sky_tx_cost = (17.4 * 10 ** -3) / (3600 * 10 ** 6)
# sky_rx_cost = (19.7 * 10 ** -3) / (3600 * 10 ** 6)
# sky_on_cost = (365 * 10 ** -6) / (3600 * 10 ** 6)
# sky_int_cost = (19.7 * 10 ** -3) / (3600 * 10 ** 6)

# wismote_tx_cost = (25.8 * 10 ** -3) / (3600 * 10 ** 6)
# wismote_rx_cost = (22.3 * 10 ** -3) / (3600 * 10 ** 6)
# wismote_on_cost = (365 * 10 ** -6) / (3600 * 10 ** 6)
# wismote_int_cost = (25.8 * 10 ** -3) / (3600 * 10 ** 6)


def powertracker2csv(folder, shift=0):

    with open(pj(folder, "powertracker.log")) as powertracker_file:
        powertracker_logs = powertracker_file.read()

        monitored_iterable = re.finditer(
            r"^(Sky|Wismote)_(?P<mote_id>\d+) MONITORED (?P<monitored_time>\d+)",
            powertracker_logs, re.MULTILINE)
        on_iterable = re.finditer(
            r"^(Sky|Wismote)_(?P<mote_id>\d+) ON (?P<on_time>\d+)",
            powertracker_logs, re.MULTILINE)
        tx_iterable = re.finditer(
            r"^(Sky|Wismote)_(?P<mote_id>\d+) TX (?P<tx_time>\d+)",
            powertracker_logs, re.MULTILINE)
        rx_iterable = re.finditer(
            r"^(Sky|Wismote)_(?P<mote_id>\d+) RX (?P<rx_time>\d+)",
            powertracker_logs, re.MULTILINE)
        int_iterable = re.finditer(
            r"^(Sky|Wismote)_(?P<mote_id>\d+) INT (?P<int_time>\d+)",
            powertracker_logs, re.MULTILINE)

        all_iterable = zip(monitored_iterable, on_iterable, tx_iterable, rx_iterable, int_iterable)

        fields = ["mote_id", "monitored_time",
                  "tx_time", "rx_time", "on_time", "int_time"]

        output_folder = pj(folder, "results")
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        with open(pj(output_folder, "powertracker.csv"), "w") as csv_output:
            writer = DictWriter(csv_output, delimiter=',', fieldnames=fields)
            writer.writeheader()

            for matches in all_iterable:
                row = {}
                for match in matches:
                    all(m.groupdict()["mote_id"] == matches[0].groupdict()["mote_id"]
                        for m in matches)
                    row.update((k, int(v))
                               for k, v in match.groupdict().items())
                # Passing the result from us to s
                row["monitored_time"] = float(row["monitored_time"]) / (10 ** 6)
                row["tx_time"] = float(row["tx_time"]) / (10 ** 6)
                row["rx_time"] = float(row["rx_time"]) / (10 ** 6)
                row["on_time"] = float(row["on_time"]) / (10 ** 6)
                row["int_time"] = float(row["int_time"]) / (10 ** 6)
                if row["monitored_time"] > shift:
                    writer.writerow(row)
