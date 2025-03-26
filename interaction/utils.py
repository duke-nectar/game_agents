def path_finder(start_location, end_location):
    start_location = tuple(start_location)
    end_location = tuple(end_location)
    # Define the possible movements in the map
    movements = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    
    # Initialize the queue with the start location
    queue = [(start_location, [start_location])]
    
    # Initialize a set to keep track of visited locations
    visited = set()
    
    while queue:
        (location, path) = queue.pop(0)
        # If the current location is the end location, return the path
        if location == end_location:
            return path
        
        # Mark the current location as visited
        visited.add(location)
        
        # Explore all possible movements from the current location
        for movement in movements:
            new_location = (location[0] + movement[0], location[1] + movement[1])
            
            # Check if the new location is within the map and not visited before
            if new_location not in visited:
                queue.append((new_location, path + [new_location]))
    
    # If no path is found, return an empty list
    return []
