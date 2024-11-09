import networkx as nx
import matplotlib.pyplot as plt


G = nx.DiGraph()

G.add_nodes_from(["A", "B", "C", "D", "E", "F", "G", "H"])
G.add_edge("A", "B", weight=4)
G.add_edge("A", "C", weight=8)
G.add_edge("B", "D", weight=8)
G.add_edge("B", "E", weight=11)
G.add_edge("D", "A", weight=7)
G.add_edge("C", "F", weight=4)
G.add_edge("C", "G", weight=2)
G.add_edge("C", "H", weight=2)
G.add_edge("C", "H", use_full=True)


# Visualize the graph
pos = nx.planar_layout(G)
nx.draw_networkx_nodes(G, pos)
nx.draw_networkx_edges(G, pos)
nx.draw_networkx_labels(G, pos)
nx.draw_networkx_edge_labels(
    G, pos, edge_labels={(u, v): d["weight"] for u, v, d in G.edges(data=True)}
)

plt.show()