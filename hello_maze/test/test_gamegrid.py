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

        color_map = ColorMap(
            start_color=(255,255,255),
            end_color=(0,0,0),
            start=0,
            end = 10)
        
        l_1 = Layer('MAIN',1,default_color=color_map[5])
        pos_1 = bg.Position(0,0)
        l_1.set_position(pos_1)
        grid.layer_mgr.add_layer(layer=l_1)

        renderer.render()
        tmp_file_name = TEST_TMP_DIR + '/' + self._testMethodName + "002" + ".png"
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

    def test_colormap(self):
        color_map = ColorMap(
            start_color=(255,255,255),
            end_color=(0,0,0),
            start=0,
            end = 10)
        color_6 = color_map[6]
        logging.debug(f"colormap[6] = {color_6}")
        self.assertEqual(len(color_6),3,"Color map 6 is size 3")
        self.assertEqual(color_6[0],102,"Color map 6 has value 102")
        self.assertEqual(color_6[1],102,"Color map 6 has value 102")
        self.assertEqual(color_6[2],102,"Color map 6 has value 102")


    def test_layer_manager(self):
        mgr = LayerManager()
        l_1 = Layer('Main',10)
        l_2 = Layer('Between',15)
        l_3 = Layer('Last',99)
        mgr.add_layer(l_1)
        mgr.add_layer(l_3)
        mgr.add_layer(l_2)
        logging.debug(f"Layers: {mgr.layers}")
        self.assertEqual(mgr.layers[0],l_1,"List of layers is sorted on the order 1")
        self.assertEqual(mgr.layers[1],l_2,"List of layers is sorted on the order 2")
        self.assertEqual(mgr.layers[2],l_3,"List of layers is sorted on the order 3")

        pos_1 = bg.Position(1,1)
        pos_2 = bg.Position(2,2)

        self.assertIsNone(mgr.get_color(pos_1),"Position that is not on any layer returns None")
        l_2.set_position(pos_2,color=Color.WHITE)
        self.assertEqual(mgr.get_color(pos_2),Color.WHITE,"Pos 2 layer 2 is used")
        l_3.set_position(pos_2,color=Color.BLACK)
        self.assertEqual(mgr.get_color(pos_2),Color.WHITE,"Pos 2 layer 3 is not used")
        l_1.set_position(pos_2,color=Color.BLACK)
        self.assertEqual(mgr.get_color(pos_2),Color.BLACK,"Pos 2 layer 1 is  used")