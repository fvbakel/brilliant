from __future__ import annotations
from basegrid import *
import numpy as np

class Material(ExtendedEnum):
    NONE                  = '_'
    FLOOR                 = 'f'
    FLOOR_MARKED          = ' '
    FLOOR_HIGHLIGHTED     = 'F'
    STONE                 = '*'
    PLASTIC               = 'P'
    PLASTIC_MARKED        = 'p'
    PLASTIC_HIGHLIGHTED   = '0'

class Color(ExtendedEnum):
    WHITE = (255,255,255)
    BLACK = (0,0,0)

class ColorMap:
    def __init__(self, 
            start_color:tuple[int,int,int], 
            end_color:tuple[int,int,int], 
            start:float, 
            end:float):
        self.start_color = np.array(start_color)
        self.end_color = np.array(end_color)
        self.start = float(start)
        self.end = float(end)
        self.range = float(end - start)
        self.ratios = (self.end_color - self.start_color) / self.range

    def __getitem__(self, value:float):
        color = tuple(self.start_color + (self.ratios * (value - self.start)))
        return (int(color[0]), int(color[1]), int(color[2]))

class Layer:
    pass

class Layer:

    def __init__(self,name:str,order:int,default_color:tuple[int,int,int] = Color.BLACK):
        if name is None or len(name) == 0:
            raise ValueError(f'Name "{name}" is not allowed for a Layer')

        self.name = name
        self._order = order
        self.active = True
        self.positions:dict[Position,tuple[int,int,int]] = dict()
        self.default_color = default_color 

    def set_position(self,position:Position,color:tuple[int,int,int] = None):
        if color is None:
            self.positions[position] = self.default_color
        else:
            self.positions[position] = color

    def remove_position(self,position:Position):
        self.positions.pop(position)

    def __repr__(self) -> str:
        return f"{self._order} - {self.name}"

from functools import cmp_to_key
class LayerManager:

    def __init__(self):
        self.layers:list[Layer] = []
        self._layers_map:dict[str,Layer] = dict()

    @staticmethod
    def compare_order(layer_1:Layer,layer_2:Layer):
        return layer_1._order - layer_2._order

    def add_layer(self,layer:Layer):
        if layer.name in self._layers_map:
            raise ValueError(f'Layer with name: {layer.name} already exists!')
        self.layers.append(layer)
        self._layers_map[layer.name] = layer
        if len(self.layers) > 1:
            self.layers.sort(key=cmp_to_key(LayerManager.compare_order))
        
    def remove_layer(self,layer:Layer):
        self.layers.remove(layer)
        self._layers_map.pop(layer.name)

    def get_layer(self,name:str):
        return self._layers_map.get(name,None)

    def reset(self):
        self.layers.clear()
        self._layers_set.clear()

    def get_color(self,position:Position):
        for layer in self.layers:
            if not layer.active:
                continue
            if position in layer.positions:
                return layer.positions[position]
        return None

class GameContent:
    pass

class Behavior: 
    pass

class GameContent:
    def __init__(self):
        self.position:Position | None   = None
        self.solid:bool                 = False
        self.mobile:bool                = False
        self._guest:GameContent | None  = None
        self.material                   = Material.FLOOR
        self.trace_layer:Layer | None   = None
        self.changed                    = False
        self.behavior:Behavior | None   = None

    def can_host_guest(self):
        if self.solid == False and self._guest is None:
            return True
        return False

    def has_guest_ability(self):
        if self.solid == False:
            return True
        return False

    @property
    def guest(self):
        return self._guest

    @guest.setter
    def guest(self,guest:GameContent | None):
        self.changed = True
        self._guest = guest
        if guest is not None:
            guest.position = self.position

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

class BehaviorFactory:
    pass

