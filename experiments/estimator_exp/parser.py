# -*- coding: utf8 -*-

import networkx as nx
import json
from netaddr import IPAddress
from binascii import unhexlify
import pdb
from collections import defaultdict
from collections import namedtuple
from csv import DictWriter
from csv import DictReader
from itertools import chain
from os.path import join as pj
import numpy as np
import operator
import os
import re
import subprocess
import pandas as pd
import logging
import numpy as np
import xml.etree.ElementTree as ET
import datetime

log = logging.getLogger("parsing")

# RATE of information
RATE = 250000.0

# Broadcast cost
dis_packet = 39.0 * 47.0 / RATE
dio_packet = 30.0 * 80.0 / RATE

time_regexp = "^(?P<time>\d+)"
mote_id_regexp = "ID:(?P<mote_id>\d+)"
time_regexp_iotlab = "^(?P<time>\d+.\d+)"
mote_id_regexp_iotlab = "(?P<mote_id>(?<=;)(.*)(?=;))"

# fieldnames = ["time", "mote_id", "node", "strobes",
#               "message_type", "message", "tx", "rx", "size",
#               "rime", "clock", "cpu", "lpm", "irq", "green_led", "yellow_led", "red_led", "sensors", "serial"]


# message_t = namedtuple("Message", fieldnames)
# message_t.__new__.__defaults__ = tuple(len(fieldnames) * [None])


def ipv6_to_host(s):
    return int(s.split(":")[-1:][0], 16)


def powertracker2csv(folder, shift=0):
    """
    format :
    Sky_2 MONITORED 9898083 us
    Sky_2 ON 180565 us 1,82 %
    Sky_2 TX 83860 us 0,85 %
    Sky_2 RX 2595 us 0,03 %
    Sky_2 INT 907 us 0,01 %

    sky_tx_cost = (17.4 * 10 ** -3) / (3600 * 10 ** 6)
    sky_rx_cost = (19.7 * 10 ** -3) / (3600 * 10 ** 6)
    sky_on_cost = (365 * 10 ** -6) / (3600 * 10 ** 6)
    sky_int_cost = (19.7 * 10 ** -3) / (3600 * 10 ** 6)

    wismote_tx_cost = (25.8 * 10 ** -3) / (3600 * 10 ** 6)
    wismote_rx_cost = (22.3 * 10 ** -3) / (3600 * 10 ** 6)
    wismote_on_cost = (365 * 10 ** -6) / (3600 * 10 ** 6)
    wismote_int_cost = (25.8 * 10 ** -3) / (3600 * 10 ** 6)
    """
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

        all_iterable = zip(
            monitored_iterable, on_iterable, tx_iterable, rx_iterable, int_iterable)

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
                row["monitored_time"] = float(
                    row["monitored_time"]) / (10 ** 6)
                row["tx_time"] = float(row["tx_time"]) / (10 ** 6)
                row["rx_time"] = float(row["rx_time"]) / (10 ** 6)
                row["on_time"] = float(row["on_time"]) / (10 ** 6)
                row["int_time"] = float(row["int_time"]) / (10 ** 6)
                if row["monitored_time"] > shift:
                    writer.writerow(row)




