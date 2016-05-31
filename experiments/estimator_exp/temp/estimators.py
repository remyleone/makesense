#!/usr/bin/env python

import pdb
import fnmatch
import itertools
import logging
import operator
import os
import re
from os.path import join as pj
from csv import DictReader, DictWriter
from collections import defaultdict, namedtuple
from multiprocessing import Pool
from matplotlib import pyplot as plt
import networkx as nx
from networkx.readwrite import json_graph
from scipy import stats
from scipy.interpolate import interp1d
import numpy as np
from numpy import ediff1d, mean

plt.close('all')

logging.basicConfig(filename="estimator.log", filemode="w", level=logging.DEBUG)

log = logging.getLogger("estimators")

# Time required to send a 802.15.4 ACK packet
ack_time = 352 * 10 ** -6

# Amount of time that a node have to repeat in average the sending of a message
# while running Contiki MAC
repeat_sender = 4.24

# Amount of time that a node have to stay
repeat_receiver = 1.5

# Time at which we start to estimate the traffic
#SHIFT = 35.451328
SHIFT = 0

# Temporal BIN
BIN = 25

#
used_model = "802.15.4"

# Considered estimators
estimators = ["noinfo", "radio", "route"]

# root node
root = 1

bin_fieldnames = ["bin_start",
                  "tx", "tx_estimated", "tx_outcast",
                  "rx", "rx_estimated", "rx_outcast"]


def estimation_to_do_in(folder):
    for estimation_path in os.listdir(folder):
        if fnmatch.fnmatch(estimation_path, "estimation_*"):
            log.info(estimation_path)
            yield estimation_path


def load_estimation(path):
    """
    Will load the packet_size estimation from a csv and return an interpolation
    on the whole range of message_size.
    """
    payload_size = []
    tx_sender, rx_sender = [], []
    tx_receiver, rx_receiver = [], []
    with open(path) as f:
        reader = DictReader(f)
        for row in reader:
            payload_size.append(float(row["payload_size"]))
            tx_sender.append(float(row["tx_sender"]))
            rx_sender.append(float(row["rx_sender"]))
            tx_receiver.append(float(row["tx_receiver"]))
            rx_receiver.append(float(row["rx_receiver"]))

    res = {"tx_sender_reference": interp1d(payload_size, tx_sender),
           "rx_sender_reference": interp1d(payload_size, rx_sender),
           "tx_receiver_reference": interp1d(payload_size, tx_receiver),
           "rx_receiver_reference": interp1d(payload_size, rx_receiver)}

    return res


