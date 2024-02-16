import networkx as nx
import matplotlib.pyplot as plt
import numpy as np
import tqdm as tqdm
import random

# Initialize the graph
G = nx.Graph()
G.add_edges_from([
    (0, 1, {'weight': 6}), (0, 4, {'weight': 9}),
    (1, 3, {'weight': 11}), (2, 4, {'weight': 10}),
    (3, 4, {'weight': 7})
])

potential_roads = [(0, 2), (0, 3), (1, 2), (1, 4), (2, 3)]

nt = {edge: 0 for edge in G.edges()}


# Method for calculating the distance between 2 nodes using dijkstra
def CalculateShortestPath(G, source, target):
    try:
        # Find the shortest path from source to target using Dijkstra's algorithm
        path_length = nx.dijkstra_path_length(G, source=source, target=target, weight='weight')
    except nx.NetworkXNoPath:
        path_length = np.inf
    return path_length


def Benefit(G, X, Y, d, nt, f=0.8):
    spdX_Y = CalculateShortestPath(G, X, Y)  # Improvement in speed variable
    dX_Y = spdX_Y * f  # Distance from X to Y

    # Calculate the direct benefit
    direct_benefit = (spdX_Y - dX_Y) * (
            nt.get((X, Y), 0) + (nt.get((Y, X), 0)))  # considers trips from Y to X as well as X to Y

    # Calculate the indirect benefits through neighbors
    indirect_benefit = 0
    for n1 in G.neighbors(Y):
        for n2 in G.neighbors(X):
            if (X, n1) in nt and (Y, n2) in nt:  # Adjusted to check network traffic nt
                spdX_n1 = CalculateShortestPath(G, X, n1)
                spdY_n2 = CalculateShortestPath(G, Y, n2)
                dX_Y = CalculateShortestPath(G, X, Y) * f
                indirect_benefit += max(spdX_n1 + spdY_n2 - dX_Y, 0) * (nt.get((X, n1), 0) + nt.get((n2, Y), 0))

    total_benefit = direct_benefit + indirect_benefit
    return total_benefit


def SimulateTraffic(G, nt, potential_roads, iterations=36000, AgentCount=100):
    plt.ion()
    fig, ax = plt.subplots()
    fixed_positions = nx.spring_layout(G)

    for iteration in tqdm.tqdm(range(iterations)):
        for _ in range(AgentCount):
            nodes_list = list(G.nodes())
            if len(nodes_list) < 2:
                print("not enough nodes for sampling.")
                continue

            # Provide initial start and end nodes
            start, end = random.sample(nodes_list, 2)

            try:
                path = nx.shortest_path(G, source=start, target=end, weight='weight')
                for i in range(len(path) - 1):
                    edge = (path[i], path[i + 1])
                    reverse_edge = (path[i + 1], path[i])
                    if edge in nt:
                        nt[edge] += 1
                    elif reverse_edge in nt:
                        nt[reverse_edge] += 1
                    else:
                        nt[edge] = 1
            except (nx.NetworkXNoPath, nx.NetworkXError):
                print("Error: No path! {e}")
                continue
        yield {
            'iteration': iteration + 1,
            'total_iterations': iterations,
            'message': f"Simulating traffic, iteration {iteration + 1}/{iterations}"
        }

    plt.ioff()


def evaluate_and_update_road_benefits(G, d, nt, potential_roads, k=1):
   selected_roads = []


    for _ in range(k):
       road_benefits = []
       for road in potential_roads:
           X, Y = road
           benefit = Benefit(G, X, Y, d, nt, f=0.8)
           road_benefits.append((road, benefit))
       road_benefits.sort(key=lambda  x: x[1], reverse=True)

       if not road_benefits:
           break # No more roads to evaluate, so just break

        # select the road with the highest benefit

       best_road, best_benefit = road_benefits[0]
       selected_roads.append((best_road, best_benefit))

       # Add the best road to the graph
       G.add_edge(*best_road, weight=best_benefit)

       # Remove the added road from the list of potential roads
       potential_roads.remove(best_road)
       nt = {edge: 0 for edge in G.edges()}
       for _ in SimulateTraffic(G, nt, potential_roads, iterations=36000, AgentCount= 100):
        pass

    return selected_roads
