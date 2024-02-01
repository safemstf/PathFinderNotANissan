# Create a simulation environment using NetworkX
    # Generate 60 nodes "N" with random connections to 2 other nodes "P" should be set to 0.05 or 5
    # but, for R1, we will use a predefined set of nodes listed below:
        #G.add_edges_from([(0, 2, {'weight': 6}), (0, 3, {'weight': 9}), (1, 2, {'weight': 11}), (1, 4, {'weight': 10}),
                  # (2, 3, {'weight': 7})])
        # after creating the nodes we will draw them using matplotlib and networkX drawing functions:
        # the tutorial defines some values here:
            #links = [(u, v) for (u, v, d) in G.edges(data=True)]
            # pos = nx.nx_pydot.graphviz_layout(G)
            # nx.draw_networkx_nodes(G, pos, node_size=1200, node_color='lightgreen', linewidths=0.25)  # draw nodes
            # nx.draw_networkx_edges(G, pos, edgelist=links, width=4)  # draw edges

    # calculate weight function
        # find the weight of traveling from node a to node b
        # Find the shortest path from source to target using Dijkstra's algorithm and networkx built in library command
        # path_length to the new node= nx.dijkstra_path_length(G, source=start_node_id, target=target_node_id, weight='weight')
        # StoredWeights.append(path_length of new road) add to the array using append
        # return path_length



    # define PathFinder(nodes, roads)
        # define the value of "k"
        # start array to store loss values
        # loop that cycles 36,000 (for seconds)
        # loop 100 times (T)
            # select 2 random nodes from the set of nodes in the graph G
            # calculate the weight using calculate weight function to find how far it would be to go between the nodes.
            # create a new temporary road
            # calculate using calculate weight function the difference the new road makes
            # save loss in a loss array that you can sort later.
            # start a trip to different nodes with a shrinkage factor "f" between 0.6 and 0.8

            # call calculate loss(new weight, old weight)
                # Use networkx djkstra to calculate old weight: "L" (old weight - new weight) x traffic volume = loss
                # if loss is zero or negative it means new weight is large and a bad path was found
            # store the values in loss array

            # if loss is positive it means a better road was found.
            # only 3 new roads should be generated a time "k"
            # store positive values in loss array

            # sort array based on value
            # choose the 3 highest values as new roads
            # return new roads






