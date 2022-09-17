from dataclasses import dataclass
from os import name
from PIL import Image, ImageDraw
import logging

class Node: pass

class Edge:

    def __init__(self,parent:Node,child:Node):
        self.parent:Node = parent
        self.child:Node = child
        self.active =True

    def reset(self):
        self.active = False

    def enable(self):
        self.active = True
    
    def disable(self):
        self.active = False

class Node:

    def __init__(self,col,row,weight):
        self.col = col
        self.row = row
        self.label = MatrixGraph.make_label(col,row)
        self.weight = weight
        self.child_edges:set[Edge] = set()
        self.parent_edges:set[Edge] = set()
        self.prev:Node = None
        self.dist = -1 # is for infinit
        self.visited = False

    def __repr__(self):
        return self.label
        
    def reset(self):
        self.prev = None
        self.dist = -1 # is for infinit
        self.visited = False

    def add_child_edge(self,node:Node):
        if self == node:
            print("ERROR: connect to self is not allowed")
            return

        if not self.has_child_node(node):
            edge = Edge(self,node)
            self.child_edges.add(edge)
            node.add_parent_edge(edge)
            return edge

    def add_parent_edge(self,edge):
        self.parent_edges.add(edge)

    def has_child_node(self,node):
        for edge in self.child_edges:
            if edge.child == node:
                return True
        return False

    def visit_all(self):
        self.visited = True
        for edge in self.child_edges:
            if edge.child.visited == False:
                edge.child.visit_all()

class MatrixGraph:

    def __init__(self):
        self.nodes:dict[str,Node] = dict()
        self.edges:set[Edge] = set()
        self._first = None
        self._last = None
        self.size = GridSize(0,0)

    def reset(self):
        for node in self.nodes.values():
            node.reset()
        for edge in self.edges:
            edge.reset()
    
    def get(self,col,row) ->Node:
        label = MatrixGraph.make_label(col,row)
        if label in self.nodes:
            return self.nodes[label]
        else:
            return None

    def get_or_create(self,col,row,weight):
        label = MatrixGraph.make_label(col,row)
        if label in self.nodes:
            return self.nodes[label]
        else:
            node = Node(col,row,weight)
            self.nodes[label] = node
            if self._first is None:
                self._first = node
            return node
    
    def init_first_and_last(self):
        self._first = self.get(0,0)
        self._last = self.get((self.size.nr_of_cols-1),self.size.nr_of_rows-1)

    
    def is_fully_connected(self):
        self.reset()
        current = self._first
        current.visit_all()

        for node in self.nodes.values():
            if not node.visited:
                logging.info(f"Node {node} is not connected")
                return False
        
        return True

    def check_recursion_first(self):
        return self.check_recursion(self._first)

    def check_recursion(self,node:Node):
        path = [node]
        is_recursive = self._check_recursion_internal(None,node,path)
        if is_recursive:
            logging.debug("Recursion found in path: {}".format(' -> '.join(map(str,path))))
        return is_recursive

    def _check_recursion_internal(self,previous_node:Node,current_node:Node,path:list[Node]):
        for edge in current_node.child_edges:
            if edge.child == previous_node:
                continue
            else:
                path.append(edge.child)
                if edge.child in set(path[:-1]):
                    return True
                if self._check_recursion_internal(current_node,edge.child,path):
                    return True
                path.pop()
        return False

    def get_min_node_not_visited(self):
        current = None
        for node in self.nodes.values():
            if node.visited == False:
                if current is None and node.dist != -1:
                    current = node
                else:
                    if node.dist != -1 and node.dist < current.dist:
                        current = node
        return current

    def sum_path_l_r(self):
        total = 0
        start = self.get(0,0)
        end = self.get((self.size.nr_of_cols -1),(self.size.nr_of_rows -1))
        path = self.find_short_path_dijkstra(start,end)

        for node in path:
            total = total + node.weight
        print(path)
        print("Sum is:", total)
    
    def sum_path_l_r_col(self):
        total = 0
        start = self.first
        end = self.last
        path = self.find_short_path_dijkstra(start,end)

        for node in path:
            total = total + node.weight
        print(path)
        print("Sum is:", total)

    def find_short_path_dijkstra(self,start,end):
        path = []
        self.reset()

        found = False
        
        start.dist = 0 
        current = start
        while current and not found:
            current.visited = True
            for edge in current.child_edges:
                other = edge.child
                if other.visited == False:
                    alt = current.dist + other.weight
                    if other.dist == -1 or alt < other.dist:
                        other.dist = alt
                        other.prev = current
            current = self.get_min_node_not_visited()
            if current == end:
                found = True
        
        if not found:
            print("Unable to find path from %s to %s" % (start.label, end.label))
        else:
            current = end
            while current is not None:
                path.insert(0,current)
                current = current.prev
        return path

    def make_label(col,row):
        return str(col) + "-" + str(row)

    def init_edges(self,allowed_directions = set(["r","d"])):
        row = 0
        while row  < self.size.nr_of_rows:
            col = 0
            while col < self.size.nr_of_cols:
                current = self.get(col,row)
                if current is None:
                    print("Error, can not find: ",MatrixGraph.make_label(col,row))
                else:
                    if "r" in allowed_directions and col != (self.size.nr_of_cols - 1):
                        child = self.get(col+1,row)
                        if child is not None:
                            edge = current.add_child_edge(child)
                            self.edges.add(edge)
                        else:
                            print("Error, can not find child in next col for: ",current.label)
                    if "l" in allowed_directions and col != 0:
                        child = self.get(col-1,row)
                        if child is not None:
                            edge = current.add_child_edge(child)
                            self.edges.add(edge)
                        else:
                            print("Error, can not find child in previous col for: ",current.label)
                    if "d" in allowed_directions and row != (self.size.nr_of_rows - 1):
                        child = self.get(col,row +1)
                        if child is not None:
                            edge = current.add_child_edge(child)
                            self.edges.add(edge)
                        else:
                            print("Error, can not find child in next row for: ",current.label)    
                    if "u" in allowed_directions and row != 0:
                        child = self.get(col,row -1)
                        if child is not None:
                            edge = current.add_child_edge(child)
                            self.edges.add(edge)
                        else:
                            print("Error, can not find child in previous row for: ",current.label)    

                col = col + 1
            row = row + 1

    def make_plain_graph(nr_of_cols = 4,nr_of_rows = 4,allowed_directions = set(["r","d"])):
        graph = MatrixGraph()
        graph.size.nr_of_cols = nr_of_cols
        graph.size.nr_of_rows = nr_of_rows

        for row in range(0,graph.size.nr_of_rows):
            for col in range(0,graph.size.nr_of_cols):
                node = graph.get_or_create(col,row,1)

        graph.init_first_and_last()
        graph.init_edges(allowed_directions)

        return graph
   
    def read_from_file(filename,allowed_directions = set(["r","d"])):
        graph = MatrixGraph()
        line_nr = 0
        with open(filename) as fp:
            for line in fp:
                if line is not None:
                    line = line.strip()
                    fields = line.split(",")
                    if graph.size.nr_of_cols == 0:
                        graph.size.nr_of_cols = len(fields)
                    col = 0
                    
                    for field in fields:
                        if field != "-":
                            node = graph.get_or_create(line_nr,col,int(field))
                        col = col + 1
                    line_nr = line_nr + 1
        graph.nr_of_rows = line_nr
       
        graph.init_first_and_last()
        graph.init_edges(allowed_directions)

        return graph

