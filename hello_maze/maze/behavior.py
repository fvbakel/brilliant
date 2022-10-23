
from dataclasses import dataclass,field
from basegrid import *
from gamegrid import *
import logging
import random

@dataclass
class MoveInfo:
    start_pos:Position
    available_hosts:dict[Direction,GameContent]
    available_positions:set[Position] = field(init=False, repr=False)
    all_positions:set[Position] = field(init=False, repr=False)

    def __post_init__(self):
        self.available_positions = set([content.position for content in self.available_hosts.values() if content.can_host_guest() ])
        self.all_positions = set([content.position for content in self.available_hosts.values()])

    def has_available(self):
        return len(self.available_positions) > 0

    def is_dead_end(self):
        return len(self.all_positions) == 1

    def get_random_available(self,exclude:set[Position] = set()):
        if not self.has_available():
            return None
        remain = self.available_positions - exclude
        if len(remain) == 0:
            remain = self.available_positions
        if len(remain) == 1:
            return next(iter(remain))
        return random.choice(tuple(remain))

class AutomaticMove(Behavior):

    def __init__(self,game_grid:GameGrid):
        super().__init__(game_grid)
        self.history = Route()
        self.nr_stand_still = 0
        self.moveInfo:MoveInfo = None

    @Behavior.subject.setter
    def subject(self,subject:GameContent):
        Behavior.subject.fset(self,subject)
        self.record_new_position()

    def record_new_position(self):
        self.history.append(self._subject.position)

    def determine_new_pos(self,start_position:Position):
        return None

    def do_one_cycle(self):
        if not self._subject is None:
            self.moveInfo = MoveInfo(self._subject.position,self.game_grid.get_available_hosts(self._subject.position))
            new_pos = self.determine_new_pos()
            if new_pos is None:
                self.nr_stand_still +=1
            else:
                self.nr_stand_still = 0
                self.game_grid.move_content(self._subject,new_pos)
                self.record_new_position()

class RandomMove(AutomaticMove):

    def determine_new_pos(self):
        return self.moveInfo.get_random_available()

class RandomDistinctMove(AutomaticMove):

    def determine_new_pos(self):
        return self.moveInfo.get_random_available(exclude=self.history.positions)

class RandomCommonMove(AutomaticMove):

    def __init__(self,game_grid:GameGrid):
        super().__init__(game_grid)
        if hasattr(self.game_grid,'random_common_move'):
            self.coordinator = self.game_grid.random_common_move
        else:
            self.coordinator = self
            self.game_grid.random_common_move = self.coordinator


    def determine_new_pos(self):
        return self.coordinator._determine_new_pos(self.moveInfo)
    
    def _determine_new_pos(self,moveInfo:MoveInfo):
        return moveInfo.get_random_available(exclude=self.history.positions)

class BlockDeadEnds(AutomaticMove):
    def __init__(self,game_grid:GameGrid):
        super().__init__(game_grid)
        self.todo:list[Position] = []
        self.path_back:list[Position] = []

    def determine_new_pos(self):
        if not self.moveInfo.has_available():
            return None

        if self.nr_stand_still > 10:
            self.nr_stand_still = 0
            logging.debug(f"""{self.moveInfo.start_pos} is standing still
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
                        
                        return self.select_move()
            else:
                self.todo.insert(0,self.moveInfo.start_pos)
                return self.moveInfo.get_random_available()
            return None

        if len(self.path_back) > 0:
            return self.select_move_back()
        else:
            return self.select_move()

    def determine_move_back_path(self):
        if len(self.todo) > 0:
            target = self.todo.pop()
            self.set_path_back(self.moveInfo.start_pos,target)
            self.reduce_path()

    # TODO: Make more generic an reusable
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
        for index, pos in reversed(list(enumerate(self.history.path))):
            if pos == target:
                start_index = index
                break
        for index, pos in list(enumerate(self.history.path))[start_index:]:
            if pos == start:
                end_index = index
                break

        if not start_index is None and not end_index is None:
            self.path_back = self.history.path[start_index:end_index]

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
    def select_move_back(self):
        if len(self.path_back) > 0:
            next = self.path_back[-1]
            if next in self.moveInfo.available_positions:
                return self.path_back.pop()

    def select_move(self):
        possible_filtered = self.moveInfo.available_positions - self.history.positions
        all_filtered = self.moveInfo.all_positions - self.history.positions
        if len(all_filtered) == 0:
            self.determine_move_back_path()
            return self.select_move_back()
        
        selected = self.moveInfo.get_random_available()
        if len(possible_filtered) == 0:
            return None
        if len(possible_filtered) == 1:
            selected =  possible_filtered.pop()
        else:
            selected = random.choice(tuple(possible_filtered))
        all_filtered.discard(selected)
        if len(all_filtered) >0:
            self.todo.append(self.moveInfo.start_pos)
        return selected

class Spoiler(BlockDeadEnds):

    def __init__(self,game_grid:GameGrid):
        super().__init__(game_grid)
        self.win_path:list[Position] = []
        self.win_known = False
        if hasattr(self.game_grid,'coordinator'):
            self.coordinator = self.game_grid.coordinator
        else:
            self.coordinator = self
            self.game_grid.coordinator = self.coordinator

    def unregister(self):
        super().unregister()
        if not self.win_known:
            self.set_path_back(self.history.end,self.history.start)
            self.reduce_path()
            if len(self.path_back) > 0:
                self.coordinator.win_path = self.path_back 
                self.coordinator.win_path.append(self._subject.position)
                self.path_back = []

    def determine_new_pos(self):
        if len(self.coordinator.win_path) > 0 and not self.win_known:
            logging.debug("Win path is now known!")
            self.set_win_path()

        if self.win_known:
            return self.select_move_back()
        else:
            return super().determine_new_pos()
    
    def set_win_path(self):
        self.win_known = True
        self.path_back = []
        tail_path:list[Position] = []
        for win_pos in reversed(self.coordinator.win_path):
            tail_path.append(win_pos)
            if self.history.has_position(win_pos):
                if self.moveInfo.start_pos != win_pos:
                    self.set_path_back(self.moveInfo.start_pos,win_pos)
                    self.reduce_path()
                self.path_back =  tail_path[:-1] + self.path_back
                break
        
        if len(self.path_back) == 0:
            # below is a problem if the square size > 0
            logging.debug("Not possible to calculate a win path")
            self.win_known = False


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
                    self.nr_of_steps.append(behavior.history.length -1)
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