class GameGrid(Grid):
    
    def __init__(self,size:Size):
        super().__init__(size)
        self.behaviors:dict[int,set[Behavior]] = dict()
        self.layer_mgr = LayerManager()

    def get_location(self,position:(Position | tuple[int,int])) -> GameContent:
        return super().get_location(position)

    def set_location(self,position:(Position | tuple[int,int]),content:GameContent):
        if isinstance(position,tuple):
            content.position = Position(position[0],position[1])
        else:
            content.position = position
        super().set_location(position,content)

    # TODO improve below to make more generic
    def add_to_first_free_spot(self,particle:Particle):
        for col in range(0,self.size.nr_of_cols):
            content = self.get_location((col,0))
            if content.can_host_guest():
                content.guest = particle
                return True
        return False

    def set_behavior_last_spots(self,behavior_type:type[Behavior]):
        col:list[GameContent]
        behaviors:list[Behavior] = []
        for col in self.locations:
            content = col[-1]
            if  content is not None and \
                    not content.solid:
                behavior = behavior_type(self)  # type: ignore
                behavior.subject = content  # type: ignore
                behaviors.append(behavior)
        return behaviors

    def add_manual_content(self,content:GameContent,factory:BehaviorFactory):
        if content is None or not content.mobile:
            return None
        if content.behavior is not None:
            return None
        if not self.add_to_first_free_spot(content):
            return None
        behavior = factory.get_new(self)
        behavior.subject = content
        return behavior

    def move_content_direction(self,content_to_move:GameContent,direction:Direction):
        if direction == Direction.HERE or content_to_move is None:
            return
        request_pos = content_to_move.position.get_position_in_direction(direction)
        self.move_content(content_to_move,request_pos)

    def move_content(self,content_to_move:GameContent,request_position:Position):
        if      content_to_move is None or \
                not content_to_move.mobile or \
                not self.has_location(request_position):
            return

        request_content = self.get_location(request_position)
        if not request_content.can_host_guest():
            return

        source_content = self.get_location(content_to_move.position)

        request_content.guest = content_to_move
        source_content.guest = None

        if content_to_move.trace_layer is not None:
            content_to_move.trace_layer.set_position(source_content.position)

    def get_available_hosts(self,position:Position):
        result:dict[Direction,GameContent] = dict()
        for direction in Direction:
            if direction == Direction.HERE:
                continue
            candidate_pos = position.get_position_in_direction(direction)
            if self.has_location(candidate_pos):
                candidate_content = self.get_location(candidate_pos)
                if candidate_content.has_guest_ability():
                    result[direction]= candidate_content
        return result
        

    def register_behavior(self,behavior:Behavior):
        if not behavior.priority in self.behaviors:
            self.behaviors[behavior.priority]= set()
          
        self.behaviors[behavior.priority].add(behavior)

    def unregister_behavior(self,behavior:Behavior):
        if behavior.priority in self.behaviors:
            self.behaviors[behavior.priority].discard(behavior)

    def do_one_cycle(self):
        priorities = sorted(self.behaviors.keys())
        for priority in priorities:
            # check if it is still in the list because 
            # one cycle could have removed an other behavior 
            # from the original list
            if priority not in self.behaviors:
                continue
            for behavior in list(self.behaviors[priority]):    
                if behavior in self.behaviors[priority]:
                    behavior.do_one_cycle()


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
        row:list[GameContent]
        for row in self.game_grid.locations:
            self._render_row(row)
        self._post_render()

    def render_changed(self):
        if self.output is None:
            return
        for row in self.game_grid.locations:
            content:GameContent
            for content in row:
                if content is not None and content.changed:
                    self._render_content(content)
                    content.changed = False

    def _render_row(self,row:list[GameContent]):
        for content in row:
            self._render_content(content)

    def _render_content(self,content:GameContent):
        if content is not None:
            material = self._get_material(content)
            self._render_material(content.position,material)
            
    def _get_material(self,content:GameContent) -> Material:
        if content is None:
            return Material.NONE
        
        if content.guest is not None:
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

    def _render_row(self,row:list[GameContent]):
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
            self.material_map[Material.PLASTIC_HIGHLIGHTED.value] = (0,139,0)
        if not Material.NONE.value in self.material_map:
            self.material_map[Material.NONE.value] = (125,125,125)

    def _init_image(self):
        self.output = np.full   (  (self.game_grid.size.nr_of_rows,self.game_grid.size.nr_of_cols,3),
                                    fill_value = Color.WHITE.value,
                                    dtype=np.uint8
                                )
    def _pre_render(self):
        self._init_image()

    def _render_content(self,content:GameContent):
        if content is not None:
            if content.guest is not None:
                return super()._render_content(content)
            color = self.game_grid.layer_mgr.get_color(content.position)
            if color is None:
                return super()._render_content(content)
            self._set_color(content.position,color)
            
    def _set_color(self,position:Position,color:tuple[int,int,int]):
        self.output[position.row,position.col] = color

    def _render_material(self,position:Position,material:Material):
        material_str = material.value
        self._set_color(position,self.material_map[material_str])

class Behavior:

    def __init__(self,game_grid:GameGrid):
        self.game_grid = game_grid
        self.priority:int
        self.game_grid.register_behavior(self)
        self._subject:GameContent = None  # type: ignore

    @property
    def subject(self):
        return self._subject

    @subject.setter
    def subject(self,subject:GameContent):
        self._subject = subject
        if self._subject is not None:
            self._subject.behavior = self

    def do_one_cycle(self):
        pass

    def unregister(self):
        self.game_grid.unregister_behavior(self)

class ManualMove(Behavior):

    def __init__(self,game_grid:GameGrid):
        self.priority = 9
        super().__init__(game_grid)
        self.next_move:Direction = Direction.HERE

    def set_move(self,direction:Direction):
        self.next_move = direction

    def do_one_cycle(self):
        if self.next_move != Direction.HERE and not self._subject is None:
            self.game_grid.move_content_direction(self._subject,self.next_move)
        self.next_move = Direction.HERE

class BehaviorFactory:
    def __init__(self):
        self.behavior_type:type[Behavior] = Behavior
        self.is_default = True

    def get_new(self,game_grid:GameGrid) -> Behavior:
        return self.behavior_type(game_grid)