from random import randbytes, random, randrange, sample, randint
import copy
import sys
import statistics
from typing import Any
import numpy as np
import cv2

from genetic_nn.creature_basics import (
    Creature, 
    ALL_SENSOR_TYPES, ALL_ACTION_TYPES, NR_OF_HIDDEN_NEURONS, TOTAL_NR_OF_NEURONS,
    Gen,
    SensorType,ActionType
)

from basegrid import (
    Grid,Size,Position, ExtendedEnum,
    Direction
)

def copy_dna(dna:list[bytes],mutation_probability:float):
    if random() < mutation_probability:
        new_dna = copy.deepcopy(dna)
        nr_of_gens = len(new_dna)
        index = randrange(nr_of_gens)
        new_dna[index] = flip_random_bit(new_dna[index])
        return new_dna, True
    else:
        return dna, False

def flip_random_bit(gen_code:bytes):
    nr_of_bytes = len(gen_code)
    int_value = int.from_bytes(gen_code,byteorder=sys.byteorder)
    int_value ^= 1 << randrange((nr_of_bytes * 8) -1)
    return int_value.to_bytes(nr_of_bytes,byteorder=sys.byteorder)

def random_gen_code(valid_only:bool = False):
    if valid_only:
        gen_type = randint(0,1)
        if gen_type == 0:
            from_id = randrange(0,len(ALL_SENSOR_TYPES))
            to_id = randrange(len(ALL_SENSOR_TYPES), (len(ALL_SENSOR_TYPES) + NR_OF_HIDDEN_NEURONS))
        else:
            from_id = randrange(len(ALL_SENSOR_TYPES), (len(ALL_SENSOR_TYPES) + NR_OF_HIDDEN_NEURONS))
            to_id = randrange( (len(ALL_SENSOR_TYPES) + NR_OF_HIDDEN_NEURONS), TOTAL_NR_OF_NEURONS)
        weight = randbytes(2)
        return from_id.to_bytes(1,byteorder=sys.byteorder) + to_id.to_bytes(1,byteorder=sys.byteorder) + weight
    else:
        return randbytes(4)

def median(input):
    if len(input) == 0:
        return 0
    return statistics.median(input)

class TileType:
    WALL = 1

