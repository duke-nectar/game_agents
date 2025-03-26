def path_finder(start_location, end_location):
    start_location = tuple(start_location)
    end_location = tuple(end_location)
    path = [start_location]
    current_location = start_location
    
    while current_location != end_location:
        if current_location[0] < end_location[0]:
            current_location = (current_location[0] + 1, current_location[1])
        elif current_location[0] > end_location[0]:
            current_location = (current_location[0] - 1, current_location[1])
        elif current_location[1] < end_location[1]:
            current_location = (current_location[0], current_location[1] + 1)
        elif current_location[1] > end_location[1]:
            current_location = (current_location[0], current_location[1] - 1)
        path.append(current_location)
    return path
    
    # If no path is found, return an empty list
    return []
if __name__ == "__main__":
    print(path_finder((0,0),(60,23)))    