def cast_message(d):
    """
    Do standard casting for messages
    """
    d["mote_id"] = int(d["mote_id"])
    
    d["time"] = float(d["time"]) / (10 ** 6)
    return d


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
    messages = set()

    ###################
    # SERIAL MESSAGES #
    ###################

    # mote_id => node that emit the serial log
    # node => node that emit the message
    # Typically when a message come to root, mote_id => root, node => node that emitted the
    # message
    fieldnames = ["time", "mote_id", "node", "message_type", "message", "tx", "rx", "size"]

    message_t = namedtuple("Message", fieldnames)
    message_t.__new__.__defaults__ = tuple(len(fieldnames) * [None])

    # Regular expression used for matching logs in serial

    time_regexp = "^(?P<time>\d+)"
    mote_id_regexp = "ID:(?P<mote_id>\d+)"

    battery_recalibration_regexp = r" ".join([time_regexp,
                                              mote_id_regexp,
                                              "Battery recalibration"])
    log.debug(battery_recalibration_regexp)
    parent_regexp = r" ".join([time_regexp, mote_id_regexp,
                               "Preferred Parent (?P<node>\d+)$"])

    neighbor_regexp = r" ".join([time_regexp, mote_id_regexp,
                                 "Neighbor (?P<node>\d+)$"])

    data_regexp = r" ".join([time_regexp,
                             mote_id_regexp,
                             "DATA recv \'(?P<message>(.)*)\' from (?P<node>\d+)$"])

    # We count all the RPL package
    dis_regexp = r" ".join([time_regexp, mote_id_regexp,
                            "RPL: Sending a DIS"])
    dio_regexp = r" ".join([time_regexp, mote_id_regexp,
                            "(RPL: Sending a multicast-DIO|RPL: Sending unicast-DIO)"])
    dao_regexp = r" ".join([time_regexp, mote_id_regexp,
                            "RPL: Sending DAO with prefix"])

    count_stats = defaultdict(int)

    with open(pj(folder, "serial.log")) as serial_file:
        for line in serial_file:

            # Simple count of parent messages
            parent_match = re.match(parent_regexp, line, re.MULTILINE)
            if parent_match:
                d = parent_match.groupdict()
                d = cast_message(d)

                d["node"] = int(d["node"])
                d["message_type"] = "parent"

                messages.add(message_t(**d))
                count_stats["parent_count"] += 1

            neighbor_match = re.match(neighbor_regexp, line, re.MULTILINE)
            if neighbor_match:
                d = neighbor_match.groupdict()
                d = cast_message(d)

                d["node"] = int(d["node"])
                d["message_type"] = "neighbor"

                messages.add(message_t(**d))
                count_stats["neighbor_count"] += 1

            data_match = re.match(data_regexp, line, re.MULTILINE)
            if data_match:
                d = data_match.groupdict()
                d = cast_message(d)

                d["node"] = int(d["node"])
                d["message_type"] = "data"
                d["size"] = len(d["message"])

                messages.add(message_t(**d))
                count_stats["data_count"] += 1

            battery_recalibration_match = re.match(battery_recalibration_regexp, line, re.MULTILINE)
            if battery_recalibration_match:
                d = battery_recalibration_match.groupdict()

                d["message_type"] = "battery_recalibration"

                messages.add(message_t(**d))
                count_stats["battery_recalibration_count"] += 1

            dis_match = re.match(dis_regexp, line, re.MULTILINE)
            if dis_match:
                d = dis_match.groupdict()
                d = cast_message(d)

                d["message_type"] = "rpl"

                messages.add(message_t(**d))
                count_stats["dis_count"] += 1
                count_stats["rpl_count"] += 1

            dio_match = re.match(dio_regexp, line, re.MULTILINE)
            if dio_match:
                d = dio_match.groupdict()
                d = cast_message(d)

                d["message_type"] = "rpl"
                messages.add(message_t(**d))
                count_stats["dio_count"] += 1
                count_stats["rpl_count"] += 1

            dao_match = re.match(dao_regexp, line, re.MULTILINE)
            if dao_match:
                d = dao_match.groupdict()
                d = cast_message(d)

                d["message_type"] = "rpl"
                messages.add(message_t(**d))
                count_stats["dao_count"] += 1
                count_stats["rpl_count"] += 1

    for name, count in count_stats.items():
        if count:
            log.info("%s: %d" % (name, count))
        else:
            log.warning("No packets for %s" % name)
    log.info("serial messages loaded")

    # ###############
    # POWERTRACKER #
    # ###############

    # Preparing the list of power_tracker messages for each node

    power_tracker_rows = defaultdict(list)
    with open(pj(folder, "powertracker.csv")) as energy_f:
        powertracker_count = 0
        for row in DictReader(energy_f):
            mote_id = int(row["mote_id"])
            m = {"time": float(row["monitored_time"]),
                 "rx": float(row["rx_time"]),
                 "tx": float(row["tx_time"]),
                 "message_type": "energy",
                 "node": int(row["mote_id"])}
            power_tracker_rows[mote_id].append(m)
            messages.add(message_t(**m))
            powertracker_count += 1
    log.info("powertracker: %d" % powertracker_count)

    #######################################
    # IMPORTANT: We sort messages by time #
    #######################################

    #messages = sorted(messages, key=operator.itemgetter("time"))
    sorted_messages = sorted(messages, key=operator.attrgetter("time"))
    log.info("messages sorted")

    ##########################################
    # MESSAGE logging for debugging purposes #
    ##########################################

    log.info(pj(folder, "messages.csv"))
    with open(pj(folder, "messages.csv"), "w") as f:
        writer = DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for m in sorted_messages:
            writer.writerow(m._asdict())
    log.info("messages saved")
    return sorted_messages


