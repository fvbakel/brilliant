from random import randbytes, random, randrange, sample, randint, choice
import copy
import sys
import statistics
from typing import Any
import numpy as np
import pandas as pd
import cv2
import os.path
from typing import Callable

from basegrid import (
    Grid,Size,Position, ExtendedEnum,
    Direction
)


from genetic_nn.creature_basics import (
    Creature, 
    ALL_SENSOR_TYPES, ALL_ACTION_TYPES, NR_OF_HIDDEN_NEURONS, TOTAL_NR_OF_NEURONS,
    Gen,
    SensorType,ActionType
)

from genetic_nn.sim_parameters import (
    SimParameters
)

from genetic_nn.wall_build import (
    generate_wall_positions,WallMode
)

from genetic_nn.to_graphviz import Gen2Graphviz

def range_minus_one_to_one(n:float):
    if n < 0 or n> 1:
        raise ValueError(f"Expected value between 0 and 1 but got {n}")
    return (n * 2) -1

def copy_dna(dna:list[bytes],mutation_probability:float):
    if random() < mutation_probability:
        new_dna = copy.deepcopy(dna)
        nr_of_gens = len(new_dna)
        index = randrange(nr_of_gens)
        what_mutation = randint(0,2)
        if what_mutation == 0:
            new_dna[index] = flip_random_bit(new_dna[index])
        elif what_mutation == 1:
            new_dna.append(flip_random_bit(new_dna[index]))
            # new_dna.insert(index,flip_random_bit(new_dna[index]))
        else:
            new_dna.pop(index)
        return new_dna, True
    else:
        return dna, False

def mix_dna(dna_1:list[bytes],dna_2:list[bytes]):
    dna_list = [dna_1,dna_2]
    new_dna:list[bytes] = []
    
    if len(dna_1) == len(dna_2):
        for i in range(0,len(dna_1)):
            dna_index = randint(0,1)
            new_dna.append(dna_list[dna_index][i])
    else:
        return dna_1

    return new_dna

