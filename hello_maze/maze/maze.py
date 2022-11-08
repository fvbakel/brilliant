from basegrid import *
from gamegrid import *
from .behavior import *

import graph as gr
from dataclasses import dataclass
from os import PathLike
import logging
import random
import graphviz

class Square:

    def __init__(self,position:Position,node:gr.Node):
        self.position = position
        self.node = node
        self.edge_pairs:dict[Direction,gr.EdgePair] = dict()
        self.is_short_part = False
        self.is_first=False
        self.is_last=False

@dataclass
class SquareRelation:
    parent:Square
    child:Square    = None
    active:bool     = True

class SquareGeometry:

    def __init__(self,game_pos:Position,square_width:int,wall_width:int):

        self.square_width = square_width
        self.wall_width = wall_width
        x = self._wall_start_end_positions(game_pos.col)
        y = self._wall_start_end_positions(game_pos.row)

        self.walls:dict[Direction,Rectangle] = dict()
        
        self.walls[Direction.LEFT] = Rectangle( Position(x[0],y[0]),Position(x[1],y[3]))
        self.walls[Direction.UP] = Rectangle( Position(x[0],y[0]),Position(x[3],y[1]))
        self.walls[Direction.RIGHT] = Rectangle( Position(x[2],y[0]),Position(x[3],y[3]))
        self.walls[Direction.DOWN] = Rectangle( Position(x[0],y[2]),Position(x[3],y[3]))

        self.outer_rectangle = Rectangle( Position(x[0],y[0]),Position(x[3],y[3]))
        self.inner_rectangle = Rectangle( Position(x[1]+1,y[1]+1),Position(x[2]-1,y[2]-1))

    def _wall_start_end_positions(self,square_index:int):
        x:list[int] = []
        start = (square_index * self.square_width) + (square_index * self.wall_width)
        x.append(start)
        x.append(x[0] + self.wall_width -1)
        x.append(x[1] + self.square_width + 1)
        x.append(x[2] + self.wall_width -1)
        return x

class SquareGrid(Grid):
    
    def get_location(self,position:(Position | tuple[int,int])) -> Square:
        return super().get_location(position)

    def set_location(self,position:(Position | tuple[int,int]),content:Square):
        super().set_location(position,content)

    def get_square_neighbor(self,current_square:Square,direction:Direction) ->SquareRelation:
        
        if direction in current_square.edge_pairs:
            pair = current_square.edge_pairs[direction]
            child_pos = current_square.position.get_position_in_direction(direction)
            relation = SquareRelation(current_square)
            relation.active = pair.is_active()
            relation.child = self.get_location(child_pos)
            #return  (self.get_location(child_pos),pair.is_active())
            return relation
        return None

    def has_wall(self,square:Square,direction:Direction):
        if square.is_first and direction == Direction.UP:
            return False
        if square.is_last and direction == Direction.DOWN:
            return False
        square_rel = self.get_square_neighbor(square,direction)
        if square_rel == None:
            return True
        return not square_rel.active

class SquareGeometryGrid(Grid):

    def get_location(self,position:(Position | tuple[int,int])) -> SquareGeometry:
        return super().get_location(position)

    def set_location(self,position:(Position | tuple[int,int]),content:SquareGeometry):
        super().set_location(position,content)

class Maze:

    def __init__(self,square_size:Size):
        self.square_size = square_size
        self.graph = gr.Graph()
        self.square_grid = SquareGrid(square_size)
        self._init_nodes()
        self._init_first_last()
        self._init_edges()

    def _init_nodes(self):
        for row in range(0,self.square_size.nr_of_rows):
            for col in range(0,self.square_size.nr_of_cols):
                position = Position(col,row)
                node = self.graph.get_or_create(position.get_id())
                square = Square(position,node)
                self.square_grid.set_location(position,square)
    
    def _init_first_last(self):
        self.first_square = self.square_grid.get_location((0,0))
        self.last_square = self.square_grid.get_location((self.square_size.nr_of_cols-1,self.square_size.nr_of_rows-1)) 

        self.first_square.is_first=True
        self.last_square.is_last=True

        self.graph.first = self.first_square.node
        self.graph.last = self.last_square.node

    def _init_edges(self):
        #for row in range(0,self.square_size.nr_of_rows):
         #   for col in range(0,self.square_size.nr_of_cols):
         for row in self.square_grid.locations:
            current_square:Square
            for current_square in row:
                if current_square.position.col < self.square_size.nr_of_cols -1:
                    self._add_edge_pair(current_square,Direction.RIGHT)

                if current_square.position.row < self.square_size.nr_of_rows -1:
                    self._add_edge_pair(current_square,Direction.DOWN)

    
    def _add_edge_pair(self,current_square:Square,direction:Direction):
        child_pos = current_square.position.get_position_in_direction(direction)
        child_square = self.square_grid.get_location(child_pos)
        pair = self.graph.create_edge_pair(parent=current_square.node,child=child_square.node)
        current_square.edge_pairs[direction] = pair
        
        child_square.edge_pairs[Direction.reverse(direction)] = pair

    def solve_shortest_path(self):
        self.short_path_nodes = self.graph.find_short_path_dijkstra(self.graph.first,self.graph.last)
        short_path_set = set(self.short_path_nodes)
        for row in self.square_grid.locations:
            current_square:Square
            for current_square in row:
                if current_square.node in short_path_set:
                    current_square.is_short_part = True

