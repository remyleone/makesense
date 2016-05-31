#!/usr/bin/env python3

import networkx as nx
from matplotlib import pyplot as plt
from math import sqrt
from networkx.generators.classic import wheel_graph
from networkx.readwrite import json_graph

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
