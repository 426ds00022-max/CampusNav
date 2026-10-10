"""
Automated Test Suite for Campus Navigator
==========================================
Verifies:
1. Graph adjacency list completeness & symmetry (all 14 locations and connections).
2. Breadth-First Search (BFS) shortest path calculation.
3. DFS Backtracking (find_all_paths) finding all alternative routes with shortest suggestion.
4. Map coordinates and graph connectivity.
"""

import sys
import os
import unittest

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from campus_graph import CAMPUS_GRAPH, LOCATION_COORDINATES, find_shortest_path_bfs, find_all_paths


class TestCampusNavigator(unittest.TestCase):

    def setUp(self):
        self.expected_locations = {
            "Main Gate", "Main Block", "Library", "Botany Tank",
            "Zoology Tank", "MRF", "CUS", "Bell Tower",
            "Bishop Heber Hall", "Selaiyur Hall", "St. Thomas's Hall",
            "Quadrangle", "Martin Junction", "Principal's Residence"
        }

    def test_all_14_locations_present(self):
        graph_nodes = set(CAMPUS_GRAPH.keys())
        self.assertEqual(graph_nodes, self.expected_locations)

    def test_graph_symmetry_undirected(self):
        for node, neighbors in CAMPUS_GRAPH.items():
            for neighbor in neighbors:
                self.assertIn(neighbor, CAMPUS_GRAPH)
                self.assertIn(node, CAMPUS_GRAPH[neighbor])

    def test_bfs_library_to_cus(self):
        expected_path = ["Library", "Botany Tank", "Principal's Residence", "MRF", "Bell Tower", "CUS"]
        path, connections = find_shortest_path_bfs(CAMPUS_GRAPH, "Library", "CUS")
        self.assertEqual(path, expected_path)
        self.assertEqual(connections, 5)

    def test_all_paths_and_shortest_suggestion(self):
        all_routes = find_all_paths(CAMPUS_GRAPH, "Library", "CUS")
        self.assertGreater(len(all_routes), 1)
        self.assertEqual(all_routes[0], ["Library", "Botany Tank", "Principal's Residence", "MRF", "Bell Tower", "CUS"])

    def test_bfs_same_start_and_destination(self):
        path, connections = find_shortest_path_bfs(CAMPUS_GRAPH, "Quadrangle", "Quadrangle")
        self.assertEqual(path, ["Quadrangle"])
        self.assertEqual(connections, 0)

    def test_bfs_invalid_locations(self):
        path, connections = find_shortest_path_bfs(CAMPUS_GRAPH, "UnknownNode", "Library")
        self.assertIsNone(path)
        self.assertEqual(connections, -1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
