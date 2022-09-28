from enum import Enum
from dataclasses import dataclass

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

    def get_id(self):
        return f"{self.col}-{self.row}"

class Location:

    def __init__(self,position:Position):
        self.content = None
        self.position = position

class Grid:

    def __init__(self,size:Size):
        self.size = size
        self.locations:list[list[Location]] = []
        self._init_locations()

    def _init_locations(self):
        for col in range(0,self.size.nr_of_cols):
            self.locations.append([])
            for row in range(0,self.size.nr_of_rows):
                self.locations[col].append(Location(Position(col,row)))
                self.locations[col][row].content = self._get_default_content()

    def _get_default_content(self):
        return None

    def get_location(self,position:(Position | tuple[int,int])):
        if isinstance(position,Position):
            return self.locations[position.col][position.row]
        if isinstance(position,tuple):
            return self.locations[position[0]][position[1]]
    