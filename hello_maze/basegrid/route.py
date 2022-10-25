from typing import SupportsIndex
from basegrid import Position
import logging

class Route:
    pass

class Route:

    def __init__(self,path:list[Position] = None):
        if path is None:
            self.reset_path()
        else:
            self._path = path
        self.reset_pos_map()

    def __eq__(self, other):
        if not isinstance(other,Route):
            return False
        return self._path == other._path

    def copy(self):
        return Route(self._path.copy())

    def reset(self):
        self.reset_path()
        self.reset_pos_map()

    def reset_path(self):
        self._path:list[Position] = []
    
    def reset_pos_map(self):
        self._pos_map:dict[Position,list[int]] = dict()

    def __repr__(self) -> str:
        return '->'.join(str(pos) for pos in self._path)

    @property
    def start(self):
        if len(self._path) == 0:
           return None 
        return self._path[0]
    
    @property
    def end(self):
        if len(self._path) == 0:
           return None 
        return self._path[-1]

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self,path:list[Position]):
        self._path = path

    def append(self,position:Position):
        self._path.append(position)

    def insert(self,index:SupportsIndex,position:Position):
        self._path.insert(index,position)

    def pop(self,index:SupportsIndex = None):
        if index is None:
            return self._path.pop()
        else:
            return self._path.pop(index)

    @property
    def length(self):
        return len(self._path)

    @property
    def positions(self):
        return set(self._path)

    def has_position(self,position:Position):
        return position in set(self._path)

    def reverse(self):
        self._path.reverse()

    def is_valid(self):
        if len(self._path) <= 0:
            return True
        
        previous = self._path[0]
        for pos in self._path[1:]:
            if not previous.is_neighbor(pos):
                return False
            previous = pos
        return True

    def update_pos_map(self):
        self.reset_pos_map()
        for index,pos in enumerate(self._path):
            if pos in self._pos_map:
                self._pos_map[pos].append(index)
            else:
                self._pos_map[pos] = [index]

    def optimize(self):
        self.update_pos_map()
        if len(self._pos_map) > 0 :
            cut_start = None
            cut_end = None
            cut_diff = 0
            for index_list in self._pos_map.values():
                diff = index_list[-1] - index_list[0]
                if diff > cut_diff:
                    cut_diff = diff
                    cut_start = index_list[0]
                    cut_end =  index_list[-1]

            if not cut_start is None and not cut_end is None:
                self._path =  self._path[:cut_start] + self._path[cut_end:]
                self.optimize()

    def get_sub_route(self,start:Position,end:Position):
        if start == end:
            return None

        self.update_pos_map()
        if  not start in self._pos_map or \
            not end in self._pos_map:
                return None

        start_index_list = self._pos_map[start]
        end_index_list = self._pos_map[end]
        
        start_index = start_index_list[0]
        end_index = end_index_list[-1]
        sub_path:list[Position]
        if start_index < end_index:
            sub_path = self._path[start_index:end_index+1]
        else:
            sub_path = self._path[end_index:start_index+1]
            sub_path.reverse()
        route = Route(sub_path)
        route.optimize()
        return route

    def add_route(self,route:Route):
        if self.length == 0:
            self._path = route._path
            return True
        if route.length == 0:
            return True    
        if route.end == self.start:
            self._path = route._path[:-1] + self._path
            return True
        if route.start == self.end:
            self._path.extend(route._path[1:])
            return True
        if route.end.is_neighbor(self.start):
            self._path = route._path + self._path
            return True
        if route.start.is_neighbor(self.end):
            self._path.extend(route._path)
            return True
        return False

    def get_route_to_route(self,start:Position,target_route:Route) :
        tail_path = Route()
        new_route = Route()
        for target_pos in reversed(target_route.path):
            tail_path.append(target_pos)
            if self.has_position(target_pos):
                if start != target_pos:
                    begin_route = self.get_sub_route(
                        start,
                        target_pos
                    )
                    if begin_route is None:
                        logging.debug("Can not calculate a route to the target path but target pos in target route is in my route?")
                        return None
                    begin_route.optimize()
                    new_route = begin_route
                tail_path.reverse()
                new_route.add_route(tail_path)
                break
        
        if new_route.length == 0:
            logging.debug("Not possible to calculate a route to the target route ")
            return None

        return new_route
