
from basegrid import *

import cv2
import numpy as np

class Material(Enum):
    NONE                  = '_'
    FLOOR                 = 'f'
    FLOOR_MARKED          = ' '
    FLOOR_HIGHLIGHTED     = 'F'
    STONE                 = '*'
    PLASTIC               = 'P'
    PLASTIC_MARKED        = 'p'
    PLASTIC_HIGHLIGHTED   = '0'

class Color(Enum):
    WHITE = (255,255,255)
    BLACK = (0,0,0)

class GameContent:
    def __init__(self):
        self.position:Position  = None
        self.solid:bool         = False
        self.mobile:bool        = False
        self.guest:GameContent  = None
        self.material           = Material.FLOOR


class Floor(GameContent):
    def __init__(self):
        super().__init__()
        self.solid:bool         = False
        self.mobile:bool        = False
        self.material           = Material.FLOOR

class Wall(GameContent):
    def __init__(self):
        super().__init__()
        self.solid:bool     = True
        self.mobile:bool    = False
        self.material       = Material.STONE

class Particle(GameContent):
    def __init__(self):
        super().__init__()
        self.solid:bool     = True
        self.mobile:bool    = True
        self.material       = Material.PLASTIC

class GameGrid(Grid):
    
    def get_location(self,position:(Position | tuple[int,int])) -> GameContent:
        return super().get_location(position)

    def set_location(self,position:(Position | tuple[int,int]),content:GameContent):
        super().set_location(position,content)

class GameGridRender:

    def __init__(self,game_grid:GameGrid):
        self.game_grid = game_grid
        self.output=None

    def _pre_render(self):
        self.output=None
    
    def _post_render(self):
        pass

    def render(self):
        self._pre_render()
        for row in range(0,self.game_grid.size.nr_of_rows):
            self._render_row(row)
        self._post_render()

    def _render_row(self,row:int):
        for col in range(0,self.game_grid.size.nr_of_cols):
            self._render_location(position=Position(col,row))
    
    def _render_location(self,position:Position):
        content =self.game_grid.get_location(position)
        material = self._get_material(content)
        self._render_material(position,material)
        
    def _get_material(self,content:GameContent) -> Material:
        if content == None:
            return Material.NONE
        
        if content.guest != None:
            return self._get_material(content.guest)
        
        return content.material

    def _render_material(self,position:Position,material:Material):
        pass

class TextGameGridRender(GameGridRender):

    def __init__(self,game_grid:GameGrid, material_map:dict[Material,str] = dict()):
        super().__init__(game_grid)
        self.output = ""
        self.material_map = material_map

    def _pre_render(self):
        self.output = ""

    def _render_row(self,row:int):
        self.output += "\n"
        super()._render_row(row)



    def _render_material(self,position:Position,material:Material):
        material_str = material.value
        if material_str in self.material_map:
            material_str = self.material_map[material_str]
        self.output += material_str

class ImageGameGridRender(GameGridRender):

    def __init__(self,game_grid:GameGrid, material_map:dict[str,tuple[int,int,int]] = dict()):
        super().__init__(game_grid)
        self._init_image()
        self.material_map = material_map
        self._init_material_map()
    
    def _init_material_map(self):
        if not Material.STONE.value in self.material_map:
            self.material_map[Material.STONE.value] = Color.BLACK.value
        if not Material.FLOOR.value in self.material_map:
            self.material_map[Material.FLOOR.value] = Color.WHITE.value
        if not Material.FLOOR_MARKED.value in self.material_map:
            self.material_map[Material.FLOOR_MARKED.value] = (255,0,0)
        if not Material.FLOOR_HIGHLIGHTED.value in self.material_map:
            self.material_map[Material.FLOOR_HIGHLIGHTED.value] = (0,255,0)
        if not Material.PLASTIC.value in self.material_map:
            self.material_map[Material.PLASTIC.value] = (255,255,0)
        if not Material.PLASTIC_MARKED.value in self.material_map:
            self.material_map[Material.PLASTIC_MARKED.value] = (255,0,155)
        if not Material.PLASTIC_HIGHLIGHTED.value in self.material_map:
            self.material_map[Material.PLASTIC_HIGHLIGHTED.value] = (0,255,255)
        if not Material.NONE.value in self.material_map:
            self.material_map[Material.NONE.value] = (125,125,125)



    def _init_image(self):
        self.output = np.full   (  (self.game_grid.size.nr_of_rows,self.game_grid.size.nr_of_cols,3),
                                    fill_value = Color.WHITE.value,
                                    dtype=np.uint8
                                )

    def _pre_render(self):
        self._init_image()

  #  def _render_row(self,row:int):
  #      self.output += "\n"
  #      super()._render_row(row)

    def _render_material(self,position:Position,material:Material):
        material_str = material.value
        position_int = position
        if isinstance(position,tuple):
            position_int = Position(position[0],position[1])
        self.output[position_int.row,position_int.col] = self.material_map[material_str]
