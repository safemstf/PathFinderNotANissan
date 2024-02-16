import datetime
import csv
import random

import networkx as nx
import numpy as np
import tqdm


class TrafficSimulation:
    # todo: change to 360000 after testing
    def __init__(self, graph, potential_roads, iterations=360, agent_count=100, update_interval=500):
        self.G = graph
        self.graph_original = graph.copy()
        self.graph = graph.copy()
        self.initial_potential_roads = potential_roads.copy()
        self.potential_roads = potential_roads.copy()
        self.selected_roads = []
        self.road_details = {}

        self.iterations = iterations
        self.agent_count = agent_count
        self.traffic_data_per_iteration = []
        self.update_interval = update_interval
        self.nt = {edge: 0 for edge in self.graph.edges()}
        self.traffic_data_per_iteration = []
        self.simulation_data = []

    def calculate_shortest_path(self, source, target):
        """Calculate the shortest path length between two nodes."""
        try:
            return nx.dijkstra_path_length(self.graph, source, target, weight='weight')
        except nx.NetworkXNoPath:
            return np.inf

    def benefit(self, x, y):
        """Calculate the benefit of adding a road between nodes x and y."""
        current_spdXY = self.calculate_shortest_path(x, y)
        proposed_dXY = current_spdXY * 0.8  # Adjusted road length to simulate new road
        direct_benefit = (current_spdXY - proposed_dXY) * (self.nt.get((x, y), 0) + self.nt.get((y, x), 0))

        indirect_benefit = 0
        for n1, n2 in set((n1, n2) for n1 in self.graph.neighbors(y) for n2 in self.graph.neighbors(x) if n1 != n2):
            current_spdXN1 = self.calculate_shortest_path(x, n1)
            current_spdYN2 = self.calculate_shortest_path(y, n2)
            indirect_path_length = current_spdXN1 + proposed_dXY + current_spdYN2
            original_spdN1N2 = self.calculate_shortest_path(n1, n2)
            traffic_volume_adjustment = self.nt.get((n1, n2), 0) + self.nt.get((n2, n1), 0)
            if indirect_path_length < original_spdN1N2:
                indirect_benefit += (original_spdN1N2 - indirect_path_length) * traffic_volume_adjustment

        return direct_benefit + indirect_benefit

    def simulate_traffic(self, callback=None):
        """Simulate traffic to update nt with new traffic counts."""
        start, end = None, None

        for iteration in tqdm.tqdm(range(self.iterations), desc="Simulating Traffic"):
            for _ in range(self.agent_count):
                if len(self.graph.nodes()) >= 2:
                    # Proceed with simulation
                    start, end = random.sample(list(self.graph.nodes()), 2)
                    path = nx.shortest_path(self.graph, source=start, target=end, weight='weight')

                    for i in range(len(path) - 1):
                        edge = (path[i], path[i + 1])
                        if edge in self.nt:
                            self.nt[edge] += 1
                        elif (edge[1], edge[0]) in self.nt:  # For undirected graphs
                            self.nt[(edge[1], edge[0])] += 1
                        else:
                            print(f"Edge not found in nt: {edge}")

                    # After each iteration append and store data for post-processing
                    print(f"Sample traffic counts after iteration {iteration}: {dict(list(self.nt.items())[:5])}")
                    self.traffic_data_per_iteration.append(self.nt.copy())

                    # store for post-processing
                    traffic_snapshot = {"iteration": iteration, "traffic_counts": dict(list(self.nt.items())[:5])}
                    self.simulation_data.append(traffic_snapshot)
                else:
                    print("Not enough nodes in the graph to start the simulation.")
                    pass

            if callback and iteration % self.update_interval == 0 and start is not None and end is not None:
                callback(currentPath=[(start, end)], trafficData=self.nt)

        if callback:
            callback(trafficData=self.nt)
        self.save_graph_edges_to_csv()
        self.save_traffic_counts_to_csv()
        yield {"progress": self.iterations, "total_iterations": self.iterations,
               "message": "Simulation complete: {self.iterations} iterations"}

    def evaluate_and_update_road_benefits(self, k=1):
        """Evaluate potential roads for benefits, select and update the graph with the best k roads."""
        road_benefits = [(road, self.benefit(*road)) for road in self.potential_roads if
                         road not in self.selected_roads]
        road_benefits.sort(key=lambda x: x[1], reverse=True)

        for road, benefit in road_benefits[:k]:
            traffic_volume = self.nt.get(road, 0) + self.nt.get((road[1], road[0]), 0)
            proposed_weight = self.calculate_shortest_path(*road) * 0.8
            current_weight = self.graph[road[0]][road[1]]['weight'] if self.graph.has_edge(*road) else np.nan
            # Store each road evaluation in the DataFrame
            self.simulation_data.append({
                'Road': str(road),
                'Benefit': benefit,
                'Traffic Volume': traffic_volume,
                'Proposed Weight': proposed_weight,
                'Current Weight': current_weight
            })

        # Update selected roads based on benefits
        for i in range(min(k, len(road_benefits))):
            best_road, _ = road_benefits[i]
            self.graph.add_edge(*best_road, weight=self.road_details[best_road]['proposed_weight'])
            self.selected_roads.append(best_road)

        # Adjust potential_roads for the next evaluation
        self.potential_roads = [road for road in self.initial_potential_roads if road not in self.selected_roads]
        selected_road_details = [self.road_details[road] for road in self.selected_roads[-k:]]

        return selected_road_details

    def save_traffic_counts_to_csv(self):
        now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_path = f"TrafficCounts_{now}.csv"

        with open(file_path, 'w', newline='') as csvfile:
            fieldnames = ['iteration', 'traffic_counts']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for data in self.simulation_data:
                writer.writerow({'iteration': data['iteration'], 'traffic_counts': data['traffic_counts']})

        print(f"Traffic counts saved successfully to {file_path}.")

    def save_graph_edges_to_csv(self):
        now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        file_path = f"GraphEdges_{now}.csv"

        with open(file_path, 'w', newline='') as csvfile:
            fieldnames = ['From', 'To', 'Weight']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for u, v, attrs in self.G.edges(data=True):
                writer.writerow({'From': u, 'To': v, 'Weight': attrs.get('weight', None)})

        print(f"Graph edges saved successfully to {file_path}.")
