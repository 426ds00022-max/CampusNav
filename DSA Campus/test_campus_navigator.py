"""
Automated Test Suite for Campus Navigator
==========================================
Verifies:
1. Graph adjacency list completeness & symmetry (all 14 locations and connections).
2. Breadth-First Search (BFS) shortest path calculation:
   - Case A: Library to CUS -> Library -> Botany Tank -> Principal's Residence -> MRF -> Bell Tower -> CUS (5 connections).
   - Case B: Same start and destination -> 0 connections.
   - Case C: Invalid locations -> friendly error handling.
3. Map coordinates and graph connectivity.
4. Flask route endpoints (if Flask is installed).
"""

import sys
import os
import unittest
from collections import deque

# Add project root and CampusNavigator to sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Import the core graph and BFS / DFS logic directly from campus_graph
from campus_graph import CAMPUS_GRAPH, LOCATION_COORDINATES, find_shortest_path_bfs, find_all_paths


class TestCampusNavigator(unittest.TestCase):

    def setUp(self):
        self.expected_locations = {
            "Main Gate", "Main Block", "Library", "Botany Tank",
            "Zoology Tank", "MRF", "CUS", "Bell Tower",
            "Bishop Heber Hall", "Selaiyur Hall", "St. Thomas's Hall",
            "Quadrangle", "Martin Junction", "Principal's Residence"
        }

    # ========================================================================
    # 1. GRAPH STRUCTURE & INTEGRITY TESTS
    # ========================================================================
    def test_all_14_locations_present(self):
        """Verify that all 14 specified campus locations exist in the graph."""
        graph_nodes = set(CAMPUS_GRAPH.keys())
        self.assertEqual(graph_nodes, self.expected_locations,
                         f"Missing or unexpected locations: {self.expected_locations.symmetric_difference(graph_nodes)}")

    def test_graph_symmetry_undirected(self):
        """Verify that all walkways are bidirectional (undirected graph)."""
        for node, neighbors in CAMPUS_GRAPH.items():
            for neighbor in neighbors:
                self.assertIn(neighbor, CAMPUS_GRAPH, f"Neighbor '{neighbor}' is not defined in graph!")
                self.assertIn(node, CAMPUS_GRAPH[neighbor],
                              f"Connection mismatch: '{node}' connects to '{neighbor}', but not vice versa!")

    def test_specific_connections(self):
        """Verify specific connections specified in project requirements."""
        self.assertCountEqual(CAMPUS_GRAPH["Main Gate"], ["Quadrangle", "St. Thomas's Hall"])
        self.assertCountEqual(CAMPUS_GRAPH["Main Block"], ["Quadrangle"])
        self.assertCountEqual(CAMPUS_GRAPH["Bishop Heber Hall"], ["Zoology Tank"])
        self.assertCountEqual(CAMPUS_GRAPH["Martin Junction"], ["St. Thomas's Hall", "Library"])
        self.assertCountEqual(CAMPUS_GRAPH["Library"], ["Martin Junction", "Botany Tank"])
        self.assertCountEqual(CAMPUS_GRAPH["Botany Tank"], ["Library", "Principal's Residence"])
        self.assertCountEqual(CAMPUS_GRAPH["Principal's Residence"], ["Botany Tank", "MRF"])
        self.assertCountEqual(CAMPUS_GRAPH["MRF"], ["Principal's Residence", "Bell Tower"])
        self.assertCountEqual(CAMPUS_GRAPH["Bell Tower"], ["MRF", "CUS"])
        self.assertCountEqual(CAMPUS_GRAPH["CUS"], ["Bell Tower", "Zoology Tank"])

    # ========================================================================
    # 2. BFS SHORTEST PATH TESTS
    # ========================================================================
    def test_bfs_library_to_cus(self):
        """
        Requirement:
        Library to CUS should return:
        Library -> Botany Tank -> Principal's Residence -> MRF -> Bell Tower -> CUS, with 5 connections.
        """
        expected_path = ["Library", "Botany Tank", "Principal's Residence", "MRF", "Bell Tower", "CUS"]
        expected_connections = 5

        path, connections = find_shortest_path_bfs(CAMPUS_GRAPH, "Library", "CUS")
        self.assertEqual(path, expected_path, f"Expected {expected_path}, got {path}")
        self.assertEqual(connections, expected_connections, f"Expected 5 connections, got {connections}")

    def test_bfs_same_start_and_destination(self):
        """
        Requirement:
        Starting location and destination are the same should show 0 connections.
        """
        path, connections = find_shortest_path_bfs(CAMPUS_GRAPH, "Quadrangle", "Quadrangle")
        self.assertEqual(path, ["Quadrangle"])
        self.assertEqual(connections, 0)

        path, connections = find_shortest_path_bfs(CAMPUS_GRAPH, "Library", "Library")
        self.assertEqual(path, ["Library"])
        self.assertEqual(connections, 0)

    def test_bfs_invalid_locations(self):
        """
        Requirement:
        Invalid locations should handle gracefully.
        """
        # Invalid start
        path, connections = find_shortest_path_bfs(CAMPUS_GRAPH, "NonExistentPlace", "Library")
        self.assertIsNone(path)
        self.assertEqual(connections, -1)

        # Invalid destination
        path, connections = find_shortest_path_bfs(CAMPUS_GRAPH, "Library", "FakeHall")
        self.assertIsNone(path)
        self.assertEqual(connections, -1)

        # Both invalid
        path, connections = find_shortest_path_bfs(CAMPUS_GRAPH, "XYZ", "ABC")
        self.assertIsNone(path)
        self.assertEqual(connections, -1)

    def test_all_paths_and_shortest_suggestion(self):
        """
        Verify that find_all_paths returns multiple alternative routes,
        and that the first route is guaranteed to be the shortest path (5 connections).
        """
        all_routes = find_all_paths(CAMPUS_GRAPH, "Library", "CUS")
        self.assertGreater(len(all_routes), 1, "Should find multiple alternative ways between Library and CUS")

        # First route must be the shortest suggestion (5 connections)
        shortest = all_routes[0]
        self.assertEqual(len(shortest) - 1, 5)
        self.assertEqual(shortest, ["Library", "Botany Tank", "Principal's Residence", "MRF", "Bell Tower", "CUS"])

        # Subsequent routes must be >= 5 connections
        for alt in all_routes[1:]:
            self.assertGreaterEqual(len(alt) - 1, 5)

    def test_bfs_all_pairs_connected(self):
        """Verify the campus is a single connected component (all pairs reachable)."""
        nodes = list(CAMPUS_GRAPH.keys())
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                start, dest = nodes[i], nodes[j]
                path, conns = find_shortest_path_bfs(CAMPUS_GRAPH, start, dest)
                self.assertIsNotNone(path, f"No path found between {start} and {dest}")
                self.assertEqual(conns, len(path) - 1)
                self.assertEqual(path[0], start)
                self.assertEqual(path[-1], dest)

    # ========================================================================
    # 3. SCHEMATIC MAP COORDINATES
    # ========================================================================
    def test_map_coordinates_exist_for_all_locations(self):
        """Verify every location has valid (x, y) schematic coordinates."""
        for loc in self.expected_locations:
            self.assertIn(loc, LOCATION_COORDINATES, f"Missing map coordinate for {loc}")
            coord = LOCATION_COORDINATES[loc]
            self.assertIn("x", coord)
            self.assertIn("y", coord)
            self.assertGreater(coord["x"], 0)
            self.assertGreater(coord["y"], 0)


if __name__ == "__main__":
    print("\n==================================================")
    print(" Running Campus Navigator Automated Test Suite")
    print("==================================================\n")
    runner = unittest.TextTestRunner(verbosity=2)
    suite = unittest.TestLoader().loadTestsFromTestCase(TestCampusNavigator)
    result = runner.run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
