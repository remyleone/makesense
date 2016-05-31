#!/usr/bin/env python
# -*- coding: utf-8 -*-

from itertools import product
import pdb
from collections import defaultdict, namedtuple
from csv import DictReader, DictWriter
from os.path import join as pj
from pandas import DataFrame
from scipy.interpolate import interp1d
import itertools
import logging
import networkx as nx
import numpy as np
import os
import pandas as pd

logging.basicConfig(level=logging.INFO)

handler = logging.FileHandler('hello.log')
handler.setLevel(logging.INFO)
log = logging.getLogger("estimators")
log.addHandler(handler)


# Time required to send a 802.15.4 ACK packet
ack_time = 352 * 10 ** -6

# Amount of time that a node have to repeat in average the sending of a message
# while running Contiki MAC
repeat_sender = 3.76

# Amount of time that a node have to stay
repeat_receiver = 1.5

# RATE of information
RATE = 250000.0

# Time at which we start to estimate the traffic
#SHIFT = 35.451328
SHIFT = 0

# Temporal BIN
BIN = 25

# Considered estimators
estimators = ["noinfo", "route"]

kinds = ["tx", "rx"]

# root node
root = 1

bin_fieldnames = ["bin_start",
                  "tx", "tx_estimated", "tx_outcast",
                  "rx", "rx_estimated", "rx_outcast",
                  "time_explained", "mac_time"]

# Broadcast cost
dis_packet = 39.0 * 47.0 / RATE
dio_packet = 30.0 * 80.0 / RATE

fieldnames = ["time", "mote_id", "node", "strobes",
              "message_type", "message", "tx", "rx", "size"]


message_t = namedtuple("Message", fieldnames)
message_t.__new__.__defaults__ = tuple(len(fieldnames) * [None])


