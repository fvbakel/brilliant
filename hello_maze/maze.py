from basegrid import *
from gamegrid import *
from graph import *

import logging
import random
import graphviz

class Square():

    def __init__(self,position:Position,node:Node):
        self.position = position
        self.node = node
        self.edge_pairs:dict[Direction,EdgePair] = dict()
        self.is_short_part = False

class SquareGrid(Grid):
    
    def get_location(self,position:(Position | tuple[int,int])) -> Square:
        return super().get_location(position)

    def set_location(self,position:(Position | tuple[int,int]),content:Square):
        super().set_location(position,content)

    def get_square_neighbor(self,current_square:Square,direction:Direction) ->tuple[Square,bool] | None:
        if direction in current_square.edge_pairs:
            pair = current_square.edge_pairs[direction]
            child_pos = current_square.position.get_position_in_direction(direction)
            return  (self.get_location(child_pos),pair.is_active())
        return None


class MazeGraph:

    def __init__(self,size:Size):
        self.size = size
        self.graph = Graph()
        self.square_grid = SquareGrid(size)
        self._init_nodes()
        self._init_edges()


    def _init_nodes(self):
        for row in range(0,self.size.nr_of_rows):
            for col in range(0,self.size.nr_of_cols):
                position = Position(col,row)
                node = self.graph.get_or_create(position.get_id())
                square = Square(position,node)
                self.square_grid.set_location(position,square)
        
        self.graph.first = self.square_grid.get_location((0,0)).node
        self.graph.last = self.square_grid.get_location((self.size.nr_of_cols-1,self.size.nr_of_rows-1)).node

    def _init_edges(self):
        for row in range(0,self.size.nr_of_rows):
            for col in range(0,self.size.nr_of_cols):
                position = Position(col,row)
                current_square = self.square_grid.get_location(position)
                if col < self.size.nr_of_cols -1:
                    self._add_edge_pair(current_square,Direction.RIGHT)

                if row < self.size.nr_of_rows -1:
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



class MazeGraphGenerator:

    def __init__(self,size:Size):
        self.maze_graph = MazeGraph(size=size)
        self.regenerate()

    def regenerate(self):
        self.edge_pairs = self.maze_graph.graph.edge_pairs.copy()
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
            if not self.maze_graph.graph.is_fully_connected():
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
        child_square_details = self.square_grid.get_square_neighbor(current_square,direction)
        if child_square_details != None:
            self._add_edge(current_square,child_square_details[0],child_square_details[1])

    def _add_square_as_node(self,square:Square):
        id = self.get_square_id(square)
        color='black'
        if square.is_short_part:
            color='red'
        self._current_graph.node(name=id,shape='rect',color=color)
    
    def get_square_id(self,square:Square):
        return square.position.get_id()

    def _add_edge(self,square:Square,child_square:Square,active:bool):
        style = 'invis'
        if active:
            style='filled'

        color = 'black'
        if active and square.is_short_part and child_square.is_short_part:
            color = 'red'
        
        self._current_graph.edge(self.get_square_id(square),self.get_square_id(child_square),style=style,color=color)

    def render(self,filename:PathLike | str,directory:PathLike | str, format='svg'):
        self.dot.render(filename=filename,directory=directory, format=format)