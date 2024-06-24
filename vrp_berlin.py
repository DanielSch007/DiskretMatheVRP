import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from ortools.constraint_solver import pywrapcp, routing_enums_pb2

# Define the depot and customer locations
depot = (13.3694, 52.5259)  # Berlin Central Station coordinates
customers = [
    (13.4094, 52.5200),  # Alexanderplatz
    (13.3777, 52.5163),  # Brandenburg Gate
    (13.4386, 52.5194),  # East Side Gallery
    (13.3904, 52.5107),  # Checkpoint Charlie
    (13.3745, 52.5075),  # Potsdamer Platz
    (13.3280, 52.5076),  # Kurfürstendamm
    (13.4105, 52.5022),  # Mercedes-Benz Arena
    (13.4540, 52.5128)   # Treptower Park
]

demands = [1, 2, 1, 2, 1, 2, 1, 2]
vehicle_capacity = 10
num_vehicles = 3

def create_data_model():
    data = {}
    data['locations'] = [depot] + customers
    data['num_locations'] = len(data['locations'])
    data['num_vehicles'] = num_vehicles
    data['depot'] = 0
    data['demands'] = [0] + demands
    data['vehicle_capacities'] = [vehicle_capacity] * num_vehicles
    return data

def compute_euclidean_distance_matrix(locations):
    distances = np.zeros((len(locations), len(locations)))
    for i, loc1 in enumerate(locations):
        for j, loc2 in enumerate(locations):
            if i != j:
                distances[i][j] = np.linalg.norm(np.array(loc1) - np.array(loc2))
    return distances

def print_solution(data, manager, routing, solution):
    total_distance = 0
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        plan_output = 'Route for vehicle {}:\n'.format(vehicle_id)
        route_distance = 0
        while not routing.IsEnd(index):
            plan_output += ' {} ->'.format(manager.IndexToNode(index))
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(previous_index, index, vehicle_id)
        plan_output += ' {}\n'.format(manager.IndexToNode(index))
        plan_output += 'Distance of the route: {}m\n'.format(route_distance)
        print(plan_output)
        total_distance += route_distance
    print('Total distance of all routes: {}m'.format(total_distance))

def main():
    data = create_data_model()
    manager = pywrapcp.RoutingIndexManager(data['num_locations'], data['num_vehicles'], data['depot'])
    routing = pywrapcp.RoutingModel(manager)
    distance_matrix = compute_euclidean_distance_matrix(data['locations'])

    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return int(distance_matrix[from_node][to_node])

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    def demand_callback(from_index):
        from_node = manager.IndexToNode(from_index)
        return data['demands'][from_node]

    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,
        data['vehicle_capacities'],
        True,
        'Capacity')

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

    solution = routing.SolveWithParameters(search_parameters)
    if solution:
        print_solution(data, manager, routing, solution)
        return data, manager, routing, solution
    else:
        print('No solution found !')
        return None, None, None, None

def visualize_solution(data, manager, routing, solution):
    fig, ax = plt.subplots(figsize=(10, 10))
    berlin_shapefile_path = "ne_110m_admin_0_boundary_lines_land.shp"
    berlin_shapefile = gpd.read_file(berlin_shapefile_path)
    berlin_shapefile.plot(ax=ax, color='lightgrey')
    ax.set_title('Vehicle Routing Problem Solution in Berlin')

    ax.plot(depot[0], depot[1], 'rs', markersize=10, label='Depot')

    for i, customer in enumerate(customers):
        ax.plot(customer[0], customer[1], 'bo', markersize=5)
        ax.text(customer[0], customer[1], f' {i+1}', fontsize=12)

    colors = ['r', 'g', 'b', 'y', 'c', 'm']
    for vehicle_id in range(num_vehicles):
        index = routing.Start(vehicle_id)
        while not routing.IsEnd(index):
            from_node = manager.IndexToNode(index)
            previous_index = index
            index = solution.Value(routing.NextVar(index))
            to_node = manager.IndexToNode(index)
            if from_node != to_node:
                x_values = [data['locations'][from_node][0], data['locations'][to_node][0]]
                y_values = [data['locations'][from_node][1], data['locations'][to_node][1]]
                line = mlines.Line2D(x_values, y_values, color=colors[vehicle_id], linestyle='-', linewidth=2)
                ax.add_line(line)

    ax.legend()
    plt.show()

if __name__ == '__main__':
    data, manager, routing, solution = main()
    if solution:
        visualize_solution(data, manager, routing, solution)
