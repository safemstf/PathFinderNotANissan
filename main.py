# main.py
import tkinter as tk
from TrafficSimulationApp import TrafficSimulationApp
from LargerNetwork import initialize_graph


def main():
    root = tk.Tk()
    root.configure(bg='dark slate gray')

    graph, potential_roads = initialize_graph(nodes=60, k=3)
    app = TrafficSimulationApp(root, graph, potential_roads)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
