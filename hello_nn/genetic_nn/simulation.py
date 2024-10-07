from random import randbytes, random, randrange, sample, randint
from genetic_nn.creature_basics import Creature, ALL_SENSOR_TYPES, ALL_ACTION_TYPES, NR_OF_HIDDEN_NEURONS, TOTAL_NR_OF_NEURONS,Gen
import copy
import sys
import statistics

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



class DNA2NetworkSimulation:

    def __init__(self):
        self.nr_of_cycles           = 1000
        self.population_size        = 3000
        self.nr_of_initial_gens     = 16
        self.mutation_probability   = 0.03
        self.initial_valid_gens     = True
        self.current_creatures:list[Creature]  = []
        self.current_cycle          = 1
        self.nr_mutated             = 0

    def make_random_population(self):
        for i in range(0,self.population_size):
            dna = []
            for j in range(0,self.nr_of_initial_gens):
                dna.append(random_gen_code(self.initial_valid_gens))
            self.current_creatures.append(Creature(dna=dna))

    def do_one_cycle(self):
        self.current_cycle += 1
        self.reproduce_population()

    def reproduce_one(self,creature:Creature):
        new_dna, mutated = copy_dna(creature.dna,self.mutation_probability)
        if mutated:
            self.nr_mutated += 1
            return Creature(dna=new_dna)
        else:
            return creature

    def reproduce_population(self):
        survivors = [y for y in self.current_creatures if y.has_valid_network]
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
        return len([y for y in self.current_creatures if y.has_valid_network])
    
    @property
    def survivors(self):
        return [y for y in self.current_creatures if y.has_valid_network]

    def statistics(self):
        output = []
        output.append(("current_cycle",self.current_cycle))
        output.append(("population_size",self.population_size))
        output.append(("nr_of_initial_gens",self.nr_of_initial_gens))
        output.append(("nr_of_valid_creatures",self.nr_of_valid_creatures))
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
        output.append(("average_nr_valid_gens_per_creatures",sum(nr_of_valid_gens) / self.nr_of_valid_creatures))
        output.append(("median_nr_valid_gens_per_creatures",statistics.median(nr_of_valid_gens)))

        output.append(("average_nr_sensors_per_creatures",sum(nr_of_sensors) / self.nr_of_valid_creatures))
        output.append(("median_nr_sensors_per_creatures",statistics.median(nr_of_sensors)))

        output.append(("average_nr_actions_per_creatures",sum(nr_of_actions) / self.nr_of_valid_creatures))
        output.append(("median_nr_actions_per_creatures",statistics.median(nr_of_actions)))

        for key,value in count_sensors_map.items():
            output.append((f"sensor {key} ",value))

        for key,value in count_actions_map.items():
            output.append((f"action {key} ",value))
        
        return output