class MazeGame:

    def __init__(self,maze:Maze,square_width:int,wall_width:int):
        self.maze=maze
        self.square_width = square_width
        self.wall_width = wall_width

        width = self._calculate_game_length(self.maze.square_size.nr_of_cols)
        height = self._calculate_game_length(self.maze.square_size.nr_of_rows)
        self.game_size = Size(width,height)

        self.geometry = SquareGeometryGrid(self.maze.square_size)
        self.game_grid = GameGrid(self.game_size)
        self.short_path_layer = Layer('Shortest path',10,(255,0,0))
        self.short_path_layer.active = False
        self.game_grid.layer_mgr.add_layer(self.short_path_layer)
        self.maze.solve_shortest_path()
        self._init_geometry()

    def _calculate_game_length(self,nr_of_squares:int):
        # wall | wall   | wall | wall   | wall
        # wall | square | wall | square | wall
        # wall | square | wall | square | wall
        # wall | wall   | wall | wall   | wall

        #     0123456789...
        #  00 ********************
        #  01 ********************
        #  02 **    **    **    **
        #  03 **    **    **    **
        #  04 **    **    **    **
        #  05 **    **    **    **
        #  06 ********************
        #  07 ********************
        nr_of_walls = nr_of_squares +1
        return nr_of_squares * self.square_width + nr_of_walls * self.wall_width

    def _init_geometry(self):
        for row in self.maze.square_grid.locations:
            square:Square
            for square in row:
                square_geom = SquareGeometry(square.position,self.square_width,self.wall_width)
                self.geometry.set_location(square.position,square_geom)
                self._init_square_on_game_grid(square,square_geom)

    def _init_square_on_game_grid(self,square:Square,square_geometry:SquareGeometry):
        for direction in Direction:
            if direction == Direction.HERE:
                continue
            if self.maze.square_grid.has_wall(square,direction):
                rect = square_geometry.walls[direction]
                for game_pos in rect.positions():
                    self.game_grid.set_location(game_pos,Wall())
        
        # remaining is floor
        for pos in square_geometry.outer_rectangle.positions():
            content = self.game_grid.get_location(pos)
            if content == None:
                content = Floor()
                if square.is_short_part:
                    self.short_path_layer.add_position(pos)
                    
                self.game_grid.set_location(pos,content)
            if isinstance(content,Floor):
                # if up or left square is short path but this is not 
                # then this position is not the shortest path
                if not square.is_short_part:
                    if pos in self.short_path_layer.positions:
                        self.short_path_layer.remove_position(pos)


class MazeGenerator:

    def __init__(self,size:Size):
        self.maze = Maze(square_size=size)
        self.regenerate()

    def regenerate(self):
        self.edge_pairs = self.maze.graph.edge_pairs.copy()
        self._enable_all_edges()
        self._generate()

    def _enable_all_edges(self):
        for pair in self.edge_pairs:
            pair.enable()

    def _generate(self):
        while len(self.edge_pairs) > 0:
            pair = random.choice(tuple(self.edge_pairs))
            self.edge_pairs.remove(pair)
            pair.disable()
            if not self.maze.graph.is_fully_connected():
                pair.enable()

