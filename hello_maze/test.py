from make_maze import *
import logging

class TestFunctions:
    def test_maze_draw():
        logging.debug("Maze draw test 1")
        size = GridSize(4,4)
        maze_img = MazeImage(size,"test")

        maze_img.enable_all()
 
        maze_img.squares[0][0].set_up_value(False)
        maze_img.squares[0][1].set_left_value(False)
        maze_img.squares[0][1].set_down_value(False)
        maze_img.squares[1][1].set_right_value(False)
        maze_img.squares[1][2].set_down_value(False)
        maze_img.squares[3][2].set_up_value(False)
        maze_img.squares[3][3].set_left_value(False)
        maze_img.squares[3][3].set_down_value(False)
  
        maze_img.draw_squares()

        #maze_img.img.show(f"Maze {maze_img.name}")
        maze_img.img.save("/home/fvbakel/tmp/maze_draw_test1.png")

        logging.debug("Maze draw test 1 end")

        logging.debug("Maze draw test 2")
        size = GridSize(4,4)
        graph = MatrixGraph.make_plain_graph(size,set(["r","d","u","l"]))
        maze_img.set_graph(graph)
        maze_img.draw_squares()
        maze_img.img.save("/home/fvbakel/tmp/maze_draw_test2.png")
        logging.debug("Maze draw test 2 end")

        test_name = "maze_draw_test_3"
        logging.debug(f"{test_name} Start")
        size = GridSize(2,2)
        maze_img = MazeImage(size,"test")
        graph = MatrixGraph.make_plain_graph(size,set(["r","d"]))
        maze_img.set_graph(graph)
        maze_img.draw_squares()
        maze_img.img.save(f"/home/fvbakel/tmp/{test_name}.png")
        logging.debug(f"{test_name} end")

        test_name = "maze_draw_test_4"
        logging.debug(f"{test_name} Start")
        size = GridSize(4,4)
        maze_img = MazeImage(size,test_name)
        graph = MatrixGraph.make_plain_graph(size,set(["r","d","u","l"]))
        
        maze_img.set_graph(graph)
        maze_img.draw_squares()
        maze_img.img.save(f"/home/fvbakel/tmp/{test_name}.png")
        logging.debug(f"{test_name} end")

    def test_fully_connected():
        size = GridSize(4,4)
        
        logging.debug("Fully connected test 1")
        graph = MatrixGraph.make_plain_graph(size,set(["r","d","u","l"]))
        assert(graph.is_fully_connected())
        logging.debug("Fully connected test 1 passed")

        logging.debug("Fully connected test 2")
        graph = MatrixGraph.make_plain_graph(size,set(["r","d"]))
        assert(graph.is_fully_connected())
        logging.debug("Fully connected test 2 passed")

        logging.debug("Fully connected test 3")
        graph = MatrixGraph.make_plain_graph(size,set(["r"]))
        assert(not graph.is_fully_connected())
        logging.debug("Fully connected test 3 passed")

    def test_MazeGenerator():
        size = GridSize(2,2)
        test_name = "maze_gen_test_1"
        logging.debug(f"{test_name} Start")
        maze_gen = MazeGenerator(size)
        graph = maze_gen.graph

        maze_img = MazeImage(size,test_name)
        maze_img.set_graph(graph)
        maze_img.draw_squares()
        maze_img.img.save(f"/home/fvbakel/tmp/{test_name}.png")
        Graph2Dot(graph).render(f"{test_name}.dot","/home/fvbakel/tmp")

        assert(not graph.check_recursion_first())
        assert(graph.is_fully_connected)
        logging.debug(f"{test_name} end")

        size = GridSize(30,10)
        test_name = "maze_gen_test_2"
        logging.debug(f"{test_name} Start")
        maze_gen = MazeGenerator(size)
        graph = maze_gen.graph

        maze_img = MazeImage(size,test_name)
        maze_img.set_graph(graph)
        maze_img.draw_squares()
        maze_img.img.save(f"/home/fvbakel/tmp/{test_name}.png")
        # Graph2Dot(graph).render(f"{test_name}.dot","/home/fvbakel/tmp")

        assert(not graph.check_recursion_first())
        assert(graph.is_fully_connected)
        logging.debug(f"{test_name} end")

    def test_check_recursion_first():
        size = GridSize(4,4)
        logging.debug("test_check_recursion_first test 1")
        graph = MatrixGraph.make_plain_graph(size,set(["r","d","u","l"]))
        assert(graph.check_recursion_first())
        logging.debug("test_check_recursion_first test 1 passed")

        logging.debug("test_check_recursion_first test 2")
        graph = MatrixGraph.make_plain_graph(size,set(["r","d"]))
        assert(not graph.check_recursion_first())
        logging.debug("test_check_recursion_first test 2 passed")

        size = GridSize(2,2)
        logging.debug("test_check_recursion_first test 3")
        graph = MatrixGraph.make_plain_graph(size,set(["r","d","u","l"]))
        assert(graph.check_recursion_first())
        Graph2Dot(graph).render("test_check_recursion.dot","/home/fvbakel/tmp")
        logging.debug("test_check_recursion_first test 3 passed")

    def test_position_get_direction():
        pos_base  = Position(1,1)
        pos_up    = Position(1,0)
        pos_down  = Position(1,2)
        pos_left  = Position(0,1)
        pos_right = Position(2,1)
        pos_equal = Position(1,1)

        assert(pos_base.get_direction(pos_up) == "u")
        assert(pos_base.get_direction(pos_down) == "d")
        assert(pos_base.get_direction(pos_left) == "l")
        assert(pos_base.get_direction(pos_right) == "r")
        assert(pos_base.get_direction(pos_equal) == "equal")

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    TestFunctions.test_maze_draw()
    TestFunctions.test_fully_connected()
    TestFunctions.test_check_recursion_first()
    TestFunctions.test_position_get_direction()
    TestFunctions.test_MazeGenerator()