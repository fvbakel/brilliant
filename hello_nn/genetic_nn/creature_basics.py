from minimal_nn import *
from graph import *
from basegrid import *

import sys
import numpy as np

class SensorType(ExtendedEnum):
    LEFT    = 'left free'
    RIGHT   = 'right free'
    UP      = 'up free'
    DOWN    = 'down free'
    ROW_POS = 'row pos'
    COL_POS = 'col pos'
    OSIL_4  = 'osil 4'
    OSIL_16 = 'osil 16'
    OSIL_64 = 'osil 64'
    TIME    = 'time'

class ActionType(ExtendedEnum):
    MOVE_LEFT    = 'l'
    MOVE_RIGHT   = 'r'
    MOVE_UP      = 'u'
    MOVE_DOWN    = 'd'
    STOP         = 's'

class NeuronType(ExtendedEnum):
    INPUT   = 'I'
    HIDDEN  = 'H'
    OUTPUT  = 'O'

ALL_SENSOR_TYPES = [sensor_type for sensor_type in SensorType]
ALL_ACTION_TYPES = [action_type for action_type in ActionType]
NR_OF_HIDDEN_NEURONS =  6 # len(ALL_SENSOR_TYPES) #+ len(ALL_ACTION_TYPES)
TOTAL_NR_OF_NEURONS = len(ALL_SENSOR_TYPES) + len(ALL_ACTION_TYPES) + NR_OF_HIDDEN_NEURONS
MAX_WEIGHT = 24

#
# ID of neurons
# SENSOR_TYPES (0,1,2,3, .., ) HIDDEN_NEURONS ( 5,6,7, ..) (OUTPUT_NEURONS ( 10,11,12, ..))
# Modules is used. So incase the total is 100 Neurons. And byte code encodes for 1023 then 1023 % 100 = ID 23 is used

class Sensor:
    def __init__(self, type:SensorType,neuron:'Neuron'):
        self.type:SensorType    = type
        self.neuron:Neuron      = neuron
        self.current_value      = 0

class Action:
    def __init__(self,type:ActionType,neuron:'Neuron'):
        self.type:ActionType    = type
        self.neuron:Neuron      = neuron

class Neuron:
    ALL_NEURONS: list['Neuron'] = []

    def __init__(self):
        self.type:NeuronType
        self.id:int
        self.type_index:int

    @classmethod 
    def from_byte(cls,byte:int):
        id = byte % TOTAL_NR_OF_NEURONS
        return cls.ALL_NEURONS[id]
    
    @classmethod 
    def from_ID(cls,id:int):
        return cls.ALL_NEURONS[id]
    
    @classmethod
    def make_all_neurons(cls):
        for id in range (0,TOTAL_NR_OF_NEURONS):
            new_neuron = Neuron()
            new_neuron.id = id
            if new_neuron.id < len(ALL_SENSOR_TYPES):
                new_neuron.type_index = new_neuron.id
                new_neuron.type = NeuronType.INPUT
            elif new_neuron.id >= len(ALL_SENSOR_TYPES) and new_neuron.id < (len(ALL_SENSOR_TYPES) + NR_OF_HIDDEN_NEURONS):
                new_neuron.type_index = new_neuron.id - len(ALL_SENSOR_TYPES)
                new_neuron.type = NeuronType.HIDDEN
            else:
                new_neuron.type_index = new_neuron.id - len(ALL_SENSOR_TYPES) - NR_OF_HIDDEN_NEURONS
                new_neuron.type = NeuronType.OUTPUT
            cls.ALL_NEURONS.append(new_neuron)

Neuron.make_all_neurons()


"""
A gen is 4 bytes represent 1 neural network connection
DNA is a list gen

byte 1      : from neuron
byte 2      : to neuron
byte 3 & 4  : weight, unsigned int

This module wil convert gen

"""
class Gen:
    def __init__(self,gen_code:bytes):
        self.gen_code       = gen_code
        self.from_neuron    = Neuron.from_byte(gen_code[0])
        self.to_neuron      = Neuron.from_byte(gen_code[1])
        self.weight_int     = int.from_bytes(gen_code[2:],byteorder=sys.byteorder) % MAX_WEIGHT
        self.weight         = self.weight_int - (0.5 * MAX_WEIGHT)
        self.use_full       = False

    def is_valid_connection(self):
        if  self.from_neuron.type == NeuronType.INPUT and \
            self.to_neuron.type   == NeuronType.HIDDEN:
                return True
        if  self.from_neuron.type == NeuronType.HIDDEN and \
            self.to_neuron.type   == NeuronType.OUTPUT:
                return True
        return False

