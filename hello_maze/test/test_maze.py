import basegrid as bg
from maze import *
from test.test_config import *
import logging
import unittest
from graph import *
import cv2

class TestMaze(unittest.TestCase):

    def test_maze_generator(self):
        size = bg.Size(4,4)
        maze_gen =  MazeGenerator(size)

        r = Graph2Dot(maze_gen.maze.graph)
        r.render(self._testMethodName + "001" + ".dot",TEST_TMP_DIR)

        r = Squares2Dot(maze_gen.maze.square_grid)
        r.render(self._testMethodName + "002" + ".dot",TEST_TMP_DIR)

        maze_gen.maze.solve_shortest_path()
        r.refresh()
        #r = Squares2Dot(maze_gen.maze_graph.square_grid)
        r.render(self._testMethodName + "003" + ".dot",TEST_TMP_DIR)

    def test_maze_game(self):
        size = bg.Size(4,4)
        maze_gen =  MazeGenerator(size)
        game = MazeGame(maze_gen.maze,square_width=4,wall_width=2)

        renderer = TextGameGridRender(game.game_grid)
        renderer.render()
        tmp_file_name = TEST_TMP_DIR + '/' + self._testMethodName + "001" + ".txt"
        logging.debug(f"Dumping test maze {tmp_file_name}")
        with open(tmp_file_name, 'w') as f:
            f.write(renderer.output)
        self.assertTrue(renderer.output[1] == Material.STONE.value,f"Left corner of maze is a wall and thus stone. '{renderer.output[1]}' != '{Material.STONE.value}'" )

        material_map:dict[str,str] = dict()
        material_map[Material.STONE.value] = '*'
        material_map[Material.FLOOR_MARKED.value] = ' '
        material_map[Material.FLOOR_HIGHLIGHTED.value] = ' '
        material_map[Material.FLOOR.value] = ' '
        renderer = TextGameGridRender(game.game_grid,material_map=material_map)
        renderer.render()
        tmp_file_name = TEST_TMP_DIR + '/' + self._testMethodName + "002" + ".txt"
        logging.debug(f"Dumping test maze {tmp_file_name}")
        with open(tmp_file_name, 'w') as f:
            f.write(renderer.output)
        self.assertTrue(renderer.output[1] == '*',f"Left corner of maze is a wall and thus stone wit custom rendering. '{renderer.output[1]}' != '*'" )

        renderer = ImageGameGridRender(game.game_grid)
        renderer.render()
        tmp_file_name = TEST_TMP_DIR + '/' + self._testMethodName + "003" + ".png"
        logging.debug(f"Dumping test maze as png {tmp_file_name}")
        cv2.imwrite(tmp_file_name,renderer.output)
        logging.debug(renderer.output[0,0])
        self.assertFalse(renderer.output[0,0].any(),f"Left corner of maze is a wall and thus black" )
