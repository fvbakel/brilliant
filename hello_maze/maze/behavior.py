
from dataclasses import dataclass,field
from typing import SupportsIndex
from basegrid import *
from gamegrid import *
from graph import *
import logging
import random

from gamegrid.gamegrid import BehaviorFactory

@dataclass
class MoveInfo:
    start_pos:Position
    all_hosts:dict[Direction,GameContent]
    visited:set[Position]
    available_positions:set[Position] = field(init=False, repr=False)
    new_available_positions:set[Position] = field(init=False, repr=False)
    all_positions:set[Position] = field(init=False, repr=False)
    new_positions:set[Position] = field(init=False, repr=False)

    def __post_init__(self):
        self.available_positions = set([content.position for content in self.all_hosts.values() if content.can_host_guest() ])
        self.new_available_positions = self.available_positions - self.visited
        self.all_positions = set([content.position for content in self.all_hosts.values()])
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
    
    def get_first_available_direction(self,search_order:tuple(Direction)):
        for direction in search_order:
            if direction in self.all_hosts:
                host = self.all_hosts[direction]
                if host.can_host_guest():
                    if host.position in self.new_available_positions:
                        return host.position
        return None

    def get_available_directions(self):
        new_directions:dict[Direction,Position] = dict()
        for direction,host in self.all_hosts.items():
            if host.can_host_guest():
                new_directions[direction] = host.position
        return new_directions

    def get_new_available_directions(self):
        new_directions:dict[Direction,Position] = dict()
        for direction,host in self.all_hosts.items():
            if host.can_host_guest():
                if host.position in self.new_available_positions:
                    new_directions[direction] = host.position
        return new_directions

class Coordinator:
    pass

class AutomaticMove(Behavior):

    def __init__(self,game_grid:GameGrid):
        self.priority = 10
        super().__init__(game_grid)
        self.history = Route()
        self.nr_stand_still = 0
        self.moveInfo:MoveInfo = None
        self.router:Router
        self.navigator:Navigator
        self.todo:ToDoManager
        self.discoverer:Discoverer
        self.standstill:StandStillHandler
        self.coordinator:Coordinator

    @Behavior.subject.setter
    def subject(self,subject:GameContent):
        Behavior.subject.fset(self,subject)
        self.record_new_position()

    def record_new_position(self):
        self.history.append(self._subject.position)

    def notify_cur_pos(self):
        if self.coordinator is not None:
            self.coordinator.notify_cur_pos(self.moveInfo)
        if self.navigator is not None:
            self.navigator.notify_cur_pos(self.moveInfo)
        if self.todo is not None:
            self.todo.notify_cur_pos(self.moveInfo)

    def notify_new_pos(self,new_pos:Position):
        if self.coordinator is not None:
            self.coordinator.notify_new_pos(self.moveInfo,new_pos)
        if self.navigator is not None:
            self.navigator.notify_new_pos(self.moveInfo,new_pos)
        if self.todo is not None:
            self.todo.notify_new_pos(self.moveInfo,new_pos)

    def do_one_cycle(self):
        if self._subject is not None:
            self.moveInfo = MoveInfo(   
                self._subject.position,
                self.game_grid.get_available_hosts(self._subject.position),
                self.history.positions
            )
            self.notify_cur_pos()
            new_pos = self.determine_new_pos()
            if new_pos is None:
                self.nr_stand_still +=1
            else:
                self.nr_stand_still = 0
                self.game_grid.move_content(self._subject,new_pos)
                self.notify_new_pos(new_pos)
                self.record_new_position()
    
    def register_coordinator(self,coordinator_type:type[Coordinator]):
        if hasattr(self.game_grid,'coordinator'):
            self.coordinator = self.game_grid.coordinator
        else:
            self.coordinator = coordinator_type()
            self.game_grid.coordinator = self.coordinator

    def unregister(self):
        super().unregister()
        if self.coordinator is None:
            return
        self.coordinator.register_finish(self)

    def determine_new_pos(self):

        if not self.moveInfo.has_available():
            return None
        
        if self.standstill is not None:
            new_pos = self.standstill.get_move()
            if not new_pos is None:
                return new_pos

        if  self.router is not None and \
                self.router.has_route() and \
                self.router.locked:
            return self.router.get_new_pos()

        if  self.router is not None and \
                self.coordinator is not None and \
                not self.router.locked:
            win_route = self.coordinator.get_finish_route(self)
            if win_route is not None:
                self.router.set_route(win_route)
                self.router.locked = True

        if self.router is not None and self.router.has_route():
            return self.router.get_new_pos()

        if self.coordinator is not None and self.router is not None:
            discover_route = self.coordinator.get_discover_route(self)
            if discover_route is not None:
                self.router.set_route(discover_route)
                return self.router.get_new_pos()

        if not self.moveInfo.has_new_positions():
            if not self.request_new_route():
                return None
            return self.router.get_new_pos()
        else:
            return self.select_discover_move()

    def request_new_route(self):
        if self.router is None or self.router.locked:
            return False
        
        if self.coordinator is not None:
            discover_route = self.coordinator.get_discover_route(self)
            if discover_route is not None:
                self.router.set_route(discover_route)
                return True

        if self.todo is None or self.navigator is None:
            return False
        
        if not self.todo.has_to_do():
            return False
        target = self.todo.get_next()
        new_route = self.navigator.get_route(self.moveInfo.start_pos,target)
        if new_route is None:
            logging.error("Can not find path back ")
            return False
        self.router.set_route(new_route)
        return True

    def select_discover_move(self):
        selected:Position = None
        if self.coordinator is not None:
            selected = self.coordinator.get_discover_pos(self)
        if selected is None and \
                not self.discoverer is None:
            selected = self.discoverer.get_move()
        # TODO Move to begin og the move
        #if selected is not None and \
        #        self.todo is not None:
        #    self.todo.notify(self.moveInfo)
        return selected

