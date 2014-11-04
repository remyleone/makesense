# -*- coding: utf8 -*-


import pdb
from collections import defaultdict
from collections import namedtuple
from csv import DictWriter
from csv import DictReader
from itertools import chain
from os.path import join as pj
from scipy import stats
import numpy as np
import operator
import os
import re
import subprocess
import pandas as pd
import logging

log = logging.getLogger("parsing")

# RATE of information
RATE = 250000.0

# Broadcast cost
dis_packet = 39.0 * 47.0 / RATE
dio_packet = 30.0 * 80.0 / RATE

time_regexp = "^(?P<time>\d+)"
mote_id_regexp = "ID:(?P<mote_id>\d+)"

fieldnames = ["time", "mote_id", "node", "strobes",
              "message_type", "message", "tx", "rx", "size",
              "rime", "clock", "cpu", "lpm", "irq", "green_led", "yellow_led", "red_led", "sensors", "serial"]


message_t = namedtuple("Message", fieldnames)
message_t.__new__.__defaults__ = tuple(len(fieldnames) * [None])

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


def pcap2csv(folder):
    """
    Execute a simple filter on PCAP and count
    """
    print("start pcap2csv")
    with open(pj(folder, "results", "pcap.csv"), "w") as output_file:
        command = ["tshark",
                   "-T", "fields",
                   "-E", "header=y",
                   "-E", "separator=,",
                   "-e", "frame.time_relative",
                   "-e", "frame.len",
                   "-e", "wpan.src64",
                   "-e", "wpan.dst64",
                   "-e", "icmpv6.type",
                   "-e", "ipv6.src",
                   "-e", "ipv6.dst",
                   "-e", "icmpv6.code",
                   "-e", "data.data",
                   "-r", pj(folder, "output.pcap")]
        print(str(command))
        process = subprocess.Popen(command, stdout=subprocess.PIPE)
        stdout, stderr = process.communicate()
        output_file.write(stdout)


def format_pcap_csv(folder):
    df = pd.read_csv(pj(folder, "results", "pcap.csv"))
    df.rename(columns={"frame.time_relative": "time",
                       "frame.len": "length",
                       "wpan.src64": "mac_src",
                       "wpan.dst64": "mac_dst",
                       "ipv6.src": "ip_src",
                       "icmpv6.type": "icmpv6_type",
                       "ipv6.dst": "ip_dst",
                       "icmpv6.code": "icmp_code",
                       "data.data": "payload"
                       }, inplace=True)

    SIM_TIME = 200
    df["time"] *= SIM_TIME / df.time.max()

    def f(x):
        if isinstance(x["mac_dst"], str):
            try:
                return ipv6_to_host(x["mac_dst"])
            except:
                return x["mac_dst"]
    df.mac_dst = df.apply(f, axis=1)

    def f(x):
        if isinstance(x["mac_src"], str):
            try:
                return ipv6_to_host(x["mac_src"])
            except:
                return x["mac_src"]
    df.mac_src = df.apply(f, axis=1)

    def f(x):
        if isinstance(x["ip_src"], str):
            try:
                
                return ipv6_to_host(x["ip_src"])
            except:
                return x["ip_src"]
    df.ip_src = df.apply(f, axis=1)

    df.icmpv6_type = df.icmpv6_type.apply(lambda x: "rpl" if x == 155 else x)
    code = {0: "dis", 1: "dio", 2: "dao"}
    df.icmp_code = df.icmp_code.apply(lambda x: code[x] if x in code else x)

    def f(x):
        if isinstance(x["payload"], str):
            return "udp"
        else:
            return x["icmpv6_type"]
    df.icmpv6_type = df.apply(f, axis=1)

    # ACK packets
    def f(x):
        if x["length"] == 5:
            return "ack"
        else:
            return x["icmpv6_type"]
    df.icmpv6_type = df.apply(f, axis=1)

    # Forwarding
    def f(x):
        if x.icmpv6_type == "udp":
            if x.mac_src != x.ip_src:
                return True
            else:
                return False
        else:
            return False
    df["forwarding"] = df.apply(f, axis=1)

    df.to_csv(pj(folder, "results", "pcap_relooked.csv"), index=False)



def cast_message(d):
    """
    Do standard casting for messages
    """
    d["mote_id"] = int(d["mote_id"])
    d["time"] = float(d["time"]) / (10 ** 6)
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


def _handle_dis_log(match, stats):
    d = match.groupdict()
    d = cast_message(d)
    d["node"] = int(d["mote_id"])
    d["message_type"] = "dis"

    stats[d["node"], "dis_time"] += dis_packet
    stats[d["node"], "rpl_time"] += dis_packet

    return message_t(**d)
_handle_dis_log.regexp = r" ".join([time_regexp, mote_id_regexp, "RPL: Sending a DIS"])


def _handle_dao_log(match, stats):
    d = match.groupdict()
    d = cast_message(d)

    d["message_type"] = "dao"
    d["node"] = int(d["mote_id"])

    stats[d["node"], "dao_count"] += 1
    stats[d["node"], "rpl_count"] += 1

    return message_t(**d)
_handle_dao_log.regexp = r" ".join([time_regexp, mote_id_regexp, "RPL: Sending DAO with prefix"])


def _handle_overhearing_log(match, stats):
    d = match.groupdict()
    d = cast_message(d)

    d["message_type"] = "overhearing"
    stats[d["mote_id"], "overhearing_count"] += 1
    return message_t(**d)
_handle_overhearing_log.regexp = r" ".join([time_regexp, mote_id_regexp, "contikimac: data not for us"])


