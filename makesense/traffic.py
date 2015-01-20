# coding: utf-8

"""
Generating traffic for different protocols and application
"""

import itertools
import json
import logging
import random
import re
import subprocess
import time
import urlparse

from .settings import COAP_CLIENT


FORMAT = '%(asctime)s [%(name)s] %(message)s'
logging.basicConfig(format=FORMAT, level=logging.INFO)


class Traffic:
    """
    Traffic type generator for CoAP traffic, ICMPv6 traffic
    """

    def __init__(self, protocol=None, destinations=None, count=1, output_file=None,
                 timeout=1, interface="tun0"):
        """
        Set up a traffic type
        :param protocol:
        :param destinations:
        :param count:
        :param output_file:
        :param timeout:
        :param interface:
        """

        # CoAP, ping and HTTP supported
        if protocol not in ["coap", "ping", "http"]:
            raise Exception("Protocol not recognized")
        else:
            self.protocol = protocol

        # list of the targets that will be fetched
        if not destinations:
            raise Exception("No targets")
        else:
            self.destinations = destinations

        # Output file where to log the traffic
        if output_file:
            self.output_file = output_file

        self.timeout = timeout
        self.count = count
        self.interface = interface
        self.settings = None

    def __str__(self):
        """
        JSON representation
        :rtype : string
        """
        return json.dumps(
            {'protocol': self.protocol, 'destinations': self.destinations}
        )

    # Protocol specific

    def coap(self):
        """
        Generate a CoAP traffic towards a precise node
        """
        log = logging.getLogger("coap")
        paths = self.settings.get("coap_path", ["/.well-known/core"])
        destinations = self.destinations

        for coap_path, destination in itertools.product(paths, destinations):
            command = [COAP_CLIENT]
            url = "coap://[%s]%s" % (destination, coap_path)
            command.append(url)
            log.info(str(command))
            self.output_file.write("%s\n" % command)
            subprocess.Popen(command, stdout=self.output_file)

    def http(self):
        """
        Generate HTTP traffic towards a precise node
        """
        log = logging.getLogger("http")
        command = ["curl", "-g"]
        path = self.settings.get("http_path", "/")
        destination = random.choice(self.destinations)
        url = "http://[%s]%s" % (destination, path)
        log.info(url)
        command.append(url)
        subprocess.Popen(command, stdout=self.output_file)

    def ping(self):
        """
        Generate ping traffic towards a precise node
        """
        log = logging.getLogger("ping")

        def _get_match_groups(ping_output, regex):
            """
            Get match groups
            """
            match = regex.search(ping_output)
            if not match:
                raise ValueError
            return match.groups()

        def parse(ping_output, target):
            """
            Parses the `ping_output` string into a dictionary containing the
            following fields:

            `host`: *string*; the target host name that was pinged
            `sent`: *int*; the number of ping request packets sent
            `received`: *int*; the number of ping reply packets received
            `min_ping`: *float*; the minimum (fastest) round trip ping
                         request & reply time in milliseconds
            `avg_ping`: *float*; the average round trip ping time in
                         milliseconds
            `max_ping`: *float*; the maximum (slowest) round trip ping time in
                        milliseconds
            `jitter`: *float*; the standard deviation between round trip ping
                        times in milliseconds
            """

            matcher = re.compile(r'(\d+) packets transmitted, (\d+) received')
            sent, received = _get_match_groups(ping_output, matcher)

            try:
                matcher = re.compile(r'(\d+.\d+)/(\d+.\d+)/(\d+.\d+)/(\d+.\d+)')
                min_ping, avgping, max_ping, jitter = _get_match_groups(ping_output,
                                                                        matcher)

                ping_result = {'host': target, 'sent': sent, 'received': received,
                               'min_ping': min_ping, 'avg_ping': avgping,
                               'max_ping': max_ping, 'jitter': jitter}

                log.info("[ping] %s", str(result))
                return ping_result
            except ValueError:
                return {}

        command = ["ping6"]

        # Timeout
        command.extend(["-w", str(self.timeout)])

        # Count ping packets
        command.extend(["-c", str(self.count)])

        # Network interface used
        command.extend(["-I", self.interface])

        # Host
        destination = random.choice(self.destinations)
        command.append(destination)

        log.info(str(command))
        process = subprocess.Popen(command, stdout=subprocess.PIPE)
        out, _ = process.communicate()
        result = parse(out, target=destination)
        self.settings.get("output_file").write(str(result) + "\n")
        self.settings.get("output_file").flush()
        return result

    # RPL info traffic class
    def rplinfo(self):
        """
        This traffic class will extract the RPL information from a network
        using the rplinfo resource.
        """
        log = logging.getLogger("rplinfo")
        paths = self.settings.get("coap_path", ["/.well-known/core"])
        destinations = self.settings["destinations"]
        output_file = self.settings["output_file"]
        for destination in destinations:

            output_file.write("# Node %s\n" % destination)
            output_file.flush()

            for path in paths:
                url = urlparse.ParseResult(
                    "coap", "[%s]" % destination, path, "", "", ""
                ).geturl()
                command = [COAP_CLIENT, url]
                log.info("[coap] - %s", command)
                index_process = subprocess.Popen(command,
                                                 stdout=subprocess.PIPE)
                index_process.wait()
                out, _ = index_process.communicate()
                out = out.split("\n")[1]
                # We get the amount of routes that is to be extracted
                for resource in range(int(out)):
                    url = urlparse.ParseResult(
                        "coap", "[%s]" % destination, path, "",
                        "index=%d" % resource, ""
                    ).geturl()
                    command = [COAP_CLIENT, url]
                    log.info("[coap] - %s", command)
                    json_fetch_process = subprocess.Popen(command,
                                                          stdout=output_file)
                    json_fetch_process.wait()

    # Alias function

    def run(self):
        """
        Execute the defined task. It's an alias to the traffic_type defined
        function
        """
        traffic_type = self.protocol
        return getattr(self, traffic_type)()

    def sleep(self):
        """
        Trigger the sleep function
        """
        if 'sleep_type' in self.settings:
            sleep_type = self.settings["sleep_type"]
            getattr(self, sleep_type)()

    def launch(self):
        """
        Execute run and sleep one after the other for a precise amount of time
        """
        log = logging.getLogger("launch")
        work_to_do = []
        if "infinite" in self.settings:
            work_to_do = itertools.count(1)
        if "times" in self.settings:
            work_to_do = range(1, self.settings["times"] + 1)
        for iteration in work_to_do:
            traffic_type = self.settings["traffic_type"]
            log.info("[traffic %s] - Iteration %d", traffic_type, iteration)
            self.run()
            self.sleep()

    # Sleep function

    def exp_sleep(self):
        """
        An exponential sleep in order to simulate a Poisson traffic class
        """
        log = logging.getLogger("exp_sleep")
        if 'sleep_lambda' in self.settings:
            sleep_time = random.expovariate(self.settings["sleep_lambda"])
            log.info("Sleeping for %f s", sleep_time)
            time.sleep(sleep_time)

    def const_sleep(self):
        """
        A constant sleep to have a regular traffic
        """
        log = logging.getLogger("const_sleep")
        if "sleep_const" in self.settings:
            sleep_time = self.settings["sleep_const"]
            log.info("Sleeping for %f s", sleep_time)
            time.sleep(sleep_time)

    def uniform_sleep(self):
        """
        A uniform sleep within min_sleep and max_sleep
        """
        log = logging.getLogger("uniform_sleep")
        if "min_sleep" in self.settings and "max_sleep" in self.settings:
            min_sleep = self.settings["sleep_min"]
            max_sleep = self.settings["sleep_max"]
            sleep_time = random.uniform(min_sleep, max_sleep)
            log.info("Sleeping for %f s", sleep_time)
            time.sleep(sleep_time)
