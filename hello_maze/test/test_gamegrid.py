from gamegrid import *
from test.test_config import *
import basegrid as bg
import logging
import unittest
import cv2

class TestModel(unittest.TestCase):

    def test_direction(self):
        l = bg.Direction.LEFT
        self.assertTrue(l==bg.Direction.LEFT)

    def make_test_grid(self):
        grid_size = bg.Size(10,10)
        grid = GameGrid(grid_size)

        grid.set_location((0,0),Wall())
        grid.set_location((1,0),Floor())
        grid.set_location((2,0),Floor())
        floor = Floor()
        floor.material = Material.FLOOR_MARKED
        grid.set_location((3,0),floor)
        floor = grid.get_location((1,0))
        floor.guest = Particle()
        grid.set_location((4,1),Floor())

        # row 2
        grid.set_location((0,1),Wall())
        grid.set_location((1,1),Floor())
        grid.set_location((2,1),Floor())
        grid.set_location((3,1),Floor())
        grid.set_location((4,1),Floor())

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

    def test_ManualMoveControl(self):
        grid = self.make_test_grid()
        renderer = ImageGameGridRender(grid)
        
        
        particle = Particle()
        
        grid.add_to_first_free_spot(particle=particle)
        control = ManualMove(grid)
        control.subject = particle
        
        renderer.render()
        tmp_file_name = TEST_TMP_DIR + '/' + self._testMethodName + "before" + ".png"
        logging.debug(f"Writing image {tmp_file_name}")
        cv2.imwrite(tmp_file_name,renderer.output)

        control.set_move(bg.Direction.DOWN)
        control.do_one_cycle()

        renderer.render()
        tmp_file_name = TEST_TMP_DIR + '/' + self._testMethodName + "after down" + ".png"
        logging.debug(f"Writing image {tmp_file_name}")
        cv2.imwrite(tmp_file_name,renderer.output)