def _handle_dio_log(match, stats):
    d = match.groupdict()
    d = cast_message(d)

    d["node"] = int(d["mote_id"])
    d["message_type"] = "dio"

    stats[d["node"], "dio_time"] += dio_packet
    stats[d["node"], "rpl_time"] += dio_packet

    return message_t(**d)
_handle_dio_log.regexp = r" ".join([time_regexp, mote_id_regexp, "(RPL: Sending a multicast-DIO|RPL: Sending unicast-DIO)"])


def _handle_forward_log(match, stats):
    d = match.groupdict()
    d = cast_message(d)

    d["node"] = int(d["mote_id"])
    d["message_type"] = "forwarding"

    # TODO: Hard coded one
    stats[d["mote_id"], "forwarding_time"] += 8.0 * frame_size(10) / RATE

    return message_t(**d)
_handle_forward_log.regexp = r" ".join([time_regexp, mote_id_regexp, "Forwarding packet to"])


def _handle_battery_recalibration_log(match, stats):
    d = match.groupdict()
    d = cast_message(d)

    d["node"] = int(d["mote_id"])
    d["message_type"] = "battery_recalibration"

    stats[d["node"], "battery_recalibration_count"] += 1
    return message_t(**d)
_handle_battery_recalibration_log.regexp = r" ".join([time_regexp, mote_id_regexp, "Battery recalibration"])


def _handle_parent_log(match, stats):
    # Simple count of parent messages

    d = match.groupdict()
    d = cast_message(d)

    d["node"] = int(d["node"])
    d["message_type"] = "parent"

    stats[d["node"], "parent_count"] += 1

    return message_t(**d)
_handle_parent_log.regexp = r" ".join([time_regexp, mote_id_regexp, "Preferred Parent (?P<node>\d+)$"])


def _handle_mac_log(match, stats):
    d = match.groupdict()
    d = cast_message(d)

    d["node"] = int(d["mote_id"])
    d["message_type"] = "mac"
    d["strobes"] = int(d["strobes"])
    d["size"] = int(d["size"])

    stats[d["mote_id"], "mac_time"] += (d["strobes"] + 1) * 8.0 * d["size"] / RATE
    return message_t(**d)
_handle_mac_log.regexp = r" ".join([time_regexp, mote_id_regexp, "contikimac: send \(strobes=(?P<strobes>\d+), len=(?P<size>\d+), ack, no collision\), done$"])


def _handle_udp_sending_log(match, stats):
    d = match.groupdict()
    d = cast_message(d)

    d["node"] = int(d["mote_id"])
    d["message_type"] = "udp_sending"
    d["size"] = len(d["message"])

    stats[d["node"], "data_time"] += 8.0 * frame_size(d["size"]) / RATE
    return message_t(**d)
_handle_udp_sending_log.regexp = r" ".join([time_regexp, mote_id_regexp, "DATA send to root \'(?P<message>(.)*)\'$"])


def _handle_udp_reception_log(match, stats):
    d = match.groupdict()
    d = cast_message(d)

    d["node"] = int(d["node"])
    d["message_type"] = "udp_reception"
    d["size"] = len(d["message"])

    stats[d["node"], "data_time"] += 8.0 * frame_size(d["size"]) / RATE
    return message_t(**d)
_handle_udp_reception_log.regexp = r" ".join([time_regexp, mote_id_regexp, "DATA recv \'(?P<message>(.)*)\' from (?P<node>\d+)$"])


def _handle_neighbor_log(match, stats):
    d = match.groupdict()
    d = cast_message(d)

    d["node"] = int(d["node"])
    d["message_type"] = "neighbor"

    stats[d["node"], "neighbor_count"] += 1

    return message_t(**d)
_handle_neighbor_log.regexp = r" ".join([time_regexp, mote_id_regexp, "Neighbor (?P<node>\d+)$"])

def _handle_stats_log(match, stats):
    d = match.groupdict()
    d = cast_message(d)

    d["node"] = int(d["mote_id"])
    d["message_type"] = "stats"
    for field in ["clock", "cpu", "lpm", "irq", "green_led", "yellow_led", "red_led", "tx", "rx", "sensors", "serial"]:
        d[field] = int(d[field])
    return message_t(**d)
_handle_stats_log.regexp = r" ".join([
    time_regexp,
    mote_id_regexp,
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
        messages = set()
        for row in DictReader(energy_f):
            m = {"time": float(row["monitored_time"]),
                 "rx": float(row["rx_time"]),
                 "tx": float(row["tx_time"]),
                 "message_type": "energy",
                 "node": int(row["mote_id"])}
            messages.add(message_t(**m))
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
    messages = set()
    with open(pj(folder, "serial.log")) as serial_file:
        for line in serial_file:
            for handler in _handlers:
                match = re.match(handler.regexp, line, re.MULTILINE)
                if match:
                    message = handler(match, stats)
                    messages.add(message)
                    break
        return messages


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
        chain(serial2message(folder, stats), powertracker2message(folder, stats)),
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

def parse_iotlab_energy(folder):
    current_df = pd.read_csv(pj(folder, "current.csv"), header=None, names=['mote_id', 'time', 'current'])
    voltage_df = pd.read_csv(pj(folder, "voltage.csv"), header=None, names=['mote_id', 'time', 'voltage'])
    power_df = pd.read_csv(pj(folder, "power.csv"), header=None, names=['mote_id', 'time', 'power'])
    temp_df = pd.merge(current_df, voltage_df, how="left", on=["mote_id", "time"])
    res_df = pd.merge(temp_df, power_df, how="left", on=["mote_id", "time"])
    res_df.to_csv(pj(folder, "energy.csv"), index=False)
