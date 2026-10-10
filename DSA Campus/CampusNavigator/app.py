"""
Campus Navigator - Flask Application
-------------------------------------
A beginner-friendly web application that helps college students find the shortest 
route between campus locations using a Graph data structure and Breadth-First Search (BFS).
"""

import os
from flask import Flask, render_template, request, jsonify
from collections import deque

# Get absolute path to the directory containing this app.py
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Initialize the Flask application with explicit template and static paths
app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static")
)

# ============================================================================
# 1. CAMPUS GRAPH DATA STRUCTURE (Adjacency List)
# ============================================================================
# A graph consists of:
# - Vertices (Nodes): Campus locations (e.g., Library, Quadrangle)
# - Edges: Walkways/roads connecting two locations.
#
# We use a Python Dictionary where:
# Key   = Location name (String)
# Value = List of neighboring locations directly connected by a walkway
#
# Because walkways can be walked in both directions, the graph is "Undirected".
# ============================================================================

CAMPUS_GRAPH = {
    "Main Gate": [
        "Quadrangle",
        "St. Thomas's Hall"
    ],
    "Quadrangle": [
        "Main Gate",
        "Main Block",
        "Selaiyur Hall",
        "St. Thomas's Hall"
    ],
    "Main Block": [
        "Quadrangle"
    ],
    "St. Thomas's Hall": [
        "Main Gate",
        "Martin Junction",
        "Quadrangle"
    ],
    "Martin Junction": [
        "St. Thomas's Hall",
        "Library"
    ],
    "Library": [
        "Martin Junction",
        "Botany Tank"
    ],
    "Botany Tank": [
        "Library",
        "Principal's Residence"
    ],
    "Principal's Residence": [
        "Botany Tank",
        "MRF"
    ],
    "MRF": [
        "Principal's Residence",
        "Bell Tower"
    ],
    "Bell Tower": [
        "MRF",
        "CUS"
    ],
    "CUS": [
        "Bell Tower",
        "Zoology Tank"
    ],
    "Zoology Tank": [
        "CUS",
        "Selaiyur Hall",
        "Bishop Heber Hall"
    ],
    "Selaiyur Hall": [
        "Zoology Tank",
        "Quadrangle"
    ],
    "Bishop Heber Hall": [
        "Zoology Tank"
    ]
}

# Node coordinates for the schematic campus map (X, Y in a 1000 x 620 SVG canvas)

LOCATION_COORDINATES = {
    "Main Gate": {"x": 100, "y": 500, "category": "Entrance"},
    "Main Block": {"x": 170, "y": 330, "category": "Academic"},
    "Quadrangle": {"x": 260, "y": 400, "category": "Central"},
    "St. Thomas's Hall": {"x": 200, "y": 510, "category": "Residence"},
    "Martin Junction": {"x": 350, "y": 510, "category": "Junction"},
    "Library": {"x": 480, "y": 470, "category": "Academic"},
    "Botany Tank": {"x": 590, "y": 390, "category": "Scenic"},
    "Principal's Residence": {"x": 620, "y": 260, "category": "Admin"},
    "MRF": {"x": 540, "y": 140, "category": "Facility"},
    "Bell Tower": {"x": 400, "y": 110, "category": "Landmark"},
    "CUS": {"x": 270, "y": 150, "category": "Dining"},
    "Zoology Tank": {"x": 330, "y": 250, "category": "Scenic"},
    "Bishop Heber Hall": {"x": 180, "y": 220, "category": "Residence"},
    "Selaiyur Hall": {"x": 360, "y": 350, "category": "Residence"},
}


