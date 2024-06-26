import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import geopandas as gpd
import contextily as ctx
from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver import routing_enums_pb2

# Coordinates and names for the Ritz Carlton Hotel in Berlin and sightseeing attractions
depot = (13.3767, 52.5096)
depot_name = "Ritz Carlton Hotel"

sightseeing_attractions = [
    (13.3777, 52.5163, 'Brandenburg Gate'),
    (13.3752, 52.5096, 'Potsdamer Platz'),
    (13.3830, 52.5186, 'Reichstag Building'),
    (13.3916, 52.5325, 'Berlin Wall Memorial'),
    (13.3976, 52.5319, 'Museum Island'),
    (13.2837, 52.5186, 'Charlottenburg Palace'),
    (13.4009, 52.5192, 'Berlin Cathedral'),
    (13.3904, 52.5076, 'Checkpoint Charlie'),
    (13.4390, 52.5027, 'East Side Gallery'),
    (13.4132, 52.5219, 'Alexanderplatz'),
]

# Number of vehicles
num_vehicles = 1

# Data model
data = {
    'locations': [depot] + [loc[:2] for loc in sightseeing_attractions],
    'num_locations': 1 + len(sightseeing_attractions),
    'num_vehicles': num_vehicles,
    'depot': 0
}

# Visualization function
def visualize_tourist_route(data, manager, routing, solution):
    fig, ax = plt.subplots(figsize=(15, 10))
    ax.set_title('Tourist Route in Berlin')

    # Plot depot
    ax.plot(depot[0], depot[1], 'rs', markersize=10, label=depot_name)

    # Plot sightseeing attractions
    for i, (x, y, name) in enumerate(sightseeing_attractions, start=1):
        ax.plot(x, y, 'go', markersize=5, label=f'S{i}: {name}')
        ax.text(x, y, f'S{i}', fontsize=12, ha='right')

    # Plot route
    colors = ['b']
    visit_orders = [[] for _ in range(num_vehicles)]

    for vehicle_id in range(num_vehicles):
        index = routing.Start(vehicle_id)
        while not routing.IsEnd(index):
            from_node = manager.IndexToNode(index)
            visit_orders[vehicle_id].append(from_node)
            index = solution.Value(routing.NextVar(index))
        visit_orders[vehicle_id].append(manager.IndexToNode(index))

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

    # Set x and y axis limits to zoom in on Berlin
    ax.set_xlim([13.2, 13.6])
    ax.set_ylim([52.4, 52.6])

    # Add basemap
    berlin_df = gpd.GeoDataFrame(geometry=gpd.points_from_xy([x[0] for x in data['locations']], [x[1] for x in data['locations']]))
    berlin_df = berlin_df.set_crs(epsg=4326)
    berlin_df = berlin_df.to_crs(epsg=3857)
    ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik, crs=berlin_df.crs.to_string(), zoom=12)


    # Create legend for visit order
    visit_legend = []
    for i in range(num_vehicles):
        visit_order_str = ', '.join([f'S{node}' if node > 0 else '' for node in visit_orders[i]])
        visit_legend.append(mlines.Line2D([], [], color='white', marker='o', markersize=10, label=f'Tourist {i+1}: {visit_order_str}'))
    
    ax.legend(handles=visit_legend, loc='lower right', title='Visit Order', fontsize='small')



    plt.show()

# Dummy main function to call the visualizer
def main():
    manager = pywrapcp.RoutingIndexManager(len(data['locations']), data['num_vehicles'], data['depot'])
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return int(((data['locations'][from_node][0] - data['locations'][to_node][0]) ** 2 +
                    (data['locations'][from_node][1] - data['locations'][to_node][1]) ** 2) ** 0.5)

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

    solution = routing.SolveWithParameters(search_parameters)
    return data, manager, routing, solution

# Run the VRP solution and visualize
if __name__ == '__main__':
    data, manager, routing, solution = main()
    if solution:
        visualize_tourist_route(data, manager, routing, solution)