class Router:
    selectable = True
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

    def notify_cur_pos(self,moveInfo:MoveInfo):
        pass

    def notify_new_pos(self,moveInfo:MoveInfo,new_pos:Position):
        pass

    def get_route_to_route(self,start:Position,target_route:Route) -> (Route | None):
        return None

    def get_route(self,start:Position,target:Position) -> (Route | None):
        return None

class GraphNavigator(Navigator):
    selectable = True
    def __init__(self):
        self.graph = Graph()
        self.new_condition = NewNode()

    def notify_cur_pos(self,moveInfo:MoveInfo):
        cur_node = self.graph.get_or_create(moveInfo.start_pos.get_id())
        cur_node.position = moveInfo.start_pos
        cur_node.discoverd = True
        cur_node.visit_pending = False
        for child_pos in moveInfo.all_positions:
            child_node = self.graph.get_or_create(child_pos.get_id())
            if not hasattr(child_node,'position'):
                child_node.position = child_pos
                child_node.discoverd = False
                child_node.visit_pending = False
            self.graph.create_edge_pair(cur_node,child_node)
        return None
    
    def notify_new_pos(self,moveInfo:MoveInfo,new_pos:Position):
        new_node = self.graph.get_or_create(new_pos.get_id())
        new_node.visit_pending = True
    
    def get_route(self,start:Position,target:Position) -> (Route | None):
        if start is None or target is None:
            return None

        start_node = self.graph.get_node(start.get_id())
        target_node = self.graph.get_node(target.get_id())

        if start_node is None or target_node is None:
            return None
        
        path = self.graph.find_short_path_dijkstra(start_node,target_node)
        return self.path_to_route(path)

    def path_to_route(self,path):
        if len(path) == 0:
            return None
        
        route = Route()
        for node in path:
            route.append(node.position)
        return route

    def get_discover_route(self,moveInfo:MoveInfo):
        start_node = self.graph.get_node(moveInfo.start_pos.get_id())
        if start_node is None:
            return None

        for edge in start_node.child_edges:
            if self.new_condition.check(edge.child):
                return Route([edge.child.position])

        path = self.graph.find_short_path_condition(start_node,self.new_condition)
        return self.path_to_route(path)

class RouteBasedNavigator(Navigator):
    selectable = True
    def __init__(self,base_route:Route):
        self.base_route = base_route

    def get_route_to_route(self,start:Position,target_route:Route) :
        new_route = self.base_route.get_route_to_route(start,target_route)
        if new_route is not None:
            new_route.optimize()
        return new_route

    def get_route(self,start:Position,target:Position):
        new_route = self.base_route.get_sub_route(start,target)
        if new_route is not None:
            new_route.optimize()
        return new_route

