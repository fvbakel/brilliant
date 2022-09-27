from email.headerregistry import HeaderRegistry
from enum import Enum
from dataclasses import dataclass
import enum
from modulefinder import STORE_NAME
from pickle import NONE

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

class Cell:

    def __init__(self,position:Position):
        self.content:CellContent = None
        self.position = position

class CellContent:
    def __init__(self):
        self.solid:bool         = False
        self.mobile:bool        = False
        self.guest:CellContent  = None
        self.material           = Material.FLOOR


class Floor(CellContent):
    def __init__(self):
        super().__init__()
        self.solid:bool         = False
        self.mobile:bool        = False
        self.material           = Material.FLOOR

class Wall(CellContent):
    def __init__(self):
        super().__init__()
        self.solid:bool     = True
        self.mobile:bool    = False
        self.material       = Material.STONE

class Particle(CellContent):
    def __init__(self):
        super().__init__()
        self.solid:bool     = True
        self.mobile:bool    = True
        self.material       = Material.PLASTIC

class Material(Enum):
    NONE                  = '_'
    FLOOR                 = 'F'
    FLOOR_MARKED          = 'f'
    FLOOR_HIGHLIGHTED     = 'H'
    STONE                 = 'S'
    PLASTIC               = 'P'
    PLASTIC_MARKED        = 'p'
    PLASTIC_HIGHLIGHTED   = '0'
    
    
class Grid:

    def __init__(self,size:Size):
        self.size = size
        # cells: [col][row]
        self.cells:list[list[Cell]] = []
        self._init_cells()

    def _init_cells(self):
        for col in range(0,self.size.nr_of_cols):
            self.cells.append([])
            for row in range(0,self.size.nr_of_rows):
                self.cells[col].append(Cell(Position(col,row)))
                self.cells[col][row].content = self._get_default_content()

    def _get_default_content(self):
        return None

    def get_cell(self,position:(Position | tuple[int,int])):
        if isinstance(position,Position):
            return self.cells[position.col][position.row]
        if isinstance(position,tuple):
            return self.cells[position[0]][position[1]]
    

class MazeGrid(Grid):
    
    def __init__(self,grid_size:Size):
        super().__init__(grid_size)

class MazeGridRender:

    def __init__(self,maze_grid:MazeGrid):
        self.maze_grid = maze_grid
        self.output=None

    def _pre_render(self):
        self.output=None
    
    def _post_render(self):
        pass

    def render(self):
        self._pre_render()
        for row in range(0,self.maze_grid.size.nr_of_rows):
            self._render_row(row)
        self._post_render()

    def _render_row(self,row:int):
        for col in range(0,self.maze_grid.size.nr_of_cols):
            self._render_cell(self.maze_grid.get_cell((col,row)))
    
    def _render_cell(self,cell:Cell):
        material = self._get_material(cell.content)
        self._render_material(cell.position,material)
        
    def _get_material(self,content:CellContent) -> Material:
        if content == None:
            return Material.NONE

        if content.guest != None:
            return self._get_material(content.guest)

        return content.material

    def _render_material(self,position:(Position | tuple[int,int]),material:Material):
        pass

class TextMazeGridRender(MazeGridRender):

    def __init__(self,maze_grid:MazeGrid):
        super().__init__(maze_grid)
        self.output = ""

    def _pre_render(self):
        self.output = ""

    def _render_row(self,row:int):
        self.output += "\n"
        super()._render_row(row)

    def _render_material(self,position:(Position | tuple[int,int]),material:Material):
        self.output += str(material.value)

