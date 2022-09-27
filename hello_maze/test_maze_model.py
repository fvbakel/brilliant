from turtle import down, left
from maze_model import *
import logging
import unittest

"""
grid:    --->  cols -->
        |   0               |   1               |   2   |   3 
    ↓ 0 |   Cell 0-0        |   Cell 1-0        |
    ↓   |                   |                   |
    ↓---|-------------------|-------------------|--
 rows 1 |   Cell 0-1        |   Cell 1-1        |
    ↓   |                   |                   |
    ↓---|-------------------|-------------------|--
"""
class TestModel(unittest.TestCase):

    def test_direction(self):
        l = Direction.LEFT
        self.assertTrue(l==Direction.LEFT)

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

    def make_test_grid(self):
        grid_size = Size(10,10)
        grid = MazeGrid(grid_size)

        cell_1 = grid.get_cell((0,0))
        cell_1.content = Wall()
        cell_2 = grid.get_cell((1,0))
        cell_2.content = Floor()
        cell_2.content.guest = Particle()

        return grid
        

    def test_TextMazeGridRender(self):
        grid = self.make_test_grid()

        renderer = TextMazeGridRender(grid)
        renderer.render()
        print(renderer.output)

def main():
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()

if __name__ == "__main__":
    main()