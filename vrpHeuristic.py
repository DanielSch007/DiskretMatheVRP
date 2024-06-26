# Import libraries
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.lines as mlines

# Using the Nearest Neighbor heuristic

def read_excel_file(filename, sheet_name):
    """
    Read coordinates and demand values from a specific sheet in an Excel file.
    Assumes the data is in columns labeled 'X', 'Y', and 'Demand'.
    """
    df = pd.read_excel(filename, sheet_name=sheet_name)
    coordinates = df[['X', 'Y']].values
    demands = df['Demand'].values
    return coordinates, demands

def calculate_distance_matrix(coordinates):
    """
    Calculate the distance matrix between coordinates.
    """
    num_points = len(coordinates)
    dist_matrix = np.zeros((num_points, num_points))

    for i in range(num_points):
        for j in range(num_points):
            dist_matrix[i, j] = calculate_distance(coordinates, i, j)

    return dist_matrix

def calculate_distance(coordinates, i, j):
    """
    Calculate the Euclidean distance between two points.
    """
    x1, y1 = coordinates[i]
    x2, y2 = coordinates[j]
    return np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

def calculate_total_distance(route, dist_matrix):
    """
    Calculate the total distance of a given route using the distance matrix.
    """
    total_distance = 0
    num_points = len(route)

    for i in range(num_points - 1):
        current_node = route[i]
        next_node = route[i + 1]
        total_distance += dist_matrix[current_node, next_node]

    return total_distance

def nearest_neighbor(dist_matrix, demands, capacity):
    """
    Apply the Nearest Neighbor heuristic to find initial routes for VRP.
    """
    num_points = dist_matrix.shape[0]
    visited = np.zeros(num_points, dtype=bool)
    routes = []

    while np.sum(visited) < num_points:
        current_node = 0  # Start at node 0
        current_capacity = 0
        route = [current_node]
        visited[current_node] = True

        while current_capacity + demands[current_node] <= capacity:
            current = route[-1]
            nearest = None
            min_dist = float('inf')

            for neighbor in np.where(~visited)[0]:
                if demands[neighbor] + current_capacity <= capacity and dist_matrix[current, neighbor] < min_dist:
                    nearest = neighbor
                    min_dist = dist_matrix[current, neighbor]

            if nearest is None:
                break

            route.append(nearest)
            visited[nearest] = True
            current_capacity += demands[nearest]

        routes.append(route)

    return routes

def format_output(routes):
    """
    Format the final routes as required.
    In this example, it returns a list of routes.
    """
    return routes

def vrp_solver(filename, sheet_name, capacity):
    """
    Solve the VRP using the provided filename for coordinates and vehicle capacity.
    """
    coordinates, demands = read_excel_file(filename, sheet_name)
    dist_matrix = calculate_distance_matrix(coordinates)
    routes = nearest_neighbor(dist_matrix, demands, capacity)
    formatted_routes = format_output(routes)
    return formatted_routes, coordinates

def plot_routes(routes, coordinates, location_names):
    """
    Plot the routes on a 2D graph with legends for location names and visit orders.
    """
    fig, ax = plt.subplots()
    
    for route in routes:
        route_coords = coordinates[route]
        ax.plot(route_coords[:, 0], route_coords[:, 1], marker='o')
        for i, point in enumerate(route):
            ax.text(route_coords[i, 0], route_coords[i, 1], str(point), fontsize=12, ha='right')

    # Create legend for sightseeing locations
    handles = [mlines.Line2D([], [], color='black', marker='o', linestyle='None', markersize=10, label=f'{i}: {name}') for i, name in enumerate(location_names)]
    sightseeing_legend = ax.legend(handles=handles, loc='upper right', title='Sightseeing Locations')

    # Create legend for visit order
    visit_legend = []
    num_vehicles = len(routes)
    for i in range(num_vehicles):
        visit_order_str = ', '.join([str(node) for node in routes[i] if node < len(location_names)])
        visit_legend.append(mlines.Line2D([], [], color='white', marker='o', markersize=10, label=f'Tourist {i+1}: {visit_order_str}'))
    
    visit_legend_handle = ax.legend(handles=visit_legend, loc='lower right', title='Visit Order')
    
    # Add both legends to the plot
    ax.add_artist(sightseeing_legend)
    ax.add_artist(visit_legend_handle)
    
    ax.set_title("Vehicle Routing Problem Solution")
    ax.set_xlabel("X Coordinate")
    ax.set_ylabel("Y Coordinate")
    ax.grid()
    plt.show()

# Define the location names
location_names = [
    'Ritz Carlton Hotel', 'Brandenburg Gate', 'Potsdamer Platz', 'Reichstag Building', 
    'Berlin Wall Memorial', 'Museum Island', 'Charlottenburg Palace', 
    'Berlin Cathedral', 'Checkpoint Charlie', 'East Side Gallery', 
    'Alexanderplatz'
]

# Use nearest neighbor
filename = "Mappe1.xlsx"  # Copy file path
sheet_name = "Tabelle1"  # Specify the name of the sheet or its index
capacity = 2010  # Specify the capacity of the vehicle
solution, coordinates = vrp_solver(filename, sheet_name, capacity)

for route in solution:
    print(route)

# Plot the routes
plot_routes(solution, coordinates, location_names)
