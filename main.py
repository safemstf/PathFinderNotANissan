# Create a simulation environment using NetworkX
    # Generate 60 nodes "N" with random connections to 2 other nodes "P" should be set to 0.05 or 5
    # class nodes(roads)
        # node id for nodes array and hashing
        # calculate the roads linked to the node and store in road ID's as (StartNodeEndNode 1234 or node 12 to node 34)



    # calculate loss
        # Use networkx djkstra to calculate old weight: "L" (old weight - new weight) x traffic volume = loss
            # if loss is zero or negative it means new weight is large and a bad path was found
                # store the values in loss array

            # if loss is positive it means a better road was found.
                # only 3 new roads should be generated a time "k"
                # store positive values in loss array

    # define PathFinder(nodes, roads)
        # start array to store loss values
        # loop that cycles 36,000 (for seconds)
        # loop 100 times (T)
            # find near by nodes (use internal function from NetworkX)
            # start a trip to different nodes with a shrinkage factor "f" between 0.6 and 0.8

            # call calculate loss(new weight, old weight)

        # sort array based on value
        # choose the 3 highest values as new roads
        # return new roads






