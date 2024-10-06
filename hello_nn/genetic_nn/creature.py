from minimal_nn import *
from genetic_nn.simulation import *
from graph import *
from basegrid import *
import sys

class SensorType(ExtendedEnum):
    LEFT    = 'left free'
    RIGHT   = 'right free'
    UP      = 'up free'
    DOWN    = 'down free'

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

ALL_SENSOR_TYPES = SensorType.list()
ALL_ACTION_TYPES = ActionType.list()
NR_OF_HIDDEN_NEURONS = len(ALL_SENSOR_TYPES) + len(ALL_ACTION_TYPES)
TOTAL_NR_OF_NEURONS = len(ALL_SENSOR_TYPES) + len(ALL_ACTION_TYPES) + NR_OF_HIDDEN_NEURONS
MAX_WEIGHT = 1024

#
# ID of neurons
# SENSOR_TYPES (0,1,2,3, .., ) HIDDEN_NEURONS ( 5,6,7, ..) (OUTPUT_NEURONS ( 10,11,12, ..))
# Modules is used. So incase the total is 100 Neurons. And byte code encodes for 1023 then 1023 % 100 = ID 23 is used

class Sensor:
    def __init__(self, type:SensorType):
        self.type = type
        self.current_value = 0

class Action:
    def __init__(self,type:ActionType):
        self.type = type

class Neuron:
    def __init__(self):
        self.type:NeuronType
        self.id:int
        self.index:int

    @classmethod 
    def from_byte(cls,byte:int):
        new_neuron = Neuron()
        new_neuron.id = byte % TOTAL_NR_OF_NEURONS
        if new_neuron.id < len(ALL_SENSOR_TYPES):
            new_neuron.index = new_neuron.id
            new_neuron.type = NeuronType.INPUT
        elif new_neuron.id >= len(ALL_SENSOR_TYPES) and new_neuron.id < (len(ALL_SENSOR_TYPES) + NR_OF_HIDDEN_NEURONS):
            new_neuron.index = new_neuron.id - len(ALL_SENSOR_TYPES)
            new_neuron.type = NeuronType.HIDDEN
        else:
            new_neuron.index = new_neuron.id - len(ALL_SENSOR_TYPES) - NR_OF_HIDDEN_NEURONS
            new_neuron.type = NeuronType.OUTPUT
        return new_neuron


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
        self.weight         = int.from_bytes(gen_code[2:],byteorder=sys.byteorder) % MAX_WEIGHT

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
        self.dna:list[bytes] = dna
        self.gens:list[Gen] = []
        self.network:Network = Network()
        self.sensors:list[Sensor] = []
        self.actions:list[Action] = []
        self.has_valid_network = True

        self._init_dna()

    def _init_dna(self):
        self._init_gens()
        self._init_sensor_and_actions()

    def _init_gens(self):
        for gen_code in self.dna:
            self.gens.append(Gen(gen_code))

    def _init_sensor_and_actions(self):
        sensor_types:set[SensorType] = set()
        hidden_neurons:set[int] = set()
        action_types:set[ActionType] = set()
        for valid_gen in [gen for gen in self.gens if gen.is_valid_connection()]:
            if valid_gen.from_neuron.type == NeuronType.INPUT:
                sensor_types.add(ALL_SENSOR_TYPES[valid_gen.from_neuron.index])
            if valid_gen.from_neuron.type == NeuronType.HIDDEN:
                hidden_neurons.add(valid_gen.from_neuron.index)
            if valid_gen.to_neuron.type == NeuronType.HIDDEN:
                hidden_neurons.add(valid_gen.to_neuron.index)
            if valid_gen.to_neuron.type == NeuronType.OUTPUT:
                action_types.add(ALL_SENSOR_TYPES[valid_gen.to_neuron.index])
        
        for sensor_type in sensor_types:
            self.sensors.append(Sensor(sensor_type))
        for action_type in action_types:
            self.actions.append(Action(action_type))


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

        hidden_neurons_list = list(hidden_neurons)
        hidden_neurons_map:dict[int,int] = dict()
        for index,neuron in enumerate(hidden_neurons_list):
            print(f"hidden_neurons_map: {neuron} -> {index}")
            hidden_neurons_map[neuron] = index
        
        # set weight on network    
        for valid_gen in [gen for gen in self.gens if gen.is_valid_connection()]:
            from_layer_index = -1
            from_index = -1
            to_index = -1
            if valid_gen.from_neuron.type == NeuronType.INPUT:
                from_layer_index = 0
                for index,input_sensor in enumerate(self.sensors):
                    sensor_type = ALL_SENSOR_TYPES[valid_gen.from_neuron.index]
                    if input_sensor.type == sensor_type:
                        from_index = index
                to_index = hidden_neurons_map[valid_gen.to_neuron.index]
            if valid_gen.from_neuron.type == NeuronType.HIDDEN:
                from_layer_index = 1
                print(f"valid_gen.from_neuron.index {valid_gen.from_neuron.index}")
                from_index = hidden_neurons_map[valid_gen.from_neuron.index]
                for index,action in enumerate(self.actions):
                    action_type = ALL_ACTION_TYPES[valid_gen.to_neuron.index]
                    if action.type == action_type:
                        to_index = index

            self.network.layers[from_layer_index].weights[from_index,to_index] = valid_gen.weight

