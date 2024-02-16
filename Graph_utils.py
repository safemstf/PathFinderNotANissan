# graph_utils.py
import networkx as nx
import matplotlib.pyplot as plt

def draw_graph(graph, pos, current_path=None):
    """
    Draws the graph using matplotlib, highlighting the current path if provided.
    """
    plt.clf()  # Clear the current figure
    nx.draw(graph, pos, with_labels=True, node_color='skyblue', edge_color='k')
    if current_path:
        nx.draw_networkx_edges(graph, pos, edgelist=current_path, edge_color='r', width=2)
    plt.draw()

def update_graph_visualization(ax, canvas, graph, pos, current_path=None):
    """
    Clears the existing graph visualization and redraws it based on the current state.
    """
    ax.clear()
    draw_graph(graph, pos, current_path)
    canvas.draw_idle()
