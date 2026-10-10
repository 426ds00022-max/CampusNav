"""
Campus Navigator - Graph Data Structure and Pathfinding Algorithms
-------------------------------------------------------------------
Core data structures logic for campus navigation:
1. CAMPUS_GRAPH: Undirected Adjacency List.
2. find_shortest_path_bfs: Breadth-First Search for minimum connection count.
3. find_all_paths: Depth-First Search with backtracking to find all alternative simple paths.
"""

from collections import deque

# ============================================================================
# 1. CAMPUS GRAPH DATA STRUCTURE (Adjacency List)
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

# Schematic campus coordinates for SVG map (X, Y on a 1000 x 620 canvas)
LOCATION_COORDINATES = {
    "Main Gate": {"x": 120, "y": 500, "category": "Entrance"},
    "Main Block": {"x": 110, "y": 320, "category": "Academic"},
    "Quadrangle": {"x": 260, "y": 380, "category": "Central"},
    "St. Thomas's Hall": {"x": 300, "y": 520, "category": "Residence"},
    "Martin Junction": {"x": 490, "y": 520, "category": "Junction"},
    "Library": {"x": 670, "y": 500, "category": "Academic"},
    "Botany Tank": {"x": 860, "y": 420, "category": "Scenic"},
    "Principal's Residence": {"x": 870, "y": 240, "category": "Admin"},
    "MRF": {"x": 750, "y": 120, "category": "Facility"},
    "Bell Tower": {"x": 560, "y": 100, "category": "Landmark"},
    "CUS": {"x": 380, "y": 120, "category": "Dining"},
    "Zoology Tank": {"x": 480, "y": 230, "category": "Scenic"},
    "Bishop Heber Hall": {"x": 310, "y": 220, "category": "Residence"},
    "Selaiyur Hall": {"x": 400, "y": 340, "category": "Residence"},
}


# ============================================================================
# 2. BREADTH-FIRST SEARCH (BFS) - SUGGESTED SHORTEST ROUTE
# ============================================================================
def find_shortest_path_bfs(graph, start, destination):
    """
    Finds the shortest path between start and destination in an unweighted graph.
    BFS traverses layer-by-layer; the first time it reaches destination, the
    path has the minimum number of connections.
    """
    if start not in graph or destination not in graph:
        return None, -1

    if start == destination:
        return [start], 0

    queue = deque([(start, [start])])
    visited = {start}

    while queue:
        current_location, current_path = queue.popleft()

        for neighbor in graph.get(current_location, []):
            if neighbor not in visited:
                new_path = current_path + [neighbor]

                if neighbor == destination:
                    connections = len(new_path) - 1
                    return new_path, connections

                visited.add(neighbor)
                queue.append((neighbor, new_path))

    return None, -1


# ============================================================================
# 3. DEPTH-FIRST SEARCH (DFS) WITH BACKTRACKING - ALL POSSIBLE WAYS
# ============================================================================
def find_all_paths(graph, start, destination, max_paths=10):
    """
    Finds all possible simple paths between start and destination.
    A simple path never visits any location more than once (no infinite cycles).
    
    Returns:
    - List of paths, sorted in ascending order of connection count
      so that the shortest route is always the first recommendation!
    """
    if start not in graph or destination not in graph:
        return []

    if start == destination:
        return [[start]]

    all_paths = []

    def dfs(current, visited, current_path):
        # Prevent runaway recursion by capping total simple paths
        if len(all_paths) >= max_paths:
            return

        if current == destination:
            all_paths.append(list(current_path))
            return

        for neighbor in graph.get(current, []):
            if neighbor not in visited:
                visited.add(neighbor)
                current_path.append(neighbor)
                dfs(neighbor, visited, current_path)
                # Backtrack: unmark neighbor so other alternative routes can use it
                current_path.pop()
                visited.remove(neighbor)

    visited_set = {start}
    dfs(start, visited_set, [start])

    # Sort so the shortest route is at index 0 (suggested route)
    all_paths.sort(key=lambda p: len(p))
    return all_paths