class Squares2Dot:

    def __init__(self,square_grid:SquareGrid):
        self.square_grid = square_grid
        self.refresh()

    def refresh(self):
        self._sub_graphs: dict[str, graphviz.Graph] = dict()
        self.dot = graphviz.Graph()
        self.dot.attr(rankdir='LR')
        self._current_graph:graphviz.Graph = self.dot
        
        self._create_subgraphs()
        self._add_squares()
        self._post_process_sub_graphs()
    
    def _add_subgraph(self,name:str):
        self._sub_graphs[name] = graphviz.Graph(name=name)
        self._sub_graphs[name].attr(rankdir='LR')

    def _create_subgraphs(self):
        for row in range(0,self.square_grid.size.nr_of_rows):
            self._add_subgraph(f"row_{row}")
        for col in range(0,self.square_grid.size.nr_of_cols):
            self._add_subgraph(f"col_{col}")
            self._set_active_graph(f"col_{col}")
            self._current_graph.attr(rank="same")
    
    def _post_process_sub_graphs(self):
        for name,graph in self._sub_graphs.items():
            self.dot.subgraph(graph)

    def _set_active_graph(self,name:str=None):
        if name is None:
            self._current_graph = self.dot
        else:
            self._current_graph = self._sub_graphs[name]

    def _add_squares(self):
        for row in self.square_grid.locations:
            current_square:Square
            for current_square in row:
                col_index = current_square.position.col
                row_index = current_square.position.row
                self._set_active_graph(f"row_{row_index}")
                self._add_square_as_node(current_square)

                if col_index < self.square_grid.size.nr_of_cols -1:
                    self._add_square_edge(current_square,Direction.RIGHT)

                self._set_active_graph(f"col_{col_index}")
                if current_square.position.row < self.square_grid.size.nr_of_rows -1:
                    self._add_square_edge(current_square,Direction.DOWN)

    
    def _add_square_edge(self,current_square:Square,direction:Direction,active_only=True):
        square_relation = self.square_grid.get_square_neighbor(current_square,direction)
        if square_relation != None:
            self._add_edge(square_relation)

    def _add_square_as_node(self,square:Square):
        id = self.get_square_id(square)
        color='black'
        if square.is_short_part:
            color='red'
        self._current_graph.node(name=id,shape='rect',color=color)
    
    def get_square_id(self,square:Square):
        return square.position.get_id()

    #def _add_edge(self,square:Square,child_square:Square,active:bool):
    def _add_edge(self,square_relation:SquareRelation):
        style = 'invis'
        if square_relation.active:
            style='filled'

        color = 'black'
        if  square_relation.active and \
            square_relation.parent.is_short_part and \
            square_relation.child.is_short_part:
                color = 'red'
        
        self._current_graph.edge(   self.get_square_id(square_relation.parent),
                                    self.get_square_id(square_relation.child),
                                    style=style,color=color
                                )

    def render(self,filename:PathLike | str,directory:PathLike | str, format='svg'):
        self.dot.render(filename=filename,directory=directory, format=format)