def sometimes_mix_dna(dna_1:list[bytes],dna_2:list[bytes],probability:float):
    if random() < probability:
        return mix_dna(dna_1,dna_2)
    return dna_1

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

    def __init__(self,parameters:SimParameters = SimParameters()):
        self.parameters:SimParameters = parameters

        self.current_creatures:list[Creature]  = []
        self.current_cycle          = 0
        self.current_step           = 0
        self.nr_mutated             = 0
        self.grid                   = Grid(Size(self.parameters.nr_of_cols,self.parameters.nr_of_rows))
        self.render                 = GridRender(self.grid)
        self.wall_positions         = set()

        self.nr_top_for_nn_details  = 3
        self.record                 = 0
        self.current_wall_mode      = WallMode.RANDOM.value

        Creature.START_ENERGY       = self.parameters.start_energy

        self.stats_df:pd.DataFrame | None = None

    def run_simulation(self):

        """     import cProfile, pstats, io
        from pstats import SortKey
        pr = cProfile.Profile()
        pr.enable()
        """
        if len(self.current_creatures) == 0:
            self.make_initial_population()
        self.save_population()
        while self.current_cycle < self.parameters.max_nr_of_cycles and self.nr_of_survivors > 0:
            report = False
            if  self.current_cycle <= self.parameters.report_initial_cycles or \
                self.current_cycle % self.parameters.report_interval_cycles == 0:
                    report = True

            self.do_one_cycle(make_video=report)
            if self.nr_of_survivors > self.record:
                report = True
                self.record = self.nr_of_survivors
            if report:
                self.report()
        self.report()
        """
        pr.disable()
        s = io.StringIO()
        sortby = SortKey.CUMULATIVE
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()
        print(s.getvalue())
        """

    def report(self):
        self.save_population(alive_only=True)
        self.render.render()
        self.render.save_output(f'./{self.parameters.sim_dir}/{self.current_cycle:04d}_end_situation.png')

    def reset_grid(self):
        self.wall_positions, self.current_wall_mode = generate_wall_positions(self.parameters.wall_mode,self.grid.size)
        
        for row in range(0,self.grid.size.nr_of_rows):
            for col in range(self.grid.size.nr_of_cols):
                pos = Position(col=col,row=row)
                if  pos in self.wall_positions:
                    self.grid.set_location(position=pos, content=TileType.WALL)
                else:
                    self.grid.set_location(position=pos, content=None)
        

    def make_initial_population(self):
        filename = f"{self.parameters.sim_dir}/dna_start.txt"
        if os.path.isfile(filename):
            print(f"Loading initial population from file: {filename}")
            self.load_population(filename)
        else:
            self.make_random_population()

    def make_random_creature(self):
        dna = []
        for j in range(0,self.parameters.nr_of_initial_gens):
            dna.append(random_gen_code(self.parameters.initial_valid_gens))
        creature = Creature(dna=dna)
        if not creature.has_valid_network:
            creature = self.make_random_creature()
        return creature

    def make_random_population(self):
        for i in range(0,self.parameters.population_size):
            creature = self.make_random_creature()
            self.current_creatures.append(creature)

    def save_population(self,alive_only=False):
        filename = f"{self.parameters.sim_dir}/{self.current_cycle:04d}_dna.txt"
        dna_strings = self.dna_as_str_list(alive_only)
        with open(filename, "w") as f:
            for dna_string in dna_strings:
                f.write(f"{dna_string}\n")
        self.dna_stats(dna_strings)

    def load_population(self,filename:str):
        with open(filename, "r") as f:
            for line in f:
                dna_string = line.strip()
                creature = Creature.from_hex_string(dna_string=dna_string)
                self.current_creatures.append(creature)
                if len(self.current_creatures) == self.parameters.population_size:
                    break
        if len(self.current_creatures) < self.parameters.population_size:
            self.reproduce_population()

    def do_one_cycle(self,make_video:False):
        self.current_cycle += 1
        print(f"Start cycle {self.current_cycle:04d}")
        if self.current_cycle > 1:
            self.reproduce_population()
        self.reset_grid()
        self.assign_random_positions()

        if make_video:
            codec = 'avc1' #'H264'
            out = cv2.VideoWriter(filename=f'./{self.parameters.sim_dir}/{self.current_cycle:04d}.mp4',fourcc=cv2.VideoWriter_fourcc(*codec), fps=30, frameSize=(self.grid.size.nr_of_cols,self.grid.size.nr_of_rows))

        for self.current_step in range(1, self.parameters.nr_of_steps_per_cycle + 1):
            if make_video:
                self.render.render()
                out.write(self.render.output)
            self.do_one_step()
        self.select_survivors()

        self.append_statistics()
        self.save_statistics()
        if make_video:
            self.render.render()
            out.write(self.render.output)
            out.release()

    def assign_random_positions(self):
        wall_positions_flat_ids = set([self.grid.get_flat_id(pos) for pos in self.wall_positions])
        flat_ids = set(self.grid.flat_ids) - wall_positions_flat_ids
        flat_position_ids = sample(population=list(flat_ids),k=self.nr_of_valid_creatures)
        for index,creature in enumerate(self.valid_creatures):
            pos = self.grid.get_position(flat_position_ids[index])
            self.set_creature_position(new_pos=pos,creature=creature)
    
    def do_one_step(self):
        creatures = sample(population=self.valid_creatures ,k=self.nr_of_valid_creatures)
        for creature in creatures:
            self.assign_sensor_values(creature)
            if creature.energy > 0:
                action = creature.decide_action()
                self.do_action_on_creature(action,creature)

    def assign_sensor_values(self,creature:Creature):
        for sensor in creature.sensors:
            if sensor.type == SensorType.LEFT:
                sensor.current_value = self.ratio_neighbor_free_in_direction(pos=creature.current_position,direction=Direction.LEFT)
            elif sensor.type == SensorType.RIGHT:
                sensor.current_value = self.ratio_neighbor_free_in_direction(pos=creature.current_position,direction=Direction.RIGHT)
            elif sensor.type == SensorType.UP:
                sensor.current_value = self.ratio_neighbor_free_in_direction(pos=creature.current_position,direction=Direction.UP)
            elif sensor.type == SensorType.DOWN:
                sensor.current_value = self.ratio_neighbor_free_in_direction(pos=creature.current_position,direction=Direction.DOWN)
            elif sensor.type == SensorType.ROW_POS:
                sensor.current_value = creature.current_position.row / self.grid.size.nr_of_rows
            elif sensor.type == SensorType.COL_POS:
                sensor.current_value = creature.current_position.col / self.grid.size.nr_of_cols
            elif sensor.type == SensorType.ROW_POS_INV:
                sensor.current_value = (self.grid.size.nr_of_rows - creature.current_position.row) / self.grid.size.nr_of_rows
            elif sensor.type == SensorType.COL_POS_INV:
                sensor.current_value = (self.grid.size.nr_of_cols - creature.current_position.col) / self.grid.size.nr_of_cols
            elif sensor.type == SensorType.OSIL_4:
                sensor.current_value = self.osil(4)
            elif sensor.type == SensorType.OSIL_16:
                sensor.current_value = self.osil(16)
            elif sensor.type == SensorType.OSIL_64:
                sensor.current_value = self.osil(64)
            elif sensor.type == SensorType.TIME:
                sensor.current_value = self.current_step / self.parameters.nr_of_steps_per_cycle
            elif sensor.type == SensorType.TIME_INV:
                sensor.current_value = (self.parameters.nr_of_steps_per_cycle - self.current_step) / self.parameters.nr_of_steps_per_cycle
            elif sensor.type == SensorType.RANDOM:
                sensor.current_value = random()
            if self.parameters.negative_sensors:
                sensor.current_value = range_minus_one_to_one(sensor.current_value)

    def osil(self,fase:int):
        remain = self.current_step % fase
        if remain > ((fase/2) -1):
            return 1
        else:
            return 0
        
    def ratio_neighbor_free_in_direction(self,pos:Position,direction:Direction):
        if self.parameters.max_vision == 0:
            return 0
        nr_free = self.nr_neighbor_free_in_direction(pos,direction)
        return  nr_free / self.parameters.max_vision
        
    
    def nr_neighbor_free_in_direction(self,pos:Position,direction:Direction):
        nr_free = 0
        next_pos = pos.get_position_in_direction(direction)
        is_free = True
        while is_free and nr_free < self.parameters.max_vision: 
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

    def do_action_on_creature(self,action:ActionType | None,creature:Creature):
        new_pos:Position | None = None
        if action == ActionType.MOVE_LEFT:
            new_pos =  creature.current_position.get_position_in_direction(Direction.LEFT)
        elif action == ActionType.MOVE_RIGHT:
            new_pos =  creature.current_position.get_position_in_direction(Direction.RIGHT)
        elif action == ActionType.MOVE_UP:
            new_pos =  creature.current_position.get_position_in_direction(Direction.UP)
        elif action == ActionType.MOVE_DOWN:
            new_pos =  creature.current_position.get_position_in_direction(Direction.DOWN)
        elif action == ActionType.SLEEP:
            creature.energy += 1
        else:
            creature.energy -= 2

        if new_pos is not None and creature.energy > 0:
            self.set_creature_position(new_pos=new_pos,creature=creature)
            energy_cost = self.parameters.gen_energy_cost * len(creature.gens)
            creature.energy -= energy_cost

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
        survive_width =  round(self.grid.size.nr_of_cols * 0.2)
        for creature in self.current_creatures:
            if  not creature.has_valid_network or \
                    creature.current_position.col > survive_width :
                        creature.alive = False

    def a_sexual_reproduce_one(self,creature:Creature):
        new_dna, mutated = copy_dna(creature.dna,self.parameters.mutation_probability)
        if mutated:
            self.nr_mutated += 1
        return Creature(dna=new_dna)
    
    def sexual_reproduce_one(self,creature_1:Creature, creature_2:Creature):
        new_dna_1, mutated = copy_dna(creature_1.dna,self.parameters.mutation_probability)
        if mutated:
            self.nr_mutated += 1
        new_dna_2, mutated = copy_dna(creature_2.dna,self.parameters.mutation_probability)
        if mutated:
            self.nr_mutated += 1

        new_dna = sometimes_mix_dna(new_dna_1,new_dna_2,probability=self.parameters.mix_probability)
        return Creature(dna=new_dna)

    def reproduce_population(self):
        if self.nr_of_survivors == 0:
            return

        nr_new_to_create = self.parameters.population_size
        new_creatures:list[Creature] = []

        # add random creatures if needed
        for i in range(0, self.parameters.nr_of_always_random ):
            creature = self.make_random_creature()
            new_creatures.append(creature)
            nr_new_to_create -= 1

        if self.nr_of_survivors < self.parameters.survivor_threshold:
            for i in range(0, self.parameters.survivor_threshold - self.nr_of_survivors ):
                creature = self.make_random_creature()
                new_creatures.append(creature)
                nr_new_to_create -= 1

        # recreate all survivors
        while nr_new_to_create > self.nr_of_survivors:
            for creature in self.survivors:
                new_creatures.append(self.reproduce_one(creature))
                nr_new_to_create -= 1

        # random select survivors that are allowed to create one more copy
        extra = sample(self.survivors,nr_new_to_create)
        for creature in extra:
            new_creatures.append(self.reproduce_one(creature))

        self.current_creatures = new_creatures

    def reproduce_one(self, creature:Creature):
        if self.parameters.sexual_reproduce:
            partner = choice(self.survivors)
            return self.sexual_reproduce_one(creature,partner)
        elif self.parameters.competition_reproduce:
            competition = choice(self.survivors)
            if creature.energy >= competition.energy:
                return self.a_sexual_reproduce_one(creature)
            else:
                return self.a_sexual_reproduce_one(competition)
        else:
            return self.a_sexual_reproduce_one(creature)

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

    def save_statistics(self):
        self.stats_df.to_csv(f'./{self.parameters.sim_dir}/statistics.csv')

    def append_statistics(self):
        stats_current_cycle = self.stats_current_cycle()
        stats_current_cycle_row = dict()
        for key,value in  stats_current_cycle.items():
            stats_current_cycle_row[key] = [value]
        df_new_row = pd.DataFrame(stats_current_cycle_row)

        if self.stats_df is None:
            self.stats_df = df_new_row
        else:
            self.stats_df = pd.concat([self.stats_df, df_new_row], ignore_index = True)
            self.stats_df.reset_index()


    def stats_current_cycle(self) -> dict[str,int | float]:
        output:dict[str,int | float] = dict()
        output["cycle"] = self.current_cycle
        output["population_size"] = self.parameters.population_size
        output["nr_of_initial_gens"] = self.parameters.nr_of_initial_gens
        output["nr_of_valid_creatures"] = self.nr_of_valid_creatures
        output["nr_of_survivors"] = self.nr_of_survivors
        output["nr_mutated"] = self.nr_mutated
        output["wall_mode"] = self.current_wall_mode

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
            output["average_nr_valid_gens_per_creatures"] = sum(nr_of_valid_gens) / self.nr_of_survivors
            output["median_nr_valid_gens_per_creatures"] = median(nr_of_valid_gens)

            output["average_nr_sensors_per_creatures"] = sum(nr_of_sensors) / self.nr_of_survivors
            output["median_nr_sensors_per_creatures"] = median(nr_of_sensors)

            output["average_nr_actions_per_creatures"] = sum(nr_of_actions) / self.nr_of_survivors
            output["median_nr_actions_per_creatures"] = median(nr_of_actions)

        for key,value in count_sensors_map.items():
            output[f"sensor {key}"] = value

        for key,value in count_actions_map.items():
            output[f"action {key}"] = value
        
        return output

    def dna_stats(self,dna_strings:list[str]):
        df = pd.DataFrame(columns=['DNA'],data = dna_strings )
        dna_common = df.groupby('DNA')['DNA'].count().sort_values(ascending=False).head(self.nr_top_for_nn_details)
        for nr,data in enumerate(dna_common.items()):
            dna_string = data[0]
            count = data[1]
            creature = Creature.from_hex_string(dna_string=dna_string)
            graph = Gen2Graphviz(creature=creature) 
            graph.makeSimpleClusterGraph()
            graph.render(filename=f"{self.current_cycle:04d}_nn_{nr+1}_{count}.dot",directory=self.parameters.sim_dir)
        
        gen_map:dict[str,int] = dict()
        for dna_string in dna_strings:
            gen_codes = dna_string.split(sep=' ')
            for gen_code in gen_codes:
                if gen_code not in gen_map:
                    gen_map[gen_code] = 0
                gen_map[gen_code] += 1
        
        sorted_gen_map = sorted(gen_map.items(), key=lambda item: item[1], reverse=True)
        with open(f"{self.parameters.sim_dir}/{self.current_cycle:04d}_gen_stats.txt", "w") as file:
            for gen_code, value in sorted_gen_map:
                file.write(f"{gen_code},{value}\n")


    def dna_as_str_list(self,alive_only:bool = True):
        dna_strings:list[str] = []
        for creature in self.current_creatures:
            if alive_only and not creature.alive:
                continue
            hex_dna:list[str] = []
            for gen_code in creature.dna:
                hex_dna.append(gen_code.hex())
            dna_string = ' '.join(hex_dna)
            dna_strings.append(dna_string)
        return dna_strings



