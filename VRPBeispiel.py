import requests
import folium

class CVRP:
    def __init__(self, depot, customers, distances, demands, capacity, num_vehicles):
        self.depot = depot
        self.customers = customers
        self.distances = distances
        self.demands = demands
        self.capacity = capacity
        self.num_vehicles = num_vehicles
        self.routes = [[depot, customer, depot] for customer in customers]
    
    # auf Folie 22 erklärt
    def calculate_savings(self):
        savings = {}
        for i in self.customers: #einsparung vo jeder möglichen kante berechnen
            for j in self.customers:
                if i != j:
                    savings[(i, j)] = self.distances[self.depot][i] + self.distances[self.depot][j] - self.distances[i][j]
        return sorted(savings.items(), key=lambda item: item[1], reverse=True)
    
    # auf Folie 24 erklärt
    def merge_routes(self, savings):
        for (i, j), saving in savings:
            route_i = next((route for route in self.routes if i in route), None)
            route_j = next((route for route in self.routes if j in route), None)
            if route_i and route_j and route_i != route_j:
                total_demand = sum(self.demands[node] for node in route_i[1:-1] + route_j[1:-1])
                if total_demand <= self.capacity: # wenn Kapazität erlaubt neue Route
                    new_route = route_i[:-1] + route_j[1:]
                    self.routes.remove(route_i)
                    self.routes.remove(route_j)
                    self.routes.append(new_route)
    
    def solve(self):
        savings = self.calculate_savings()
        self.merge_routes(savings)
        return self.routes[:self.num_vehicles]

# Daten aus Overpass API (https://python-overpy.readthedocs.io/en/latest/)
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

# Beispielproblem für Treptow-Köpenick
depot = (52.41667, 13.56667)  # Depot-Koordinaten (Beispiel)
customers = [(52.437, 13.568), (52.412, 13.565), (52.430, 13.572), (52.418, 13.563)]  # Kunden (Beispiel)
distances = {
    depot: {cust: 0 for cust in customers},
    **{cust: {cust2: 0 for cust2 in customers} for cust in customers}
}  # Distanzen (Beispiel, alle Distanzen sind 0)
demands = {cust: 1 for cust in customers}  # Bedarfe (Beispiel, alle Bedarfe sind 1)
capacity = 4  # Kapazität (Beispiel)
num_vehicles = 2  # Anzahl Fahrzeuge (Beispiel)

# VRP lösen
cvrp = CVRP(depot, customers, distances, demands, capacity, num_vehicles)
routes = cvrp.solve()

# Restaurants aus OpenStreetMap abrufen (Treptow-Köpenick)
area_name = 'Treptow-Köpenick'
restaurants = get_osm_restaurants(area_name)
print("Restaurants:", restaurants)  # Debugging-Ausgabe

# Karte erstellen und Depot, Restaurants, Routen einzeichnen
map_center = depot  # Zentrum der Karte auf das Depot setzen
map_osm = folium.Map(location=map_center, zoom_start=13)

# Depot markieren
folium.Marker(location=depot, popup='Depot', icon=folium.Icon(color='blue')).add_to(map_osm)

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
