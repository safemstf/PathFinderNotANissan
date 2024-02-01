import networkx as nx
import matplotlib.pyplot as plt
import tqdm as tqdm
import random

# Empty Graph
G = nx.Graph()

# create Graph
G.add_edges_from([(0, 2, {'weight': 6}), (0, 3, {'weight': 9}), (1, 2, {'weight': 11}), (1, 4, {'weight': 10}),
                  (2, 3, {'weight': 7})])

# some properties todo: Modify this to match our assignment
print("node degree and node clustering")
for v in nx.nodes(G):
    print(f"{v} {nx.degree(G, v)} {nx.clustering(G, v)}")

print()
print("the adjacency list")
for line in nx.generate_adjlist(G):
    print(line)

links = [(u, v) for (u, v, d) in G.edges(data=True)]
pos = nx.nx_pydot.graphviz_layout(G)
nx.draw_networkx_nodes(G, pos, node_size=1200, node_color='lightgreen', linewidths=0.25)  # draw nodes
nx.draw_networkx_edges(G, pos, edgelist=links, width=4)  # draw edges

# node labels
nx.draw_networkx_labels(G, pos, font_size=20, font_family="sans-serif")
# edge weight labels

edge_labels = nx.get_edge_attributes(G, 'weight', 'trips')
print(edge_labels)
# print("%.2f" % edge_labels)
nx.draw_networkx_edge_labels(G, pos, edge_labels)

plt.show()

StoredWeights = []  # Node1Node2Weight


# calculate loss function
def CalculateWeight(start_node_id, target_node_id):
    # Find the shortest path from source to target using Dijkstra's algorithm
    path_length = nx.dijkstra_path_length(G, source=start_node_id, target=target_node_id, weight='weight')
    StoredWeights.append(path_length)
    return path_length


# Create New roads
def Pathfinder():
    k = 3
    NewRoadLoss = []

    for i in range(36000):
        for j in range(100):
            a, b = random.sample(G.nodes(), 2)

            OldRoadWeight = CalculateWeight(a, b) # find distance using existing edges

            G.add_edges_from([(a, b)])
            tempRoadWeight = CalculateWeight(a, b)  # maybe multiply by "f" here?

            tempRoadLoss = OldRoadWeight - tempRoadWeight
            NewRoadLoss.append((a, b, tempRoadLoss))

            # sort NewRoadLoss
            NewRoadLoss.sort(key=lambda x: [2], reverse=True)
            top_k_edges = NewRoadLoss[:k]
            # todo: remove poor quality roads low volume and High weight roads
            # connectivity factor has to be 0.5 (reference canvas)
            return top_k_edges
