import requests
import folium
import geopy.distance

class CVRP:
    def __init__(self, depot, customers, distances, demands, capacity, num_vehicles):
        self.depot = depot
        self.customers = customers
        self.distances = distances
        self.demands = demands
        self.capacity = capacity
        self.num_vehicles = num_vehicles
        self.routes = [[depot, customer, depot] for customer in customers]
    
    #einsparung berechnen (Folie 22) von jeder möglichen Kante
    def calculate_savings(self):
        savings = {}
        for i in self.customers:
            for j in self.customers:
                if i != j:
                    savings[(i, j)] = self.distances[self.depot][i] + self.distances[self.depot][j] - self.distances[i][j]
        return sorted(savings.items(), key=lambda item: item[1], reverse=True)
    
    #Routen kombinieren wenn die Nebenbedingungen es zulassen (Folie 24)
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
    
# Overpass API (https://python-overpy.readthedocs.io/en/latest/) für Map Daten
def get_osm_restaurants(area_name):
    overpass_url = "http://overpass-api.de/api/interpreter"
    overpass_query = f"""
    [out:json];
    area[name="{area_name}"]->.a;
    node(area.a)[amenity=restaurant];
    out center;
    """
    response = requests.get(overpass_url, params={'data': overpass_query})
    data = response.json()
    
    restaurants = []
    for element in data['elements']:
        name = element.get('tags', {}).get('name', 'Unnamed')
        lat = element['lat']
        lon = element['lon']
        restaurants.append({'name': name, 'location': (lat, lon)})
    
    return restaurants

# Distanz berechnung mit geopy
def calculate_distance_matrix(depot, customers):
    locations = [depot] + customers
    distances = {}
    for loc1 in locations:
        distances[loc1] = {}
        for loc2 in locations:
            if loc1 == loc2:
                distances[loc1][loc2] = 0
            else:
                distances[loc1][loc2] = geopy.distance.distance(loc1, loc2).km
    return distances

# HTW-Berlin als Depot
depot = (52.45731, 13.52637)  # HTW Berlin Koordinaten

# Restaurants aus OpenStreetMap abrufen (Treptow-Köpenick)
area_name = 'Treptow-Köpenick'
restaurants = get_osm_restaurants(area_name)
customers = [tuple(rest['location']) for rest in restaurants]
demands = {customer: 1 for customer in customers}  # Beispiel: alle Restaurants haben Bedarf von 1
capacity = 4  # Beispiel: Kapazität eines Fahrzeugs
num_vehicles = 3  # Beispiel: Anzahl der Fahrzeuge

# Distanzmatrix berechnen
distances = calculate_distance_matrix(depot, customers)

# VRP lösen
cvrp = CVRP(depot, customers, distances, demands, capacity, num_vehicles)
routes = cvrp.solve()

# Karte erstellen und Depot, Restaurants, Routen einzeichnen
map_center = depot  # Zentrum der Karte auf das Depot setzen
map_osm = folium.Map(location=map_center, zoom_start=13)

# Depot markieren
folium.Marker(location=depot, popup='Depot (HTW Berlin)', icon=folium.Icon(color='blue')).add_to(map_osm)

# Restaurants einzeichnen
for restaurant in restaurants:
    folium.Marker(location=restaurant['location'], popup=restaurant['name']).add_to(map_osm)

# Routen einzeichnen
for route in routes:
    folium.PolyLine(locations=route, color='red', weight=2.5, opacity=0.8).add_to(map_osm)

# Karte als HTML-Datei speichern und im Browser öffnen
map_osm.save('treptow_koepenick_vrp_map.html')
import webbrowser
webbrowser.open('treptow_koepenick_vrp_map.html')
