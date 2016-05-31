import re
from itertools import chain
import logging
from csv import DictWriter, DictReader
from os.path import join as pj
import operator
from collections import namedtuple
from collections import defaultdict

logging.basicConfig(filename="parse_serial.log", filemode="w", level=logging.INFO)
log = logging.getLogger("parse_serial")

# RATE of information
RATE = 250000.0

# Broadcast cost
dis_packet = 39.0 * 47.0 / RATE
dio_packet = 30.0 * 80.0 / RATE

time_regexp = "^(?P<time>\d+)"
mote_id_regexp = "ID:(?P<mote_id>\d+)"

fieldnames = ["time", "mote_id", "node", "strobes",
              "message_type", "message", "tx", "rx", "size"]


message_t = namedtuple("Message", fieldnames)
message_t.__new__.__defaults__ = tuple(len(fieldnames) * [None])


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


_handlers = [
    _handle_battery_recalibration_log,
    _handle_dao_log,
    _handle_udp_reception_log,
    _handle_udp_sending_log,
    _handle_dio_log,
    _handle_dis_log,
    _handle_forward_log,
    _handle_mac_log,
    _handle_neighbor_log,
    _handle_overhearing_log,
    _handle_parent_log,
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
