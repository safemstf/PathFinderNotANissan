import tkinter as tk
import traceback
from threading import Thread
from tkinter import messagebox, Toplevel, ttk
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from SimulationLogic import TrafficSimulation


class TrafficSimulationApp:
    def __init__(self, master, graph, potential_roads):
        super().__init__()

        self.master = master
        # Graph initializations
        self.graph = graph
        self.potential_roads = potential_roads
        self.pos = nx.spring_layout(self.graph)

        self.G = None  # Graph
        self.potentialRoads = None
        self.pos = None  # Positions for nodes
        self.fig = None
        self.canvas = None
        self.progress_label = None
        self.simulation_thread_lambda = None
        self.run_button = None
        self.leaderboardWindow = None
        self.ax = None
        self.canvas_widget = None
        self.data_button = None
        self.visualize_button = None

        self.prepare_simulation()

        # Initialize UI components
        self.configure_main_window()
        self.setup_simulation_graph()
        self.setupUI()

        # Simulation Initializations
        self.simulation = TrafficSimulation(self.G, potential_roads)
        self.simulationThread = Thread(target=self.runSimulation, daemon=True)  # Initialize the thread here
        self.simulationActive = False
        self.currentPath = []

    def configure_main_window(self):
        """Configure the main application window."""
        self.master.title("Traffic Simulation Analysis")
        self.master.geometry("1600x900")
        self.master.configure(bg='dark slate gray')

    def setup_simulation_graph(self):
        # Initialize the graph with nodes and edges
        self.G = nx.Graph()
        self.G.add_edges_from([
            (0, 1, {'weight': 6}), (0, 4, {'weight': 9}),
            (1, 3, {'weight': 11}), (2, 4, {'weight': 10}),
            (3, 4, {'weight': 7})
        ])
        self.potentialRoads = [(0, 2), (0, 3), (1, 2), (1, 4), (2, 3)]
        self.pos = nx.spring_layout(self.G)

    def setupUI(self):
        """Set up the user interface components."""
        self.setup_canvas()
        self.setup_buttons()
        self.updateGraphVisualization(currentPath=None)

    def start_simulation(self):
        if not self.simulationActive:
            self.simulationActive = True
            self.run_button.config(state='disabled', text="Simulation Running")
            Thread(target=self.simulation_thread_lambda).start()

    def setup_canvas(self):
        """Set up the canvas for graph visualization."""
        self.fig, self.ax = plt.subplots(figsize=(8, 6))
        self.ax.axis('off')

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def setup_buttons(self):
        """Setup control buttons."""
        style = ttk.Style()
        style.configure('TButton', font=('Arial', 12), background='#333', foreground='black')
        self.run_button = ttk.Button(self.master, text="Start Simulation", command=self.start_simulation,
                                     style='TButton')
        self.run_button.pack(side=tk.BOTTOM, pady=20)

    def highlight_path(self, source, target):
        path = nx.dijkstra_path(self.G, source, target, weight='weight')
        path_edges = list(zip(path, path[1:]))
        nx.draw_networkx_nodes(self.G, self.pos, nodelist=path, node_color='r')
        nx.draw_networkx_edges(self.G, self.pos, edgelist=path_edges, edge_color='r', width=2)
        self.canvas.draw()

    def updateGraphVisualization(self, currentPath=None):
        self.simulation = None
        self.ax.clear()
        # Basic graph drawing
        nx.draw(self.G, self.pos, with_labels=True, node_color='skyblue', edge_color='k', ax=self.ax, node_size=500)

        # Drawing potential roads with a distinct style
        nx.draw_networkx_edges(self.G, self.pos, edgelist=self.potentialRoads, edge_color='green', style='dashed',
                               ax=self.ax)

        # Highlighting the current path
        if currentPath:
            nx.draw_networkx_edges(self.G, self.pos, edgelist=[currentPath], edge_color='darkblack', width=3,
                                   ax=self.ax)

        # Visualizing traffic density as a heatmap
        if self.simulation and hasattr(self.simulation, 'nt'):
            for edge, traffic in self.simulation.nt.items():
                intensity = np.log1p(traffic) / np.log1p(max(self.simulation.nt.values()))
                nx.draw_networkx_edges(self.G, self.pos, edgelist=[edge], width=2, edge_color=[(1, 0, 0, intensity)],
                                       ax=self.ax)
            else:
                pass

        self.canvas.draw()

    def prepare_simulation(self):
        """Prepares and returns a simulation instance, along with a thread to run it."""
        self.simulation = TrafficSimulation(self.graph, self.potential_roads)
        self.simulation_thread_lambda = lambda: self.runSimulation()

    def runSimulation(self):
        if len(self.G.nodes) < 2:
            messagebox.showinfo("Simulation Error", "Not enough nodes in the graph to start the simulation.")
            exit()
        if not self.simulation:
            self.simulation = TrafficSimulation(self.G, self.potentialRoads)  # Initialize the simulation

        try:
            for progress in self.simulation.simulate_traffic():
                if not self.simulationActive:  # Check for pause state
                    break
                print(progress['message'])
                if 'error' in progress:
                    messagebox.showerror("Error", progress['error'])
                    break
        except Exception as e:
            traceback.print_exc()
            messagebox.showerror("Error", str(e))
        finally:
            if self.simulationActive:  # If still active, finalize the simulation
                self.finalizeSimulation()

    def export_graph_structure(self):
        """Export the graph structure as a list of edges for post-processing."""
        return list(self.graph.edges(data=True))

    def finalizeSimulation(self):
        selected_road_details = self.simulation.evaluate_and_update_road_benefits()
        for detail in selected_road_details:
            road = detail['road']
            # Assuming bidirectional traffic, sum both directions
            traffic_volume = self.simulation.nt.get(road, 0) + self.simulation.nt.get((road[1], road[0]), 0)
            detail['traffic_volume'] = traffic_volume
        self.updateGraphVisualization(currentPath=None)
        self.simulationActive = False
        self.run_button.config(state='normal', text="Start Simulation")

    def displayBenefitMatrix(self):
        # This is a placeholder
        matrixWindow = Toplevel(self.master)
        matrixWindow.title("Benefit Matrix")

    def on_closing(self):
        if self.simulationActive:
            if messagebox.askyesno("Confirm Exit", "Simulation is running. Are you sure you want to exit?"):
                self.master.destroy()
        else:
            self.master.destroy()
