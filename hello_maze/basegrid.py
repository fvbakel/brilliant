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

@dataclass
class Size:
    nr_of_cols:int
    nr_of_rows:int

@dataclass
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