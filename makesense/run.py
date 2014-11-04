# coding: utf-8

"""
Run_exp steps.

All live I/O are performed here
"""

# import logging
import os
import subprocess
# from threading import Thread, Event
# import time

# import errno
# from . import Step

# from steps.traffic import Traffic
# from steps.utils import test_telnet_port, node_address


# class Worker(Thread):
#     """
#     Worker useful to implement dependencies between different threads.
#     """

#     def __init__(self, target, requires=None, provides=None):
#         if not provides:
#             provides = []
#         if not requires:
#             requires = []
#         super(Worker, self).__init__()
#         self.target = target
#         self.requires = requires
#         self.provides = provides

#     def run(self):
#         for event in self.requires:
#             event.wait()
#         self.target()
#         for event in self.provides:
#             event.set()


def run_experiment(name, contiki, cooja, simulation_file):
    """
    Launch the COOJA simulation of an experiment.
    All the log of the experiment will be stored in COOJA.log
    """
    main_command = ["java", "-mx512m"]
    # COOJA
    main_command.extend(["-jar", cooja])
    # Simulation file
    main_command.append("".join(["-nogui=", simulation_file]))
    # CONTIKI
    main_command.append("".join(["-contiki=", contiki]))
    # log.info("[exp %s] %s", name, str(main_command))
    subprocess.Popen(main_command)


# class Run(Step):
#     """
#     Run exp implementation
#     """


#     def connect_serial(self):
#         """
#         Connect to all serial socket in order to have a log for every nodes.
#         """
#         log = logging.getLogger("connect_serial")
#         logging.info(self.settings["title"])

#         telnet_processes = {}
#         for mote in self.motes:
#             if "socket_port" in mote:
#                 path_log = PJ(self.result_folder, "logs",
#                               str(mote["mote_id"]) + ".log")
#                 log_file = open(path_log, "wb")
#                 port = str(mote["socket_port"])

#                 connected = False
#                 while not connected:
#                     connected = test_telnet_port("localhost", port)
#                     time.sleep(0.1)
#                 serial_socket = subprocess.Popen(
#                     ["telnet", "localhost", port],
#                     stdout=log_file)
#                 telnet_processes[mote["mote_id"]] = serial_socket
#                 log.info("OK Port " + port)

#     def connect_tunslip(self):
#         """
#         Connect through a TUNSLIP.

#         You need root privileges in order to run this command. In order to
#         make the simulation easier, you could for instance run the whole
#         simulation with sudo privileges. This way, the simulation doesn't stop
#         half way through to ask you for a password.
#             sudo -v; fab run_exp:rpl_udp
#         """
#         log = logging.getLogger("connect_tunslip")
#         log.info(self.settings["title"])

#         tunslip_processes = {}
#         for mote in self.settings["motes"]:
#             if "tunslip_port" in mote:
#                 interface = mote["tunslip_interface"]
#                 port = str(mote["tunslip_port"])
#                 prefix = mote["tunslip_prefix"]
#                 tunslip_command = ["sudo", TUNSLIP, "-a", "localhost",
#                                    "-p", port, "-t", interface,
#                                    prefix]
#                 stderr_output = open(PJ(self.default, "logs",
#                                         "tunslip_" + port + "_stderr.log"),
#                                      "w")
#                 stdout_output = open(PJ(self.default, "logs",
#                                         "tunslip_" + port + "_stdout.log"),
#                                      "w")
#                 log.info(str(tunslip_command))

#                 # Test if the port is open
#                 connected = False
#                 while not connected:
#                     connected = test_telnet_port("localhost", port)
#                     time.sleep(0.1)
#                 tunslip_process = subprocess.Popen(tunslip_command,
#                                                    stderr=stderr_output,
#                                                    stdout=stdout_output)
#                 tunslip_processes[mote["mote_id"]] = tunslip_process
#                 time.sleep(0.1)
#                 if os.path.exists("/sys/class/net/" + interface):
#                     log.info("OK Port %s", port)
#                 else:
#                     log.error("FAIL PORT %s", port)

