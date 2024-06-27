class CVRP:
    def __init__(self, depot, customers, distances, demands, capacity, num_vehicles):
        self.depot = depot
        self.customers = customers
        self.distances = distances
        self.demands = demands
        self.capacity = capacity
        self.num_vehicles = num_vehicles
        self.routes = [[depot, customer, depot] for customer in customers]
    
    def calculate_savings(self):
        savings = {}
        for i in self.customers:
            for j in self.customers:
                if i != j:
                    savings[(i, j)] = self.distances[self.depot][i] + self.distances[self.depot][j] - self.distances[i][j]
        return sorted(savings.items(), key=lambda item: item[1], reverse=True)
    
    def merge_routes(self, savings):
        for (i, j), saving in savings:
            route_i = next((route for route in self.routes if i in route), None)
            route_j = next((route for route in self.routes if j in route), None)
            if route_i and route_j and route_i != route_j:
                total_demand = sum(self.demands[node] for node in route_i[1:-1] + route_j[1:-1])
                if total_demand <= self.capacity:
                    new_route = route_i[:-1] + route_j[1:]
                    self.routes.remove(route_i)
                    self.routes.remove(route_j)
                    self.routes.append(new_route)
    
    def solve(self):
        savings = self.calculate_savings()
        self.merge_routes(savings)
        return self.routes[:self.num_vehicles]

# Beispielproblem
depot = 0
customers = [1, 2, 3, 4]
distances = [
    [0, 10, 15, 0, 10],
    [10, 0, 30, 25, 30],
    [15, 30, 0, 30, 20],
    [20, 25, 30, 0, 15],
    [10, 30, 20, 15, 0]
]
demands = [0, 5, 10, 5, 10]
capacity = 10
num_vehicles =2

# CVRP lösen
cvrp = CVRP(depot, customers, distances, demands, capacity, num_vehicles)
routes = cvrp.solve()
print("Endgültige Routen:", routes)
