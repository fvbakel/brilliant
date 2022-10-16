import basegrid as bg

import random
import numpy as np
import logging

class Material(bg.Enum):
    NONE                  = '_'
    FLOOR                 = 'f'
    FLOOR_MARKED          = ' '
    FLOOR_HIGHLIGHTED     = 'F'
    STONE                 = '*'
    PLASTIC               = 'P'
    PLASTIC_MARKED        = 'p'
    PLASTIC_HIGHLIGHTED   = '0'

class Color(bg.Enum):
    WHITE = (255,255,255)
    BLACK = (0,0,0)

class GameContent:
    pass

class Behavior: 
    pass

class GameContent:
    def __init__(self):
        self.position:bg.Position   = None
        self.solid:bool             = False
        self.mobile:bool            = False
        self._guest:GameContent     = None
        self.material               = Material.FLOOR
        self.trace_material         = Material.NONE
        self.changed                = False
        self.behavior:Behavior      = None

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

class GameGrid(bg.Grid):
    
    def __init__(self,size:bg.Size):
        super().__init__(size)
        self.behaviors:dict[int,set[Behavior]] = dict()

    def get_location(self,position:(bg.Position | tuple[int,int])) -> GameContent:
        return super().get_location(position)

    def set_location(self,position:(bg.Position | tuple[int,int]),content:GameContent):
        if isinstance(position,tuple):
            content.position = bg.Position(position[0],position[1])
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
                behavior = behavior_type(self)  # type: ignore
                behavior.subject = content  # type: ignore
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

    def move_content_direction(self,content_to_move:GameContent,direction:bg.Direction):
        if direction == bg.Direction.HERE or content_to_move is None:
            return
        request_pos = content_to_move.position.get_position_in_direction(direction)
        self.move_content(content_to_move,request_pos)

    def move_content(self,content_to_move:GameContent,request_position:bg.Position):
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

    def get_available_directions(self,position:bg.Position):
        result:dict[bg.Direction,GameContent] = dict()
        for direction in bg.Direction:
            if direction == bg.Direction.HERE:
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

    def _render_material(self,position:bg.Position,material:Material):
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

    def _render_material(self,position:bg.Position,material:Material):
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

    def _render_material(self,position:bg.Position,material:Material):
        material_str = material.value
        self.output[position.row,position.col] = self.material_map[material_str]

class Behavior:

    def __init__(self,game_grid:GameGrid):
        self.game_grid = game_grid
        self.priority:int = 10
        self.game_grid.register_behavior(self)
        self._subject:GameContent = None  # type: ignore

    @property
    def subject(self):
        return self._subject

    @subject.setter
    def subject(self,subject:GameContent):
        self._subject = subject
        if not self._subject is None:
            self._subject.behavior = self

    def do_one_cycle(self):
        pass

    def unregister(self):
        self.game_grid.unregister_behavior(self)

class ManualMove(Behavior):

    def __init__(self,game_grid:GameGrid):
        super().__init__(game_grid)
        self.next_move:bg.Direction = bg.Direction.HERE

    def set_move(self,direction:bg.Direction):
        self.next_move = direction

    def do_one_cycle(self):
        if self.next_move != bg.Direction.HERE and not self._subject is None:
            self.game_grid.move_content_direction(self._subject,self.next_move)
        self.next_move = bg.Direction.HERE

#
# TODO: Move all below to a separate module
class AutomaticMove(Behavior):

    def __init__(self,game_grid:GameGrid):
        super().__init__(game_grid)
        self.history_path:list[bg.Position] = []
        self.history_path_set:set[bg.Position] = set()
        self.nr_stand_still = 0

    @Behavior.subject.setter
    def subject(self,subject:GameContent):
        Behavior.subject.fset(self,subject)
        self.record_new_position()

    def record_new_position(self):
        self.history_path.append(self._subject.position)
        self.history_path_set.add(self._subject.position)

    def determine_new_pos(self,start_position:bg.Position):
        return None

    def do_one_cycle(self):
        if not self._subject is None:
            new_pos = self.determine_new_pos(self._subject.position)
            if new_pos is None:
                self.nr_stand_still +=1
            else:
                self.nr_stand_still = 0
                self.game_grid.move_content(self._subject,new_pos)
                self.record_new_position()

class RandomMove(AutomaticMove):

    def determine_new_pos(self,start_position:bg.Position):
        possible_hosts = self.game_grid.get_available_directions(start_position)
        possible_positions = tuple([content.position for content in possible_hosts.values() if content.can_host_guest() ])
        if len(possible_positions) == 0:
            return None
        
        return random.choice(tuple(possible_positions))

