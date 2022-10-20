import logging
import unittest
from test.test_basegrid import *
from test.test_gamegrid import *
from test.test_graph import *
from test.test_maze import *


def main():
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()

if __name__ == "__main__":
    main()