@dataclass
class GridSize:
    nr_of_cols:int
    nr_of_rows:int

class MazeImage:
    def __init__(self,size:GridSize ,name:str ):
        self.size = size
        self.name = name
        self.squares:list[list[Square]] = []
        # TODO calculate based on size
        self.square_size = 100
        self.line_width = 5
        
        self.width = (size.nr_of_cols * (self.square_size - self.line_width)) + self.line_width
        self.height = (size.nr_of_rows * (self.square_size - self.line_width)) + self.line_width

        self.bg_color = 1
        self.fg_color = 0
        
        self._init_img()
        self._init_squares()



    def draw_squares(self):
        for row in range(0,self.size.nr_of_rows):
            for col in range(0,self.size.nr_of_cols):
                self.squares[row][col].draw(self.draw,self.fg_color)

    def _init_squares(self):
        for row in range(0,self.size.nr_of_rows):
            self.squares.append([])
            for col in range(0,self.size.nr_of_cols):
                self.squares[row].append(Square(col,row,self.square_size,self.line_width))
        
        for row in range(0,self.size.nr_of_rows):
            for col in range(0,self.size.nr_of_cols):
                if row != 0:
                    self.squares[row][col].up_neighbor = self.squares[row -1][col]
                if row != self.size.nr_of_rows -1:
                    self.squares[row][col].down_neighbor = self.squares[row +1][col]
                if col != 0:
                    self.squares[row][col].left_neighbor = self.squares[row][col -1]
                    logging.debug(f"setting left neighbor for: {row},{col} to {self.squares[row][col].left_neighbor.row},{self.squares[row][col].left_neighbor.col}")
                if col != self.size.nr_of_cols -1:
                    self.squares[row][col].right_neighbor = self.squares[row][col + 1]

    def _init_img(self):
        self.img  = Image.new( mode = "1", size = (self.width, self.height),color=self.bg_color )
        self.draw = ImageDraw.Draw(self.img)

    def get_square(self,col:int,row:int):
        return self.squares[col,row]

    def draw_graph(self,graph:MatrixGraph):
        if self.size != graph.size:
            print("Error, size of maze is different from graph!")
            return

        for row  in range(0,self.size.nr_of_rows):
            for col  in range(0,self.size.nr_of_cols):
                current_node = graph.get(col,row)
                if current_node is None:
                    print("Error, can not find: ",MatrixGraph.make_label(col,row))
                    return
                else:
                    return

