#!/usr/bin/env python

from matplotlib import pyplot as plt
import networkx as nx
import json
from math import sqrt
from itertools import product
from os.path import join as PJ
from networkx.readwrite import json_graph
from BeautifulSoup import BeautifulSoup

RADIO_RANGE = 42

def distance(x1, x2, y1, y2):
    return sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

def radio_tree(folder):
    """
    Compute the radio graph
    """
    pos = {}
    radio_net = nx.Graph()
    with open(PJ(folder, "main.csc")) as f:
        soup = BeautifulSoup(f.read())
        soup.prettify()
        motes = [mote for mote in soup.findAll("mote")]
        for mote in motes:
            if mote.findAll("x"):
                x = float(mote.findAll("x")[0].string)
                y = float(mote.findAll("y")[0].string)
                mote_id = int(mote.findAll("id")[0].string)
                radio_net.add_node(mote_id, x=x, y=y)
                pos[mote_id] = [x, y]

        for (a, d_a), (b, d_b) in product(radio_net.nodes(data=True), radio_net.nodes(data=True)):
            d = distance(d_a["x"], d_b["x"], d_a["y"], d_b["y"])
            if d < RADIO_RANGE:
                radio_net.add_edge(a, b)

    with open(PJ(folder, "radio_tree.json"), "w") as rpl_tree_f:
        rpl_tree_f.write(json_graph.dumps(radio_net,
                                          indent=4, sort_keys=True))
    return pos

def plot_radio_tree(folder, pos):
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    ax1.set_title("Radio tree")
    ax1.axis("off")
    radio_net = nx.Graph()

    with open(PJ(folder, "radio_tree.json")) as f:
        radio_net = json_graph.loads(f.read())
        nx.draw_networkx(radio_net, pos=pos, ax=ax1, edge_color='r', arrows=True)

        fig.savefig(PJ(folder, "radio_tree.pdf"), format="pdf")
        fig.savefig(PJ(folder, "radio_tree.png"), format="png")


folders = ["./chaine/chaine_high/", "./chaine/chaine_high_calibration/",
           "./chaine/chaine_medium/", "./chaine/chaine_medium_calibration/",
           "./chaine/chaine_low/", "./chaine/chaine_low_calibration/",

           "./fleur/fleur_high/", "./fleur/fleur_high_calibration/",
           "./fleur/fleur_medium/", "./fleur/fleur_medium_calibration/",
           "./fleur/fleur_low/", "./fleur/fleur_low_calibration/",

           "./arbre/arbre_high/", "./arbre/arbre_high_calibration/",
           "./arbre/arbre_medium/", "./arbre/arbre_medium_calibration/",
           "./arbre/arbre_low/", "./arbre/arbre_low_calibration/",

           "./arbre_overhearing/arbre_high/", "./arbre_overhearing/arbre_high_calibration/",
           "./arbre_overhearing/arbre_medium/", "./arbre_overhearing/arbre_medium_calibration/",
           "./arbre_overhearing/arbre_low/", "./arbre_overhearing/arbre_low_calibration/"

           ]


for folder in folders:
    print("%sradio_tree.pdf" % folder)
    pos = radio_tree(folder)
    plot_radio_tree(folder, pos=pos)

