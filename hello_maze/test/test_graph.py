from graph import *
from test.test_config import *
import unittest

class TestGraph(unittest.TestCase):

    def test_fully_connected(self):
        graph = Graph()
        A = graph.get_or_create("A")
        B = graph.get_or_create("B")
        C = graph.get_or_create("C")
        D = graph.get_or_create("D")

        graph.first = A
        graph.last = D
        graph.create_edge_pair(A,B)
        graph.create_edge_pair(C,D)
        self.assertFalse(graph.is_fully_connected(),"Two separate groups")

        graph.create_edge_pair(A,C)
        self.assertTrue(graph.is_fully_connected(),"AC connects both groups")

        graph.create_edge_pair(B,D)
        self.assertTrue(graph.is_fully_connected(),"Recursive but fully connected")

        pairs = list(graph.edge_pairs)
        pairs[0].disable()
        self.assertTrue(graph.is_fully_connected(),"With one inactive edge pair still fully connected")

        pairs[1].disable()
        self.assertFalse(graph.is_fully_connected(),"With two inactive edge pairs no longer fully connected")

    def test_recursion(self):
        graph = Graph()
        A = graph.get_or_create("A")
        B = graph.get_or_create("B")
        C = graph.get_or_create("C")
        D = graph.get_or_create("D")

        graph.first = A
        graph.last = D
        graph.create_edge_pair(A,B)
        graph.create_edge_pair(C,D)

        self.assertFalse(graph.check_recursion_first(),"Not fully connected and not recursive")
        graph.create_edge_pair(A,C)
        self.assertFalse(graph.check_recursion_first(),"Connected in one direction only")
        graph.create_edge_pair(B,D)
        self.assertTrue(graph.check_recursion_first(),"recursion A -> B -> D -> c -> A")

        pairs = list(graph.edge_pairs)
        pairs[0].disable()
        self.assertFalse(graph.check_recursion_first(),"recursion broken with inactive edge")

    def test_graph2Dot(self):
        graph = Graph()
        A = graph.get_or_create("A")
        B = graph.get_or_create("B")
        C = graph.get_or_create("C")
        D = graph.get_or_create("D")

        graph.first = A
        graph.last = D
        graph.create_edge_pair(A,B)
        graph.create_edge_pair(C,D)

        r = Graph2Dot(graph)
        r.render(self._testMethodName + "001" + ".dot",TEST_TMP_DIR)
