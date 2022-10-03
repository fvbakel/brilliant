from basegrid import *
from gamegrid import *
from graph import *

import logging
import random
import graphviz

class Square:

    def __init__(self,position:Position,node:Node):
        self.position = position
        self.node = node
        self.edge_pairs:dict[Direction,EdgePair] = dict()
        self.is_short_part = False
        self.is_first=False
        self.is_last=False

@dataclass
class SquareRelation:
    parent:Square
    child:Square    = None
    active:bool     = True

class SquareGeometry:

    def __init__(self,game_pos:Position,square_width:int,wall_width:int):

        self.square_width = square_width
        self.wall_width = wall_width
        x = self._wall_start_end_positions(game_pos.col)
        y = self._wall_start_end_positions(game_pos.row)

        self.walls:dict[Direction,Rectangle] = dict()
        
        self.walls[Direction.LEFT] = Rectangle( Position(x[0],y[0]),Position(x[1],y[3]))
        self.walls[Direction.UP] = Rectangle( Position(x[0],y[0]),Position(x[3],y[1]))
        self.walls[Direction.RIGHT] = Rectangle( Position(x[2],y[0]),Position(x[3],y[3]))
        self.walls[Direction.DOWN] = Rectangle( Position(x[0],y[2]),Position(x[3],y[3]))

        self.outer_rectangle = Rectangle( Position(x[0],y[0]),Position(x[3],y[3]))
        self.inner_rectangle = Rectangle( Position(x[1]+1,y[1]+1),Position(x[2]-1,y[2]-1))

    def _wall_start_end_positions(self,square_index:int):
        x:list[int] = []
        start = (square_index * self.square_width) + (square_index * self.wall_width)
        x.append(start)
        x.append(x[0] + self.wall_width -1)
        x.append(x[1] + self.square_width + 1)
        x.append(x[2] + self.wall_width -1)
        return x

class SquareGrid(Grid):
    
    def get_location(self,position:(Position | tuple[int,int])) -> Square:
        return super().get_location(position)

    def set_location(self,position:(Position | tuple[int,int]),content:Square):
        super().set_location(position,content)

    def get_square_neighbor(self,current_square:Square,direction:Direction) ->SquareRelation:
        
        if direction in current_square.edge_pairs:
            pair = current_square.edge_pairs[direction]
            child_pos = current_square.position.get_position_in_direction(direction)
            relation = SquareRelation(current_square)
            relation.active = pair.is_active()
            relation.child = self.get_location(child_pos)
            #return  (self.get_location(child_pos),pair.is_active())
            return relation
        return None

    def has_wall(self,square:Square,direction:Direction):
        if square.is_first and direction == Direction.UP:
            return False
        if square.is_last and direction == Direction.DOWN:
            return False
        square_rel = self.get_square_neighbor(square,direction)
        if square_rel == None:
            return True
        return not square_rel.active

class SquareGeometryGrid(Grid):

    def get_location(self,position:(Position | tuple[int,int])) -> SquareGeometry:
        return super().get_location(position)

    def set_location(self,position:(Position | tuple[int,int]),content:SquareGeometry):
        super().set_location(position,content)

