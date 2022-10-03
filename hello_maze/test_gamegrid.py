from gamegrid import *
import logging
import unittest

TEST_TMP_DIR = "./tmp"

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

        renderer = TextGameGridRender(grid)
        renderer.render()
        print(renderer.output)

    def test_ImageGameGridRender(self):
        grid = self.make_test_grid()

        renderer = ImageGameGridRender(grid)
        renderer.render()
        
        tmp_file_name = TEST_TMP_DIR + '/' + self._testMethodName + "001" + ".png"
        logging.debug(f"Writing image {tmp_file_name}")
        cv2.imwrite(tmp_file_name,renderer.output)

def main():
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()

if __name__ == "__main__":
    main()