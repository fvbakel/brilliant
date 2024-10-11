from enum import Enum
from dataclasses import dataclass
import logging
from typing import Any

class Position: pass

class ExtendedEnum(Enum):

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))

class Direction(ExtendedEnum):
    LEFT    = 'l'
    RIGHT   = 'r'
    UP      = 'u'
    DOWN    = 'd'
    HERE    = 'h'

    @classmethod
    def reverse(cls,direction):
        if direction == Direction.LEFT:
            return Direction.RIGHT
        if direction == Direction.RIGHT:
            return Direction.LEFT
        if direction == Direction.UP:
            return Direction.DOWN
        if direction == Direction.DOWN:
            return Direction.UP
        return direction

class Orientation(ExtendedEnum):
    HORIZONTAL  = 'horizontal'
    VERTICAL    = 'vertical'

@dataclass(frozen=True,eq=True)
class Size:
    nr_of_cols:int
    nr_of_rows:int

    def inverse(self):
        return Size(self.nr_of_rows,self.nr_of_cols)

@dataclass(frozen=True,eq=True)
class Position:
    col:int
    row:int

    def get_direction(self,pos:Position) -> Direction:
        if self == pos:
            return Direction.HERE

        if self.col == pos.col:
            if self.row > pos.row:
                return Direction.UP
            if self.row < pos.row:
                return Direction.DOWN
        
        if self.row == pos.row:
            if self.col > pos.col:
                return Direction.LEFT
            if self.col < pos.col:
                return Direction.RIGHT

    def get_position_in_direction(self,direction:Direction):
        if direction == Direction.RIGHT:
            return Position(self.col+1,self.row)
        if direction == Direction.LEFT:
            return Position(self.col-1,self.row)
        if direction == Direction.UP:
            return Position(self.col,self.row-1)
        if direction == Direction.DOWN:
            return Position(self.col,self.row+1)
        if direction == Direction.HERE:
            return self
        logging.FATAL(f"Unexpected direction {direction}")
    
    def get_all_neighbors(self):
        neighbors:set[Position] = set()
        neighbors.add(Position(self.col,self.row + 1))
        neighbors.add(Position(self.col + 1,self.row))
        neighbors.add(Position(self.col,self.row - 1))
        neighbors.add(Position(self.col - 1,self.row))
        return neighbors

    def is_neighbor(self,position:Position):
        if position is None:
            return False

        if self == position:
            return False

        delta_col = abs(self.col - position.col)
        delta_row = abs(self.row - position.row)
        if delta_col == 0 and  delta_row == 1:
            return True
        if delta_col == 1 and  delta_row == 0:
            return True
        return False

    def get_id(self):
        return f"{self.col}-{self.row}"
    
    def __repr__(self) -> str:
        return self.get_id()

class Grid:

    def __init__(self,size:Size):
        self.size = size
        self.locations:list[list[Any]] = []
        self._init_locations()

    def _init_locations(self):
        for col in range(0,self.size.nr_of_cols):
            self.locations.append([])
            for row in range(0,self.size.nr_of_rows):
                self.locations[col].append(self._get_default(row,col))

    def _get_default(self,col:int,row:int):
        return None

    def has_location(self,position:(Position | tuple[int,int])):
        if  0 <= position.col < self.size.nr_of_cols and \
            0 <= position.row < self.size.nr_of_rows:
                return True
        return False

    def get_location(self,position:(Position | tuple[int,int])):
        if isinstance(position,Position):
            return self.locations[position.col][position.row]
        if isinstance(position,tuple):
            return self.locations[position[0]][position[1]]

    def set_location(self,position:(Position | tuple[int,int]),content:Any):
        if isinstance(position,Position):
            self.locations[position.col][position.row] = content
        if isinstance(position,tuple):
            self.locations[position[0]][position[1]] = content

    @property
    def flat_ids(self):
        return list(range(0,self.size.nr_of_cols * self.size.nr_of_rows))

    def get_position(self,flat_id:int):
        row_index = flat_id // self.size.nr_of_cols
        col_index = flat_id %  self.size.nr_of_cols
        return Position(col=col_index,row=row_index)
    
    def get_flat_id(self, pos:Position):
        return  pos.row * self.size.nr_of_cols + pos.col 

@dataclass
class Rectangle:
    up_left:Position
    down_right:Position

    def positions(self) -> list[Position]:
        for col in range(self.up_left.col,self.down_right.col+1):
            for row in range(self.up_left.row,self.down_right.row+1):
                yield Position(col,row)