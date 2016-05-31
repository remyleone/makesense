# coding: utf-8

from collections import Counter
from itertools import product
import json
import random

from networkx.readwrite import json_graph
import networkx as nx

from . import Step
from .settings import log, PJ, ROOT_DIR


serial_template = """
<plugin>
  SerialSocketServer
  <mote_arg>{mote_id}</mote_arg>
  <width>422</width>
  <height>69</height>
  <location_x>-9</location_x>
  <location_y>409</location_y>
</plugin>
"""

mote_template = """
<mote>
    <interface_config>
        org.contikios.cooja.interfaces.Position
        <x>{x}</x>
        <y>{y}</y>
    </interface_config>
    <interface_config>
        org.contikios.cooja.mspmote.interfaces.MspMoteID
        <id>{mote_id}</id>
    </interface_config>
    <motetype_identifier>{mote_type}</motetype_identifier>
</mote>
"""


class Topology(Step):

    """

    Step in charge of creating the random grid.

    First the border_routers are placed on a 100x100 grid
    then we place the coap_servers while being sure they
    are at transmission distance of an already placed node.
    """

    def __init__(self):
        Step.__init__(self)
        self.load_settings()
        # Dummy graph
        self.g = nx.Graph()
        self.transmitting_range = self.settings["transmitting_range"]
        self.repartition = Counter({k: int(v)
                                    for k, v
                                    in self.settings["repartition"].items()})
        self.node_types = self.repartition.elements()
        self.n = sum(1 for _ in self.repartition.elements())
        self.generate_random()

    def generate_grid(self, length=2, width=2, delta_length=1, delta_width=1):
        """
        Generate a JSON ready to be past in a exp.JSON for having big
        simulation.
        """
        # generate positions
        positions = [{"x": pos_x, "y": pos_y, "mote_id": mote_id}
                     for mote_id, (pos_x, pos_y)
                     in zip(range(length * width),
                            product(range(0, length, delta_length),
                                    range(0, width, delta_width)))]
        mote_types = [{"mote_type": random.choice(["router", "server"])}
                      for _ in range(length * width)]

        #
        final_results = {"motes": [dict(position.items() + mote_type.items())
                                   for (position, mote_type)
                                   in zip(positions, mote_types)]}
        log.info(json.dumps(final_results))

    def generate_random(self):
        """
        Generate a ready random positioning of motes using random_layout

        :rtype : JSON
        :return: a JSON document ready to be inserted in the exp.json
        """
        # Range of a node in the geometric graph
        p = 0.4
        dilatation = 0.8 * float(self.transmitting_range) / p

        self.g.add_nodes_from([1, 2])
        while not nx.is_connected(self.g):
            self.g = nx.random_geometric_graph(self.n, p)
        # Dilatation to avoid complete graph
        for node, data in self.g.nodes(data=True):
            self.g.add_node(
                node,
                pos=[data["pos"][0] * dilatation,
                     data["pos"][1] * dilatation])

        # Id starting at 1
        mapping = dict(zip(self.g.nodes(), range(1, self.n + 1)))
        nx.relabel_nodes(self.g, mapping, copy=False)
        self.motes = []
        pos = nx.get_node_attributes(self.g, "pos")
        for (node, (x, y)), mote_type in zip(pos.items(), self.node_types):
            self.g.add_node(node, mote_type=mote_type)
            d = {"mote_type": mote_type, "x": float(x), "y": float(y)}
            # TODO: find a better solution for default tunslip
            if mote_type == "rpl-border-router":
                d.update({
                    "mote_id": 1,
                    "socket_port": 60001,
                    "tunslip_port": 60001,
                    "tunslip_prefix": "aaaa::1",
                    "tunslip_interface": "tun0"})
            else:
                d.update({
                    "mote_id": node,
                    "socket_port": 60000 + node})
            self.motes.append(d)

        # Settings of a experiment (exp.json)
        self.json_settings = json.loads(open(PJ(ROOT_DIR, "exp.json")).read())
        self.json_settings["settings"]["motes"] = self.motes

    @property
    def serial_socket(self):
        return "".join([serial_template.format(**node)
                        for node in self.motes])

    @property
    def nodes_in_xml(self):
        # XML export
        return "".join([mote_template.format(**node)
                        for node in self.motes])

    @property
    def nodes_in_json(self):

        # JSON export
        return json.dumps(self.motes, indent=4, sort_keys=True)

    def save_all(self):
        """
        Save to file all the different view on the topology.
        """
        # Save the graph
        with open(PJ(ROOT_DIR, "graph.json"), "w") as f:
            f.write(json_graph.dumps(self.g, indent=4, sort_keys=True))

        # Save the serial settings
        with open(PJ(ROOT_DIR, "serial_socket.xml"), "w") as f:
            f.write(self.serial_socket)

        # Save the motes
        with open(PJ(ROOT_DIR, "motes.json"), "w") as f:
            f.write(self.nodes_in_json)

        # Save the motes XML (ready to insert in simulation file)
        with open(PJ(ROOT_DIR, "motes.xml"), "w") as f:
            f.write(self.nodes_in_xml)

        # Save the settings for the complete experiments
        with open(PJ(ROOT_DIR, "exp.json"), "w") as f:
            f.write(json.dumps(self.json_settings, indent=4, sort_keys=True))
