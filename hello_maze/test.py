import logging
import unittest
from test_basegrid import *
from test_gamegrid import *
from test_graph import *
from test_maze import *


def main():
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()

if __name__ == "__main__":
    main()