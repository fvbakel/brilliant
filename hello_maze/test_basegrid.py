from basegrid import *
import logging
import unittest

class TestBasegrid(unittest.TestCase):

    def test_direction(self):
        l = Direction.LEFT
        self.assertTrue(l==Direction.LEFT)
        r = Direction.reverse(l)
        self.assertTrue(r==Direction.RIGHT)

    def test_position(self):
        base = Position(5,5)
        
        base    = Position(5,5)
        up      = Position(5,4)
        right   = Position(6,5)
        down    = Position(5,6)
        left    = Position(4,5)
        here    = Position(5,5)

        self.assertEqual(base.get_direction(up),Direction.UP)
        self.assertEqual(base.get_direction(right),Direction.RIGHT)
        self.assertEqual(base.get_direction(down),Direction.DOWN)
        self.assertEqual(base.get_direction(left),Direction.LEFT)
        self.assertEqual(base.get_direction(here),Direction.HERE)

def main():
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()

if __name__ == "__main__":
    main()