class RouteShortCutNavigator(RouteBasedNavigator):
    selectable = True

    def get_route_to_route(self,start:Position,target_route:Route) :
        new_route = self.base_route.get_route_to_route(start,target_route)
        if new_route is not None:
            new_route.optimize()
            new_route.apply_short_cuts()
        return new_route

    def get_route(self,start:Position,target:Position):
        new_route = self.base_route.get_sub_route(start,target)
        if new_route is not None:
            new_route.optimize()
            new_route.apply_short_cuts()
        return new_route

class ToDoManager:
    selectable = False

    def notify_cur_pos(self,moveInfo:MoveInfo):
        pass

    def notify_new_pos(self,moveInfo:MoveInfo):
        pass

    def has_to_do(self) -> bool:
        pass

    def get_next(self) -> (None | Position):
        pass

class PositionList(ToDoManager):
    selectable = True
    def __init__(self):
        self.reset()

    def reset(self):
        self._to_do:list[Position] = []
        self._to_do_set:set[Position] = set()

    def notify_cur_pos(self,moveInfo:MoveInfo):
        if moveInfo.start_pos in self._to_do_set:
            self._to_do.remove(moveInfo.start_pos)
            self._to_do_set.discard(moveInfo.start_pos)

    def notify_new_pos(self,moveInfo:MoveInfo,new_pos:Position):
        if moveInfo.nr_new_positions() > 0:
            remain = set(moveInfo.new_positions)
            remain.discard(new_pos)
            if len(remain) >  0:
                self.append(moveInfo.start_pos)

    def append(self,position:Position):
        if position in self._to_do_set:
            return
        self._to_do.append(position)
        self._to_do_set.add(position)

    def insert(self,index:SupportsIndex,position:Position):
        if position in self._to_do_set:
            return
        self._to_do.insert(index,position)
        self._to_do_set.add(position)

    def discard(self,position:Position):
        if position in self._to_do_set:
            self._to_do.remove(position)
            self._to_do_set.discard(position)

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

class SmartPositionList(PositionList):
    selectable = True

    def __init__(self):
        super().__init__()
        self._todo_vs_remain:dict[Position,set[Position]] = dict()
        self._remain_vs_todo:dict[Position,set[Position]] = dict()

    def notify_cur_pos(self,moveInfo:MoveInfo):
        if moveInfo.start_pos in self._to_do_set:
            self._to_do.remove(moveInfo.start_pos)
            self._to_do_set.discard(moveInfo.start_pos)

        if moveInfo.start_pos in self._remain_vs_todo:
            todo_s = self._remain_vs_todo.pop(moveInfo.start_pos)
            for todo in todo_s:
                self._todo_vs_remain[todo].discard(moveInfo.start_pos)
                if len(self._todo_vs_remain[todo]) == 0:
                    if todo in self._to_do_set:
                        self._to_do.remove(todo)
                        self._to_do_set.discard(todo)

    def notify_new_pos(self,moveInfo:MoveInfo,new_pos:Position):
        if moveInfo.nr_new_positions() > 0:
            remain = set(moveInfo.new_positions)
            remain.discard(new_pos)
            if len(remain) >  0: 
                self.append(moveInfo.start_pos)
                self._add_remain(moveInfo.start_pos,remain)

    def _add_remain(self,start_pos:Position,remain:set[Position]):
        self._todo_vs_remain[start_pos] = remain
        for pos in remain:
            if pos not in self._remain_vs_todo:
                self._remain_vs_todo[pos] = set()
            self._remain_vs_todo[pos].add(start_pos)
        
class RandomSmartPosition(SmartPositionList):

    def get_next(self):
        if self.nr_to_do() == 0:
            return None
        next = random.choice(self._to_do)
        self._to_do_set.discard(next)
        return next

class Discoverer:
    def __init__(self,mover:AutomaticMove):
        self.mover = mover

    def get_move(self) -> (Position | None):
        return None
    
class RandomNewDiscoverer(Discoverer):
    selectable = True
    def get_move(self):
        return self.mover.moveInfo.get_random_new_available()

class RandomDiscoverer(Discoverer):
    selectable = True
    def get_move(self):
        return self.mover.moveInfo.get_random_available()

