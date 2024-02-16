import csv
import tkinter as tk
from tkinter import filedialog, ttk
import matplotlib
import ast
import networkx as nx
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

matplotlib.use('TkAgg')


class SimulationAnalysis(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Traffic Simulation Analysis")
        self.geometry("1200x800")
        self.graph_structure_file = "GraphEdges.csv"
        self.traffic_counts_file = "TrafficCounts.csv"
        self.graph_structure = self.load_graph_structure()
        self.simulation_data = self.load_and_preprocess_traffic_counts(self.traffic_counts_file)
        self.init_ui()

    def select_file(self, title):
        filename = filedialog.askopenfilename(title=title, filetypes=[("CSV files", "*.csv")])
        if not filename:  # User canceled the dialog
            self.destroy()
        return filename

    def load_graph_structure(self):
        G = nx.Graph()
        try:
            with open(self.graph_structure_file, mode='r', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    G.add_edge(row['From'], row['To'], weight=float(row['Weight']))
        except Exception as e:
            print(f"Failed to load graph structure: {e}")
        return G

    def load_and_preprocess_traffic_counts(self, csv_file):
        if not csv_file:
            raise ValueError("CSV file path must be provided")

        traffic_data = []
        with open(csv_file, mode='r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                iteration = int(row['iteration'])  # Ensure iteration is an integer
                traffic_counts = ast.literal_eval(row['traffic_counts'])
                for road, count in traffic_counts.items():
                    road_str = f"{road[0]}-{road[1]}"  # Convert tuple to string if necessary
                    traffic_data.append({
                        'Iteration': iteration,
                        'Road': road_str,
                        'Traffic Volume': count
                    })
        return traffic_data

    def init_ui(self):
        # Tabs
        tab_control = ttk.Notebook(self)
        graph_tab = ttk.Frame(tab_control)
        heatmap_tab = ttk.Frame(tab_control)
        tab_control.add(graph_tab, text='Network Graph')
        tab_control.add(heatmap_tab, text='Traffic Heatmap')
        tab_control.pack(expand=1, fill='both')
        benefit_button = tk.Button(self, text="Show Road Benefits", command=self.show_road_benefits)
        benefit_button.pack()

        # Network Graph
        self.visualize_graph(graph_tab)

        # Traffic Heatmap
        self.visualize_traffic_heatmap(heatmap_tab)

    def visualize_graph(self, parent):
        fig = Figure(figsize=(8, 6))
        ax = fig.add_subplot(111)
        self.draw_network_graph(ax)
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def draw_network_graph(self, ax):
        G = self.graph_structure
        pos = nx.spring_layout(G)
        weights = nx.get_edge_attributes(G, 'weight').values()
        nx.draw(G, pos, ax=ax, with_labels=True, node_color='skyblue', edge_color=list(weights),
                width=4, edge_cmap=plt.get_cmap('viridis'), node_size=500)
        ax.set_title("Network Graph")

    def visualize_traffic_heatmap(self, parent):
        traffic_df = pd.DataFrame(self.simulation_data)
        if not traffic_df.empty:
            fig = Figure(figsize=(10, 4))
            ax = fig.subplots()
            heatmap_data = traffic_df.pivot_table(index='Road', columns='Iteration', values='Traffic Volume',
                                                  aggfunc=np.mean)
            sns.heatmap(heatmap_data, ax=ax, cmap="Reds", annot=True, fmt=".0f")
            ax.set_title("Traffic Volume Heatmap")
            canvas = FigureCanvasTkAgg(fig, master=parent)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        else:
            label = tk.Label(parent, text="Insufficient data for heatmap.")
            label.pack()

    def show_road_benefits(self):
        road_benefits = self.calculate_all_road_benefits()
        benefit_frame = tk.Toplevel(self)
        benefit_frame.title("Road Benefit Analysis")

        for road, benefit in road_benefits.items():
            road_str = f"Road {road}: Benefit = {benefit:.2f}"
            label = tk.Label(benefit_frame, text=road_str)
            label.pack()

    def calculate_all_road_benefits(self):
        # Example: Calculate benefits for each potential road.
        # This requires self.nt and self.G to be defined and populated.
        road_benefits = {}
        potential_roads = [(0, 2), (0, 3), (1, 2), (1, 4), (2, 3)]  # Example potential roads
        for road in potential_roads:
            benefit = self.calculate_benefit(*road)
            road_benefits[road] = benefit
        return road_benefits

    def calculate_benefit(self, x, y):
        """Calculate the benefit of adding a road between nodes x and y."""
        current_spdXY = self.calculate_shortest_path(x, y)
        proposed_dXY = current_spdXY * 0.6  # Adjusted road length to simulate new road
        direct_benefit = (current_spdXY - proposed_dXY) * (
                self.nt.get((x, y), 0) + self.nt.get((y, x), 0))  # look again at this

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

    def calculate_shortest_path(G, source, target):
        """Calculate the shortest path length between two nodes."""
        try:
            return nx.dijkstra_path_length(G, source, target, weight='weight')
        except nx.NetworkXNoPath:
            return np.inf


if __name__ == "__main__":
    app = SimulationAnalysis()
    app.mainloop()
