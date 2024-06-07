from django.shortcuts import render
from django.http import JsonResponse
import networkx as nx
import json
from math import radians, sin, cos, sqrt, atan2
from geopy.distance import geodesic


def haversine_distance(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * atan2(sqrt(a), sqrt(1-a))
    R = 6371  # Radius of the Earth in kilometers
    distance = R * c
    return distance

# Heuristic function for A* 
def heuristic(u, v):
    return haversine_distance(u[1], u[0], v[1], v[0])


with open('path_app/oran_ways.geojson', 'r', encoding='utf-8') as f:
    data = json.load(f)

G = nx.Graph()

for feature in data['features']:
    if feature['geometry']['type'] == 'LineString':
        way_coords = feature['geometry']['coordinates']
        for i in range(len(way_coords) - 1):
            u = tuple(way_coords[i])  
            v = tuple(way_coords[i + 1]) 
            distance = haversine_distance(v[1], v[0], u[1], u[0])  
            G.add_edge(v, u, weight=distance)
            
def find_nearest_node(G, lat, lon):
    min_dist = float('inf')
    nearest_node = None
    for node in G.nodes:
        node_lat, node_lon = node
        dist = haversine_distance(lat, lon, node_lat, node_lon)
        if dist < min_dist:
            min_dist = dist
            nearest_node = node
    print(f"Nearest node to ({lat}, {lon}) is {nearest_node} with distance {min_dist}")
    return nearest_node




def index(request):
    return render(request, 'index.html')

# Assuming the average walking speed is 5 km/h
WALKING_SPEED_KMH = 5

def calculate_distance(path):
    distance = 0.0
    for i in range(len(path) - 1):
        start_point = path[i]
        end_point = path[i + 1]
        distance += geodesic((start_point[1], start_point[0]), (end_point[1], end_point[0])).km
    return distance


def calculate_path(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        start_lat, start_lon = data['start']['lat'], data['start']['lng']
        end_lat, end_lon = data['end']['lat'], data['end']['lng']

        # Find the nearest nodes in the graph
        start_node = find_nearest_node(G, start_lon, start_lat)
        end_node = find_nearest_node(G, end_lon ,end_lat )

        # Calculate the shortest path using A*
        if start_node and end_node:
            shortest_path = nx.astar_path(G, start_node, end_node, weight='weight', heuristic=heuristic)

            distance = calculate_distance(shortest_path)

            estimated_time_hours = distance / WALKING_SPEED_KMH
            estimated_time_minutes = estimated_time_hours * 60

            path = [(node[0], node[1]) for node in shortest_path]  # Reverse the coordinates for Leaflet
            return JsonResponse({ 
            'path': path,
            'distance': distance,
            'estimated_time_minutes': estimated_time_minutes})
        else:
            return JsonResponse({'error': 'Could not find nearest nodes for the given coordinates.'}, status=400)
