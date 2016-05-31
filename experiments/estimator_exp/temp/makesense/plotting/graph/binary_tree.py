#!/usr/bin/env python3

from itertools import product
import json
import networkx as nx
from matplotlib import pyplot as plt
from networkx.readwrite import json_graph
from math import sqrt

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


with open("graph_radio.json", "w") as f:
    f.write(json_graph.dumps(g,sort_keys=True,
        indent=4, separators=(',', ': ') ))

    # Drawing
pos = nx.spectral_layout(g)
nx.draw(g, pos, node_color="g")
nx.draw_networkx_nodes(g, pos, nodelist=[1], node_color="b")

plt.savefig("topology_tree.pdf", format="pdf")
plt.show()