#     def generate_traffic(self):
#         """
#         Function that will run the different traffic class defined in the
#         settings file.
#         """
#         log = logging.getLogger("generate_traffic")
#         # Waiting for tunslip to be active
#         log.info("Start")

#         traffic_pool = {}
#         for traffic_class in self.traffic_classes:
#             # Compilation of output log folder
#             settings = self.traffic_classes[traffic_class]
#             output_path = PJ(self.default, *settings["output_path"])
#             with open(output_path, "a+") as output_file:
#                 settings["output_file"] = output_file
#                 traffic_pool[traffic_class] = Traffic(**settings)
#                 traffic_pool[traffic_class].launch()

#     def test_connectivity(self):
#         """
#         Test if the network is up and running. We need to run this function
#         before sending any meaningful traffic

#         We use ping traffic class in order to test
#         """
#         log = logging.getLogger("test_connectivity")
#         log.info(self.settings["title"])

#         for mote in self.motes:
#             address = node_address(mote["mote_id"])
#             log.info("Testing %s", address)
#             ping_traffic = Traffic(
#                 protocol="ping",
#                 destinations=[address],
#                 output_file=open(PJ(self.default, "logs",
#                                     "test_connectivity.log"), "w")
#             )
#             connected = None
#             while not connected:
#                 result_ping = ping_traffic.run()
#                 if result_ping:
#                     connected = True
#                     log.info("%s - OK :)", address)
#                 else:
#                     log.info("%s - KO :(", address)

#     def __init__(self, name):
#         """
#         Run an experiment while connecting serial socket. When this function
#         terminates it means that the whole experiment is also finished.
#         """
#         Step.__init__(self, name)
#         self.load_settings()
#         log = logging.getLogger("run_exp")
#         logging.info(self.settings["title"])

#         # Fetch run_exp settings & create shortcuts
#         self.motes = self.settings["motes"]

#         # Create events
#         self.simulation_launched = Event()
#         self.tunslip_connected = Event()
#         self.serial_sockets_connected = Event()
#         self.network_ready = Event()

#         for result_folder in self.result_folders:
#             self.result_folder = result_folder
#             link_path = self.default
#             worker_pool = set()
#             try:
#                 os.symlink(self.result_folder, link_path)
#             except OSError, err:
#                 if err.errno == errno.EEXIST:
#                     os.unlink(link_path)
#                     os.symlink(self.result_folder, link_path)

#             # Launching experiment
#             exp_thread = Worker(
#                 target=self.launch,
#                 provides=[self.simulation_launched]
#             )
#             exp_thread.start()
#             worker_pool.add(exp_thread)

#             # Connexion tunslip
#             if "connect_tunslip" in self.settings:
#                 tunslip_thread = Worker(
#                     target=self.connect_tunslip,
#                     requires=[self.simulation_launched],
#                     provides=[self.tunslip_connected])
#                 tunslip_thread.start()
#                 worker_pool.add(tunslip_thread)

#             # Connexion Serial
#             if "connect_serial" in self.settings:
#                 serial_thread = Worker(
#                     target=self.connect_serial,
#                     requires=[self.simulation_launched],
#                     provides=[self.serial_sockets_connected]
#                 )
#                 serial_thread.start()
#                 worker_pool.add(serial_thread)

#             # Traffic generation
#             if "traffic_classes" in self.settings:
#                 self.traffic_classes = self.settings["traffic_classes"]
#                 test_connectivity_thread = Worker(
#                     target=self.test_connectivity,
#                     requires=[self.tunslip_connected],
#                     provides=[self.network_ready])
#                 test_connectivity_thread.start()
#                 worker_pool.add(test_connectivity_thread)

#                 traffic_thread = Worker(
#                     target=self.generate_traffic,
#                     requires=[self.network_ready, self.tunslip_connected])
#                 traffic_thread.start()
#                 worker_pool.add(traffic_thread)

#             # We wait for all thread to be finished
#             for thread in worker_pool:
#                 thread.join()
#             log.info("Finished in %s", result_folder)