def pcap2csv(folder, filename="output.csv"):
    """
    Execute a simple filter on PCAP and count
    """
    # Getting raw data
    with open(pj(folder, filename), "w") as f:

        command = ["tshark",
                   "-T", "fields",
                   "-E", "header=y",
                   "-E", "separator=,",
                   # IoT-lab pcap are suspicious
                   "-Y", "udp || icmpv6",
                   "-e", "frame.time_epoch",
                   "-e", "frame.protocols",
                   "-e", "frame.len",
                   "-e", "wpan.fcs",
                   "-e", "wpan.seq_no",
                   "-e", "wpan.src16",
                   "-e", "wpan.dst16",
                   "-e", "wpan.src64",
                   "-e", "wpan.dst64",
                   "-e", "icmpv6.type",
                   "-e", "ipv6.src",
                   "-e", "ipv6.dst",
                   "-e", "icmpv6.code",
                   "-e", "udp.dstport",
                   "-e", "udp.srcport",
                   "-e", "data.data",
                   "-r", pj(folder, "output.pcap")]

        print(str(command))
        process = subprocess.Popen(command, stdout=subprocess.PIPE)
        stdout, stderr = process.communicate()
        f.write(stdout)

    df_pcap = pd.read_csv(pj(folder, "output.csv"))
    df_pcap["source_info"] = "testbed_pcap"
    df_pcap.rename(columns={
                       "frame.time_epoch": "time",
                       "frame.len": "frame_length",
                       }, inplace=True)

    # Transforming hostname to DNS name
    grenoble_ip_mac = {}
    with open("/home/sieben/.grenoble.json") as f:
        grenoble_ip_mac = json.load(f)
    # Attention au broadcast
    grenoble_ip_mac["ff02::1a"] = "Multicast"
    grenoble_ip_mac["ff02::1"] = "Multicast"
    grenoble_ip_mac["aaaa::ff:fe00:1"] = "gateway"

    # Sorting out MAC informations

    ## Broadcast packets
    df_pcap["broadcast"] = df_pcap["wpan.dst16"] == "0xffff"
    df_pcap.drop('wpan.dst16', axis=1, inplace=True)
    df_pcap.drop('wpan.src16', axis=1, inplace=True)

    mac_col = {"wpan.src64": "mac_src", "wpan.dst64": "mac_dst"}
    for old_col, new_col in mac_col.items():
        df_pcap[new_col] = df_pcap[df_pcap[old_col].notnull()][old_col]\
        .str.replace(":", "")\
        .apply(lambda x: str(IPAddress(int(x, 16) ^ (2 ** 57))))\
        .map(grenoble_ip_mac)
        df_pcap.drop(old_col, axis=1, inplace=True)

    # ACK packets
    df_pcap["ack"] = df_pcap["frame_length"] == 5

    # Sorting out ICMPv6 informations (mostly RPL)

    icmpv6 = {0: "dis", 1: "dio", 2: "dao"}
    df_pcap["rpl_type"] = df_pcap[df_pcap["icmpv6.type"] == 155]["icmpv6.code"].map(icmpv6)
    for col in ["icmpv6.type", "icmpv6.code"]:
        df_pcap.drop(col, axis=1, inplace=True)

    ip_col = {"ipv6.src": "ip_src", "ipv6.dst": "ip_dst"}
    for old_col, new_col in ip_col.items():
        df_pcap[new_col] = df_pcap[old_col]\
            .str.replace("(aaaa|fe80)::", "::")\
            .map(grenoble_ip_mac)
        df_pcap.drop(old_col, axis=1, inplace=True)

    # Packets Forwarding
    # TODO: Trouver une meilleure caractérisation
    df_pcap["forwarding"] = df_pcap[df_pcap.frame_length > 10][
        (df_pcap.mac_src != df_pcap.ip_src) | (df_pcap.mac_dst != df_pcap.ip_dst)]\
        .ack == False

    # Sorting out application packets
    udp = {
        6789: "monitoring",
        5678: "data"
    }
    df_pcap["udp_type"] = df_pcap["udp.dstport"].map(udp)

    df_pcap["payload"] = df_pcap[df_pcap["data.data"].notnull()]["data.data"].apply(
        lambda x: unhexlify(x.replace(":", "")))

    for col in ["udp.dstport", "udp.srcport", "data.data"]:
        df_pcap.drop(col, axis=1, inplace=True)

    # Counting all packets
    df_pcap.groupby("mac_src").size()

    # We normalize the timestamp
    df_pcap["norm_time"] = (df_pcap.time - df_pcap.time.min()) / (df_pcap.time - df_pcap.time.min()).max()

    # We add real datetime
    df_pcap.set_index(pd.DatetimeIndex(df_pcap.time.apply(lambda x: datetime.datetime.fromtimestamp(x))), inplace=True)

    df_pcap.to_csv(pj(folder, "pretty_pcap.csv"))


def cast_message(d):
    """
    Do standard casting for messages
    """
    d["mote_id"] = d["mote_id"]
    d["time"] = float(d["time"])
    return d


def frame_size(size):
    """
    Very basic function that gives the size of the frame sent on the wire
    for a UDP packet
    10: 55
    20: 65
    30: 75
    40: 85
    50: 95
    """
    d = {'udp': 8, 'ipv6_hop': 8, '6lowpan': 6, '802.15.4': 23}
    if size > 50:
        log.warning('Fragmentation occurred I cannot compute reliably')
    total = sum(d.values() + [size])
    log.debug("frame_size Payload size: %d ; On wire size %d", size, total)
    return total


