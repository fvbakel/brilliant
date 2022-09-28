from basegrid import *
import logging
import unittest

class TestBasegrid(unittest.TestCase):

    def test_direction(self):
        l = Direction.LEFT
        self.assertTrue(l==Direction.LEFT)
        r = Direction.reverse(l)
        self.assertTrue(r==Direction.RIGHT)

def main():
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()

if __name__ == "__main__":
    main()