def outcast(l, current_t):
    """
    Function taking a stream of known values about the state of
    known and trying to compute an outcast value.

    Right now we use a linear regression
    """
    all_time, all_tx, all_rx = [], [], []
    for (time, tx, rx) in l:
        all_time.append(time)
        all_tx.append(tx)
        all_rx.append(rx)

    # BEWARE: Right now we add the trend and the transaction
    # maybe we are counting the same thing twice.
    res = []
    for kind in [all_tx, all_rx]:
        if len(all_time) > 1:
            slope, intercept, r_value, p_value, std_err = stats.linregress(
                all_time, kind)
            res.append(slope * current_t + intercept)
        else:
            res.append(None)

    return tuple(res)


class Estimator(object):
    """
    General Estimator Workflow.
    """

    def __init__(self, folder, reference):

        # GENERAL SETTINGS

        self.folder = folder
        self.recalibration = False

        # GRAPH SETTINGS

        # All routes are unique.
        self.rpl_graph = nx.DiGraph()

        # Each node got a several neighbors
        self.radio_graph = nx.Graph()

        self.root = 1
        self.route_path, self.radio_path = {}, {}

        # We use the route stored in self.route_path, for each node in the path
        # minus the final destination, we compute all the neighbors of a node.
        # This nodes will be the one over hearing when a transmission occurs.

        # REFERENCE SETTINGS

        self.tx_sender = reference["tx_sender_reference"]
        self.rx_sender = reference["rx_sender_reference"]
        self.tx_receiver = reference["tx_receiver_reference"]
        self.rx_receiver = reference["rx_receiver_reference"]

        # ESTIMATION SETTINGS

        # This determined when all routes are known by the estimators
        self.all_route_known = False

        # root is supposed non energy constrained therefore we are not
        # interested
        # 0 is the information when a parent is missing
        self.excluded_nodes = [0, None]
        self.targets = set()

        # This dict is used to do outcast and recalibration
        # node, kind -> [(time, value), ...]
        self.last_known_powertracker = defaultdict(list)

        # Count how much message an estimator see by bins
        # bin_start, node, estimator -> count
        self.bin_message_data_count = defaultdict(float)
        self.bin_rpl_count = defaultdict(float)

        # Store the last value of powertracker
        # target, kind => Value
        self.last_powertracker = defaultdict(float)

        # bin_start, node, kind -> value
        self.bin_powertracker = defaultdict(float)
        self.bin_powertracker["bins"] = set()

        # {target, estimator, time: [...], target, estimator, tx: [...]}
        self.series_estimation = defaultdict(list)

        # bin_start, target, estimator, kind -> value
        self.bin_estimation = defaultdict(float)
        self.bin_estimation["bins"] = set()

        self.message_size = defaultdict(list)

    def refresh_route(self):
        """
        Refresh routing and radio table
        """
        self.route_path = {n: nx.shortest_path(self.rpl_graph, n, self.root)
                           for n in self.rpl_graph.nodes()
                           if nx.has_path(self.rpl_graph, n, self.root)}

        self.radio_path = {n: list(itertools.chain(*[self.radio_graph.neighbors(n_)
                                                     for n_ in self.route_path[n][:-1]]))
                           for n in self.route_path}

    def noinfo_estimation(self, current_message):
        """
        Simply account for node and destination
        :param current_message:
        """
        bin_start = BIN * int(current_message.time / BIN)
        self.bin_message_data_count[bin_start, current_message.node, "noinfo"] += 1
        node = current_message.node

        transaction = defaultdict(float)
        transaction[node, "tx"] += self.tx_sender(current_message.size)
        transaction[node, "rx"] += self.rx_sender(current_message.size)
        return transaction

    def route_estimation(self, message):
        """
        For a given message this will estimate the energy consumed by
        all nodes forwarding the message through the RPL tree.

        :param current_message:
        """
        node = message.node
        size = message.size
        bin_start = BIN * int(message.time / BIN)
        self.bin_message_data_count[bin_start, node, "route"] += 1

        t = defaultdict(float)
        t[node, "tx"] += self.tx_sender(size)
        t[node, "rx"] += self.rx_sender(size)

        # Forwarders of the message
        try:
            forwarders = self.route_path[node]
            for forwarder in forwarders[1: -1]:
                self.bin_message_data_count[bin_start, forwarder, "route"] += 1
                t[forwarder, "tx"] += self.tx_sender(size) + self.tx_receiver(size)
                t[forwarder, "rx"] += self.rx_sender(size) + self.rx_receiver(size)
        except KeyError as error:
            log.warning("No route in route_estimation for node %s" % error)
            log.info(self.route_path)
        return t

    def radio_estimation(self, message):
        """
        For a given message, this will estimate the energy consumed by
        nodes that over hear the message transmission.
        """
        size = message.size
        node = message.node
        bin_start = BIN * int(message.time / BIN)
        self.bin_message_data_count[bin_start, node, "radio"] += 1

        t = defaultdict(float)
        t[node, "tx"] += self.tx_sender(size)
        t[node, "rx"] += self.rx_sender(size)

        # Starting as route
        try:
            forwarders = self.route_path[node]
            for forwarder in forwarders[1: -1]:
                self.bin_message_data_count[bin_start, forwarder, "radio"] += 1
                t[forwarder, "tx"] += self.tx_sender(size) + self.tx_receiver(size)
                t[forwarder, "rx"] += self.rx_sender(size) + self.rx_receiver(size)

            # Sending to all listener nodes a rx_cost. In particular
            # a same node could receive several time the same message.
            # TODO: Does nodes listen to all repeated messages?
            for listener in self.radio_path[node]:
                if listener != self.root:
                    self.bin_message_data_count[bin_start, listener, "radio"] += 1
                    t[listener, "rx"] += self.rx_receiver(size)
        except KeyError as error:
            log.warning("No route in radio_estimation for node %s" % error)
            log.debug(str(self.route_path))

        return t

    def update_estimator(self, estimator, target, tx=0.0, rx=0.0, time=None):
        # Adding to the series values
        if tx or rx:
            self.series_estimation[target, estimator, "time"].append(time)
            self.series_estimation[target, estimator, "tx"].append(tx)
            self.series_estimation[target, estimator, "rx"].append(rx)

            # Adding to the bin version
            bin_start = BIN * int(time / BIN)
            self.bin_estimation["bins"].add(bin_start)

            self.bin_estimation[bin_start, target, estimator, "tx"] += tx
            self.bin_estimation[bin_start, target, estimator, "rx"] += rx

    def handle_battery_recalibration_message(self, message, *args, **kwargs):
        """
        TODO !!!
        We update all estimators with the last value.
        We assume that the node send us through a notification
        the amount of time that the node spent in TX and in RX
        """
        node = message.node
        if self.recalibration:

            t = message.time
            tx, rx = self.last_powertracker[node, "tx"], self.last_powertracker[node, "rx"]
            self.last_known_powertracker[node].append((t, tx, rx))

            # We make a transaction that put the estimators at the right level
            # for each estimator
            for estimator in estimators:

                estimated_tx = self.total_estimation[node, estimator, "tx"]
                estimated_rx = self.total_estimation[node, estimator, "rx"]

                update_tx = tx - estimated_tx
                update_rx = rx - estimated_rx

                self.update_estimator(estimator, node,
                                      time=t, tx=update_tx, rx=update_rx)

    def handle_energy_message(self, message, *args, **kwargs):
        """
        Handle the message from powertracker
        """
        current_node = message.node
        current_t = message.time
        bin_start = BIN * int(current_t / BIN)

        self.bin_powertracker[bin_start, current_node, "tx"] = message.tx
        self.bin_powertracker[bin_start, current_node, "rx"] = message.rx
        self.bin_powertracker["bins"].add(bin_start)

        self.last_powertracker[current_node, "tx"] = message.tx
        self.last_powertracker[current_node, "rx"] = message.rx

        if self.recalibration:
            outcast_tx, outcast_rx = outcast(self.last_known_powertracker[current_node],
                                             current_t)

            for estimator in estimators:
                self.update_estimator(estimator, current_node,
                                      time=current_t,
                                      tx=outcast_tx,
                                      rx=outcast_rx)

    def handle_data_message(self, current_message, *args, **kwargs):
        current_node = current_message.node
        current_t = current_message.time
        self.message_size[current_node].append(current_message.size)
        if self.all_route_known:

            for estimator in [self.noinfo_estimation, self.route_estimation, self.radio_estimation]:
                transaction = estimator(current_message)
                name_estimator = estimator.__name__.replace("_estimation", "")
                for node in self.targets:
                    tx = transaction[node, "tx"]
                    rx = transaction[node, "rx"]
                    if tx or rx:
                        self.update_estimator(name_estimator,
                                              node,
                                              tx=tx,
                                              rx=rx,
                                              time=current_t)
        else:
            log.info("Not all route known at %f" % current_t)
            log.info(self.route_path)

    def handle_rpl_message(self, current_message, *args, **kwargs):
        """
        Simply count the amount of RPL messages that a node send in a
        bin
        """
        current_node = current_message.node
        current_t = current_message.time
        bin_start = BIN * int(current_t / BIN)

        self.bin_rpl_count[bin_start, current_node] += 1

    def handle_neighbor_message(self, current_message, *args, **kwargs):
        """
        Build up the radio representation at the gateway
        """
        neighbor = current_message.node
        node = current_message.mote_id
        self.radio_graph.add_edge(node, neighbor)
        self.refresh_route()

    def handle_parent_message(self, current_message, *args, **kwargs):
        """
        Build up the RPL representation at the gateway
        """
        parent = current_message.node
        node = current_message.mote_id
        self.rpl_graph.add_edge(node, parent)
        self.radio_graph.add_edge(node, parent)
        self.refresh_route()

        # Condition to know of all routes are known
        diff = set(self.rpl_graph.nodes()) - self.targets
        if diff:
            log.info("No all route known at %f" % current_message.time)
            log.info("Missing routes for %s", diff)
            self.all_route_known = False
        else:
            log.info("All route known at %f" % current_message.time)
            self.all_route_known = True

    def handle_generic_message(self, current_message, *args, **kwargs):
        """
        # Estimation are correlated through nodes and through time
        # Therefore we need to encapsulate any piece of information into
        # an atomic message that will be interpreted
        # by different estimator
        """
        for handler in dir(self):
            if handler.startswith("handle"):
                print(handler)
        raise RuntimeError('No {} method'.format('handle_%s_message' % current_message.message_type))

    def estimate(self, messages):
        """
        Estimation occurs here

        BEWARE ALL MESSAGES NEEDS TO BE SORTED BY TIME !!!
        """
        # Powertracker bin useful to plot a comparative with the estimation

        # time, TX, RX
        for message in messages:
            if message.node not in self.excluded_nodes:
                self.targets.add(message.node)
                self.targets.add(message.mote_id)
                method_name = "handle_%s_message" % message.message_type
                handler = getattr(self, method_name, None)
                if handler is None:
                    handler = self.handle_generic_message
                handler(message)

    def diff_bin_powertracker(self, bin_start, target, kind):
        return self.bin_powertracker[bin_start, target, kind] - self.bin_powertracker[bin_start - BIN, target, kind]
    
    def diff_bin_estimator(self, bin_start, target, estimator, kind):
        return self.bin_estimator[bin_start, target, estimator, "tx"] - self.bin_estimator[bin_start - BIN, target, estimator, "tx"]

    def check(self, targets):
        self.check_estimator_order(targets)
        self.check_estimators_starts_with_message(targets)
        self.check_model_trustworthy(targets)

    def check_model_trustworthy(self, targets):
        """
        Give some common values for tx and rx
        """
        log.info("Start check_model_trustworthy")
        for (bin_start, target, estimator) in itertools.product(self.bin_estimation["bins"],
                                                                targets, estimators):
            tx = self.bin_estimation[bin_start, target, estimator, "tx"]
            rx = self.bin_estimation[bin_start, target, estimator, "rx"]
            count = float(self.bin_message_data_count[bin_start, target, estimator])

            avg_size = mean(self.message_size[target])

            log.info("==========================================")
            log.info("Summary for node %d [%s] during bin %d" % (target, estimator, bin_start))
            try:
                log.info("Messages accounted: %d" % count)
                log.info("TX %f" % tx)
                log.info("RX %f" % rx)
                log.info("Average cost per message (tx): %f" % (tx / count))
                log.info("Average cost per message (rx): %f" % (rx / count))
                log.info("Average size of data message: %f" % avg_size)
                log.info("----")
                log.info("Modeled cost per message (tx, sender): %f" % self.tx_sender(avg_size))
                log.info("Modeled cost per message (rx, sender): %f" % self.rx_sender(avg_size))
                log.info("Modeled cost per message (tx, received): %f" % self.tx_receiver(avg_size))
                log.info("Modeled cost per message (rx, received): %f" % self.rx_receiver(avg_size))
            except ZeroDivisionError:
                log.warning("No message !!")
            log.info("==========================================")

    def check_estimators_starts_with_message(self, targets):
        """
        The goal of this check is to insure that we start
        providing estimations only when the first message
        hit us. No matter of the recalibration or not we shouldn't
        provide any estimation if we don't see anything.
        """
        log.info("starts check_estimators_starts_with_message")
        for (target, estimator) in itertools.product(targets, estimators):
            try:
                estimation_start = self.series_estimation[target, estimator, "time"][0]
                log.info("Estimation for node %d starts at %f" % (target, estimation_start))
            except IndexError as e:
                print("Problem for: %d, %d" % (target, estimator))
                raise e

    def check_estimator_order(self, targets):
        """
        The goal of this check is to ensure that:

        - noinfo is stricly inferior to route
        - noinfo is stricly inferior to radio
        """
        log.info("starts check_estimator_order")
        bins = sorted(self.bin_estimation["bins"])
        error_count = 0

        for (bin_start, target) in itertools.product(bins, targets):

            noinfo_tx = self.bin_estimation[bin_start, target, "noinfo", "tx"]
            noinfo_rx = self.bin_estimation[bin_start, target, "noinfo", "rx"]
            route_tx = self.bin_estimation[bin_start, target, "route", "tx"]
            route_rx = self.bin_estimation[bin_start, target, "route", "rx"]
            radio_tx = self.bin_estimation[bin_start, target, "radio", "tx"]
            radio_rx = self.bin_estimation[bin_start, target, "radio", "rx"]

            rx = self.diff_bin_powertracker(bin_start, target, "rx")
            tx = self.diff_bin_powertracker(bin_start, target, "tx")

            checks = {
                # Noinfo is the basis of all other estimators
                "noinfo_rx_lower_radio_tx": (noinfo_tx <= radio_tx),
                "noinfo_rx_lower_radio_rx": (noinfo_rx <= radio_rx),
                "noinfo_tx_lower_route_tx": (noinfo_tx <= route_tx),
                "noinfo_rx_lower_route_rx": (noinfo_rx <= route_rx),

                # Noinfo and route miss phenomenon
                "noinfo_tx_lower_tx": (noinfo_tx <= tx),
                "noinfo_rx_lower_rx": (noinfo_rx <= rx),
                "route_tx_lower_tx": (route_tx <= tx),
                "route_rx_lower_rx": (route_rx <= rx)
            }

            for name, check in checks.items():
                if not check:
                    error_count += 1
                    print("~~ WARNING check_estimator_order")
                    print("test: %s" % name)
                    print("target: %d" % target)
                    print("bin_start: %d" % bin_start)
                    print("noinfo_rx: %f noinfo_tx: %f" % (noinfo_rx, noinfo_tx))
                    print("route_rx: %f route_tx: %f" % (route_rx, route_tx))
                    print("radio_rx: %f radio_tx: %f" % (radio_rx, radio_tx))
                    print("rx: %f tx: %f" % (rx, tx))
                    print("~~")
        print("error_count: %d" % error_count)

    def save(self, targets):
        """

        We add global to print the aggregated results of each estimator
        """
        log.info("Save folder: %s" % self.folder)

        # TODO: Make an aggregated view

        for (target, estimator) in itertools.product(targets, estimators):

            # SERIES BY NODES

            path = pj(
                self.folder, "estimation", "series_estimation_%s_%s.csv" %
                (target, estimator))
            with open(path, "w") as f:
                print("Saving estimation to %s" % path)
                writer = DictWriter(f, ["time", "tx", "rx"])
                writer.writeheader()

                time_series = self.series_estimation[target, estimator, "time"]
                tx_series = self.series_estimation[target, estimator, "tx"]
                rx_series = self.series_estimation[target, estimator, "rx"]
                for time, tx, rx in zip(time_series, tx_series, rx_series):
                    writer.writerow({"tx": tx, "rx": rx, "time": time})

            # BINS BY NODES

            bin_path = pj(self.folder, "estimation",
                          "bin_estimation_%s_%s.csv" % (target, estimator))
            with open(bin_path, "w") as f:
                print("Saving estimation to %s" % bin_path)
                writer = DictWriter(f, bin_fieldnames)
                writer.writeheader()

                for bin_start in sorted(self.bin_estimation["bins"]):
                    tx = self.diff_bin_powertracker(bin_start, target, "tx")
                    rx = self.diff_bin_powertracker(bin_start, target, "rx")
                    tx_estimated = self.bin_estimation[bin_start, target, estimator, "tx"]
                    rx_estimated = self.bin_estimation[bin_start, target, estimator, "rx"]
                    writer.writerow({"bin_start": bin_start,
                                     "tx": tx, "rx": rx,
                                     "tx_estimated": tx_estimated,
                                     "rx_estimated": rx_estimated})

        # BINS GLOBAL

        for estimator in estimators:
            sum_bin_path = pj(self.folder, "estimation",
                              "bin_estimation_global_%s.csv" % estimator)

            log.info("Saving estimation to %s" % sum_bin_path)
            with open(sum_bin_path, "w") as f:
                writer = DictWriter(f, bin_fieldnames)
                writer.writeheader()

                for bin_start in sorted(self.bin_estimation["bins"]):

                    tx = sum(self.diff_bin_powertracker(bin_start, target, "tx")
                             for target in targets)
                    rx = sum(self.diff_bin_powertracker(bin_start, target, "rx")
                             for target in targets)
                    tx_estimated = sum(self.bin_estimation[bin_start, target,
                                                           estimator, "tx"]
                                       for target in targets)
                    rx_estimated = sum(self.bin_estimation[bin_start, target,
                                                           estimator, "rx"]
                                       for target in targets)

                    d = {"bin_start": bin_start, "tx": tx, "rx": rx,
                         "tx_estimated": tx_estimated,
                         "rx_estimated": rx_estimated}

                    writer.writerow(d)


