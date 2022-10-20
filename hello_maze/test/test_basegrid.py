from basegrid import *
import logging
import unittest

class TestBasegrid(unittest.TestCase):

    def test_direction(self):
        l = Direction.LEFT
        self.assertTrue(l==Direction.LEFT)
        r = Direction.reverse(l)
        self.assertTrue(r==Direction.RIGHT)

        logging.debug("Listing directions as strings")
        directions = Direction.list()
        for direction in directions:
            logging.debug(direction)
        self.assertTrue('r' in directions,"'r' is in Directions")
        
        logging.debug("Listing directions as objects")
        #directions = Direction.list()
        for direction in Direction:
            logging.debug(direction)
        self.assertTrue(Direction.RIGHT in Direction,"Direction.RIGHT is in Directions")

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

    def test_rectangle(self):
        rect = Rectangle(Position(0,0),Position(2,4))
        logging.debug("Dumping rectangle positions:")
        for pos in rect.positions():
            logging.debug("Pos: " + str(pos))
        
        positions = set(rect.positions())

        self.assertTrue(Position(0,0) in positions,"0-0 is in rectangle 0-0,2-4")
        self.assertTrue(Position(2,4) in positions,"2-4 is in rectangle 0-0,2-4")
        self.assertTrue(len(positions) == 15,"rectangle 0-0,2-4 has 3 * 5 = 15 positions")
