# GraphInit.py
import networkx as nx


def initialize_graph(nodes=60, k=3):
    graph = nx.random_graphs.watts_strogatz_graph(nodes, k, 0.5)
    potential_roads = []  # This could be populated based on your simulation needs
    return graph, potential_roads


# R2: benefit calculation clearly marked and displayed.
    # because of import issue. trouble importing data from simulation
    # recommend 2 roads to be built explicitly
    # benefit matrix

# R3: 60 nodes recommend 3 roads


# R4: change the value of f to 0.8 and test the results

# R5: double the connectivity to see the results.
    # what are the top 3 roads to be constructed.