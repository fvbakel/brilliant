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
        upright = Position(6,4)

        self.assertEqual(base.get_direction(up),Direction.UP)
        self.assertEqual(base.get_direction(right),Direction.RIGHT)
        self.assertEqual(base.get_direction(down),Direction.DOWN)
        self.assertEqual(base.get_direction(left),Direction.LEFT)
        self.assertEqual(base.get_direction(here),Direction.HERE)

        self.assertTrue(base.is_neighbor(up))
        self.assertTrue(base.is_neighbor(down))
        self.assertTrue(base.is_neighbor(left))
        self.assertTrue(base.is_neighbor(right))

        self.assertFalse(base.is_neighbor(here))
        self.assertFalse(up.is_neighbor(down))
        self.assertFalse(down.is_neighbor(up))
        self.assertFalse(left.is_neighbor(right))
        self.assertFalse(right.is_neighbor(left))

        self.assertFalse(base.is_neighbor(upright))

    def test_rectangle(self):
        rect = Rectangle(Position(0,0),Position(2,4))
        logging.debug("Dumping rectangle positions:")
        for pos in rect.positions():
            logging.debug("Pos: " + str(pos))
        
        positions = set(rect.positions())

        self.assertTrue(Position(0,0) in positions,"0-0 is in rectangle 0-0,2-4")
        self.assertTrue(Position(2,4) in positions,"2-4 is in rectangle 0-0,2-4")
        self.assertTrue(len(positions) == 15,"rectangle 0-0,2-4 has 3 * 5 = 15 positions")

    def test_flat_id(self):
        size = Size(nr_of_cols=5,nr_of_rows=2)
        grid = Grid(size = size)
        self.assertEqual(len(grid.flat_ids),10)
        pos = grid.get_position(0)
        self.assertEqual(Position(0,0),pos)
        pos = grid.get_position(4)
        self.assertEqual(Position(4,0),pos)
        pos = grid.get_position(5)
        self.assertEqual(Position(0,1),pos)
        pos = grid.get_position(6)
        self.assertEqual(Position(1,1),pos)
        pos = grid.get_position(7)
        self.assertEqual(Position(2,1),pos)

        size = Size(nr_of_cols=2,nr_of_rows=5)
        grid = Grid(size = size)
        self.assertEqual(len(grid.flat_ids),10)
        pos = grid.get_position(0)
        self.assertEqual(Position(0,0),pos)
        pos = grid.get_position(4)
        self.assertEqual(Position(0,2),pos)
        pos = grid.get_position(5)
        self.assertEqual(Position(1,2),pos)
        pos = grid.get_position(6)
        self.assertEqual(Position(0,3),pos)
        pos = grid.get_position(7)
        self.assertEqual(Position(1,3),pos)

    def test_has_location(self):
        size = Size(10,15)
        grid = Grid(size)

        pos = Position(0,0)
        self.assertTrue(grid.has_location(pos))
        pos = Position(9,14)
        self.assertTrue(grid.has_location(pos))
        pos = Position(10,0)
        self.assertFalse(grid.has_location(pos))
        pos = Position(0,16)
        self.assertFalse(grid.has_location(pos))
        pos = Position(-1,1)
        self.assertFalse(grid.has_location(pos))
        pos = Position(1,-1)
        self.assertFalse(grid.has_location(pos))