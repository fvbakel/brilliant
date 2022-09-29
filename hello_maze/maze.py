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

class SquareGrid(Grid):
    
    def get_location(self,position:(Position | tuple[int,int])) -> Square:
        return super().get_location(position)

    def set_location(self,position:(Position | tuple[int,int]),content:Square):
        super().set_location(position,content)


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
        self._refresh()

    def _refresh(self):
        self.dot = graphviz.Digraph()
        self.dot.attr(rankdir='LR')
        for row in range(0,self.square_grid.size.nr_of_rows):
            for col in range(0,self.square_grid.size.nr_of_cols):
                position = Position(col,row)
                current_square = self.square_grid.get_location(position)
                self._add_square_as_node(current_square)

                if col < self.square_grid.size.nr_of_cols -1:
                    self._add_square_edges(current_square,Direction.RIGHT)

                if row < self.square_grid.size.nr_of_rows -1:
                    self._add_square_edges(current_square,Direction.DOWN)

    
    def _add_square_edges(self,current_square:Square,direction:Direction):

        if direction in current_square.edge_pairs:
            pair = current_square.edge_pairs[direction]
            if pair.is_active():
                child_pos = current_square.position.get_position_in_direction(direction)
                child_square = self.square_grid.get_location(child_pos)
                self.dot.edge(self.get_square_id(current_square),self.get_square_id(child_square))


    def _add_square_as_node(self,square:Square):
        id = self.get_square_id(square)
        self.dot.node(name=id,shape='rect')
    
    def get_square_id(self,square:Square):
        return square.position.get_id()

    def render(self,filename:PathLike | str,directory:PathLike | str, format='svg'):
        self.dot.render(filename=filename,directory=directory, format=format)