class Creature:
    def __init__(self,dna:list[bytes]):
        self.dna:list[bytes]            = dna
        self.gens:list[Gen]             = []
        self.neurons:set[Neuron]        = set()
        self.use_full_neurons:set[Neuron]

        self.network:Network            = Network()
        self.sensors:list[Sensor]       = []
        self.actions:list[Action]       = []
        self.has_valid_network          = True
        self.current_position:Position | None  = None
        self.alive                      = True

        self._init_dna()

    def reset(self):
        self.current_position:Position | None  = None
        self.alive                      = True

    def _init_dna(self):
        self._init_gens_and_neurons()
        self._init_sensors()
        self._init_actions()
        self._init_network()

    def _init_gens_and_neurons(self):
        for gen_code in self.dna:
            self.gens.append(Gen(gen_code))
        for gen in self.gens:
            self.neurons.add(gen.from_neuron)
            self.neurons.add(gen.to_neuron)
        
        hidden_neuron_with_input:set[Neuron] = set()
        hidden_neuron_with_output:set[Neuron] = set()
        for valid_gen in [gen for gen in self.gens if gen.is_valid_connection()]:
            if valid_gen.from_neuron.type == NeuronType.INPUT:
                hidden_neuron_with_input.add(valid_gen.to_neuron)
            else:
                hidden_neuron_with_output.add(valid_gen.from_neuron)
        
        self.use_full_neurons =  hidden_neuron_with_input.intersection(hidden_neuron_with_output)

        if len(self.use_full_neurons) == 0:
            self.has_valid_network = False
            return
        
        for valid_gen in [gen for gen in self.gens if gen.is_valid_connection()]:
            if valid_gen.to_neuron.type == NeuronType.HIDDEN and \
               valid_gen.to_neuron in self.use_full_neurons:
                self.use_full_neurons.add(valid_gen.from_neuron)
                valid_gen.use_full = True
            if valid_gen.from_neuron.type == NeuronType.HIDDEN and \
               valid_gen.from_neuron in self.use_full_neurons:
                self.use_full_neurons.add(valid_gen.to_neuron)
                valid_gen.use_full = True

    def _init_sensors(self):
        for index,sensor_type in enumerate(ALL_SENSOR_TYPES):
            neuron = Neuron.from_ID(index)
            if neuron in self.use_full_neurons:
                self.sensors.append(Sensor(sensor_type,neuron))

    def _init_actions(self):
        for index,action_type in enumerate(ALL_ACTION_TYPES):
            neuron = Neuron.from_ID(index + len(ALL_SENSOR_TYPES) + NR_OF_HIDDEN_NEURONS )
            if neuron in self.use_full_neurons:
                self.actions.append(Action(action_type,neuron))

    def _init_network(self):
        hidden_neurons = [neuron for neuron in self.use_full_neurons if neuron.type == NeuronType.HIDDEN ]
        hidden_neurons.sort(key=lambda x: x.type_index)
        nr_of_hidden_neurons = len(hidden_neurons)
        nr_of_input = len(self.sensors)
        nr_of_output = len(self.actions)

        if  nr_of_input == 0 or \
            nr_of_hidden_neurons == 0 or \
            nr_of_output == 0:
                self.has_valid_network = False
                return
        
        input_layer = Layer(nr_of_input,nr_of_hidden_neurons)
        hidden_layer = Layer(nr_of_hidden_neurons,nr_of_output)
        self.network.add(input_layer)
        self.network.add(hidden_layer)

        hidden_neurons_map:dict[int,int] = dict()
        for index,neuron in enumerate(hidden_neurons):
            hidden_neurons_map[neuron.type_index] = index
        
        # set weight on network    
        for valid_gen in [gen for gen in self.gens if gen.use_full]:
            from_layer_index = -1
            from_index = -1
            to_index = -1
            if valid_gen.from_neuron.type == NeuronType.INPUT:
                from_layer_index = 0
                for index,input_sensor in enumerate(self.sensors):
                    if input_sensor.neuron == valid_gen.from_neuron:
                        from_index = index
                to_index = hidden_neurons_map[valid_gen.to_neuron.type_index]
            if valid_gen.from_neuron.type == NeuronType.HIDDEN:
                from_layer_index = 1
                from_index = hidden_neurons_map[valid_gen.from_neuron.type_index]
                for index,action in enumerate(self.actions):
                      if action.neuron == valid_gen.to_neuron:
                        to_index = index

            self.network.layers[from_layer_index].weights[from_index,to_index] = valid_gen.weight


    def _init_sensors_actions_network_old(self):
        sensor_types:set[SensorType] = set()
        hidden_neurons_ids:set[int] = set()
        action_types:set[ActionType] = set()
        for valid_gen in [gen for gen in self.gens if gen.is_valid_connection()]:
            if valid_gen.from_neuron.type == NeuronType.INPUT:
                sensor_types.add(ALL_SENSOR_TYPES[valid_gen.from_neuron.type_index])
            if valid_gen.from_neuron.type == NeuronType.HIDDEN:
                hidden_neurons_ids.add(valid_gen.from_neuron.type_index)
            if valid_gen.to_neuron.type == NeuronType.HIDDEN:
                hidden_neurons_ids.add(valid_gen.to_neuron.type_index)
            if valid_gen.to_neuron.type == NeuronType.OUTPUT:
                action_types.add(ALL_ACTION_TYPES[valid_gen.to_neuron.type_index])
        
        for sensor_type in sensor_types:
            self.sensors.append(Sensor(sensor_type))
        for action_type in action_types:
            self.actions.append(Action(action_type))

        nr_of_hidden_neurons = len(hidden_neurons_ids)
        nr_of_input = len(self.sensors)
        nr_of_output = len(self.actions)

        if  nr_of_input == 0 or \
            nr_of_hidden_neurons == 0 or \
            nr_of_output == 0:
                self.has_valid_network = False
                return
        
        input_layer = Layer(nr_of_input,nr_of_hidden_neurons)
        hidden_layer = Layer(nr_of_hidden_neurons,nr_of_output)
        self.network.add(input_layer)
        self.network.add(hidden_layer)

        hidden_neurons_list = sorted(list(hidden_neurons_ids))
        hidden_neurons_map:dict[int,int] = dict()
        for index,neuron_id in enumerate(hidden_neurons_list):
            hidden_neurons_map[neuron_id] = index
        
        # set weight on network    
        for valid_gen in [gen for gen in self.gens if gen.is_valid_connection()]:
            from_layer_index = -1
            from_index = -1
            to_index = -1
            if valid_gen.from_neuron.type == NeuronType.INPUT:
                from_layer_index = 0
                for index,input_sensor in enumerate(self.sensors):
                    sensor_type = ALL_SENSOR_TYPES[valid_gen.from_neuron.type_index]
                    if input_sensor.type == sensor_type:
                        from_index = index
                to_index = hidden_neurons_map[valid_gen.to_neuron.type_index]
            if valid_gen.from_neuron.type == NeuronType.HIDDEN:
                from_layer_index = 1
                from_index = hidden_neurons_map[valid_gen.from_neuron.type_index]
                for index,action in enumerate(self.actions):
                    action_type = ALL_ACTION_TYPES[valid_gen.to_neuron.type_index]
                    if action.type == action_type:
                        to_index = index

            self.network.layers[from_layer_index].weights[from_index,to_index] = valid_gen.weight
    
    def decide_action(self):
        input_values = [sensor.current_value for sensor in self.sensors]
        output = relu(self.network.calculate(input_data=input_values))
        if sum(output) == 0:
            return ActionType.STOP
        action_index = np.argmax(output)
        return self.actions[action_index].type

    @property
    def valid_gens(self):
        return [gen for gen in self.gens if gen.is_valid_connection()]
    
    @classmethod
    def from_hex_string(cls,dna_string:str):
        dna:list[bytes] = []
        gen_hex_codes = dna_string.split(' ')
        for gen_hex_code in gen_hex_codes:
            dna.append(bytes.fromhex(gen_hex_code))
        return Creature(dna=dna)

