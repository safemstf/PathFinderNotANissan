import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import networkx as nx
from threading import Thread, Event
import time
import random
from R2 import SimulateTraffic, G, potential_roads, nt


class TrafficSimulationApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Network Analysis")
        self.master.geometry("1200x800")
        self.highlighted_edges = []
        self.stop_event = Event()

        self.fig, self.ax = plt.subplots(figsize=(5, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.master)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.run_button = tk.Button(master, text="Run Simulation", command=self.start_simulation_thread)
        self.run_button.pack(side=tk.BOTTOM, pady=10)

        self.pos = nx.spring_layout(G)

        self.update_graph_visualization()
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def update_graph_visualization(self):
        if self.master.winfo_exists():
            self.ax.clear()
            nx.draw_networkx(G, self.pos, edgelist=self.highlighted_edges, edge_color='red', with_labels=True,
                             node_size=700, node_color='lightblue', ax=self.ax)
            self.canvas.draw_idle()

    def run_simulation(self):
        print("Simulation Started")
        try:
            for _ in range(10):
                if self.stop_event.is_set():
                    break
                self.master.after(0, self.update_highlighted_edges_randomly)  # Thread-safe GUI update
                time.sleep(1)  # Simulate work
            # Assuming SimulateTraffic function updates highlighted_edges and respects the stop_event
            SimulateTraffic(G, nt, potential_roads, iterations=36000, AgentCount=100)
            print("Simulation Completed")
        except Exception as e:
            # Use master.after to safely communicate with the main thread for GUI updates
            self.master.after(0, lambda err=e: messagebox.showerror("Error", str(err)))

    def update_highlighted_edges_randomly(self):
        if not self.stop_event.is_set():
            edges_list = list(G.edges())
            if edges_list:
                self.highlighted_edges = [random.choice(edges_list)]
                self.master.after(0, self.update_graph_visualization)

    def start_simulation_thread(self):
        self.stop_event.clear()
        simulation_thread = Thread(target=self.run_simulation)
        simulation_thread.start()

    def on_closing(self):
        self.stop_event.set()
        self.master.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = TrafficSimulationApp(root)
    root.mainloop()
