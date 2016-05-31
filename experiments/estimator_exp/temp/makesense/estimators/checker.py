import pdb
from itertools import product
from numpy import mean
import logging

log = logging.getLogger("check estimators")


def check(e):
    check_estimator_order(e)
    # check_estimators_starts_with_message(estimator, target)
    # check_model_trustworthy(estimator, target)


# def check_model_trustworthy(estimator, target):
#     """
#     Give some common values for TX and RX
#     """
#     log.info("Start check_model_trustworthy")
#     for (bin_start, estimator) in product(self.bin_estimation["bins"], estimators):
#         tx = self.bin_estimation[bin_start, target, estimator, "tx"]
#         rx = self.bin_estimation[bin_start, target, estimator, "rx"]
#         count = float(
#             self.bin_message_data_count[bin_start, target, estimator])

#         avg_size = mean(self.message_size[target])

#         log.info("==========================================")
#         log.info("Summary for node %d [%s] during bin %d" % (
#             target, estimator, bin_start))
#         try:
#             log.info("Messages accounted: %d" % count)
#             log.info("TX %f" % tx)
#             log.info("RX %f" % rx)
#             log.info("Average cost per message (tx): %f" % (tx / count))
#             log.info("Average cost per message (rx): %f" % (rx / count))
#             log.info("Average size of data message: %f" % avg_size)
#             log.info("----")
#             log.info("Modeled cost per message (tx, sender): %f" % self.tx_sender(avg_size))
#             log.info("Modeled cost per message (rx, sender): %f" % self.rx_sender(avg_size))
#             log.info("Modeled cost per message (tx, received): %f" % self.tx_receiver(avg_size))
#             log.info("Modeled cost per message (rx, received): %f" % self.rx_receiver(avg_size))
#         except ZeroDivisionError:
#             log.warning("No message !!")
#         log.info("==========================================")


# def check_estimators_starts_with_message(self, target):
#     """
#     The goal of this check is to insure that we start
#     providing estimations only when the first message
#     hit us. No matter of the recalibration or not we shouldn't
#     provide any estimation if we don't see anything.
#     """
#     log.info("starts check_estimators_starts_with_message")
#     for estimator in estimators:
#         try:
#             estimation_start = self.series_estimation[target, estimator, "time"][0]
#             log.info("Estimation for node %d starts at %f" % (target, estimation_start))
#         except IndexError as e:
#             log.critical("Problem for: %d, %s" % (target, estimator))


def check_estimator_order(e):
    """
    The goal of this check is to ensure that:

    - noinfo is stricly inferior to route
    - noinfo is stricly inferior to radio
    """
    log.info("starts check_estimator_order")
    bins = sorted(e.bin_estimation["bins"])
    targets = e.targets.difference([1, "", None])
    error_count = 0
    threshold = 0

    for target, bin_start in product(targets, bins):

        noinfo_tx = e.bin_estimation[bin_start, target, "noinfo", "tx"]
        noinfo_rx = e.bin_estimation[bin_start, target, "noinfo", "rx"]
        route_tx = e.bin_estimation[bin_start, target, "route", "tx"]
        route_rx = e.bin_estimation[bin_start, target, "route", "rx"]
        # radio_tx = e.bin_estimation[bin_start, target, "radio", "tx"]
        # radio_rx = e.bin_estimation[bin_start, target, "radio", "rx"]

        rx = e.diff_bin_powertracker(bin_start, target, "rx")
        tx = e.diff_bin_powertracker(bin_start, target, "tx")

        checks = {
            # Noinfo is the basis of all other estimators
            "noinfo_tx_lower_route_tx": (route_tx - noinfo_tx > threshold),
            "noinfo_rx_lower_route_rx": (route_rx - noinfo_rx > threshold),

            # Noinfo and route miss phenomenon
            "noinfo_tx_lower_tx": (tx - noinfo_tx > threshold),
            "noinfo_rx_lower_rx": (rx - noinfo_rx > threshold),
            "route_tx_lower_tx": (tx - route_tx > threshold),
            "route_rx_lower_rx": (rx - route_rx > threshold)
        }

        for name, check in checks.items():
            if not check:
                error_count += 1
                print("~~ WARNING check_estimator_order")
                print("test: %s" % name)
                print("target: %s" % target)
                print("bin_start: %s" % bin_start)
                print("noinfo_rx: %f noinfo_tx: %f" %
                      (noinfo_rx, noinfo_tx))
                print("route_rx: %f route_tx: %f" % (route_rx, route_tx))
                # print("radio_rx: %f radio_tx: %f" % (radio_rx, radio_tx))
                print("rx: %f tx: %f" % (rx, tx))
                print("~~")
    print("error_count: %d" % error_count)
