
from abc import abstractclassmethod, abstractmethod
from turtle import pos, position
from basegrid import *

import random
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

class Behavior:
    pass

class GameContent:
    def __init__(self):
        self.position:Position  = None
        self.solid:bool         = False
        self.mobile:bool        = False
        self._guest:GameContent = None
        self.material           = Material.FLOOR
        self.trace_material     = Material.NONE
        self.changed            = False
        self.behavior:Behavior  = None

    def can_host_guest(self):
        if self.solid == False and self._guest is None:
            return True
        return False

    @property
    def guest(self):
        return self._guest

    @guest.setter
    def guest(self,guest:GameContent):
        self.changed = True
        self._guest = guest
        if not guest is None:
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
    
    def __init__(self,size:Size):
        super().__init__(size)
        self.behaviors:set[Behavior] = set()

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
            if  not content is None and \
                    not content.solid:
                behavior = behavior_type(self)
                behavior.subject = content
                #self.register_behavior(behavior)
                behaviors.append(behavior)
        return behaviors

    def add_manual_content(self,content:GameContent,behavior_type:type[Behavior]):
        if content is None or not content.mobile:
            return None
        if not content.behavior is None:
            return None
        if not self.add_to_first_free_spot(content):
            return None
        behavior = behavior_type(self)
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

        if content_to_move.trace_material != Material.NONE:
            source_content.material = content_to_move.trace_material

    def get_available_directions(self,position:Position):
        result:dict[Direction,Position] = dict()
        for direction in Direction:
            if direction == Direction.HERE:
                continue
            candidate_pos = position.get_position_in_direction(direction)
            if self.has_location(candidate_pos):
                candidate_content = self.get_location(candidate_pos)
                if candidate_content.can_host_guest():
                    result[direction]= candidate_pos
        return result
        

    def register_behavior(self,behavior:Behavior):
        self.behaviors.add(behavior)

    def unregister_behavior(self,behavior:Behavior):
        self.behaviors.discard(behavior)

    def do_one_cycle(self):
        for behavior in list(self.behaviors):
            if behavior in self.behaviors:
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
                if not content is None and content.changed:
                    self._render_content(content)
                    content.changed = False

    def _render_row(self,row:list[GameContent]):
        for content in row:
            self._render_content(content)

    def _render_content(self,content:GameContent):
        if not content is None:
            material = self._get_material(content)
            self._render_material(content.position,material)
            
    def _get_material(self,content:GameContent) -> Material:
        if content is None:
            return Material.NONE
        
        if not content.guest is None:
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

    def _render_material(self,position:Position,material:Material):
        material_str = material.value
        self.output[position.row,position.col] = self.material_map[material_str]



class Behavior:

    def __init__(self,game_grid:GameGrid):
        self.game_grid = game_grid
        self.game_grid.register_behavior(self)
        self._subject:GameContent = None

    @property
    def subject(self):
        return self._subject

    @subject.setter
    def subject(self,subject:GameContent):
        self._subject = subject
        if not self._subject is None:
            self._subject.behavior = self

    @abstractclassmethod
    def do_one_cycle(self):
        pass

    def unregister(self):
        self.game_grid.unregister_behavior(self)

class ManualMove(Behavior):

    def __init__(self,game_grid:GameGrid):
        super().__init__(game_grid)
        self.next_move:Direction = Direction.HERE

    def set_move(self,direction:Direction):
        self.next_move = direction

    def do_one_cycle(self):
        if self.next_move != Direction.HERE and not self._subject is None:
            self.game_grid.move_content_direction(self._subject,self.next_move)
        self.next_move = Direction.HERE

class AutomaticMove(Behavior):

    def __init__(self,game_grid:GameGrid):
        super().__init__(game_grid)
        self.history_path:list[position] = []
        self.history_path_set:set[position] = set()

    @Behavior.subject.setter
    def subject(self,subject:GameContent):
        Behavior.subject.fset(self,subject)
        self.record_new_position()

    def record_new_position(self):
        self.history_path.append(self._subject.position)
        self.history_path_set.add(self._subject.position)

    @abstractmethod
    def determine_new_pos(self,start_position:Position):
        return None

    def do_one_cycle(self):
        if not self._subject is None:
            new_pos = self.determine_new_pos(self._subject.position)
            if not new_pos is None:
                self.game_grid.move_content(self._subject,new_pos)
                self.record_new_position()