class KeepRandomDirection(Discoverer):
    selectable = True

    def __init__(self,mover:AutomaticMove):
        super().__init__(mover)
        self.previous:Direction = None

    def get_move(self):
        new_directions = self.mover.moveInfo.get_new_available_directions()
        if self.previous  in new_directions:
            return new_directions[self.previous]
        if len(new_directions) == 0:
            return None
        elif len(new_directions) == 1:
            select =  tuple(new_directions.keys())[0]
        else:
            select = random.choice(tuple(new_directions.keys()))
        self.previous = select
        return new_directions[select]

class DirectionDiscoverer(Discoverer):
    selectable = True
    configurable = True
    def __init__(self,mover:AutomaticMove):
        super().__init__(mover)
        self.directions:tuple(Direction)

    def get_move(self):
        return self.mover.moveInfo.get_first_available_direction(self.directions)

class DirectionDiscoverer_DRLU(DirectionDiscoverer):
    selectable = True
    def __init__(self,mover:AutomaticMove):
        super().__init__(mover)
        self.directions = (Direction.DOWN,Direction.RIGHT,Direction.LEFT,Direction.UP)

class DirectionDiscoverer_RDUL(DirectionDiscoverer):
    selectable = True
    def __init__(self,mover:AutomaticMove):
        super().__init__(mover)
        self.directions = (Direction.RIGHT,Direction.DOWN,Direction.UP,Direction.LEFT)


class StandStillHandler:
    selectable = True
    def __init__(self,mover:AutomaticMove):
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

class StandStillNewRoute(StandStillHandler):
    selectable = True
    def _handle_stand_still(self):
        if  self.mover.router is None:
            return None
        if not self.mover.router.has_route():
            logging.debug(f"Moving back from pos {self.mover.moveInfo.start_pos}")
            if self.mover.request_new_route():
                return self.mover.router.get_new_pos()
        return None

class ForceNewFinishRoute(StandStillNewRoute):
    selectable = True
    def _handle_stand_still(self):
        if  self.mover.router is None:
            return None
        if self.mover.router.locked:
            self.mover.router.locked = False
            self.mover.router.reset_route()
            self.mover.nr_stand_still = 0
            return self.mover.moveInfo.start_pos
        return super()._handle_stand_still()

class ForceNewRoute(StandStillNewRoute):
    selectable = True
    def _handle_stand_still(self):
        if  self.mover.router is None:
            return None

        self.mover.router.locked = False
        self.mover.router.reset_route()
        self.mover.nr_stand_still = 0
        
        return super()._handle_stand_still()

class Coordinator:

    def get_finish_route(self,mover:AutomaticMove) -> (None | Route) :
        return None

    def register_finish(self,mover:AutomaticMove):
        pass

    def notify_cur_pos(self,moveInfo:MoveInfo):
        pass

    def notify_new_pos(self,moveInfo:MoveInfo,new_pos:Position):
        pass

    def get_discover_route(self,mover:AutomaticMove) -> (None | Route) :
        return None

    def get_discover_pos(self,mover:AutomaticMove) -> (None | Position) :
        return None

class SpoilCoordinator(Coordinator):
    selectable = True
    def __init__(self):
        self.win_routes:list[Route] = []
        self.win_positions:set[Position] = set()

    def optimize_route(self,route:Route):
        if route is not None:
            route.optimize()

    def get_finish_route(self,mover:AutomaticMove) -> (None | Route) :
        route = self._get_finish_route(mover)
        self.optimize_route(route)
        return route

    def _get_finish_route(self,mover:AutomaticMove) -> (None | Route) :
        if mover.moveInfo.start_pos in self.win_positions:
            return self._get_direct_finish_route(mover.moveInfo.start_pos)
        for pos in mover.moveInfo.all_positions:
            if pos in self.win_positions:
                win_route =  self._get_direct_finish_route(pos)
                if win_route is None:
                    return None
                win_route.insert(0,pos)
                return win_route

        if not mover.history.positions.isdisjoint(self.win_positions):
            return self._get_finish_route_to_route(mover)
        return None

    def _get_direct_finish_route(self,start_pos:Position) -> (None | Route):
        for route in self.win_routes:
            if start_pos in route.positions:
                return route.get_sub_route(start_pos,route.end)
        return None

    def _get_finish_route_to_route(self,mover:AutomaticMove) -> (None | Route):
        for route in self.win_routes:
            if not mover.history.positions.isdisjoint(route.positions):
                return mover.history.get_route_to_route(mover.moveInfo.start_pos,route)
        return None

    def register_finish(self,mover:AutomaticMove):
        if not self._is_new_win_route(mover.history):
            return

        self._add_win_route(mover.history)
        optimized_win = mover.history.copy()
        #optimized_win.optimize()
        self.optimize_route(optimized_win)
        if not self._is_new_win_route(optimized_win):
            return
        self._add_win_route(optimized_win)

    def _add_win_route(self,win_route:Route):
        self.win_positions.update(win_route.positions)
        insert_before = 0
        for index,route in enumerate(self.win_routes):
            if win_route.length < route.length:
                insert_before = index
                break
        self.win_routes.insert(insert_before,win_route)

    def _is_new_win_route(self,new_route:Route):
        new_pos = new_route.positions - self.win_positions
        if len(new_pos) > 0:
            return True
        for win_route in self.win_routes:
            if win_route != new_route:
                return True
        return False

