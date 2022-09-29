from gamegrid import *
import logging
import unittest


class TestModel(unittest.TestCase):

    def test_direction(self):
        l = Direction.LEFT
        self.assertTrue(l==Direction.LEFT)



    def make_test_grid(self):
        grid_size = Size(10,10)
        grid = GameGrid(grid_size)

        grid.set_location((0,0),Wall())
        grid.set_location((1,0),Floor())
        floor = grid.get_location((1,0))

        floor.guest = Particle()

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