class Maze:

    def __init__(self,square_size:Size):
        self.square_size = square_size
        self.graph = Graph()
        self.square_grid = SquareGrid(square_size)
        self._init_nodes()
        self._init_first_last()
        self._init_edges()

    def _init_nodes(self):
        for row in range(0,self.square_size.nr_of_rows):
            for col in range(0,self.square_size.nr_of_cols):
                position = Position(col,row)
                node = self.graph.get_or_create(position.get_id())
                square = Square(position,node)
                self.square_grid.set_location(position,square)
    
    def _init_first_last(self):
        self.first_square = self.square_grid.get_location((0,0))
        self.last_square = self.square_grid.get_location((self.square_size.nr_of_cols-1,self.square_size.nr_of_rows-1)) 

        self.first_square.is_first=True
        self.last_square.is_last=True

        self.graph.first = self.first_square.node
        self.graph.last = self.last_square.node

    def _init_edges(self):
        for row in range(0,self.square_size.nr_of_rows):
            for col in range(0,self.square_size.nr_of_cols):
                position = Position(col,row)
                current_square = self.square_grid.get_location(position)
                if col < self.square_size.nr_of_cols -1:
                    self._add_edge_pair(current_square,Direction.RIGHT)

                if row < self.square_size.nr_of_rows -1:
                    self._add_edge_pair(current_square,Direction.DOWN)

    
    def _add_edge_pair(self,current_square:Square,direction:Direction):
        child_pos = current_square.position.get_position_in_direction(direction)
        child_square = self.square_grid.get_location(child_pos)
        pair = self.graph.create_edge_pair(parent=current_square.node,child=child_square.node)
        current_square.edge_pairs[direction] = pair
        
        child_square.edge_pairs[Direction.reverse(direction)] = pair

    def solve_shortest_path(self):
        self.short_path_nodes = self.graph.find_short_path_dijkstra(self.graph.first,self.graph.last)
        short_path_set = set(self.short_path_nodes)
        for row in range(0,self.square_grid.size.nr_of_rows):   
            for col in range(0,self.square_grid.size.nr_of_cols):
                position = Position(col,row)
                current_square = self.square_grid.get_location(position)
                if current_square.node in short_path_set:
                    current_square.is_short_part = True

class MazeGame:

    def __init__(self,maze:Maze,square_width:int,wall_width:int):
        self.maze=maze
        self.square_width = square_width
        self.wall_width = wall_width

        width = self._calculate_game_length(self.maze.square_size.nr_of_cols)
        height = self._calculate_game_length(self.maze.square_size.nr_of_rows)
        self.game_size = Size(width,height)

        self.geometry = SquareGeometryGrid(self.maze.square_size)
        self.game_grid = GameGrid(self.game_size)

        self.maze.solve_shortest_path()
        self._init_geometry()

    def _calculate_game_length(self,nr_of_squares:int):
        # wall | wall   | wall | wall   | wall
        # wall | square | wall | square | wall
        # wall | square | wall | square | wall
        # wall | wall   | wall | wall   | wall

        #     0123456789...
        #  00 ********************
        #  01 ********************
        #  02 **    **    **    **
        #  03 **    **    **    **
        #  04 **    **    **    **
        #  05 **    **    **    **
        #  06 ********************
        #  07 ********************
        nr_of_walls = nr_of_squares +1
        return nr_of_squares * self.square_width + nr_of_walls * self.wall_width

    def _init_geometry(self):
        for row in range(0,self.maze.square_size.nr_of_rows):
            for col in range(0,self.maze.square_size.nr_of_cols):
                position = Position(col,row)
                square_geom = SquareGeometry(position,self.square_width,self.wall_width)
                self.geometry.set_location(position,square_geom)
                square = self.maze.square_grid.get_location(position)
                self._init_square_on_game_grid(square)

    def _init_square_on_game_grid(self,square:Square):
        square_geometry = self.geometry.get_location(square.position)

        for direction in Direction:
            if direction == Direction.HERE:
                continue
            if self.maze.square_grid.has_wall(square,direction):
                rect = square_geometry.walls[direction]
                for game_pos in rect.positions():
                    self.game_grid.set_location(game_pos,Wall())
        
        # remaining is floor
        for pos in square_geometry.outer_rectangle.positions():
            content = self.game_grid.get_location(pos)
            if content == None:
                content = Floor()
                if square.is_short_part:
                    content.material = Material.FLOOR_MARKED
                self.game_grid.set_location(pos,content)
            if isinstance(content,Floor):
                # if up or left square is short path but this is not 
                # then set the floor back to normal
                if not square.is_short_part:
                    content.material = Material.FLOOR


class MazeGenerator:

    def __init__(self,size:Size):
        self.maze = Maze(square_size=size)
        self.regenerate()

    def regenerate(self):
        self.edge_pairs = self.maze.graph.edge_pairs.copy()
        self._enable_all_edges()
        self._generate()

    def _enable_all_edges(self):
        for pair in self.edge_pairs:
            pair.enable()

    def _generate(self):
        while len(self.edge_pairs) > 0:
            pair = random.choice(tuple(self.edge_pairs))
            self.edge_pairs.remove(pair)
            pair.disable()
            if not self.maze.graph.is_fully_connected():
                pair.enable()

