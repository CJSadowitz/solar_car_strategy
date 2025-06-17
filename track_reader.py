def get_track_edge(path):
    pos_elv_dict = {}
    with open(path, "r") as file:
        for line in file.readlines():
            values = line.split(',')
            elevation = values[2]
            relative_pos = values[3]
            pos_elv_dict[float(relative_pos.strip())] = float(elevation)
    
    return pos_elv_dict

def get_elevation(relative_position, dict):
    closest_key = min(dict.keys(), key=lambda k: abs(k - relative_position))
    return dict[closest_key]