def plot_bin(folder):
    """
    Will plot for every node side by side :
        - The amount of TX estimated and real
        - The amount of RX estimated and real
    """
    color = {"tx": "red", "rx": "blue",
             "tx_estimated": "magenta", "rx_estimated": "cyan"}
    hatch = {"tx": "\\", "tx_estimated": "\\\\",
             "rx": "/", "rx_estimated": "//"}

    width = BIN

    for file_name in os.listdir(pj(folder, "estimation")):
        if file_name.startswith("bin_estimation") and file_name.endswith("csv"):

            path = pj(folder, "estimation", file_name)
            output_path_png = path.replace(".csv", ".png")
            output_path_pdf = path.replace(".csv", ".pdf")
            kinds = ["tx", "tx_estimated", "rx", "rx_estimated"]
            label_first = {kind: True for kind in kinds}
            print(output_path_pdf)

            fig = plt.figure()
            ax = fig.add_subplot(111)

            with open(path) as f:
                reader = DictReader(f)
                for row in reader:
                    # We stack TX on top of RX for each bin
                    for key, value in row.items():
                        if value:
                            row[key] = float(value)
                        else:
                            row[key] = 0.0

                    # Real RX & TX

                    shifts = [0, 0.25, 0.5, 0.75]
                    for (kind, shift) in zip(kinds, shifts):
                        ax.bar(row["bin_start"] + shift * width,
                               row[kind],
                               # bottom=bottom_powertracker,
                               width=width / 4,
                               color=color[kind],
                               hatch=hatch[kind],
                               label=kind if label_first[kind] else "")
                        label_first[kind] = False

            ax.legend(ncol=2)
            ax.set_title("estimator %s" % file_name)
            ax.set_xlabel("Time [s]")
            ax.set_ylabel("Time [s]")
            if "global" in output_path_png:
                ax.set_ylim(0, 4)
            else:
                ax.set_ylim(0, 1)

            fig.savefig(output_path_png, format="png")
            fig.savefig(output_path_pdf, format="pdf")


