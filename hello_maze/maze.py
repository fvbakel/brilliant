from gamegrid import *
from basegrid import *
from graph import *
import logging
import random

class Square():

    def __init__(self,position:Position,node,Node):
        self.position = position
        self.node = node

class NodeGrid(Grid):
    
    def get_location(self,position:(Position | tuple[int,int])) -> Node:
        return super().get_location(position)

    def set_location(self,position:(Position | tuple[int,int]),content:Node):
        super().set_location(position,content)

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


    def _init_nodes(self):
        row = 0
        while row  < self.size.nr_of_rows:
            col = 0
            while col < self.size.nr_of_cols:
                position = Position(col,row)
                node = self.graph.get_or_create(position.get_id())
                square = Square(position,node)
                self.square_grid.set_location(position,square)

    def _init_edges(self):
        row = 0
        while row  < self.size.nr_of_rows:
            col = 0
            while col < self.size.nr_of_cols:
                position = Position(col,row)
                current = self.square_grid.get_location(position).node
                if current is None:
                    raise("Error, can not find node for position: ",position)
                else:
                    if col < self.size.nr_of_cols -1:
                        child_pos = position.get_position_in_direction(Direction.RIGHT)
                        child = self.square_grid.get_location(child_pos).node
                        self.graph.create_edge(parent=current,child=child)
                    if col != 0:
                        child_pos = position.get_position_in_direction(Direction.LEFT)
                        child = self.square_grid.get_location(child_pos).node
                        self.graph.create_edge(parent=current,child=child)
                    if row < self.size.nr_of_rows -1:
                        child_pos = position.get_position_in_direction(Direction.DOWN)
                        child = self.square_grid.get_location(child_pos).node
                        self.graph.create_edge(parent=current,child=child)
                    if row != 0:
                        child_pos = position.get_position_in_direction(Direction.UP)
                        child = self.square_grid.get_location(child_pos).node
                        self.graph.create_edge(parent=current,child=child)
                col = col + 1
            row = row + 1

class MazeGraphGenerator:

    def __init__(self,size:Size):
        self.maze_graph = MazeGraph(size=size)
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

