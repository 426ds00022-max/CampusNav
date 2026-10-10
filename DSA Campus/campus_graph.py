"""
Campus Navigator - Graph Data Structure and Pathfinding Algorithms
-------------------------------------------------------------------
Core data structures logic for campus navigation:
1. CAMPUS_GRAPH: Undirected Adjacency List.
2. find_shortest_path_bfs: Breadth-First Search for minimum connection count.
3. find_all_paths: Depth-First Search with backtracking to find all alternative simple paths.
"""

from collections import deque

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


def find_shortest_path_bfs(graph, start, destination):
    """
    Finds the shortest path between start and destination in an unweighted graph.
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

def find_all_paths(graph, start, destination, max_paths=10):
    """
    Finds all possible simple paths between start and destination.
    Returns list of paths sorted by connection count (shortest first).
    """
    if start not in graph or destination not in graph:
        return []

    if start == destination:
        return [[start]]

    all_paths = []

    def dfs(current, visited, current_path):
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
                current_path.pop()
                visited.remove(neighbor)

    visited_set = {start}
    dfs(start, visited_set, [start])

    all_paths.sort(key=lambda p: len(p))
    return all_paths
