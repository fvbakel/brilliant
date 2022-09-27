from gamegrid import *
import logging
import unittest


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
        grid = GameGrid(grid_size)

        location_1 = grid.get_location((0,0))
        location_1.content = Wall()
        location_2 = grid.get_location((1,0))
        location_2.content = Floor()
        location_2.content.guest = Particle()

        return grid
        

    def test_TextGameGridRender(self):
        grid = self.make_test_grid()

        renderer = TextMazeGridRender(grid)
        renderer.render()
        print(renderer.output)

def main():
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()

if __name__ == "__main__":
    main()