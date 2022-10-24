
from dataclasses import dataclass,field
from typing import SupportsIndex
from basegrid import *
from gamegrid import *
import logging
import random

@dataclass
class MoveInfo:
    start_pos:Position
    available_hosts:dict[Direction,GameContent]
    visited:set[Position]
    available_positions:set[Position] = field(init=False, repr=False)
    new_available_positions:set[Position] = field(init=False, repr=False)
    all_positions:set[Position] = field(init=False, repr=False)
    new_positions:set[Position] = field(init=False, repr=False)

    def __post_init__(self):
        self.available_positions = set([content.position for content in self.available_hosts.values() if content.can_host_guest() ])
        self.new_available_positions = self.available_positions - self.visited
        self.all_positions = set([content.position for content in self.available_hosts.values()])
        self.new_positions = self.all_positions - self.visited

    def has_available(self):
        return len(self.available_positions) > 0
    
    def has_new_available(self):
        return len(self.new_available_positions) > 0
    
    def has_new_positions(self):
        return len(self.new_positions) > 0

    def nr_available(self):
        return len(self.available_positions)
    
    def nr_new_available(self):
        return len(self.new_available_positions)

    def nr_new_positions(self):
        return len(self.new_positions)

    def is_dead_end(self):
        return len(self.all_positions) == 1

    def _get_random(self,positions:set[Position]) -> (None | Position):
        if len(positions) == 0:
            return None
        if len(positions) == 1:
            return tuple(positions)[0]
        return random.choice(tuple(positions))

    def get_random_available(self):
        return self._get_random(self.available_positions)

    def get_random_new_available(self):
        return self._get_random(self.new_available_positions)


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

    def determine_new_pos(self):
        return None

    def do_one_cycle(self):
        if not self._subject is None:
            self.moveInfo = MoveInfo(   
                self._subject.position,
                self.game_grid.get_available_hosts(self._subject.position),
                self.history.positions
            )
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
        return self.moveInfo.get_random_new_available()

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
        return moveInfo.get_random_new_available()

class MoveBack(AutomaticMove):

    def __init__(self,game_grid:GameGrid):
        super().__init__(game_grid)
        self.path_back = Route()
    
    def set_path_back(self,start:Position,target:Position):
        sub_route = self.history.get_sub_route(start,target)
        if sub_route is None:
            self.path_back.reset()
        else:
            self.path_back = sub_route

    def optimize_move_back(self):
        self.path_back.optimize()

    def select_move_back(self):
        if self.path_back.length > 0:
            next = self.path_back.start
            if next == self.moveInfo.start_pos:
                self.path_back.pop(0)
                return self.select_move_back()
            if next in self.moveInfo.available_positions:
                return self.path_back.pop(0)

class BlockDeadEnds(MoveBack):
    def __init__(self,game_grid:GameGrid):
        super().__init__(game_grid)
        self.todo:list[Position] = []

    def determine_new_pos(self):
        if not self.moveInfo.has_available():
            return None

        if self.path_back.length > 0:
            return self.select_move_back()
        else:
            return self.select_move()

    def determine_move_back_path(self):
        if len(self.todo) > 0:
            target = self.todo.pop()
            self.set_path_back(self.moveInfo.start_pos,target)
            self.optimize_move_back()

    def select_move(self):
        if not self.moveInfo.has_new_positions():
            self.determine_move_back_path()
            return self.select_move_back()
        selected = self.moveInfo.get_random_new_available()
        if not selected is None and self.moveInfo.nr_new_positions() > 1:
            self.todo.append(self.moveInfo.start_pos)
        return selected

class BackOut(BlockDeadEnds):

    def determine_new_pos(self):
        if not self.moveInfo.has_available():
            return None

        if self.nr_stand_still > 10:
            logging.debug(f"Standstill detected on pos {self.moveInfo.start_pos}")
            if self.path_back.length == 0:
                logging.debug(f"Moving back pos {self.moveInfo.start_pos}")
                self.determine_move_back_path()

        if self.path_back.length > 0:
            return self.select_move_back()
        else:
            return self.select_move()

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

class RuleMove(AutomaticMove):
    def __init__(self,game_grid:GameGrid):
        super().__init__(game_grid)
        self.router:Router
        self.navigator:Navigator
        self.todo:ToDoManager
        self.discoverer:Discoverer
        self.standstill:StandStillHandler

    def determine_new_pos(self):
        if not self.moveInfo.has_available():
            return None

        if not self.standstill is None:
            new_pos = self.standstill.get_move()
            if not new_pos is None:
                return new_pos

        if not self.router is None and self.router.has_route():
            return self.router.get_new_pos()

        if not self.moveInfo.has_new_positions():
            if not self.request_new_route():
                return None
            return self.router.get_new_pos()
        else:
            return self.select_discover_move()

    def request_new_route(self):
        if not self.todo.has_to_do() or self.router.locked:
            return False

        target = self.todo.get_next()
        new_route = self.navigator.get_route(self.moveInfo.start_pos,target)
        if new_route is None:
            logging.error("Can not find path back ")
            return False
        new_route.optimize()
        self.router.set_route(new_route)
        return True

    def select_discover_move(self):           
        selected = self.discoverer.get_move()
        if not selected is None and self.moveInfo.nr_new_positions() > 1:
            self.todo.append(self.moveInfo.start_pos)
        return selected