class DNA2NetworkSimulation:

    def __init__(self):
        self.max_nr_of_cycles       = 10
        self.nr_of_steps_per_cycle  = 200
        self.population_size        = 800
        self.nr_of_initial_gens     = 8
        self.mutation_probability   = 0.01
        self.report_initial_cycles  = 10
        self.report_interval_cycles = 10
        self.max_vision             = 3
        self.initial_valid_gens     = True

        self.current_creatures:list[Creature]  = []
        self.current_cycle          = 0
        self.nr_mutated             = 0
        self.grid_size              = Size(150,200)
        self.grid                   = Grid(self.grid_size)
        self.render                 = GridRender(self.grid)
        self.wall_positions         = set()

    def run_simulation(self):

        import cProfile, pstats, io
        from pstats import SortKey
        pr = cProfile.Profile()
        pr.enable()

        while self.current_cycle < self.max_nr_of_cycles and self.nr_of_survivors > 0:
            self.do_one_cycle(False)
            if  self.current_cycle <= self.report_initial_cycles or \
                self.current_cycle % self.report_interval_cycles == 0:
                    self.report()
        self.report()

        pr.disable()
        s = io.StringIO()
        sortby = SortKey.CUMULATIVE
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()
        print(s.getvalue())

    def report(self):
        print('*** Statistics report ***')
        stats = self.statistics()
        for stat in stats:
            print(stat)
        self.render.render()
        self.render.save_output(f'./tmp/sim_stat_gen_{self.current_cycle:04d}.png')

    def reset_grid(self):
        wall_col        = round(self.grid.size.nr_of_cols * 0.2) + 1
        wall_size       = self.grid.size.nr_of_rows // 2
        wall_row_start  = randrange(0,self.grid.size.nr_of_rows - wall_size )
        wall_row_end    = wall_row_start + wall_size
        for row in range(0,self.grid.size.nr_of_rows):
            for col in range(self.grid.size.nr_of_cols):
                pos = Position(col=col,row=row)
                if  col == wall_col and \
                    wall_row_start <= row <= wall_row_end:
                        self.grid.set_location(position=pos, content=TileType.WALL)
                        self.wall_positions.add(pos)
                else:
                    self.grid.set_location(position=pos, content=None)

    def make_random_population(self):
        for i in range(0,self.population_size):
            dna = []
            for j in range(0,self.nr_of_initial_gens):
                dna.append(random_gen_code(self.initial_valid_gens))
            self.current_creatures.append(Creature(dna=dna))

    def do_one_cycle(self,report_details:False):
        self.current_cycle += 1
        if self.current_cycle > 1:
            self.reset_grid()
            self.reproduce_population()
        self.assign_random_positions()
        for i in range(0, self.nr_of_steps_per_cycle):
            if report_details:
                self.render.render()
                self.render.save_output(f'./tmp/sim_details_{self.current_cycle:04d}_step_{i}.png')
            self.do_one_step(i)
        self.select_survivors()

    def assign_random_positions(self):
        wall_positions_flat_ids = set([self.grid.get_flat_id(pos) for pos in self.wall_positions])
        flat_ids = set(self.grid.flat_ids) - wall_positions_flat_ids
        flat_position_ids = sample(population=list(flat_ids),k=self.nr_of_valid_creatures)
        for index,creature in enumerate(self.valid_creatures):
            pos = self.grid.get_position(flat_position_ids[index])
            self.set_creature_position(new_pos=pos,creature=creature)
    
    def do_one_step(self,step_nr:int):
        creatures = sample(population=self.valid_creatures ,k=self.nr_of_valid_creatures)
        for creature in creatures:
            self.assign_sensor_values(creature)
            action = creature.decide_action()
            self.do_action_on_creature(action,creature)

    def assign_sensor_values(self,creature:Creature):
        # TODO Improve performance?!
        for sensor in creature.sensors:
            if sensor.type == SensorType.LEFT:
                sensor.current_value = self.nr_neighbor_free_in_direction(pos=creature.current_position,direction=Direction.LEFT)
            elif sensor.type == SensorType.RIGHT:
                sensor.current_value = self.nr_neighbor_free_in_direction(pos=creature.current_position,direction=Direction.RIGHT)
            elif sensor.type == SensorType.UP:
                sensor.current_value = self.nr_neighbor_free_in_direction(pos=creature.current_position,direction=Direction.UP)
            elif sensor.type == SensorType.DOWN:
                sensor.current_value = self.nr_neighbor_free_in_direction(pos=creature.current_position,direction=Direction.DOWN)
    
    def nr_neighbor_free_in_direction(self,pos:Position,direction:Direction):
        nr_free = 0
        next_pos = pos.get_position_in_direction(direction)
        is_free = True
        while is_free and nr_free < self.max_vision: 
            is_free = self.is_position_free(pos=next_pos)
            if is_free:
                nr_free +=1
                next_pos =  next_pos.get_position_in_direction(direction)
        return nr_free

    def is_neighbor_free_in_direction(self,pos:Position,direction:Direction):
        new_pos =  pos.get_position_in_direction(direction)
        return self.is_position_free(new_pos)
    
    def is_position_free(self,pos:Position):
        if      pos is None or \
            not self.grid.has_location(pos) or \
                self.grid.get_location(pos) is not None:
                return False
        else:
            return True

    def do_action_on_creature(self,action:ActionType,creature:Creature):
        new_pos:Position | None = None
        if action == ActionType.MOVE_LEFT:
            new_pos =  creature.current_position.get_position_in_direction(Direction.LEFT)
        elif action == ActionType.MOVE_RIGHT:
            new_pos =  creature.current_position.get_position_in_direction(Direction.RIGHT)
        elif action == ActionType.MOVE_UP:
            new_pos =  creature.current_position.get_position_in_direction(Direction.UP)
        elif action == ActionType.MOVE_DOWN:
            new_pos =  creature.current_position.get_position_in_direction(Direction.DOWN)

        if new_pos is not None:
            self.set_creature_position(new_pos=new_pos,creature=creature)
    

    def set_creature_position(self,new_pos:Position,creature:Creature):
        if      new_pos is None or \
            not self.grid.has_location(new_pos) or \
                self.grid.get_location(new_pos) is not None:
                return
        
        self.grid.set_location(position=new_pos,content=creature)
        if creature.current_position is not None:
            self.grid.set_location(position=creature.current_position,content=None)
        creature.current_position = new_pos

    def select_survivors(self):
        # TODO build actual implementation
        survive_width =  round(self.grid.size.nr_of_cols * 0.2)
        print(f'survive_width={survive_width}')
        for creature in self.current_creatures:
            if  not creature.has_valid_network or \
                    creature.current_position.col > survive_width :
                        creature.alive = False

    def reproduce_one(self,creature:Creature):
        new_dna, mutated = copy_dna(creature.dna,self.mutation_probability)
        if mutated:
            self.nr_mutated += 1
        return Creature(dna=new_dna)
        """ 
            Below is a possible performance gain
            copy_creature = copy.deepcopy(creature)
            copy_creature.reset()
            return copy_creature
        """

    def reproduce_population(self):
        survivors = self.survivors
        nr_of_survivors = len(survivors)
        if nr_of_survivors == 0:
            return
        
        nr_new_to_create = self.population_size
        new_creatures:list[Creature] = []

        # first just recreate all survivors
        while nr_new_to_create > nr_of_survivors:
            for creature in survivors:
                new_creatures.append(self.reproduce_one(creature))
                nr_new_to_create -= 1

        # random select survivors that are allowed to create one more copy
        extra = sample(survivors,nr_new_to_create)
        for creature in extra:
            new_creatures.append(self.reproduce_one(creature))

        self.current_creatures = new_creatures

    @property
    def nr_of_valid_creatures(self):
        return len(self.valid_creatures)

    @property
    def valid_creatures(self):
        return [y for y in self.current_creatures if y.has_valid_network]
    
    @property
    def nr_of_survivors(self):
        return len(self.survivors)

    @property
    def survivors(self):
        return [y for y in self.current_creatures if y.alive]

    def statistics(self):
        output = []
        output.append(("current_cycle",self.current_cycle))
        output.append(("population_size",self.population_size))
        output.append(("nr_of_initial_gens",self.nr_of_initial_gens))
        output.append(("nr_of_valid_creatures",self.nr_of_valid_creatures))
        output.append(("nr_of_survivors",self.nr_of_survivors))
        output.append(("nr_mutated",self.nr_mutated))
        nr_of_valid_gens = []
        nr_of_sensors = []
        nr_of_actions = []
        count_sensors_map = dict()
        count_actions_map = dict()
        for creature in self.survivors:
            nr_of_valid_gens.append(len(creature.valid_gens))
            nr_of_sensors.append(len(creature.sensors))
            nr_of_actions.append(len(creature.actions))
            for sensor in creature.sensors:
                if sensor.type in count_sensors_map:
                    count_sensors_map[sensor.type] += 1
                else:
                    count_sensors_map[sensor.type] = 1
            for action in creature.actions:
                if action.type in count_actions_map:
                    count_actions_map[action.type] += 1
                else:
                    count_actions_map[action.type] = 1
        if self.nr_of_survivors > 0:
            output.append(("average_nr_valid_gens_per_creatures",sum(nr_of_valid_gens) / self.nr_of_survivors))
            output.append(("median_nr_valid_gens_per_creatures",median(nr_of_valid_gens)))

            output.append(("average_nr_sensors_per_creatures",sum(nr_of_sensors) / self.nr_of_survivors))
            output.append(("median_nr_sensors_per_creatures",median(nr_of_sensors)))

            output.append(("average_nr_actions_per_creatures",sum(nr_of_actions) / self.nr_of_survivors))
            output.append(("median_nr_actions_per_creatures",median(nr_of_actions)))

        for key,value in count_sensors_map.items():
            output.append((f"sensor {key} ",value))

        for key,value in count_actions_map.items():
            output.append((f"action {key} ",value))
        
        return output