class Color(ExtendedEnum):
    WHITE = (255,255,255)
    BLACK = (0,0,0)
    BLUE  = (255,0,0)
    GREEN = (0,255,0)
    RED   = (0,0,255)

class ColorScheme(ExtendedEnum):
    SIMPLE  = 0
    NEURON  = 1

class DnaColorMap:

    def __init__(self,color_scheme:ColorScheme):
        self.dna_vs_color:dict[list[Gen],tuple[int,int,int]] = dict()
        self.used_color: set[tuple[int,int,int]] =set(list(Color))
        self.color_scheme = color_scheme

    def _simple_key(self,gens:list[Gen]):
        return tuple(gen for gen in gens if gen.use_full)
    
    def _neuron_key(self,gens:list[Gen]):
        return tuple(sorted(set((gen.from_neuron.id,gen.to_neuron.id) for gen in gens if gen.use_full)))

    def _get_key(self,gens:list[Gen]):
        get_key_functions: dict[str, Callable[[list[Gen]]]] = {
            ColorScheme.SIMPLE.value: self._simple_key,
            ColorScheme.NEURON.value: self._neuron_key
        }

        return get_key_functions[self.color_scheme.value](gens)

    def get_color(self,gens:list[Gen]):
        dna_key = self._get_key(gens)
        if dna_key in self.dna_vs_color:
            return self.dna_vs_color[dna_key]
        else:
            color = self._make_new_color()
            self.dna_vs_color[dna_key] = color
            return color

    def _make_new_color(self):
        blue = randrange(1,254)
        green = randrange(1,254)
        red = randrange(1,254)
        color = (blue,green,red)
        if color in self.used_color:
            return self._make_new_color()
        self.used_color.add(color)
        return color
        

class GridRender:

    def __init__(self,grid:Grid):
        self.grid = grid    
        self._init_image()
        self.colormap = DnaColorMap(color_scheme=ColorScheme.NEURON)
    
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
                    color = self.colormap.get_color(content.gens)
                    self.output[col_index,row_index] = color  #Color.BLACK.value
                else:
                    self.output[col_index,row_index] = Color.RED.value
            elif content == TileType.WALL:
                self.output[col_index,row_index] = (255,0,255)
            else:
                self.output[col_index,row_index] = Color.BLUE.value
            

    def save_output(self,filename:str):
        if self.output is not None:
            cv2.imwrite(filename,self.output)