class SpoilShortCutCoordinator(SpoilCoordinator):
    selectable = True

    def optimize_route(self,route:Route):
        if route is not None:
            route.optimize()
            route.apply_short_cuts()

class CentralToDO(Coordinator):
    selectable = True

    def __init__(self):
        super().__init__()
        self.todo = PositionList()
        self.done:set[Position] = set()
        self.neighbor:dict[Position,Position] = dict()

    def notify_cur_pos(self,moveInfo:MoveInfo):
        self.todo.discard(moveInfo.start_pos)
        self.done.add(moveInfo.start_pos)

        for pos in moveInfo.all_positions:
            if pos not in self.done and\
                    not self.todo.has_position(pos):
                self.todo.insert(0,pos)
                self.neighbor[pos] = moveInfo.start_pos

    def notify_new_pos(self,moveInfo:MoveInfo,new_pos:Position):
        self.todo.discard(new_pos)

    def get_discover_route(self,mover:AutomaticMove) -> (None | Route) :
        target = self.todo.peek_next()
        if target in self.neighbor:
            target = self.neighbor[target]
        if target is not None:
            route = mover.navigator.get_route(mover.moveInfo.start_pos,target)
            if route is not None:
                self.todo.get_next()
                return route

class NewNode(SearchCondition):

    def check(self,current:Node) -> bool:
        return current is not None and \
                    current.discoverd == False and \
                    current.visit_pending == False

    def __repr__(self):
        return f'not discovered and no visit pending'

class GraphCoordinator(Coordinator):
    selectable = True

    def __init__(self):
        super().__init__()
        self.navigator = GraphNavigator()

    def notify_cur_pos(self,moveInfo:MoveInfo):
        self.navigator.notify_cur_pos(moveInfo)

    def notify_new_pos(self, moveInfo: MoveInfo, new_pos: Position):
        self.navigator.notify_new_pos(moveInfo, new_pos)
    
    def get_discover_route(self,mover:AutomaticMove) -> (None | Route) :
        return self.navigator.get_discover_route(mover.moveInfo)

class RandomAutomaticMove(AutomaticMove):
    selectable = True

    def __init__(self,game_grid:GameGrid):
        super().__init__(game_grid)
        self.router = None
        self.navigator = None
        self.todo = None
        self.discoverer = RandomNewDiscoverer(self)
        self.standstill = None
        self.coordinator = None
        #self.register_coordinator(SpoilCoordinator)

class TryOutAutomaticMove(AutomaticMove):
    selectable = True
    def __init__(self,game_grid:GameGrid):
        super().__init__(game_grid)
        self.router = None
        self.navigator = None
        self.todo = None
        self.discoverer = None
        self.standstill = None
        self.coordinator = None
        #self.register_coordinator(SpoilCoordinator)

class BlockAutomaticMove(AutomaticMove):
    selectable = True
    def __init__(self,game_grid:GameGrid):
        super().__init__(game_grid)
        self.router = Router(self)
        self.navigator = RouteBasedNavigator(self.history)
        self.todo = PositionList()
        self.discoverer = DirectionDiscoverer_DRLU(self)
        self.standstill = None
        self.coordinator = None
        #self.register_coordinator(SpoilCoordinator)

class SpoilAutomaticMove(AutomaticMove):
    selectable = True
    def __init__(self,game_grid:GameGrid):
        super().__init__(game_grid)
        self.router = Router(self)
        self.navigator = RouteBasedNavigator(self.history)
        self.todo = PositionList()
        self.discoverer = DirectionDiscoverer_DRLU(self)
        self.standstill = ForceNewFinishRoute(self)
        self.register_coordinator(SpoilCoordinator)

