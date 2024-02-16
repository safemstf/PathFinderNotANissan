# GraphInit.py
import networkx as nx


def initialize_graph(nodes=60, k=3):
    graph = nx.random_graphs.watts_strogatz_graph(nodes, k, 0.5)
    potential_roads = []  # This could be populated based on your simulation needs
    return graph, potential_roads
