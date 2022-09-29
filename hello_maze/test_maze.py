from graph import *
from maze import *
import logging
import unittest

import os

TEST_TMP_DIR = "./tmp"

class TestGraph(unittest.TestCase):

    def test_maze_generator(self):
        size = Size(4,4)
        maze_gen =  MazeGraphGenerator(size)

        r = Graph2Dot(maze_gen.maze_graph.graph)
        r.render(self._testMethodName + "001" + ".dot",TEST_TMP_DIR)

        r = Squares2Dot(maze_gen.maze_graph.square_grid)
        r.render(self._testMethodName + "002" + ".dot",TEST_TMP_DIR)



def main():
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()

if __name__ == "__main__":
    main()