class BackOutAutomaticMove(AutomaticMove):
    selectable = True
    def __init__(self,game_grid:GameGrid):
        super().__init__(game_grid)
        self.router = Router(self)
        self.navigator = RouteBasedNavigator(self.history)
        self.todo = PositionList()
        self.discoverer = DirectionDiscoverer_DRLU(self)
        self.standstill = StandStillNewRoute(self)
        self.coordinator = None

class ConfigurableMove(AutomaticMove):
    selectable = True
    configurable = True
    def __init__(self,game_grid:GameGrid):
        super().__init__(game_grid)
        self.router = None
        self.navigator = None
        self.todo = None
        self.discoverer = None
        self.standstill = None
        self.coordinator = None
        self.coordinator_type:type[Coordinator] = None

    def reconfigure(self):
        if self.coordinator_type is not None:
            self.register_coordinator(self.coordinator_type)

class ConfigurableFactory(BehaviorFactory):

    def __init__(self):
        self.behavior_type:type[AutomaticMove] = ConfigurableMove
        self.router_type:type[Router] = None
        self.navigator_type:type[Navigator] = None
        self.is_default = False
        self.coordinator_type:type[Coordinator] = None
        self.todo_type:type[ToDoManager] = None
        self.discover_type:type[Discoverer] = None
        self.standstill_type:type[StandStillHandler] = None
        
    def get_new(self, game_grid: GameGrid) -> Behavior:
        mover = ConfigurableMove(game_grid)

        if self._check_type(self.router_type,Router):
            mover.router = self.router_type(mover)
        
        if self._check_type(self.navigator_type,RouteBasedNavigator,False):
            mover.navigator = self.navigator_type(base_route=mover.history)
        elif self._check_type(self.navigator_type,Navigator):
            mover.navigator = self.navigator_type()

        if self._check_type(self.todo_type,ToDoManager):
            mover.todo = self.todo_type()

        if self._check_type(self.discover_type,Discoverer):
            mover.discoverer = self.discover_type(mover)

        if self._check_type(self.standstill_type,StandStillHandler):
            mover.standstill = self.standstill_type(mover)

        if self._check_type(self.coordinator_type,Coordinator):
            mover.coordinator_type = self.coordinator_type
        mover.reconfigure()
        return mover
    
    #TODO Move this to a generic module
    def _check_type(self,sub_class:type,main_class:type,log_error=True):
        if sub_class is None:
            return False
        if not issubclass(sub_class,main_class):
            if log_error:
                logging.error(f"Type {str(sub_class)} is not a {str(main_class)}")
            return False
        return True
        


class FinishDetector(Behavior):

    def __init__(self,game_grid:GameGrid):
        self.priority = 1
        super().__init__(game_grid)
        self.finished:list[GameContent] = []
        self.nr_of_steps:list[int] = []

    def do_one_cycle(self):
        if self._subject is not None and self._subject.guest is not None:
            self.finished.append(self._subject.guest)
            
            if self._subject.guest.behavior is not None:
                self._subject.guest.behavior.unregister()
                if isinstance(self._subject.guest.behavior,AutomaticMove):
                    behavior:AutomaticMove = self._subject.guest.behavior
                    self.nr_of_steps.append(behavior.history.length -1)
            if self._subject.guest.trace_material != Material.NONE:
                self._subject.material = self._subject.guest.trace_material
            self._subject.guest = None

class AutomaticAdd(Behavior):

    def __init__(self,game_grid:GameGrid):
        self.priority = 90
        super().__init__(game_grid)
        
        self.nr_started = 0
        self.active = False
        self._move_type:type[AutomaticMove]
        self.factory:BehaviorFactory = BehaviorFactory()

    @property
    def move_type(self):
        return self._move_type

    @move_type.setter
    def move_type(self,move_type:type[AutomaticMove]):
        self._move_type = move_type
        if self.factory.behavior_type == self._move_type:
            return
        if not self.factory.is_default:
            self.factory = BehaviorFactory()
        self.factory.behavior_type = self._move_type

    def do_one_cycle(self):
        if self.active:
            particle = Particle()
            particle.trace_material = Material.FLOOR_HIGHLIGHTED
            behavior = self.game_grid.add_manual_content(particle,self.factory)
            if behavior is not None:
                self.nr_started += 1