def _handle_dis_log(match):
    d = match.groupdict()
    d = cast_message(d)
    d["node"] = d["mote_id"]
    d["message_type"] = "dis"

    # stats[d["node"], "dis_time"] += dis_packet
    # stats[d["node"], "rpl_time"] += dis_packet

    return d
_handle_dis_log.regexp = r" ".join(
    [time_regexp, mote_id_regexp, "RPL: Sending a DIS"])
_handle_dis_log.regexp_iotlab = r";".join(
    [time_regexp_iotlab, mote_id_regexp_iotlab, "RPL: Sending a DIS"])


def _handle_dao_log(match):
    d = match.groupdict()
    d = cast_message(d)

    d["message_type"] = "dao"
    d["node"] = d["mote_id"]

    # stats[d["node"], "dao_count"] += 1
    # stats[d["node"], "rpl_count"] += 1

    return d
_handle_dao_log.regexp = r" ".join(
    [time_regexp, mote_id_regexp, "RPL: Sending DAO with prefix"])
_handle_dao_log.regexp_iotlab = r";".join(
    [time_regexp_iotlab, mote_id_regexp_iotlab, "RPL: Sending DAO with prefix"])


def _handle_overhearing_log(match):
    d = match.groupdict()
    d = cast_message(d)

    d["message_type"] = "overhearing"
    # stats[d["mote_id"], "overhearing_count"] += 1
    return d
_handle_overhearing_log.regexp = r" ".join(
    [time_regexp, mote_id_regexp, "contikimac: data not for us"])
_handle_overhearing_log.regexp_iotlab = r" ".join(
    [time_regexp_iotlab, mote_id_regexp_iotlab, "contikimac: data not for us"])


def _handle_dio_log(match):
    d = match.groupdict()
    d = cast_message(d)

    d["node"] = d["mote_id"]
    d["message_type"] = "dio"

    # stats[d["node"], "dio_time"] += dio_packet
    # stats[d["node"], "rpl_time"] += dio_packet

    return d
_handle_dio_log.regexp = r" ".join(
    [time_regexp, mote_id_regexp, "(RPL: Sending a multicast-DIO|RPL: Sending unicast-DIO)"])
_handle_dio_log.regexp_iotlab = r";".join(
    [time_regexp_iotlab, mote_id_regexp_iotlab, "(RPL: Sending a multicast-DIO|RPL: Sending unicast-DIO)"])


def _handle_forward_log(match):
    d = match.groupdict()
    d = cast_message(d)

    d["node"] = d["mote_id"]
    d["message_type"] = "forwarding"

    # TODO: Hard coded one
    # stats[d["mote_id"], "forwarding_time"] += 8.0 * frame_size(10) / RATE

    return d
_handle_forward_log.regexp = r" ".join(
    [time_regexp, mote_id_regexp, "Forwarding packet to"])
_handle_forward_log.regexp_iotlab = r";".join(
    [time_regexp_iotlab, mote_id_regexp_iotlab, "Forwarding packet to"])

def _handle_battery_recalibration_log(match):
    d = match.groupdict()
    d = cast_message(d)

    d["message_type"] = "battery_recalibration"

    # stats[d["node"], "battery_recalibration_count"] += 1
    return d
_handle_battery_recalibration_log.regexp = r" ".join(
    [time_regexp, mote_id_regexp, "Battery recalibration"])
_handle_battery_recalibration_log.regexp_iotlab = r";".join(
    [time_regexp_iotlab, mote_id_regexp_iotlab, "DATA recv \'energy,(?P<msg_id>\d+)\' from (?P<sender>(.*))"])


def _handle_parent_log(match):
    # Simple count of parent messages
    d = match.groupdict()
    d = cast_message(d)

    d["message_type"] = "parent"

    # stats[d["node"], "parent_count"] += 1

    return d
_handle_parent_log.regexp = r" ".join(
    [time_regexp, mote_id_regexp, "Preferred Parent (?P<node>\d+)$"])
_handle_parent_log.regexp_iotlab = r";".join(
    [time_regexp_iotlab, mote_id_regexp_iotlab, "DATA recv \'parent,(?P<msg_id>\d+),(?P<node>(.*))\' from (?P<sender>(.*))$"])


