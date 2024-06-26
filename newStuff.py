from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import matplotlib.pyplot as plt
import numpy as np

def create_data_model():
    """Stores the data for the problem."""
    data = {}
    data['distance_matrix'] = [
        [0, 29, 20, 21, 16, 31, 100],  # distances from depot (index 0) to customers 1-6, and a "non-customer" location (7)
        [29, 0, 15, 29, 28, 15, 100],  # distances from customer 1 to others and to the "non-customer" location
        [20, 15, 0, 15, 14, 25, 100],  # distances from customer 2 to others and to the "non-customer" location
        [21, 29, 15, 0, 4, 23, 100],   # distances from customer 3 to others and to the "non-customer" location
        [16, 28, 14, 4, 0, 10, 100],   # distances from customer 4 to others and to the "non-customer" location
        [31, 15, 25, 23, 10, 0, 100],  # distances from customer 5 to others and to the "non-customer" location
        [100, 100, 100, 100, 100, 100, 0],  # distances from the "non-customer" location (7) to any location
    ]

    data['demands'] = [0, 10, 5, 8, 6, 7, 0]  # demand of each customer (0 for depot), and the "non-customer" location
    data['time_windows'] = [
        (0, 5),    # depot
        (7, 12),   # 1st location
        (10, 15),  # 2nd location
        (16, 18),  # 3rd location
        (10, 13),  # 4th location
        (0, 5),    # 5th location (depot could visit it also)
        (0, 5)     # 6th location (depot could visit it also)
    ]
    data['vehicle_capacities'] = [15, 15, 15]  # capacity of each vehicle
    data['num_vehicles'] = 3
    data['depot'] = 0
    return data

def plot_solution(data, manager, routing, solution):
    """Plot the solution."""
    fig, ax = plt.subplots(figsize=(10, 8))

    # Plot all the nodes
    for i in range(len(data['distance_matrix'])):
        if i == 0:
            ax.scatter(0, 0, marker='s', color='b', label='Depot')
        elif i == len(data['distance_matrix']) - 1:
            ax.scatter(0, 0, marker='x', color='r', label='Non-customer location')
        else:
            ax.scatter(i, 0, color='g', label=f'Customer {i}')

    # Plot the routes
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        route = []
        while not routing.IsEnd(index):
            node_index = manager.IndexToNode(index)
            route.append(node_index)
            index = solution.Value(routing.NextVar(index))
        route.append(0)  # Adding depot to the end of each route
        route_coords = np.array([(node, 0) for node in route])
        ax.plot(route_coords[:, 0], route_coords[:, 1], marker='o')

    ax.legend()
    ax.set_title('Vehicle Routing Problem')
    ax.set_xlabel('X coordinate')
    ax.set_ylabel('Y coordinate')
    plt.grid(visible=True)
    plt.show()

def main():
    """Solve the VRP problem."""
    data = create_data_model()

    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']),
                                           data['num_vehicles'], data['depot'])

    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)

    # Define cost of each arc.
    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Add Time Windows constraint.
    time = 'Time'
    routing.AddDimension(
        transit_callback_index,
        30,  # allow waiting time
        30,  # maximum time per vehicle
        False,  # Don't force start cumul to zero.
        time)
    time_dimension = routing.GetDimensionOrDie(time)
    for location_idx, time_window in enumerate(data['time_windows']):
        index = manager.NodeToIndex(location_idx)
        time_dimension.CumulVar(index).SetRange(time_window[0], time_window[1])

    # Add Capacity constraint.
    def demand_callback(from_index):
        """Returns the demand of the node."""
        from_node = manager.IndexToNode(from_index)
        return data['demands'][from_node]

    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # null capacity slack
        data['vehicle_capacities'],  # vehicle maximum capacities
        True,  # start cumul to zero
        'Capacity')

    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

    # Solve the problem.
    solution = routing.SolveWithParameters(search_parameters)

    # Print solution on console.
    if solution:
        print('Objective: {}'.format(solution.ObjectiveValue()))
        index = routing.Start(0)
        plan_output = 'Routes:\n'
        while not routing.IsEnd(index):
            plan_output += ' {} -> '.format(manager.IndexToNode(index))
            index = solution.Value(routing.NextVar(index))
        plan_output += ' {}\n'.format(manager.IndexToNode(index))
        print(plan_output)

        # Plotting the solution
        plot_solution(data, manager, routing, solution)
    else:
        print('No solution found !')

if __name__ == '__main__':
    main()
