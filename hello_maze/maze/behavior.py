
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
        self.path_back = Route()

    def determine_new_pos(self):
        if not self.moveInfo.has_available():
            return None

        if self.nr_stand_still > 10:
            self.nr_stand_still = 0
            logging.debug(f"""{self.moveInfo.start_pos} is standing still
                                todo size {len(self.todo)}
                                path back {self.path_back.length}
                            """)
            if len(self.todo) > 0:
                if self.path_back.length > 0:
                    logging.debug(f""""
                                    destination {self.path_back.end}
                                    """)
                    if len(self.todo) > 0:
                        logging.debug(f""""
                                        new destination {self.todo[-1]}
                                        """)
                        self.todo.insert(0,self.path_back.end)
                        self.path_back.reset()
                        
                        return self.select_move()
            else:
                self.todo.insert(0,self.moveInfo.start_pos)
                return self.moveInfo.get_random_available()
            return None

        if self.path_back.length > 0:
            return self.select_move_back()
        else:
            return self.select_move()

    def determine_move_back_path(self):
        if len(self.todo) > 0:
            target = self.todo.pop()
            self.set_path_back(self.moveInfo.start_pos,target)
            self.reduce_path()

    def set_path_back(self,start:Position,target:Position):
        sub_route = self.history.get_sub_route(start,target)
        if sub_route is None:
            self.path_back.reset()
        else:
            self.path_back = sub_route

    def reduce_path(self):
        self.path_back.optimize()

    # TODO: Make a more generic mechanism that can be reused
    def select_move_back(self):
        if self.path_back.length > 0:
            next = self.path_back.start
            if next == self.moveInfo.start_pos:
                self.path_back.pop(0)
                return self.select_move_back()
            if next in self.moveInfo.available_positions:
                return self.path_back.pop(0)

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
        self.win_path:Route = None
        self.win_known = False
        if hasattr(self.game_grid,'coordinator'):
            self.coordinator = self.game_grid.coordinator
        else:
            self.coordinator = self
            self.game_grid.coordinator = self.coordinator

    def unregister(self):
        super().unregister()
        if not self.win_known:
            self.coordinator.win_path = Route(self.history.path)
            self.coordinator.win_path.append(self._subject.position)
            self.coordinator.win_path.optimize()
            if not self.coordinator.win_path.is_valid():
                logging.error(f"win path is not a valid path! {str(self.coordinator.win_path)}")
            self.path_back.reset()

    def determine_new_pos(self):
        if  not self.coordinator.win_path is None and \
                self.coordinator.win_path.length > 0 and  \
                not self.win_known:
            logging.debug("Win path is now known!")
            self.set_win_path()

        if self.win_known:
            return self.select_move_back()
        else:
            return super().determine_new_pos()
    
    def set_win_path(self):
        self.win_known = True
        tail_path = Route()
        self.path_back.reset()
        for win_pos in reversed(self.coordinator.win_path.path):
            tail_path.append(win_pos)
            if self.history.has_position(win_pos):
                if self.moveInfo.start_pos != win_pos:
                    begin_route = self.history.get_sub_route(self.moveInfo.start_pos,win_pos)
                    if begin_route is None:
                        logging.debug("Can not calculate a route to the win path but pos in win_pat is in history?")
                        self.win_known = False
                        break
                    begin_route.optimize()
                    self.path_back = begin_route
                tail_path.reverse()
                self.path_back.add_route(tail_path)
                break
        
        if self.path_back.length == 0:
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