def _handle_mac_log(match):
    d = match.groupdict()
    d = cast_message(d)

    d["node"] = d["mote_id"]
    d["message_type"] = "mac"
    d["strobes"] = int(d["strobes"])
    d["size"] = int(d["size"])

    # stats[
    #     d["mote_id"], "mac_time"] += (d["strobes"] + 1) * 8.0 * d["size"] / RATE
    return d
_handle_mac_log.regexp = r" ".join(
    [time_regexp, mote_id_regexp, "contikimac: send \(strobes=(?P<strobes>\d+), len=(?P<size>\d+), ack, no collision\), done$"])
_handle_mac_log.regexp_iotlab = r";".join(
    [time_regexp_iotlab, mote_id_regexp_iotlab, "contikimac: send \(strobes=(?P<strobes>\d+), len=(?P<size>\d+), ack, no collision\), done$"])


def _handle_udp_sending_log(match):
    d = match.groupdict()
    d = cast_message(d)

    d["node"] = d["mote_id"]
    d["message_type"] = "udp_sending"
    d["size"] = len(d["message"])

    # stats[d["node"], "data_time"] += 8.0 * frame_size(d["size"]) / RATE
    return d
_handle_udp_sending_log.regexp = r" ".join(
    [time_regexp, mote_id_regexp, "DATA send to root \'(?P<message>(.)*)\'$"])
_handle_udp_sending_log.regexp_iotlab = r";".join(
    [time_regexp_iotlab, mote_id_regexp_iotlab, "DATA send to 1 \'(?P<message>(.)*)\'$"])


def _handle_udp_reception_log(match):
    d = match.groupdict()
    d = cast_message(d)

    d["message_type"] = "udp_reception"

    # stats[d["node"], "data_time"] += 8.0 * frame_size(d["size"]) / RATE
    return d
_handle_udp_reception_log.regexp = r" ".join(
    [time_regexp, mote_id_regexp, "DATA recv \'(?P<message>(.)*)\' from (?P<node>\d+)$"])
_handle_udp_reception_log.regexp_iotlab = r";".join(
    [time_regexp_iotlab, mote_id_regexp_iotlab, "DATA recv \'(?P<message>(.)*)\' from (?P<sender>(.*))$"])


def _handle_neighbor_log(match):
    d = match.groupdict()
    d = cast_message(d)

    d["node"] = int(d["node"])
    d["message_type"] = "neighbor"

    # stats[d["node"], "neighbor_count"] += 1

    return d
_handle_neighbor_log.regexp = r" ".join(
    [time_regexp, mote_id_regexp, "Neighbor (?P<node>\d+)$"])
_handle_neighbor_log.regexp_iotlab = r";".join(
    [time_regexp_iotlab, mote_id_regexp_iotlab, "Neighbor (?P<node>\d+)$"])


def _handle_stats_log(match):
    d = match.groupdict()
    d = cast_message(d)

    d["node"] = d["mote_id"]
    d["message_type"] = "stats"
    for field in ["clock", "cpu", "lpm", "irq", "green_led", "yellow_led", "red_led", "tx", "rx", "sensors", "serial"]:
        d[field] = int(d[field])
    return d
_handle_stats_log.regexp = r" ".join(
    [time_regexp, mote_id_regexp,
    "E (?P<rime>\d+.\d+)",
    "clock (?P<clock>\d+)",
    "cpu (?P<cpu>\d+)",
    "lpm (?P<lpm>\d+)",
    "irq (?P<irq>\d+)",
    "gled (?P<green_led>\d+)", "yled (?P<yellow_led>\d+)", "rled (?P<red_led>\d+)",
    "tx (?P<tx>\d+)", "listen (?P<rx>\d+)",
    "sensors (?P<sensors>\d+)", "serial (?P<serial>\d+)"
])
_handle_stats_log.regexp_iotlab = r";".join(
    [time_regexp_iotlab, mote_id_regexp_iotlab,
    "E (?P<rime>\d+.\d+)",
    "clock (?P<clock>\d+)",
    "cpu (?P<cpu>\d+)",
    "lpm (?P<lpm>\d+)",
    "irq (?P<irq>\d+)",
    "gled (?P<green_led>\d+)", "yled (?P<yellow_led>\d+)", "rled (?P<red_led>\d+)",
    "tx (?P<tx>\d+)", "listen (?P<rx>\d+)",
    "sensors (?P<sensors>\d+)", "serial (?P<serial>\d+)"
])


