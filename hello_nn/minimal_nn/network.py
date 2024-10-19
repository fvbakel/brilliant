import numpy as np

class Layer:
    def __init__(self, nr_of_input_neurons:int, nr_of_output_neurons:int):
        self.nr_of_input_neurons = nr_of_input_neurons
        self.nr_of_output_neurons = nr_of_output_neurons
        self.weights = np.zeros(shape=(nr_of_input_neurons,nr_of_output_neurons))

    def forward_propagation(self, input_data):
        return np.dot(input_data, self.weights)

class Network:
    def __init__(self):
        self.layers:list[Layer] = []

    def add(self, layer:Layer):
        self.layers.append(layer)

    def calculate(self, input_data):
        output = input_data
        for layer in self.layers:
            output = layer.forward_propagation(output)

        return output
    
def tanh(input):
    return np.tanh(input)

def relu(input):
    return np.maximum(input, 0)

def convert_to_chance(input):
    return input / sum(input)

def get_max_index(input):
    return np.argmax(input)