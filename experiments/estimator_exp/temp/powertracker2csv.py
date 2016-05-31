#!/usr/bin/env python

import re
from csv import DictReader, DictWriter
from collections import defaultdict
import logging
from os.path import join as PJ

log = logging.getLogger("powertracker2csv")

def powertracker2csv(folder, shift=0):
    """
    format :
    Sky_2 MONITORED 9898083 us
    Sky_2 ON 180565 us 1,82 %
    Sky_2 TX 83860 us 0,85 %
    Sky_2 RX 2595 us 0,03 %
    Sky_2 INT 907 us 0,01 %

    NO GARANTY IF FORMAT IS DIFFERENT
    """

    path = PJ(folder, "powertracker.log")
    output_path = PJ(folder, "powertracker.csv")
    log.info("extract powertracker %s" % path)

    with open(path) as powertracker_file:
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

        with open(output_path, "w") as csv_output:
            writer = DictWriter(csv_output, delimiter=',', fieldnames=fields)
            writer.writeheader()
            tx_time = defaultdict(list)
            rx_time = defaultdict(list)

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
           "./arbre_overhearing/arbre_low/", "./arbre_overhearing/arbre_low_calibration/"]


for folder in folders:
    print(folder)
    powertracker2csv(folder)