_handlers = [
    _handle_battery_recalibration_log,
    _handle_dao_log,
    _handle_dio_log,
    _handle_dis_log,
    _handle_forward_log,
    _handle_mac_log,
    _handle_neighbor_log,
    _handle_overhearing_log,
    _handle_parent_log,
    _handle_stats_log,
    _handle_udp_reception_log,
    _handle_udp_sending_log,
]


def powertracker2message(folder, stats):
    with open(pj(folder, "results", "powertracker.csv")) as energy_f:
        messages = list()
        for row in DictReader(energy_f):
            m = {"time": float(row["monitored_time"]),
                 "rx": float(row["rx_time"]),
                 "tx": float(row["tx_time"]),
                 "message_type": "energy",
                 "node": int(row["mote_id"])}
            messages.append(m)
            stats[int(row["mote_id"]), "powertracker"] += 1
        return messages


def serial2message(folder, stats):
    """
    # mote_id => node that emit the serial log
    # node => node that emit the message
    # Typically when a message come to root, mote_id => root, node => node that emitted the
    # message

    # Regular expression used for matching logs in serial
    """
    messages = list()
    with open(pj(folder, "serial.log")) as serial_file:
        for line in serial_file:
            for handler in _handlers:
                match = re.match(handler.regexp, line, re.MULTILINE)
                if match:
                    message = handler(match)
                    messages.append(message)
                    break
        return messages, stats

def print_stats(stats):
    for name, count in sorted(stats.items()):
        if count:
            if "time" in name[1] and stats[name[0], "mac_time"]:
                total = stats[name[0], "mac_time"]
                log.info("%s: %f (%f)", name, count, count / total)
            else:
                log.info("%s: %d", name, count)
        else:

            log.warning("No packets for %s", name)


def message(folder):
    """
    Message queue preparation

    - Extract from powertracker all the message
    - Extract from the serial logs all the message.

    IMPORTANT: We only extract the message received from the root or send by
    the root.

    186572 ID:2 DATA send to 1 'Hello 1'
    187124 ID:8 DATA recv 'Hello 1' from 2
    197379 ID:8 REPLY send to 7 'Reply 1'
    197702 ID:7 REPLY recv 'Reply 1' from 8
    """
    stats = defaultdict(float)

    sorted_messages = sorted(
        chain(serial2message(folder, stats),
              # powertracker2message(folder, stats)
              ),
        key=operator.attrgetter("time"))

    print_stats(stats)

    # MESSAGE logging for debugging purposes #

    log.info(pj(folder, "results", "messages.csv"))
    with open(pj(folder, "results", "messages.csv"), "w") as f:
        writer = DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for m in sorted_messages:
            writer.writerow(m._asdict())
    log.info("messages saved")
    return sorted_messages


def csc_to_graph(name):
    tree = ET(name)
    mote_id = [int(t.text) for t in tree.findall(".//mote/interface_config/id")]
    mote_type = [t.text for t in tree.findall(".//mote/motetype_identifier")]
    x = [float(t.text) for t in tree.findall(".//mote/interface_config/x")]
    y = [float(t.text) for t in tree.findall(".//mote/interface_config/y")]
    z = [float(t.text) for t in tree.findall(".//mote/interface_config/z")]


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
                model_receiver["rx"].append(2 * bytes_to_times(192))
                model_receiver["tx"].append(ack_time)

                model_sender["time"].append(d["time"])
                model_sender["rx"].append(ack_time)
                model_sender["tx"].append(2 * bytes_to_times(192))
        print("match %d lines" % match)
        for i in model_receiver["time"]:
            print(i)


def parse_iotlab_energy(folder):
    current_df = pd.read_csv(
        pj(folder, "current.csv"), header=None, names=['mote_id', 'time', 'current'])
    voltage_df = pd.read_csv(
        pj(folder, "voltage.csv"), header=None, names=['mote_id', 'time', 'voltage'])
    power_df = pd.read_csv(
        pj(folder, "power.csv"), header=None, names=['mote_id', 'time', 'power'])
    temp_df = pd.merge(
        current_df, voltage_df, how="left", on=["mote_id", "time"])
    res_df = pd.merge(temp_df, power_df, how="left", on=["mote_id", "time"])
    res_df.to_csv(pj(folder, "energy.csv"), index=False)


