from basegrid import Position

class Route:

    def __init__(self):
        self._init()

    def _init(self):
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

    def pop(self):
        return self._path.pop()

    @property
    def length(self):
        return len(self._path)

    def has_position(self,position:Position):
        return position in set(self._path)

    def reverse(self):
        self._path.reverse()

    
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

    # TODO: think how this can be improved .....
    def get_sub_route(self,start:Position,target:Position):
        """
            the path could be like this
            [1,target,2,3,target,a,b,c,start_position,x,y,z,start_position]
            expected result from this method in that case
            [target,a,b,c]
            So mechanism is:
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