def run(folder, reference):
    print("====================================================")
    print("Working with folder %s" % folder)
    messages_list = message(folder)
    e = Estimator(folder, reference)
    e.estimate(messages_list)

    # We verify only for the nodes
    targets = [node
               for node in e.targets
               if node not in e.excluded_nodes and node != e.root]
    e.check(targets)
    e.save(targets)

    plot_bin(folder)
    print("====================================================")


if __name__ == '__main__':
    reference = load_estimation("packet_size/calibration_contikimac.csv")
    folders = ["./chaine/chaine_high/",
                #"./chaine/chaine_high_calibration/",
                # "./chaine/chaine_medium/",
                # "./chaine/chaine_medium_calibration/",
                #"./chaine/chaine_low/",
                # "./chaine/chaine_low_calibration/",

                # "./fleur/fleur_high/",
                # "./fleur/fleur_high_calibration/",
                # "./fleur/fleur_medium/",
                # "./fleur/fleur_medium_calibration/",
                # "./fleur/fleur_low/",
                # "./fleur/fleur_low_calibration/",

                # "./arbre/arbre_high/",
                # "./arbre/arbre_high_calibration/",
                # "./arbre/arbre_medium/",
                # "./arbre/arbre_medium_calibration/",
                # "./arbre/arbre_low/",
                # "./arbre/arbre_low_calibration/",

                # "./arbre_overhearing/arbre_high/",
                # "./arbre_overhearing/arbre_high_calibration/",
                # "./arbre_overhearing/arbre_medium/",
                # "./arbre_overhearing/arbre_medium_calibration/",
                # "./arbre_overhearing/arbre_low/",
                # "./arbre_overhearing/arbre_low_calibration/"
    ]
    for folder in folders:
        # try:
        run(folder, reference)
        # except Exception as e:
        #     log.warning("An exception happened in %s" % str(e))
