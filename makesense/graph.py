# -*- coding: utf-8 -*-

import json
import pdb
import os
from os.path import join as pj
import networkx as nx
import pandas as pd
from networkx.readwrite.json_graph import  node_link_data


def chain():

    g = nx.Graph()

    # Horizontal

    for i in range(11, 15):
        g.add_edge(i, i + 1)

    for i in range(7, 10):
        g.add_edge(i, i + 1)

    for i in range(4, 6):
        g.add_edge(i, i + 1)

    for i in range(2, 3):
        g.add_edge(i, i + 1)

    g.add_node(1)


    # Trans height

    g.add_edge(1, 2)
    g.add_edge(1, 3)

    g.add_edge(2, 4)
    g.add_edge(2, 5)
    g.add_edge(3, 5)
    g.add_edge(3, 6)

    g.add_edge(4, 7)
    g.add_edge(4, 8)
    g.add_edge(5, 8)
    g.add_edge(5, 9)
    g.add_edge(6, 9)
    g.add_edge(6, 10)

    g.add_edge(7, 11)
    g.add_edge(7, 12)
    g.add_edge(8, 12)
    g.add_edge(8, 13)
    g.add_edge(9, 13)
    g.add_edge(9, 14)
    g.add_edge(10, 14)
    g.add_edge(10, 15)

def tree():

    with open("graph_radio.json", "w") as f:
        f.write(json_graph.dumps(g,sort_keys=True,
            indent=4, separators=(',', ': ') ))

        # Drawing
    pos = nx.spectral_layout(g)
    nx.draw(g, pos, node_color="g")
    nx.draw_networkx_nodes(g, pos, nodelist=[1], node_color="b")

    plt.savefig("topology_tree.pdf", format="pdf")
    plt.show()

def plot_graph_chain(folder):
    g = nx.DiGraph()

    N = 7

    for i in range(1, N):
        g.add_edge(i + 1, i)

    g.add_node(1, root=True)

    with open("radio_tree.json", "w") as f:
        f.write(json_graph.dumps(g, sort_keys=True,
                indent=4, separators=(',', ': ')))

    pos = nx.circular_layout(g)
    nx.draw(g, pos=pos)
    nx.draw_networkx_nodes(g, pos, node_color='g')
    nx.draw_networkx_nodes(g, pos, nodelist=[1], node_color='b')

    nx.draw_networkx_edges(g, pos, edge_color="r", arrows=True)

    plt.savefig(pj(folder, "topology_chain.pdf"), format="pdf")

def flower():

    g = wheel_graph(7)

    g.add_edge(6, 1)
    g.add_edge(7, 6)
    g.add_edge(8, 7)

    with open("radio_graph.json", "w") as f:
        f.write(json_graph.dumps(g, sort_keys=True,
                indent=4, separators=(',', ': ')))

    pos = nx.spring_layout(g)
    nx.draw(g, pos=pos)
    nx.draw_networkx_nodes(g,pos,
                           node_color='g')
    nx.draw_networkx_nodes(g,pos,
                           nodelist=[8],
                           node_color='b')

    #nx.draw_networkx_edges(g, pos, edge_color="r", arrows=True)

    plt.savefig("topology_fleur.pdf", format="pdf")
    plt.show()


def plot_graph(self):
    """
    Plot the transmission graph of the simulation.

    TODO: Draw arrows and have a directed graph.
    http://goo.gl/Z697dH

    TODO: Graph with big nodes for big transmissions
    """
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    ax1.set_title("Transmission / RPL tree")
    ax1.axis("off")

    val_color = {"udp_server": 0.5714285714285714}

    pos = {node: data["pos"]
           for node, data in self.radio_tree.nodes(data=True)}

    # color for all nodes
    node_color = [val_color.get(data["mote_type"], 0.25)
                  for node, data in self.radio_tree.nodes(data=True)]
    # Drawing the nodes
    nx.draw_networkx_nodes(self.radio_tree, pos, node_color=node_color, ax=ax1)
    nx.draw_networkx_labels(self.radio_tree, pos, ax=ax1)

    # Drawing radio edges
    nx.draw_networkx_edges(self.radio_tree, pos, edgelist=self.radio_tree.edges(),
                           width=8, alpha=0.5, ax=ax1)

    # Adding the depth of each node.
    with open(PJ(self.result_dir, "depth.csv")) as depth_f:
        reader = DictReader(depth_f)
        for row in reader:
            node = int(row["node"])
            depth = row["depth"]

            ax1.text(pos[node][0] + 5, pos[node][1] + 5, depth,
                     bbox=dict(facecolor='red', alpha=0.5),
                     horizontalalignment='center')

    # Drawing RPL edges
    nx.draw_networkx_edges(
        self.rpl_tree, pos, edge_color='r', nodelist=[], arrows=True, ax=ax1)

    img_path = PJ(self.img_dir, "graph.pdf")
    fig.savefig(img_path, format="pdf")
    update_report(self.result_dir, "plot_graph", {
        "img_src": "img/graph.pdf",
        "comment": """
        When the edge is thick it means edges are in an RPL instance.
        Otherwise it means that the two nodes can see each others.
        """,
        "text": """
        We generate a random geometric graph then use information coming
        to the RPL root to construct the gateway representation of the RPL
        tree. We add into this tree representation the traffic generated.
        """})

def transmission_graph(self):
    """
    Plot the transmission graph of the simulation.
    """
    settings = self.settings["transmission_graph"]
    output_path = pj(self.result_folder_path, *settings["output_path"])
    fig_rplinfo, ax_transmission_graph = plt.subplots()


    net = nx.Graph()

    # nodes
    mote_types = self.settings["mote_types"]
    motes = self.settings["motes"]
    position = {}
    for mote in motes:
        mote_type = mote["mote_type"]
        mote_id = mote["mote_id"]
        position[mote_id] = (mote["x"], mote["y"])
        mote_types[mote_type] \
            .setdefault("nodes", []) \
            .append(mote["mote_id"])

    # edges
    transmitting_range = self.settings["transmitting_range"]
    for couple in itertools.product(motes, motes):
        if 0 < distance(couple) <= transmitting_range:
            net.add_edge(couple[0]["mote_id"],
                         couple[1]["mote_id"])

    for mote_type in mote_types:
        color = mote_types[mote_type]["color"]
        nodelist = mote_types[mote_type]["nodes"]
        nx.draw_networkx_nodes(net, position,
                               nodelist=nodelist,
                               node_color=color,
                               ax=ax_transmission_graph)
    nx.draw_networkx_edges(net, pos=position, ax=ax_transmission_graph)

    # labels
    nx.draw_networkx_labels(net, position, ax=ax_transmission_graph)

    plt.axis('off')
    plt.savefig(output_path)  # save as PNG
    return ax_transmission_graph


def rpl_graph(folder):
    """
    Build up the RPL representation at the gateway
    """
    output_folder = pj(folder, "results", "graph")
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    df = pd.read_csv(pj(folder, "results", "messages.csv"))
    parent_df = df[df.message_type == "parent"]

    rpl_graph = nx.DiGraph()
    for c, p in parent_df.iterrows():
        rpl_graph.add_edge(p["mote_id"], p["node"])

    with open(pj(output_folder, "rpl_graph.json"), "w") as f:
        f.write(json.dumps(node_link_data(rpl_graph),
                sort_keys=True, indent=4))
