
from abc import abstractclassmethod
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
    pass

class GameContent:
    def __init__(self):
        self.position:Position  = None
        self.solid:bool         = False
        self.mobile:bool        = False
        self._guest:GameContent  = None
        self.material           = Material.FLOOR

    def can_host_guest(self):
        if self.solid == False and self._guest == None:
            return True
        return False

    def set_guest(self,guest:GameContent):
        self._guest = guest
        if guest != None:
            guest.position =self.position

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
        if isinstance(position,tuple):
            content.position = Position(position[0],position[1])
        else:
            content.position = position
        super().set_location(position,content)

    def add_particle(self,particle:Particle):
        for col in range(0,self.size.nr_of_cols):
            content = self.get_location((col,0))
            if content.can_host_guest():
                content.set_guest(particle)
                break

    def move_content_direction(self,content_to_move:GameContent,direction:Direction):
        if direction == Direction.HERE or content_to_move == None:
            return
        request_pos = content_to_move.position.get_position_in_direction(direction)
        self.move_content(content_to_move,request_pos)

    def move_content(self,content_to_move:GameContent,request_position:Position):
        if      content_to_move == None or \
                not content_to_move.mobile or \
                not self.has_location(request_position):
            return

        request_content = self.get_location(request_position)
        if not request_content.can_host_guest():
            return

        source_content = self.get_location(content_to_move.position)

        request_content.set_guest(content_to_move)
        source_content.set_guest(None)

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
        
        if content._guest != None:
            return self._get_material(content._guest)
        
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
        self.output[position.row,position.col] = self.material_map[material_str]



class ActionControl:

    def __init__(self,game_grid:GameGrid):
        self.game_grid = game_grid
        self.current_particle:Particle = None

    @abstractclassmethod
    def do_one_cycle(self):
        pass

class ManualMoveControl(ActionControl):

    def __init__(self,game_grid:GameGrid):
        super().__init__(game_grid)
        self.next_move:Direction = Direction.HERE

    def set_current_particle(self,particle:Particle):
        self.current_particle = particle

    def set_move(self,direction:Direction):
        self.next_move = direction

    def do_one_cycle(self):
        if self.next_move != Direction.HERE and self.current_particle != None:
            self.game_grid.move_content_direction(self.current_particle,self.next_move)

        self.next_move = Direction.HERE