class Color(ExtendedEnum):
    WHITE = (255,255,255)
    BLACK = (0,0,0)
    BLUE  = (255,0,0)
    GREEN = (0,255,0)
    RED   = (0,0,255)

class GridRender:

    def __init__(self,grid:Grid):
        self.grid = grid    
        self._init_image()
    
    def _init_image(self):
        self.output = np.full   (  (self.grid.size.nr_of_rows,self.grid.size.nr_of_cols,3),
                                    fill_value = Color.WHITE.value,
                                    dtype=np.uint8
        )

    def render(self):
        row:list[Any]
        for row_index,row in enumerate(self.grid.locations):
            self._render_row(row_index,row)

    def _render_row(self,row_index:int,row:list[Any]):
        content:Creature | None
        for col_index,content in enumerate(row):
            if content is None:
                self.output[col_index,row_index] = Color.WHITE.value
            elif isinstance(content,Creature):
                if content.alive:
                    self.output[col_index,row_index] = Color.BLACK.value
                else:
                    self.output[col_index,row_index] = Color.RED.value
            elif content == TileType.WALL:
                self.output[col_index,row_index] = (255,0,255)
            else:
                self.output[col_index,row_index] = Color.BLUE.value
            

    def save_output(self,filename:str):
        if self.output is not None:
            cv2.imwrite(filename,self.output)