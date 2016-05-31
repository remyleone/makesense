#!/usr/bin/env python3

import networkx as nx
from matplotlib import pyplot as plt
from networkx.readwrite import json_graph
from os.path import join as pj


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