class MazeController:

    def __init__(self):
        self.show_short_path = False
        self.show_trace = False
        
        self.square_width = 1
        self.wall_width = 1
        self.maze_img = None

        self.nr_of_cols:int = 10
        self.nr_of_rows:int = 10
        self.manual_move:ManualMove = None
        self.move_behavior:str = 'ConfigurableMove'
        self.configure_factory = ConfigurableFactory()
        self.default_factory = BehaviorFactory()
        self._nr_started:int = 0
        self.nr_of_cycles:int = 0
        self._init_configurable_subclasses()
        self.generate_new()

    def get_all_subclasses(cls):
        all_subclasses = []

        for subclass in cls.__subclasses__():
            all_subclasses.append(subclass)
            all_subclasses.extend(MazeController.get_all_subclasses(subclass))

        return all_subclasses

    def make_class_dict(self,main_cls:type):
        result:dict[str,type[main_cls]] = dict()
        if hasattr(main_cls,'selectable'):
            if main_cls.selectable:
                result[main_cls.__name__] = main_cls
        for cls in MazeController.get_all_subclasses(main_cls):
            if hasattr(cls,'selectable') :
                if cls.selectable:
                    result[cls.__name__] = cls
        result["NONE"] = None
        return result

    def _init_configurable_subclasses(self):
        self.move_behaviors:dict[str,type[AutomaticMove]] = self.make_class_dict(AutomaticMove)
        self.routers:dict[str,type[Router]] = self.make_class_dict(Router)
        self.navigators:dict[str,type[Navigator]] = self.make_class_dict(Navigator)
        self.todo_managers:dict[str,type[ToDoManager]] = self.make_class_dict(ToDoManager)
        self.discoverers:dict[str,type[Discoverer]] = self.make_class_dict(Discoverer)
        self.standstill_handlers:dict[str,type[StandStillHandler]] = self.make_class_dict(StandStillHandler)
        self.coordinators:dict[str,type[Coordinator]] = self.make_class_dict(Coordinator)
    
    def reset_game(self):
        self.run_simulation = False
        self.manual_move = None
        self._nr_started = 0
        self.nr_of_cycles = 0
        self.fastest:int = -1
        self.game = MazeGame(self.maze_gen.maze,square_width=self.square_width,wall_width=self.wall_width)
        blank_map:dict(str,tuple[int,int,int]) = dict()
        blank_map[Material.FLOOR_MARKED.value] = Color.WHITE.value
        blank_map[Material.FLOOR_HIGHLIGHTED.value] = Color.WHITE.value
        self.renderer= ImageGameGridRender(self.game.game_grid,material_map=blank_map)
        self._add_finish_behavior()
        self._init_auto_add_behavior()
        self._update_material_map()
        self.render()

    def generate_new(self):
        self.maze_gen =  MazeGenerator(Size(self.nr_of_cols,self.nr_of_rows))
        self.reset_game()

    def _update_material_map(self):
       # if self.show_short_path:
       #     self.renderer.material_map[Material.FLOOR_MARKED.value] = (255,0,0)
       # else:
       #     self.renderer.material_map[Material.FLOOR_MARKED.value] = Color.WHITE.value
        
        if self.show_trace:
            self.renderer.material_map[Material.FLOOR_HIGHLIGHTED.value] = (0,0,126)
        else:
            self.renderer.material_map[Material.FLOOR_HIGHLIGHTED.value] = Color.WHITE.value
        

    def render(self):
        self.renderer.render()
        self.maze_img = self.renderer.output
    
    def render_changed(self):
        self.renderer.render_changed()
        self.maze_img = self.renderer.output

    def set_show_short_path(self,value:bool):
        if self.show_short_path != value:
            self.show_short_path = value
            self.game.short_path_layer.active = value
            #self._update_material_map()
            self.render()
    
    def set_show_trace(self,value:bool):
        if self.show_trace != value:
            self.show_trace = value
            self._update_material_map()
            self.render()

    def set_auto_add(self,value:bool):
        if value:
            self.auto_add_behavior.factory = self.get_factory()
            self.auto_add_behavior.active = True
        else:
            self.auto_add_behavior.active = False
    
    def set_sim(self,value:bool):
        if self.run_simulation != value:
            self.run_simulation = value

    def get_move_behavior_cls(self) -> type[AutomaticMove]:
        return self.move_behaviors.get(self.move_behavior,ConfigurableMove)

    def add_particle(self):
            particle = Particle()
            particle.trace_material = Material.FLOOR_HIGHLIGHTED
            factory = self.get_factory()
            behavior = self.game.game_grid.add_manual_content(particle,factory)
            if behavior is not None:
                self._nr_started += 1
                self.render_changed()

    def get_factory(self):
        move_type =  self.get_move_behavior_cls()
        factory = self.default_factory
        if hasattr(move_type,'configurable') and move_type.configurable:
            factory = self.configure_factory
        else:
            factory.behavior_type = move_type
        return factory

    def add_manual_particle(self):
        if self.manual_move == None:
            particle = Particle()
            particle.material = Material.PLASTIC_HIGHLIGHTED
            self.default_factory.behavior_type = ManualMove
            self.manual_move = self.game.game_grid.add_manual_content(particle,self.default_factory)
            if self.manual_move is not None:
                self._nr_started += 1
                self.render_changed()

    def _init_auto_add_behavior(self):
        self.auto_add_behavior = AutomaticAdd(self.game.game_grid)
        self.auto_add_behavior.factory = self.get_factory()

    def _add_finish_behavior(self):
        self.finish_behavior:list[FinishDetector] = self.game.game_grid.set_behavior_last_spots(FinishDetector)

    def move_manual_particle(self,direction:Direction):
        if self.manual_move != None:
            self.manual_move.set_move(direction)

    def do_one_cycle(self):
        if self.run_simulation:
            self.game.game_grid.do_one_cycle()
            if (self.nr_started - self.get_total_finished()) > 0:
                self.nr_of_cycles +=1
            self.render_changed()

    @property
    def nr_started(self):
        if self.auto_add_behavior is None:
            return self._nr_started
        return self._nr_started + self.auto_add_behavior.nr_started

    # TODO: rename this method
    def get_total_finished(self):
        total = 0
        
        if self.finish_behavior is None:
            return total
        for behavior in self.finish_behavior:
            nr_finished = len(behavior.finished)
            if nr_finished == 0:
                continue
            total += nr_finished
            # TODO move to finish behavior?
            min_steps = min(behavior.nr_of_steps)
            if self.fastest > min_steps or self.fastest == -1:
                self.fastest = min_steps
        return total