class Estimator(object):

    """
    General Estimator Workflow.
    """

    def frame_size(self, size):
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

    def __init__(self, folder):

        # logging.basicConfig(filename=pj(folder, "estimator.log"),
        #                     filemode="w", level=logging.DEBUG)

        # GENERAL SETTINGS

        self.folder = folder
        self.recalibration = True

        # GRAPH SETTINGS

        if "route" in estimators:
            self.route_path = {}

            # All routes are unique.
            self.rpl_graph = nx.DiGraph()
            self.root = 1
            self.rpl_graph.add_node(self.root)

            # This determined when all routes are known by the estimators
            self.all_route_known = False

        if "radio" in estimators:
            # Each node got a several neighbors

            # We use the route stored in self.route_path, for each node in the path
            # minus the final destination, we compute all the neighbors of a node.
            # This nodes will be the one over hearing when a transmission occurs.

            self.radio_graph = nx.Graph()
            self.radio_path = {}

        # Packet loss
        self.sending = defaultdict(list)
        self.reception = defaultdict(list)

        # REFERENCE SETTINGS

        # API: payload => time_spent_with_radio_on

        self.tx_sender = lambda x: repeat_sender * 8.0 * self.frame_size(x) / RATE
        self.rx_sender = lambda x: ack_time
        self.tx_receiver = lambda x: ack_time
        self.rx_receiver = lambda x: repeat_receiver * 8.0 * self.frame_size(x) / RATE

        # ESTIMATION SETTINGS

        # root is supposed non energy constrained therefore we are not
        # interested
        # 0 is the information when a parent is missing
        self.targets = set()

        # Count how much message an estimator see by bins
        # bin_start, node, estimator -> count
        self.bin_message_data_count = defaultdict(float)
        self.bin_rpl_count = defaultdict(float)

        self.estimated_costs = defaultdict(pd.DataFrame)

        self.estimation = defaultdict(pd.DataFrame)

        # target, estimator, kind -> value
        # self.total_estimation = defaultdict(float)

        # {target, estimator, time: [...], target, estimator, tx: [...]}
        # self.series_estimation = defaultdict(list)

        # bin_start, target, estimator, kind -> value
        # self.bin_estimation = defaultdict(float)
        # self.bin_estimation["bins"] = set()

        self.message_size = defaultdict(list)

        # bin_start, current_node => value
        self.bin_total_time = defaultdict(float)
        self.bin_total_time["bins"] = set()

        # bin_start, current_node, estimator
        self.bin_explained_time = defaultdict(float)
        self.bin_explained_time["bins"] = set()

        self.mac_time = defaultdict(list)

        if self.recalibration:

            # alpha * cost(message)
            # + (1 - alpha) (diff_E / diff_T) (current_time - last_recalibration_time)
            self.alpha = 0.25

            # target, estimator, kind => [values]
            # Used for estimators performance
            self.recalibration_record = defaultdict(pd.DataFrame)

        # Series of MAC values
        self.series_mac = defaultdict(list)

        # Series of powertracker values
        self.series_powertracker = defaultdict(list)

        # Store the last value of powertracker
        # target, kind => Value
        self.last_powertracker = defaultdict(float)

        self.messages_list = list()

        # bin_start, node, kind -> value
        self.bin_powertracker = defaultdict(float)
        self.bin_powertracker["bins"] = set()

        # We compute the powertracker interpolation here
        self.powertracker_inter = {}
        df = pd.read_csv(pj(folder, "results", "powertracker.csv"))

        # Sender
        for mote in set(df.mote_id):
            records_df = df[df.mote_id == mote]
            self.powertracker_inter[mote, "tx"] = interp1d(records_df.monitored_time,
                                                           records_df.tx_time,
                                                           bounds_error=False,
                                                           fill_value=0.0)
            self.powertracker_inter[mote, "rx"] = interp1d(records_df.monitored_time,
                                                           records_df.rx_time,
                                                           bounds_error=False,
                                                           fill_value=0.0)

        self.load_messages()

    def load_messages(self):
        with open(pj(self.folder, "results", "messages.csv")) as f:
            reader = DictReader(f)
            for row in reader:
                for key in ["time", "tx", "rx"]:
                    if row[key]:
                        row[key] = float(row[key])
                for key in ["mote_id", "node", "strobes", "size"]:
                    if row[key]:
                        row[key] = int(row[key])
                self.messages_list.append(message_t(**row))

    def refresh_route(self):
        """
        Refresh routing and radio table
        """
        if "route" in estimators:
            self.connected_to_gateway = {n for n in self.rpl_graph.nodes()
                                         if self.rpl_graph.has_edge(n, self.root)}
            self.route_path = {n: nx.shortest_path(self.rpl_graph, n, self.root)
                               for n in self.rpl_graph.nodes()
                               if nx.has_path(self.rpl_graph, n, self.root)}

        if "radio" in estimators:
            self.radio_path = {n: list(itertools.chain(*[self.radio_graph.neighbors(n_)
                                                         for n_ in self.route_path[n][:-1]]))
                               for n in self.route_path}

    def noinfo_estimation(self, message):
        """
        Simply account for node and destination
        :param message:
        """
        bin_start = BIN * int(message.time / BIN)
        self.bin_message_data_count[
            bin_start, message.node, "noinfo"] += 1
        node = message.node
        size = message.size

        transaction = defaultdict(float)
        if node in self.connected_to_gateway:
            tx = 8.0 * self.frame_size(size) / RATE
            transaction[node, "tx"] += tx
            self.bin_explained_time[bin_start, node, "noinfo"] += tx
            transaction[node, "rx"] += ack_time
        else:
            transaction[node, "tx"] += self.tx_sender(size)
            transaction[node, "rx"] += ack_time
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
        raw_tx = 8.0 * self.frame_size(size) / RATE

        transaction = defaultdict(float)
        if node in self.connected_to_gateway:
            transaction[node, "tx"] += raw_tx
            self.bin_explained_time[bin_start, node, "route"] += raw_tx
            transaction[node, "rx"] += ack_time
        else:
            transaction[node, "tx"] += self.tx_sender(size)
            transaction[node, "rx"] += ack_time

            # Forwarders of the message
            try:
                forwarders = self.route_path[node]
                for forwarder in forwarders[1: -1]:
                    self.bin_message_data_count[bin_start, forwarder, "route"] += 1
                    if forwarder in self.connected_to_gateway:
                        transaction[forwarder, "tx"] += raw_tx
                        self.bin_explained_time[bin_start, forwarder, "route"] += raw_tx
                        transaction[forwarder, "rx"] += ack_time
                    else:
                        transaction[forwarder, "tx"] += self.tx_sender(size) + ack_time
                        transaction[forwarder, "rx"] += self.rx_receiver(size) + ack_time
            except KeyError as error:
                log.warning("No route in route_estimation for node %s" % error)
                log.info(self.route_path)
        return transaction

    def update_estimator(self, estimator, target, tx=0.0, rx=0.0, time=None):
        """
        Adding up an increment to an estimator
        """
        if tx or rx:
            estimated_tx = self.total_estimation[target, estimator, "tx"] + tx
            estimated_rx = self.total_estimation[target, estimator, "rx"] + rx

            self.series_estimation[target, estimator, "time"].append(time)
            self.series_estimation[target, estimator, "tx"].append(estimated_tx)
            self.series_estimation[target, estimator, "rx"].append(estimated_rx)

            # Adding to the bin version
            bin_start = BIN * int(time / BIN)
            self.bin_estimation["bins"].add(bin_start)

            self.bin_estimation[bin_start, target, estimator, "tx"] += tx
            self.bin_estimation[bin_start, target, estimator, "rx"] += rx

    def current_cost(self, target, estimator, kind):
        if self.estimated_costs[target].empty:
            return 0.0
        else:
            return self.estimated_costs[target]["%s_%s" % (kind, estimator)].sum()

    def last_recalibration_time(self, target):
        if self.recalibration_record[target].empty:
            record = pd.DataFrame({"time": 0.0, "real_rx": 0.0, "real_tx": 0.0,
                                   "estimation_tx_noinfo": 0.0, "estimation_rx_noinfo": 0.0,
                                   "estimation_tx_route": 0.0, "estimation_rx_route": 0.0,
                                   "coef_tx": 0.0, "coef_rx": 0.0
                                   }, index=["time"])
            self.recalibration_record[target] = self.recalibration_record[target].append(record)
            return 0.0
        else:
            return self.recalibration_record[target].tail(1).time

    def coef_correction(self, target, kind):
        if self.recalibration_record[target].empty:
            return 0.0
        else:
            return self.recalibration_record[target].tail(1)["coef_%s" % kind]

    def compute_estimation(self, target, kind, estimator, time):
        # Compute an estimation taking only in account estimated cost
        current_cost = self.current_cost(target, estimator, kind)
        last_coef = self.coef_correction(target, kind)
        last_recalibration_time = self.last_recalibration_time(target)
        last_powertracker = self.powertracker_inter[target, kind](last_recalibration_time)
        current_estimation = last_powertracker + self.alpha * current_cost

        # Affect a correction
        correction = (1 - self.alpha) * last_coef * (time - self.last_recalibration_time(target))
        current_estimation += correction
        current_powertracker = last_powertracker = self.powertracker_inter[target, kind](time)
        res = {
            "kind": kind, "estimator": estimator, "time": time,
            "estimation": current_estimation, "reality": current_powertracker
        }
        record = pd.DataFrame(res, index=["time"])
        self.estimation[target] = self.estimation[target].append(record)
        return current_estimation

    def _handle_battery_recalibration_message(self, message, *args, **kwargs):
        """
        We assume that the target send us through a notification
        the amount of time that the target spent in TX and in RX
        """
        if self.recalibration:
            target = message.node
            current_time = message.time
            last_recalibration_time = self.last_recalibration_time(target)

            recalibration_record = {"time": message.time}

            for kind in kinds:
                last_powertracker = self.powertracker_inter[target, kind](last_recalibration_time)
                current_powertracker = self.powertracker_inter[target, kind](current_time)
                recalibration_record["real_%s" % (kind)] = current_powertracker

                delta_real = current_powertracker - last_powertracker
                delta_time = current_time - last_recalibration_time
                
                for estimator in estimators:

                    current_estimation = self.compute_estimation(target, kind,
                                                                 estimator, current_time)
                    recalibration_record["estimation_%s_%s" % (kind, estimator)] = current_estimation

                    # Real differences for estimator corrections
                    diff = current_powertracker - current_estimation
                    recalibration_record["diff_%s_%s" % (kind, estimator)] = diff

                    # Error
                    error = (current_powertracker - current_estimation) / delta_real
                    recalibration_record["error_%s_%s" % (kind, estimator)] = error

                recalibration_record["coef_%s" % (kind)] = delta_real / delta_time
            record = pd.DataFrame(recalibration_record, index=["time"])
            self.recalibration_record[target] = self.recalibration_record[target].append(record)
            self.recalibration_record["global"] = self.recalibration_record["global"].append(record)
            # for target, kind, estimator in product(self.targets, kinds, estimators):
            #     self.compute_estimation(target, kind, estimator, current_t)

    def _handle_forwarding_message(self, message, *args, **kwargs):
        log.debug("Handle forwarding message")
        current_node = message.node
        current_t = message.time
        bin_start = BIN * int(current_t / BIN)
        self.bin_explained_time["bins"].add(bin_start)
        self.bin_explained_time[bin_start, current_node, "route"] += 8.0 * self.frame_size(10) / RATE

    def _handle_energy_message(self, message, *args, **kwargs):
        """
        Handle the message from powertracker
        """
        # log.debug("Handle energy message")
        current_node = message.node
        current_t = message.time
        bin_start = BIN * int(current_t / BIN)

        self.series_powertracker[current_node, "tx"].append(message.tx)
        self.series_powertracker[current_node, "rx"].append(message.rx)
        self.series_powertracker[current_node, "time"].append(current_t)

        self.bin_powertracker[bin_start, current_node, "tx"] = message.tx
        self.bin_powertracker[bin_start, current_node, "rx"] = message.rx
        self.bin_powertracker["bins"].add(bin_start)

        self.last_powertracker[current_node, "tx"] = message.tx
        self.last_powertracker[current_node, "rx"] = message.rx

    def _handle_mac_message(self, message, *args, **kwargs):
        log.debug("Handle MAC message")
        node = message.node
        current_t = message.time
        bin_start = BIN * int(current_t / BIN)
        self.bin_total_time["bins"].add(bin_start)
        tx = (message.strobes + 1) * (8.0 * message.size) / RATE

        self.mac_time[node].append({"time": current_t,
                                    "mac_tx": (message.strobes + 1) * (8.0 * message.size) / RATE,
                                    "strobes": message.strobes + 1,
                                    "size": message.size})

        self.bin_total_time[bin_start, node] += tx
        self.series_mac[node, "tx"].append(current_t)
        self.series_mac[node, "time"].append(tx)

        # DIRTY HACK (DAO are probably 53 bytes long)
        if message.size == 53:
            self._handle_dao_message(message)

    def _handle_udp_reception_message(self, current_message, *args, **kwargs):
        log.debug("Handle udp_reception message")
        node = current_message.node
        current_t = current_message.time
        self.message_size[node].append(current_message.size)

        self.reception[node].append({"time": current_t,
                                     "message": current_message.message})

        if self.all_route_known:

            transactions = {
                "noinfo": self.noinfo_estimation(current_message),
                "route": self.route_estimation(current_message)
            }

            for target in self.targets:
                cost = {
                    "tx_noinfo": transactions["noinfo"][target, "tx"],
                    "rx_noinfo": transactions["noinfo"][target, "rx"],
                    "tx_route": transactions["route"][target, "tx"],
                    "rx_route": transactions["route"][target, "rx"]
                }

                if any(cost.values()):
                    cost["time"] = current_t
                    c = pd.DataFrame(cost, index=["time"])
                    self.estimated_costs[node] = self.estimated_costs[node].append(c)

                # for (kind, estimator) in product(kinds, estimators):
                #     self.compute_estimation(target, kind, estimator, current_t)
        else:
            log.info("Missing route at %f" % current_t)
            log.info(self.route_path)

    def _handle_udp_sending_message(self, message, *args, **kwargs):
        log.debug("Handle udp_sending message")
        node = message.node
        current_t = message.time

        self.sending[node].append({"time": current_t, "message": message.message})

    def _handle_dis_message(self, message, *args, **kwargs):
        log.debug("Handle DIS message")
        node = message.node
        current_t = message.time
        bin_start = BIN * int(current_t / BIN)
        self.bin_rpl_count[bin_start, node] += 1

        self.mac_time[node].append({"time": current_t,
                                    "dis_tx": 8.0 * 39.0 * 47.0 / RATE})

    def _handle_dao_message(self, message, *args, **kwargs):
        log.debug("Handle DAO message")
        node = message.node
        current_t = message.time
        bin_start = BIN * int(current_t / BIN)
        self.bin_rpl_count[bin_start, node] += 1

        # HACK
        message_strobes = 3
        message_size = 53
        self.mac_time[node].append({"time": current_t,
                                    "dao_tx": (message_strobes + 1) * (8.0 * message_size) / RATE})

    def _handle_dio_message(self, current_message, *args, **kwargs):
        log.debug("Handle DIO message")
        node = current_message.node
        current_t = current_message.time
        bin_start = BIN * int(current_t / BIN)
        self.bin_rpl_count[bin_start, node] += 1

        self.mac_time[node].append({"time": current_t,
                                    "dio_tx": 8.0 * 30.0 * 80.0 / RATE})

    def _handle_neighbor_message(self, current_message, *args, **kwargs):
        """
        Build up the radio representation at the gateway
        """
        if "radio" in estimators:
            neighbor = current_message.node
            node = current_message.mote_id
            self.radio_graph.add_edge(node, neighbor)
            self.refresh_route()

    def _handle_parent_message(self, current_message, *args, **kwargs):
        """
        Build up the RPL representation at the gateway
        """
        parent = current_message.node
        node = current_message.mote_id
        if parent:
            if "route" in estimators:
                self.rpl_graph.add_edge(node, parent)
            # if "radio" in estimators:
            #     self.radio_graph.add_edge(node, parent)
            self.refresh_route()

            # Condition to know of all routes are known
            if "route" in estimators:
                diff = set(self.rpl_graph.nodes()) - self.targets - {self.root}
                if diff:
                    log.info("Missing route at %f for %s" % (current_message.time, diff))
                    self.all_route_known = False
                else:
                    log.info("All route known at %f" % current_message.time)
                    self.all_route_known = True

    def _handle_generic_message(self, current_message, *args, **kwargs):
        """
        # Estimation are correlated through nodes and through time
        # Therefore we need to encapsulate any piece of information into
        # an atomic message that will be interpreted
        # by different estimator
        """
        for handler in dir(self):
            if handler.startswith("handle"):
                print(handler)
        raise RuntimeError('No {} method'.format(
            'handle_%s_message' % current_message.message_type))

    def _handle_overhearing_message(self, current_message, *args, **kwargs):
        pass

    def estimate(self):
        """
        Estimation occurs here

        BEWARE ALL MESSAGES NEEDS TO BE SORTED BY TIME !!!
        """
        for message in self.messages_list:
            for key in ["node", "mote_id"]:
                if getattr(message, key) and getattr(message, key) != self.root:
                    self.targets.add(getattr(message, key))
            method_name = "_handle_%s_message" % message.message_type
            handler = getattr(self, method_name, self._handle_generic_message)
            handler(message)

        # We create all the DataFrame here
        print(self.targets)
        # self.df = {node: DataFrame({"time": self.series_estimation[node, "route", "time"],

        #                             "tx_route": self.series_estimation[node, "route", "tx"],
        #                             "tx_route_cumsum": np.cumsum(self.series_estimation[node, "route", "tx"]),

        #                             "rx_route": self.series_estimation[node, "route", "rx"],
        #                             "rx_route_cumsum": np.cumsum(self.series_estimation[node, "route", "rx"]),

        #                             "tx_noinfo": self.series_estimation[node, "noinfo", "tx"],
        #                             "tx_noinfo_cumsum": np.cumsum(self.series_estimation[node, "noinfo", "tx"]),

        #                             "rx_noinfo": self.series_estimation[node, "noinfo", "rx"],
        #                             "rx_noinfo_cumsum": np.cumsum(self.series_estimation[node, "noinfo", "rx"])},
        #                            columns=["time", "tx_noinfo", "rx_noinfo",
        #                                     "tx_route", "rx_route",
        #                                     "tx_noinfo_cumsum", "rx_noinfo_cumsum",
        #                                     "tx_route_cumsum", "rx_route_cumsum"])
        #            for node in range(2, 8)}

        # for node in self.targets:
        #     bin_start = BIN * (self.df[node].time // BIN)
        #     self.df[node]["bin_start"] = bin_start
        #     self.df[node].to_csv(pj(self.folder, "pandas_%s.csv" % node), index=False)

            # pdb.set_trace()
            # grouped = self.df[node].groupby("bin_start")
            # pdb.set_trace()
            # values = {}
            # for name, group in grouped:
            #     print(name)
            #     a = group["tx"].max() - group["tx"].min()
            #     values[name] = a

    def diff_bin_powertracker(self, bin_start, target, kind):
        return self.bin_powertracker[bin_start, target, kind] - self.bin_powertracker[bin_start - BIN, target, kind]

    def diff_bin_estimator(self, bin_start, target, estimator, kind):
        return self.bin_estimator[bin_start, target, estimator, "tx"] - self.bin_estimator[bin_start - BIN, target, estimator, "tx"]

    # def save_series(self):
    #     """
    #     Save the series of estimation
    #     """
    #     for estimator, target in product(estimators, self.targets):

    #         path = pj(
    #             self.folder, "results", "estimation", "series_estimation_%s_%s.csv" %
    #             (target, estimator))
    #         with open(path, "w") as f:
    #             print("Saving estimation to %s" % path)
    #             writer = DictWriter(f, ["time", "tx", "rx"])
    #             writer.writeheader()

    #             time_series = self.series_estimation[target, estimator, "time"]
    #             tx_series = self.series_estimation[target, estimator, "tx"]
    #             rx_series = self.series_estimation[target, estimator, "rx"]
    #             for time, tx, rx in zip(time_series, tx_series, rx_series):
    #                 writer.writerow({"tx": tx, "rx": rx, "time": time})

    # def save_bin(self):
    #     for estimator, target in product(estimators, self.targets):

    #         bin_path = pj(self.folder, "results", "estimation",
    #                       "bin_estimation_%s_%s.csv" % (target, estimator))
    #         with open(bin_path, "w") as f:
    #             print("Saving estimation to %s" % bin_path)
    #             writer = DictWriter(f, bin_fieldnames)
    #             writer.writeheader()

    #             for bin_start in sorted(self.bin_estimation["bins"]):
    #                 tx = self.diff_bin_powertracker(bin_start, target, "tx")
    #                 rx = self.diff_bin_powertracker(bin_start, target, "rx")
    #                 tx_estimated = self.bin_estimation[
    #                     bin_start, target, estimator, "tx"]
    #                 rx_estimated = self.bin_estimation[
    #                     bin_start, target, estimator, "rx"]
    #                 writer.writerow({"bin_start": bin_start,
    #                                  "tx": tx, "rx": rx,
    #                                  "tx_estimated": tx_estimated,
    #                                  "rx_estimated": rx_estimated,
    #                                  "mac_time": self.bin_total_time[bin_start, target],
    #                                  "time_explained": self.bin_explained_time[bin_start,
    #                                                                            target,
    #                                                                            estimator]
    #                                  })

    def save_cost(self):
        for target in self.targets:
            cost_df = pd.DataFrame(self.estimated_costs[target])
            cost_df.set_index("time", inplace=True)
            path = pj(self.folder, "results", "estimation", "cost_%d.csv" % target)

            cost_df.to_csv(path)
            # cost_df["bin_start"] = BIN * (cost_df.time // BIN)

    def save_mac(self):
        for target in self.targets:
            mac_df = pd.DataFrame(self.mac_time[target])

            path = pj(self.folder, "results", "mac", "series_mac_%d.csv" % target)
            mac_df.to_csv(path, index=False)

            mac_df["bin_start"] = BIN * (mac_df.time // BIN)
            bin_mac = mac_df.groupby("bin_start").sum()[["dao_tx", "dio_tx", 'dis_tx', 'mac_tx']]
            bin_mac["ratio_dao"] = bin_mac.dao_tx / bin_mac.mac_tx
            bin_mac["ratio_dis"] = bin_mac.dis_tx / bin_mac.mac_tx
            bin_mac["ratio_dio"] = bin_mac.dio_tx / bin_mac.mac_tx

            path = pj(self.folder, "results", "mac", "bin_mac_%d.csv" % target)
            bin_mac.to_csv(path)

    def save_pdr(self):
        for target in self.targets:
            path = pj(self.folder, "results", "pdr", "pdr_%d.csv" % target)
            log.info(path)

            df_sending = pd.DataFrame(self.sending[target])
            df_sending.rename(columns={"time": "departure_time"}, inplace=True)

            df_reception = pd.DataFrame(self.reception[target])
            df_reception.rename(columns={"time": "arrival_time"}, inplace=True)

            res = pd.merge(df_reception, df_sending, on="message", how="outer").sort("message")

            res[["message", "departure_time", "arrival_time"]].to_csv(path, index=False)

    # def save_repartition_protocol(self):
    #     for estimator, target in product(estimators, self.targets):
    #         # Repartition protocol
    #         bin_path = pj(self.folder, "results", "protocol_estimation", "protocol_estimation_%s_%s.csv" % (target, estimator))
    #         protocol_fieldnames = ["bin_start", "rpl", "udp"]
    #         with open(bin_path, "w") as f:
    #             print("Saving protocol repartition to %s" % bin_path)
    #             writer = DictWriter(f, protocol_fieldnames)
    #             writer.writeheader()

    #             for bin_start in sorted(self.bin_estimation["bins"]):
    #                 rpl = self.bin_rpl_count[bin_start, target]
    #                 udp = self.bin_message_data_count[bin_start, target, estimator]
    #                 writer.writerow({"bin_start": bin_start, "rpl": rpl, "udp": udp})

    def save_recalibration(self):
        if self.recalibration:
            for target in self.targets:
                df = pd.DataFrame(self.recalibration_record[target])
                df["bin_start"] = BIN * (df.time // BIN)
                df.to_csv(pj(self.folder, "results", "estimation", "recalibration_%d.csv" % target), index=False)
            df = pd.DataFrame(self.recalibration_record["global"])
            df["bin_start"] = BIN * (df.time // BIN)
            df.to_csv(pj(self.folder, "results", "estimation", "recalibration_global.csv"), index=False)

    def save_powertracker(self):
        for target in self.targets:

            path = pj(self.folder, "results", "powertracker",
                      "series_powertracker_%d.csv" % target)
            with open(path, "w") as f:
                print("Saving estimation to %s" % path)
                writer = DictWriter(f, ["time", "tx", "rx"])
                writer.writeheader()

                times_series = self.series_powertracker[target, "time"]
                tx_series = self.series_powertracker[target, "tx"]
                rx_series = self.series_powertracker[target, "rx"]
                for time, tx, rx in zip(times_series, tx_series, rx_series):
                    writer.writerow({"tx": tx, "rx": rx, "time": time})

    def save_depth(self):
        res = {target: len(self.route_path[target]) - 1
               for target in self.targets}
        df = pd.DataFrame(list(res.items()), columns=["node", "depth"])
        df.to_csv(pj(self.folder, "results", "depth.csv"), index=False)

    def save_estimation(self):
        def _last_recalibration(self, target, x):
            df = self.recalibration_record[target]
            return max(df[df.time < x].time)

        def _last_coef(self, target, kind, x):
            df = self.recalibration_record[target]
            return float(df[df.time < x].tail(1)["coef_%s" % kind])
            
        for target in self.targets:
            df = pd.DataFrame(self.estimated_costs[target])
            df["last_recalibration_time"] = df.time.apply(lambda x: _last_recalibration(self, target, x))

            # At least the value at the last recalibration
            df["estimation_tx_route"] = self.powertracker_inter[target, "tx"](df["last_recalibration_time"])
            df["estimation_tx_noinfo"] = self.powertracker_inter[target, "tx"](df["last_recalibration_time"])
            df["estimation_rx_route"] = self.powertracker_inter[target, "rx"](df["last_recalibration_time"])
            df["estimation_rx_noinfo"] = self.powertracker_inter[target, "rx"](df["last_recalibration_time"])

            # Adding the cost we noticed
            df["estimation_tx_route"] += self.alpha * df.groupby("last_recalibration_time").cumsum()["tx_route"]
            df["estimation_tx_noinfo"] += self.alpha * df.groupby("last_recalibration_time").cumsum()["tx_noinfo"]
            df["estimation_rx_route"] += self.alpha * df.groupby("last_recalibration_time").cumsum()["rx_route"]
            df["estimation_rx_noinfo"] += self.alpha * df.groupby("last_recalibration_time").cumsum()["rx_noinfo"]

            # Adding the correction
            df["time_since_last_recalibration"] = df.time - df.last_recalibration_time
            df["last_coef_tx"] = df.time.apply(lambda x: _last_coef(self, target, "tx", x))
            df["last_coef_rx"] = df.time.apply(lambda x: _last_coef(self, target, "rx", x))

            df["estimation_tx_route"] += (1 - self.alpha) * df["last_coef_tx"] * df["time_since_last_recalibration"]
            df["estimation_tx_noinfo"] += (1 - self.alpha) * df["last_coef_tx"] * df["time_since_last_recalibration"]
            df["estimation_rx_route"] += (1 - self.alpha) * df["last_coef_rx"] * df["time_since_last_recalibration"]
            df["estimation_rx_noinfo"] += (1 - self.alpha) * df["last_coef_rx"] * df["time_since_last_recalibration"]

            df["tx"] = self.powertracker_inter[target, "tx"](df["time"])
            df["rx"] = self.powertracker_inter[target, "rx"](df["time"])

            df.set_index("time", inplace=True)
            df.to_csv(pj(self.folder, "results", "estimation", "estimation_%d.csv" % target))

    def save(self):
        """

        We add global to print the aggregated results of each estimator
        """
        log.info("Save folder: %s" % self.folder)

        # TODO: Make an aggregated view

        folders = [
            pj(self.folder, "results"),
            pj(self.folder, "results", "estimation"),
            pj(self.folder, "results", "pdr"),
            pj(self.folder, "results", "mac"),
            pj(self.folder, "results", "protocol_estimation"),
            pj(self.folder, "results", "powertracker"),
            pj(self.folder, "results", "strobes")
        ]
        for folder in folders:
            if not os.path.exists(folder):
                os.makedirs(folder)
        
        # self.save_bin()
        self.save_estimation()
        self.save_cost()
        self.save_depth()
        self.save_mac()
        self.save_pdr()
        self.save_powertracker()
        self.save_recalibration()
        # self.save_repartition_protocol()
        # self.save_series()

    def save_global(self):
        """
        BINS GLOBAL
        """
        for estimator in estimators:
            sum_bin_path = pj(self.folder, "results", "estimation",
                              "bin_estimation_global_%s.csv" % estimator)

            log.info("Saving estimation to %s" % sum_bin_path)
            with open(sum_bin_path, "w") as f:
                writer = DictWriter(f, bin_fieldnames)
                writer.writeheader()

                for bin_start in sorted(self.bin_estimation["bins"]):

                    tx = sum(self.diff_bin_powertracker(bin_start, target, "tx")
                             for target in self.targets)
                    rx = sum(self.diff_bin_powertracker(bin_start, target, "rx")
                             for target in self.targets)
                    tx_estimated = sum(self.bin_estimation[bin_start, target,
                                                           estimator, "tx"]
                                       for target in self.targets)
                    rx_estimated = sum(self.bin_estimation[bin_start, target,
                                                           estimator, "rx"]
                                       for target in self.targets)

                    d = {"bin_start": bin_start, "tx": tx, "rx": rx,
                         "tx_estimated": tx_estimated,
                         "rx_estimated": rx_estimated}

                    writer.writerow(d)
