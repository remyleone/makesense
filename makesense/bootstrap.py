"""
Bootstrap module.

This module will be in charge of bootstrapping a simulation by

- Generating folder and exp.json

Then optionally, it creates a random distribution of nodes with classical
firmware such as rpl border router and CoAP servers.

"""
from itertools import product
import json
import logging
import os
import random
import shutil

import networkx as nx

from . import Step
from .settings import EXPERIMENTS_FOLDER, PJ, TEMPLATE_ENV, ARCHETYPES, EXAMPLES_FOLDER
from .utils import ignored


class Bootstrap(Step):
    """

    Step in charge of creating the random grid.

    First the border_routers are placed on a 100x100 grid
    then we place the coap_servers while being sure they
    are at transmission distance of an already placed node.

    """

    def __init__(self, name,
                 repartition_dict):
        """
        Create a new experiment.
        """
        Step.__init__(self, name)

        log = logging.getLogger("bootstrap")
        log.info("Create %s", str(name))
        self.folder = PJ(EXPERIMENTS_FOLDER, name)
        settings = TEMPLATE_ENV.get_template("exp.json")

        if os.path.isdir(self.folder):
            raise OSError("The folder already exists. Aborting")

        if repartition_dict:

            # Moving classical nodes
            for archetype in repartition_dict:
                archetype_folder = PJ(EXAMPLES_FOLDER, *ARCHETYPES[archetype])
                try:
                    shutil.copytree(archetype_folder, PJ(self.folder, "nodes"))
                except OSError as err:
                    log.warn(err)

            # Creating the right JSON document to be included
            with open(PJ(self.folder, "exp.json"), "w+") as exp_settings_file:
                exp_settings_file.write(
                    settings.render(
                        {
                            "name": name,
                            "motes": self.generate_random(repartition_dict)
                        }))

        else:
            with ignored(OSError):
                os.mkdir(self.folder)
                os.mkdir(PJ(self.folder, "nodes"))
            with open(PJ(self.folder, "exp.json"), "w") as exp_settings_file:
                exp_settings_file.write(settings.render({"name": name}))

    @staticmethod
    def generate_grid(length=2, width=2, delta_length=1, delta_width=1):
        """
        Generate a JSON ready to be past in a exp.JSON for having big simulation
        """
        #generate positions
        positions = [{"x": pos_x, "y": pos_y, "mote_id": mote_id}
                     for mote_id, (pos_x, pos_y)
                     in zip(xrange(length * width),
                            product(xrange(0, length, delta_length),
                                    xrange(0, width, delta_width)))]
        mote_types = [{"mote_type": random.choice(["router", "server"])}
                      for _ in range(length * width)]

        #
        final_results = {"motes": [dict(position.items() + mote_type.items())
                                   for (position, mote_type)
                                   in zip(positions, mote_types)]}
        logging.info(json.dumps(final_results))

    @staticmethod
    def generate_random(repartition_dict):
        """
        Generate a JSON ready random positioning of motes.

        :rtype : JSON
        :return: a JSON document ready to be inserted in the exp.json
        """
        n = 0
        p = .5
        nums = []
        for node_type in repartition_dict:
            n += int(repartition_dict[node_type])
            nums += int(repartition_dict[node_type]) * [node_type]

        g = nx.fast_gnp_random_graph(n, p)
        pos = nx.random_layout(g)
        random.shuffle(nums)

        motes = []
        for node in pos:
            d = {
                "mote_id": node + 1,
                "mote_type": nums[node],
                "socket_port": 60000 + node + 1,
                "x": float(pos[node][0]),
                "y": float(pos[node][1])
            }
            if nums[node] == "border_router":
                d.update({
                    "tunslip_port": 60000 + node + 1,
                    "tunslip_prefix": "aaaa::1",
                    "tunslip_interface": "tun0"
                })
            motes.append(d)
        return json.dumps(motes, sort_keys=True,
                          indent=4, separators=(',', ': '))