class RandomMove(AutomaticMove):

    def determine_new_pos(self,start_position:Position):
        possible_directions = self.game_grid.get_available_directions(start_position)
        if len(possible_directions) == 0:
            return None
        return random.choice(tuple(possible_directions.values()))

class RandomDistinctMove(AutomaticMove):

    def determine_new_pos(self,start_position:Position):
        possible_directions = self.game_grid.get_available_directions(start_position)
        if len(possible_directions) == 0:
            return None
        possible_set = set(possible_directions.values())
        possible_filtered = possible_set - self.history_path_set
        if len(possible_filtered) == 0:
            possible_filtered = possible_directions.values()
        return random.choice(tuple(possible_filtered))

class Smart001Move(AutomaticMove):
    def __init__(self,game_grid:GameGrid):
        super().__init__(game_grid)
        self.todo:list[(Position,Position)] = list()
        self.path_back:list[Position] = list()

    def determine_new_pos(self,start_position:Position):
        possible_directions = self.game_grid.get_available_directions(start_position)
        if len(possible_directions) == 0:
            return None
    
        possible_set = set(possible_directions.values())

        if len(self.path_back) > 0:
            return self.select_move_back(possible_set)
        else:
            return self.select_move(start_position,possible_set)

    def determine_move_back_path(self,start_position:Position):
        if len(self.todo) > 0:
            target = self.todo.pop()
            self.set_path_back(start_position,target)
            self.reduce_path()

    def set_path_back(self,start:Position,target:Position):
        """
            history path could be like this
            [1,target,2,3,target,a,b,c,start_position,x,y,z,start_position]
            expected result from this method
            [target,a,b,c]
            Some mechanism is:
            1. search from the back the first occurrence of target, 
            2. from that point search the start_position
            3 return the in between
        """
        start_index:int = None
        end_index:int = None
        for index, pos in reversed(list(enumerate(self.history_path))):
            if pos == target:
                start_index = index
                break
        for index, pos in list(enumerate(self.history_path))[start_index:]:
            if pos == start:
                end_index = index
                break

        if not start_index is None and not end_index is None:
            self.path_back = self.history_path[start_index:end_index]

    def reduce_path(self):
        path = self.path_back
        pos_map = dict()
        for index,pos in enumerate(path):
            if pos in pos_map:
                pos_map[pos].append(index)
            else:
                pos_map[pos] = [index]
        
        if len(pos_map) > 0 :
            cut_start = None
            cut_end = None
            cut_diff = 0
            for pos, index_list in pos_map.items():
                diff = index_list[-1] - index_list[0]
                if diff > cut_diff:
                    cut_diff = diff
                    cut_start = index_list[0]
                    cut_end =  index_list[-1]

            if not cut_start is None and not cut_end is None:
                self.path_back =  path[:cut_start] + path[cut_end:]
                self.reduce_path()

    def select_move_back(self,possible_set:set[Position]):
        if len(self.path_back) > 0:
            next = self.path_back[-1]
            if next in possible_set:
                return self.path_back.pop()

    def select_move(self,start_position:Position,possible_set:set[Position]):
        possible_filtered = possible_set - self.history_path_set
        if len(possible_filtered) == 0:
            #TODO: switch state here, because we checked every thing here
            #possible_filtered = possible_set
            self.determine_move_back_path(start_position)
            return self.select_move_back(possible_set)
        if len(possible_filtered) == 1:
            selected = possible_filtered.pop()
        else:
            selected = random.choice(tuple(possible_filtered))
            possible_filtered.discard(selected)
            self.todo.append(start_position)
        return selected

class FinishDetector(Behavior):

    def __init__(self,game_grid:GameGrid):
        super().__init__(game_grid)
        self.finished:list[GameContent] = []

    def do_one_cycle(self):
        if not self._subject is None and not self._subject.guest is None:
            self.finished.append(self._subject.guest)
            if not self._subject.guest.behavior is None:
                self._subject.guest.behavior.unregister()
            self._subject.guest = None
            


