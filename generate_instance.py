# file that generates random instances

import random

def generate_tsp_file(filename, num_nodes):
    # generates a random instance of a TSP problem in TSPLIB format
    # reveives:
    # (1) filename: name of the file to be generated
    # (2) num_nodes: number of nodes of the problem
    with open(filename, 'w') as file:
        file.write(f"NAME: {filename}\n")
        file.write(f"TYPE: TSP\n")
        file.write(f"COMMENT: {num_nodes}-Staedte in Burma (Zaw Win)\n")
        file.write(f"DIMENSION: {num_nodes}\n")
        file.write(f"EDGE_WEIGHT_TYPE: GEO\n")
        file.write(f"EDGE_WEIGHT_FORMAT: FUNCTION\n")
        file.write(f"DISPLAY_DATA_TYPE: COORD_DISPLAY\n")
        file.write(f"NODE_COORD_SECTION\n")
        for node_id in range(1, num_nodes + 1):
            x = round(random.uniform(- 30.0, 30.0), 2) # modify to change range of the coordinates
            y = round(random.uniform(- 30.0, 30.0), 2) # modify to change range of the coordinates
            file.write(f"{node_id} {x} {y}\n")
        file.write(f"EOF\n")