# ============================================================================
# 2. BREADTH-FIRST SEARCH (BFS) ALGORITHM
# ============================================================================
def find_shortest_path_bfs(graph, start, destination):
    """
    Finds the shortest path between start and destination in an unweighted graph.
    
    Why BFS?
    - BFS explores neighbors level by level (1 hop away, then 2 hops away, etc.).
    - In an unweighted graph, the first time BFS reaches the destination node,
      the path taken is guaranteed to have the minimum number of connections (edges).

    Data Structures:
    - Queue (collections.deque): Stores paths to explore in First-In-First-Out (FIFO) order.
    - Set (visited): Keeps track of visited locations to prevent infinite loops.
    
    Returns:
    - (path, connections_count): A tuple of (list of location names, integer number of connections).
      Returns (None, -1) if no path exists.
    """
    # Case 1: Start or destination does not exist in graph
    if start not in graph or destination not in graph:
        return None, -1

    # Case 2: Start and destination are the exact same location
    if start == destination:
        return [start], 0

    # Initialize the BFS Queue
    # We store tuples of (current_node, path_taken_so_far)
    queue = deque([(start, [start])])
    
    # Visited set ensures we don't re-visit locations and prevents infinite loops
    visited = {start}

    while queue:
        # Dequeue the oldest element (FIFO)
        current_location, current_path = queue.popleft()

        # Explore all directly connected neighbors of the current location
        for neighbor in graph.get(current_location, []):
            if neighbor not in visited:
                new_path = current_path + [neighbor]

                # Check if we have reached our destination
                if neighbor == destination:
                    connections = len(new_path) - 1
                    return new_path, connections

                # Mark as visited and add to queue to explore its neighbors later
                visited.add(neighbor)
                queue.append((neighbor, new_path))

    # If the queue becomes empty and destination was never reached
    return None, -1


# ============================================================================
# 3. FLASK WEB ROUTES & API ENDPOINTS
# ============================================================================

@app.route("/")
def index():
    """Render the main Campus Navigator webpage."""
    locations = sorted(list(CAMPUS_GRAPH.keys()))
    return render_template("index.html", locations=locations)


@app.route("/api/locations", methods=["GET"])
def get_locations():
    """
    API endpoint to return all campus locations and their map coordinates.
    Useful for frontend rendering of dropdowns and interactive SVG map.
    """
    return jsonify({
        "success": True,
        "locations": sorted(list(CAMPUS_GRAPH.keys())),
        "coordinates": LOCATION_COORDINATES
    })


@app.route("/api/graph", methods=["GET"])
def get_graph():
    """API endpoint to inspect the full campus adjacency list and coordinates."""
    # Build list of unique edges for frontend SVG rendering
    unique_edges = []
    seen_edges = set()
    for node, neighbors in CAMPUS_GRAPH.items():
        for neighbor in neighbors:
            edge_id = tuple(sorted([node, neighbor]))
            if edge_id not in seen_edges:
                seen_edges.add(edge_id)
                unique_edges.append({"from": edge_id[0], "to": edge_id[1]})

    return jsonify({
        "success": True,
        "nodes": list(CAMPUS_GRAPH.keys()),
        "edges": unique_edges,
        "coordinates": LOCATION_COORDINATES
    })


@app.route("/api/route", methods=["POST"])
def get_route():
    """
    API endpoint to calculate the shortest route between two locations.
    
    Accepts JSON body:
    {
        "start": "Library",
        "destination": "CUS"
    }
    
    Returns JSON body:
    {
        "success": True,
        "start": "Library",
        "destination": "CUS",
        "path": ["Library", "Botany Tank", "Principal's Residence", "MRF", "Bell Tower", "CUS"],
        "connections": 5,
        "message": "Route found successfully!"
    }
    """
    data = request.get_json(silent=True) or {}
    start = data.get("start", "").strip()
    destination = data.get("destination", "").strip()

    # Validation: Check if inputs are provided
    if not start or not destination:
        return jsonify({
            "success": False,
            "error": "Please select both a starting location and a destination."
        }), 400

    # Validation: Check if locations exist in the campus graph
    if start not in CAMPUS_GRAPH:
        return jsonify({
            "success": False,
            "error": f"Starting location '{start}' is not recognized on campus."
        }), 400

    if destination not in CAMPUS_GRAPH:
        return jsonify({
            "success": False,
            "error": f"Destination '{destination}' is not recognized on campus."
        }), 400

    # Run the BFS algorithm
    path, connections = find_shortest_path_bfs(CAMPUS_GRAPH, start, destination)

    if path is None:
        return jsonify({
            "success": False,
            "error": f"No accessible route found between '{start}' and '{destination}'."
        }), 404

    # Build friendly response
    if connections == 0:
        message = f"You are already at {start}! No walking required (0 connections)."
    else:
        message = f"Shortest route found with {connections} connection{'s' if connections != 1 else ''}."

    return jsonify({
        "success": True,
        "start": start,
        "destination": destination,
        "path": path,
        "connections": connections,
        "message": message
    })


# ============================================================================
# 4. APPLICATION ENTRY POINT
# ============================================================================
if __name__ == "__main__":
    print("=" * 60)
    print(" Campus Navigator - Local Development Server")
    print(" Available at: http://127.0.0.1:5000")
    print("=" * 60)
    app.run(debug=True, host="127.0.0.1", port=5000)
