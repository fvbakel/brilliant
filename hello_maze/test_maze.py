from graph import *
from maze import *
import logging
import unittest

import os

TEST_TMP_DIR = "./tmp"

class TestGraph(unittest.TestCase):

    def test_maze_generator(self):
        size = Size(4,4)
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
        size = Size(4,4)
        maze_gen =  MazeGenerator(size)
        maze_gen.maze
        game = MazeGame(maze_gen.maze,square_width=4,wall_width=2)

        renderer = TextMazeGridRender(game.game_grid)
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
        renderer = TextMazeGridRender(game.game_grid,material_map=material_map)
        renderer.render()
        tmp_file_name = TEST_TMP_DIR + '/' + self._testMethodName + "002" + ".txt"
        logging.debug(f"Dumping test maze {tmp_file_name}")
        with open(tmp_file_name, 'w') as f:
            f.write(renderer.output)
        self.assertTrue(renderer.output[1] == '*',f"Left corner of maze is a wall and thus stone wit custom rendering. '{renderer.output[1]}' != '*'" )

       

def main():
    logging.basicConfig(level=logging.DEBUG)
    unittest.main()

if __name__ == "__main__":
    main()