class Router:

    def __init__(self,mover:AutomaticMove):
        self.mover = mover
        self._route = Route()
        self.locked = False

    def has_route(self):
        return self._route.length > 0

    def set_route(self,route:Route):
        if self.locked:
            return False
        self._route = route
        return True
    
    def reset_route(self):
        if self.locked:
            return False
        self._route.reset()
        return True

    def optimize_route(self):
        if self.locked:
            return
        self._route.optimize()

    def get_new_pos(self) -> (Position | None):
        if self._route is None or self._route.length == 0:
            return None
        
        next = self._route.start
        if next == self.mover.moveInfo.start_pos:
            self._route.pop(0)
            return self.get_new_pos()
        if next in self.mover.moveInfo.available_positions:
            return self._route.pop(0)
        if not next in self.mover.moveInfo.all_positions:
            # TODO: think of how to signal that this was detected?
            logging.error("Route is no longer possible")
            #self.route.reset()
            return None

class Navigator:

    def __init__(self,mover:AutomaticMove):
        self.mover = mover

    def get_route_to_route(self,target_route:Route) -> (Route | None):
        return None

    def get_route(self,start:Position,target:Position) -> (Route | None):
        return None

class HistoryNavigator(Navigator):

    def get_route_to_route(self,target_route:Route):
        tail_path = Route()
        new_route = Route()
        for target_pos in reversed(target_route.path):
            tail_path.append(target_pos)
            if self.mover.history.has_position(target_pos):
                if self.mover.moveInfo.start_pos != target_pos:
                    begin_route = self.mover.history.get_sub_route(
                        self.mover.moveInfo.start_pos,target_pos
                    )
                    if begin_route is None:
                        logging.debug("Can not calculate a route to the target path but target pos in target route is in my history?")
                        return None
                    begin_route.optimize()
                    new_route = begin_route
                tail_path.reverse()
                new_route.add_route(tail_path)
                break
        
        if new_route.length == 0:
            # below is a problem if the square size > 0
            logging.debug("Not possible to calculate a route to the target route ")
            return None

        return new_route

    def get_route(self,start:Position,target:Position):
        return self.mover.history.get_sub_route(start,target)

class ToDoManager:

    def __init__(self,mover:AutomaticMove):
        self.mover = mover
        self.reset()

    def reset(self):
        self._to_do:list[Position] = []
        self._to_do_set:set[Position] = set()

    def append(self,position:Position):
        if position in self._to_do_set:
            return
        self._to_do.append(position)
        self._to_do_set.add(position)

    def insert(self,index:SupportsIndex,position:Position):
        if position in self._to_do_set:
            return
        self._to_do.insert(index,position)
    
    def has_to_do(self):
        return len(self._to_do) > 0

    def nr_to_do(self):
        return len(self._to_do)

    def has_position(self,position:Position):
        return position in self._to_do_set

    def peek_next(self):
        if self.nr_to_do() == 0:
            return None
        return self._to_do[-1]

    def get_next(self):
        if self.nr_to_do() == 0:
            return None
        next = self._to_do.pop()
        self._to_do_set.discard(next)
        return next

class Discoverer:
    def __init__(self,mover:AutomaticMove):
        self.mover = mover

    def get_move(self) -> (Position | None):
        return None
    
class RandomNewDiscoverer(Discoverer):
    def get_move(self):
        return self.mover.moveInfo.get_random_new_available()

class RandomDiscoverer(Discoverer):
    def get_move(self):
        return self.mover.moveInfo.get_random_available()

class StandStillHandler:
    def __init__(self,mover:RuleMove):
        self.mover = mover
        self.max_stand_still = 10

    def is_stand_still(self):
        if self.mover.nr_stand_still > self.max_stand_still:
            logging.debug(f"Standstill detected on pos {self.mover.moveInfo.start_pos}")
            return True
        return False

    def _handle_stand_still(self):
        pass 

    def get_move(self):
        if self.is_stand_still():
            return self._handle_stand_still()
        else:
            return None

class StandStillBackOut(StandStillHandler):      
    def _handle_stand_still(self):
        if not self.mover.router.has_route():
            logging.debug(f"Moving back pos {self.mover.moveInfo.start_pos}")
            if self.mover.request_new_route():
                return self.mover.router.get_new_pos()
        return None

class BlockRuleMove(RuleMove):

    def __init__(self,game_grid:GameGrid):
        super().__init__(game_grid)
        self.router = Router(self)
        self.navigator = HistoryNavigator(self)
        self.todo = ToDoManager(self)
        self.discoverer = RandomNewDiscoverer(self)
        self.standstill = None
        self.follow_coordinator = False
        self.coordinator:RuleMove
        if hasattr(self.game_grid,'coordinator'):
            self.coordinator = self.game_grid.coordinator
        else:
            self.coordinator = self
            self.game_grid.coordinator = self.coordinator

class BackOutRuleMove(RuleMove):

    def __init__(self,game_grid:GameGrid):
        super().__init__(game_grid)
        self.router = Router(self)
        self.navigator = HistoryNavigator(self)
        self.todo = ToDoManager(self)
        self.discoverer = RandomNewDiscoverer(self)
        self.standstill = StandStillBackOut(self)
    

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