class RandomDistinctMove(AutomaticMove):

    def determine_new_pos(self,start_position:bg.Position):
        possible_hosts = self.game_grid.get_available_directions(start_position)
        possible_positions = tuple([content.position for content in possible_hosts.values() if content.can_host_guest() ])
        if len(possible_positions) == 0:
            return None
        possible_set = set(possible_positions)
        possible_filtered = possible_set - self.history_path_set
        if len(possible_filtered) == 0:
            possible_filtered = possible_positions
        return random.choice(tuple(possible_filtered))

class BlockDeadEnds(AutomaticMove):
    def __init__(self,game_grid:GameGrid):
        super().__init__(game_grid)
        self.todo:list[bg.Position] = []
        self.path_back:list[bg.Position] = []

    def determine_new_pos(self,start_position:bg.Position):
        possible_hosts = self.game_grid.get_available_directions(start_position)
        possible_positions = tuple([content.position for content in possible_hosts.values() if content.can_host_guest() ])
        all_host_positions = set([content.position for content in possible_hosts.values() ])
        if len(possible_positions) == 0:
            return None
    
        possible_set = set(possible_positions)

        if self.nr_stand_still > 10:
            self.nr_stand_still = 0
            logging.debug(f"""{start_position} is standing still
                                todo size {len(self.todo)}
                                path back {len(self.path_back)}
                            """)
            if len(self.todo) > 0:
                if len(self.path_back) > 0:
                    logging.debug(f""""
                                    destination {self.path_back[0]}
                                    """)
                    if len(self.todo) > 0:
                        logging.debug(f""""
                                        new destination {self.todo[-1]}
                                        """)
                        self.todo.insert(0,self.path_back[0])
                        self.path_back = []
                        
                        return self.select_move(start_position,possible_set,all_host_positions)
            else:
                selected = random.choice(tuple(possible_set))
                self.todo.insert(0,start_position)
                return selected
            return None

        if len(self.path_back) > 0:
            return self.select_move_back(possible_set)
        else:
            return self.select_move(start_position,possible_set,all_host_positions)

    def determine_move_back_path(self,start_position:bg.Position):
        if len(self.todo) > 0:
            target = self.todo.pop()
            self.set_path_back(start_position,target)
            self.reduce_path()

    # TODO: Make more generic an reusable
    def set_path_back(self,start:bg.Position,target:bg.Position):
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

    # TODO: make a more generic reusable method class
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

    #
    # TODO: Make a more generic mechanism that can be reused
    def select_move_back(self,possible_set:set[bg.Position]):
        if len(self.path_back) > 0:
            next = self.path_back[-1]
            if next in possible_set:
                return self.path_back.pop()

    def select_move(    self,
                        start_position:bg.Position,
                        possible_set:set[bg.Position],
                        all_host_positions:set[bg.Position],
                    ):
        possible_filtered = possible_set - self.history_path_set
        all_filtered = all_host_positions - self.history_path_set
        if len(all_filtered) == 0:
            self.determine_move_back_path(start_position)
            return self.select_move_back(possible_set)
        if len(possible_filtered) == 0:
            return None
        if len(possible_filtered) == 1:
            selected = possible_filtered.pop()
        else:
            selected = random.choice(tuple(possible_filtered))
            all_filtered.discard(selected)
            self.todo.append(start_position)
        return selected

class FinishDetector(Behavior):

    def __init__(self,game_grid:GameGrid):
        super().__init__(game_grid)
        self.finished:list[GameContent] = []
        self.priority = 1
        self.nr_of_steps:list[int] = []

    def do_one_cycle(self):
        if not self._subject is None and not self._subject.guest is None:
            self.finished.append(self._subject.guest)
            
            if not self._subject.guest.behavior is None:
                self._subject.guest.behavior.unregister()
                if isinstance(self._subject.guest.behavior,AutomaticMove):
                    behavior:AutomaticMove = self._subject.guest.behavior
                    self.nr_of_steps.append(len(behavior.history_path) -1)
            if self._subject.guest.trace_material != Material.NONE:
                self._subject.material = self._subject.guest.trace_material
            self._subject.guest = None


class AutomaticAdd(Behavior):

    def __init__(self,game_grid:GameGrid):
        super().__init__(game_grid)
        self.priority = 90
        self.nr_started = 0
        self.active = False
        self.move_type:type[AutomaticMove] = RandomMove

    def do_one_cycle(self):
        if self.active:
            particle = Particle()
            particle.trace_material = Material.FLOOR_HIGHLIGHTED
            behavior = self.game_grid.add_manual_content(particle,self.move_type)
            if not behavior is None:
                self.nr_started += 1
