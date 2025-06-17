import bisect

def get_track_edge(path):
    pos_elv_dict = {}
    with open(path, "r") as file:
        for line in file.readlines():
            values = line.split(',')
            elevation = values[2]
            relative_pos = values[3]
            pos_elv_dict[float(relative_pos.strip())] = float(elevation)
    file.close()
    
    return pos_elv_dict

def get_elevation(relative_position, dict):
    keys = list(dict.keys())
    idx = bisect.bisect_left(keys, relative_position)

    if idx == 0:
        closest_key = keys[0]
    elif idx == len(keys):
        closest_key = keys[-1]
    else:
        before = keys[idx - 1]
        after = keys[idx]
        closest_key = before if abs(relative_position - before) < abs(relative_position - after) else after

    return dict[closest_key]