def parse_iotlab_m3_energy(folder):

    def _parser(folder, node):
        df = pd.read_csv(pj(folder, node), header=7, sep="\t",
            names=['t', "dump", "index", "timestamp_s", "timestamp_us", "power", "voltage", "current"],
        )
        df.drop(["dump", "index"], axis=1, inplace=True)
        df.time = (df.timestamp_s + 10 ** -6 * df.timestamp_us)##.strftime("%H:%M:%S.%f")
        df.set_index(pd.DatetimeIndex(df.time.apply(lambda x: datetime.datetime.fromtimestamp(x))), inplace=True)
        df["charge"] = df.power * df.t.diff()
        df["norm_time"] =  df.t / df.t.max()
        df["node"] = node.replace(".oml", "")
        return df

    df = pd.concat([_parser(folder, f) for f in os.listdir(folder)])
    df.to_csv(pj(folder, "consumption.csv"))

def iotlabserial2message(folder):
    """
    # mote_id => node that emit the serial log
    # node => node that emit the message
    # Typically when a message come to root, mote_id => root, node => node that emitted the
    # message

    # Regular expression used for matching logs in serial
    """
    messages = list()
    with open(pj(folder, "serial.log")) as serial_file:
        for line in serial_file:
            for handler in _handlers:
                match = re.match(handler.regexp_iotlab, line, re.MULTILINE)
                if match:
                    message = handler(match)
                    messages.append(message)
                    break
        df = pd.DataFrame(messages)

        # Transforming hostname to DNS name
        grenoble_ip_mac = {}
        with open("/home/sieben/.grenoble.json") as f:
            grenoble_ip_mac = json.load(f)
        # Attention au broadcast
        grenoble_ip_mac["ff02::1a"] = "Multicast"
        grenoble_ip_mac["ff02::1"] = "Multicast"
        grenoble_ip_mac["aaaa::ff:fe00:1"] = "gateway"

        for col in ["node", "sender"]:
            df[col] = df[col]\
                .str.replace("(aaaa|fe80)::", "::")\
                .map(grenoble_ip_mac)

        # TODO: Comment organiser la mise a jour de l'arbre? Comment traiter les différents messages?
        g = nx.DiGraph()
        def update_tree(x):
            if x["message_type"] == "parent":
                g.add_edge(x["sender"], x["node"])
                for node in g.neighbors(x["sender"]):
                    if node != x["node"]:
                        g.remove_edge(x["sender"], node)
            else:
                g.add_node(x["sender"])
            return g.copy()

        df["graph"] = df[
              (df.message_type == "parent")
            | (df.message_type == "udp_reception")
            | (df.message_type == "battery_recalibration")
            ].apply(lambda x: update_tree(x), axis=1)

        # La connaissance du graphe est prolongée sur les temps où on ne reçoit pas de messages
        df["graph"].fillna(method="pad", inplace=True)

        # Compute delay

        df["sender"].fillna(df[df.message_type == "udp_sending"].mote_id + ".grenoble.iot-lab.info",
            inplace=True)

        # HACK temporaire
        df["message"] = df.message.str.replace(" from the client", "")
        df["temp_key"] = df.sender + df.message
        df["latency"] = df[["time", "temp_key"]].groupby("temp_key").time.diff()


        # Find depth
        def find_depth(x, root="m3-204.grenoble.iot-lab.info"):
            g, sender = x["graph"], x["sender"]
            if sender in g.nodes() and nx.has_path(g, sender, root):
                return len(nx.shortest_path(g, sender, root))
            else:
                return None
        df["depth"] = df[df.graph.notnull()].apply(find_depth, axis=1)

        # Find PDR

        def build_pdr(reception, sending):
            return reception.map({True: 1.0, False: 0.0}).cumsum() / sending.map({True: 1.0, False: 0.0}).cumsum()

        df["pdr_global"] = build_pdr(
            reception=(df["message_type"] == "udp_reception"),
            sending=(df["message_type"] == "udp_sending"))

        ## Now we look for pdr on different levels

        depths = [int(x) for x in df["depth"].unique() if not np.isnan(x)]
        for depth in depths:
            df["pdr_depth_%d" % depth] = build_pdr(
                reception=(df[df["depth"] == depth]["message_type"] == "udp_reception"),
                sending=(df[df["depth"] == depth]["message_type"] == "udp_sending")
            )

        # To integrate
        #df_serial.set_index(pd.DatetimeIndex(df_serial.time.apply(lambda x: datetime.datetime.fromtimestamp(x))), inplace=True)

        pdb.set_trace()

        return messages