class Squares2Dot:

    def __init__(self,square_grid:SquareGrid):
        self.square_grid = square_grid
        self.refresh()

    def refresh(self):
        self._sub_graphs: dict[str, graphviz.Graph] = dict()
        self.dot = graphviz.Graph()
        self.dot.attr(rankdir='LR')
        self._current_graph:graphviz.Graph = self.dot
        
        self._create_subgraphs()
        self._add_squares()
        self._post_process_sub_graphs()
    
    def _add_subgraph(self,name:str):
        self._sub_graphs[name] = graphviz.Graph(name=name)
        self._sub_graphs[name].attr(rankdir='LR')

    def _create_subgraphs(self):
        for row in range(0,self.square_grid.size.nr_of_rows):
            self._add_subgraph(f"row_{row}")
        for col in range(0,self.square_grid.size.nr_of_cols):
            self._add_subgraph(f"col_{col}")
            self._set_active_graph(f"col_{col}")
            self._current_graph.attr(rank="same")
    
    def _post_process_sub_graphs(self):
        for name,graph in self._sub_graphs.items():
            self.dot.subgraph(graph)

    def _add_row_structure_remove_this(self):
        self._add_subgraph("Rows")
        self._set_active_graph("Rows")
        self._current_graph.attr(rank="same")
        for row in range(0,self.square_grid.size.nr_of_rows):
            self._current_graph.node(name=f"row_{row}",style='invis')
            self._add_subgraph(f"cluster_row_{row}")

        for row in range(0,self.square_grid.size.nr_of_rows-1):
            self._current_graph.edge(f"row_{row}",f"row_{row+1}",style='invis')

        self._set_active_graph(None)
        for row in range(0,self.square_grid.size.nr_of_rows):
            position = Position(0,row)
            current_square = self.square_grid.get_location(position)
            id = self.get_square_id(current_square)
            self._current_graph.edge(f"row_{row}",id,style='invis')

    def _set_active_graph(self,name:str=None):
        if name is None:
            self._current_graph = self.dot
        else:
            self._current_graph = self._sub_graphs[name]

    def _add_squares(self):
        for row in range(0,self.square_grid.size.nr_of_rows):
            
            for col in range(0,self.square_grid.size.nr_of_cols):
                position = Position(col,row)
                current_square = self.square_grid.get_location(position)
                self._set_active_graph(f"row_{row}")
                self._add_square_as_node(current_square)

                if col < self.square_grid.size.nr_of_cols -1:
                    self._add_square_edge(current_square,Direction.RIGHT)

                self._set_active_graph(f"col_{col}")
                if row < self.square_grid.size.nr_of_rows -1:
                    self._add_square_edge(current_square,Direction.DOWN)

    
    def _add_square_edge(self,current_square:Square,direction:Direction,active_only=True):
        square_relation = self.square_grid.get_square_neighbor(current_square,direction)
        if square_relation != None:
            self._add_edge(square_relation)

    def _add_square_as_node(self,square:Square):
        id = self.get_square_id(square)
        color='black'
        if square.is_short_part:
            color='red'
        self._current_graph.node(name=id,shape='rect',color=color)
    
    def get_square_id(self,square:Square):
        return square.position.get_id()

    #def _add_edge(self,square:Square,child_square:Square,active:bool):
    def _add_edge(self,square_relation:SquareRelation):
        style = 'invis'
        if square_relation.active:
            style='filled'

        color = 'black'
        if  square_relation.active and \
            square_relation.parent.is_short_part and \
            square_relation.child.is_short_part:
                color = 'red'
        
        self._current_graph.edge(   self.get_square_id(square_relation.parent),
                                    self.get_square_id(square_relation.child),
                                    style=style,color=color
                                )

    def render(self,filename:PathLike | str,directory:PathLike | str, format='svg'):
        self.dot.render(filename=filename,directory=directory, format=format)