class Square:

    def __init__(self,col:int,row:int,outer_size:int,line_width:int):
        self.col = col
        self.row = row
        self.outer_size = outer_size
        self.line_width = line_width

        self._up     = False
        self._down   = False
        self._left   = False
        self._right  = False

        self.up_neighbor:Square      = None
        self.down_neighbor:Square    = None
        self.left_neighbor:Square    = None
        self.right_neighbor:Square   = None

        self._calculate()

    def _calculate(self):
        
        self.x1 = self.col * (self.outer_size - self.line_width )
        self.x2 = self.x1 + self.outer_size
        self.y1 = self.row * (self.outer_size - self.line_width )
        self.y2 = self.y1 + self.outer_size

        self.x1_inner = self.x1 + self.line_width
        self.x2_inner = self.x2 - self.line_width
        self.y1_inner = self.y1 + self.line_width
        self.y2_inner = self.y2 - self.line_width

        self.up_left       = (self.x1,self.y1)
        self.up_right      = (self.x2,self.y1)
        self.down_left     = (self.x1,self.y2)
        self.down_right    = (self.x2,self.y2)


    def draw(self,img_draw:ImageDraw, color):
        if self._up:
            self._draw_up(img_draw,color)
        if self._down:
            self._draw_down(img_draw,color)
        if self._right:
            self._draw_right(img_draw,color)
        if self._left:
            self._draw_left(img_draw,color)

    def set_up_value(self,value:bool):
        self._up = value
        if self.up_neighbor != None:
            self.up_neighbor._down = value

    def set_down_value(self,value:bool):
        self._down = value
        if self.down_neighbor != None:
            self.down_neighbor._up = value
    
    def set_left_value(self,value:bool):
        self._left = value
        if self.left_neighbor != None:
            logging.info("setting left neighbor right to false because left was set to false")
            self.left_neighbor._right = value
    
    def set_right_value(self,value:bool):
        self._right = value
        if self.right_neighbor != None:
            self.right_neighbor._left = value

    def set_all_value(self,value:bool):
        self.set_up_value(value)
        self.set_down_value(value)
        self.set_left_value(value)
        self.set_right_value(value)

    def enable_all(self):
        self.set_all_value(True)
        

    def disable_all(self):
        self.set_all_value(False)


    def _draw_up(self,img_draw:ImageDraw, color):
        img_draw.rectangle(
            ( 
                self.up_left,
                (self.x2,self.y1_inner)
            ),
            outline=color,
            fill=color
            )

    def _draw_left(self,img_draw:ImageDraw, color):
        img_draw.rectangle(
            ( 
                self.up_left,
                (self.x1_inner,self.y2)
            ),
            outline=color,
            fill=color
            )

    def _draw_down(self,img_draw:ImageDraw, color):
        img_draw.rectangle(
            ( 
                (self.x1,self.y2_inner),
                self.down_right
            ),
            outline=color,
            fill=color
            )

    def _draw_right(self,img_draw:ImageDraw, color):
        img_draw.rectangle(
            ( 
                (self.x2_inner,self.y1),
                self.down_right
            ),
            outline=color,
            fill=color
            )


class TestFunctions:
    def test_maze():
        size = GridSize(4,4)
        maze_img = MazeImage(size,"test")
        
        
        for row in range(0,maze_img.size.nr_of_rows):
            for col in range(0,maze_img.size.nr_of_cols):
                maze_img.squares[row][col].enable_all()
 
        maze_img.squares[0][0].set_up_value(False)
        maze_img.squares[0][1].set_left_value(False)
        maze_img.squares[0][1].set_down_value(False)
        maze_img.squares[1][1].set_right_value(False)
        maze_img.squares[1][2].set_down_value(False)
        maze_img.squares[3][2].set_up_value(False)
        maze_img.squares[3][3].set_left_value(False)
        maze_img.squares[3][3].set_down_value(False)
  
        maze_img.draw_squares()

        maze_img.img.show(f"Maze {maze_img.name}")

    def test_fully_connected():
        logging.debug("Fully connected test 1")
        graph = MatrixGraph.make_plain_graph(4,4,set(["r","d","u","l"]))
        assert(graph.is_fully_connected())
        logging.debug("Fully connected test 1 passed")

        logging.debug("Fully connected test 2")
        graph = MatrixGraph.make_plain_graph(4,4,set(["r","d"]))
        assert(graph.is_fully_connected())
        logging.debug("Fully connected test 2 passed")

        logging.debug("Fully connected test 3")
        graph = MatrixGraph.make_plain_graph(4,4,set(["r"]))
        assert(not graph.is_fully_connected())
        logging.debug("Fully connected test 3 passed")

    def test_check_recursion_first():
        logging.debug("test_check_recursion_first test 1")
        graph = MatrixGraph.make_plain_graph(4,4,set(["r","d","u","l"]))
        assert(graph.check_recursion_first())
        logging.debug("test_check_recursion_first test 1 passed")

        logging.debug("test_check_recursion_first test 2")
        graph = MatrixGraph.make_plain_graph(4,4,set(["r","d"]))
        assert(not graph.check_recursion_first())
        logging.debug("test_check_recursion_first test 2 passed")

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    TestFunctions.test_maze()
    TestFunctions.test_fully_connected()
    TestFunctions.test_check_recursion_first()


