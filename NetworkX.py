import networkx as nx
import random
import matplotlib.pyplot as plt
from tqdm import tqdm

# Initialize the network
G = nx.gnp_random_graph(6, 0.05, seed=42)  # 60 nodes, 5% chance of edge creation

# Adding road IDs
for (u, v) in G.edges():
    G[u][v]['road_id'] = f"{u}{v}"


class Node:
    def __init__(self, node_id, G):
        self.node_id = node_id
        self.linked_roads = [G[u][v]['road_id'] for u, v in G.edges(node_id)]


# Creating node objects
nodes = [Node(i, G) for i in range(6)]

# Simulation with progress monitor
for _ in tqdm(range(36), desc="Main Iteration"):
    loss_array = []

    # Assuming G is your graph from the previous steps
    pos = nx.spring_layout(G, seed=42)  # Positioning using spring layout with a fixed seed for reproducibility

    # Print node degree and clustering coefficient
    print("Node degree and node clustering:")
    for v in nx.nodes(G):
        print(f"{v} {nx.degree(G, v)} {nx.clustering(G, v)}")

    print("\nThe adjacency list:")
    for line in nx.generate_adjlist(G):
        print(line)

    # Visualization
    nx.draw_networkx_nodes(G, pos, node_size=1200, node_color='lightblue', linewidths=0.25)
    nx.draw_networkx_edges(G, pos, width=4)

    # Node labels
    nx.draw_networkx_labels(G, pos, font_size=20, font_family="sans-serif")

    # Edge weight labels
    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels)

    plt.show()
    for _ in range(100):
        start_node = random.choice(nodes)
        end_node = random.choice([node for node in nodes if node != start_node])

        # Simulating trips and calculating loss
        f = random.uniform(0.6, 0.8)  # shrinkage factor
        try:
            path_length = nx.dijkstra_path_length(G, start_node.node_id, end_node.node_id)
            new_path_length = f * path_length
            loss = (path_length - new_path_length) * random.randint(100, 1000)  # Traffic volume
            if loss > 0:
                loss_array.append((start_node.node_id, end_node.node_id, loss))
                print(loss_array)
        except nx.NetworkXNoPath:
            continue

    # Processing loss array
    loss_array.sort(key=lambda x: x[2], reverse=True)
    for new_road in loss_array[:3]:
        if not G.has_edge(new_road[0], new_road[1]):
            G.add_edge(new_road[0], new_road[1])
            G[new_road[0]][new_road[1]]['road_id'] = f"{new_road[0]}{new_road[1]}"

# The graph G now represents the final state of the network after simulation
