import unittest
import numpy as np

from minimal_nn import *

class TestNeuralNet(unittest.TestCase):

    def test_minimal_layer(self):
        layer = Layer(3,4)
        layer.weights[0,0] = 1.0
        layer.weights[0,1] = 1.0
        layer.weights[1,1] = 1.0
        layer.weights[1,2] = 1.0

        input_data = [1,2,3]
        
        print("Layer Weights:")
        print(layer.weights)
        print("Output:")
        output = layer.forward_propagation(input_data)
        print(output)

        self.assertEqual(1.0,output[0])
        self.assertEqual(3.0,output[1])
        self.assertEqual(2.0,output[2])
        self.assertEqual(0.0,output[3])

    def test_network(self):
        network = Network()
        input_layer = Layer(3,4)
        hidden_layer = Layer(4,5)
        network.add(input_layer)
        network.add(hidden_layer)

        input_layer.weights[0,0] = 1.0
        input_layer.weights[0,1] = 1.0
        input_layer.weights[1,1] = 1.0
        input_layer.weights[1,2] = 1.0

        hidden_layer.weights[0,0] = 1.0
        hidden_layer.weights[1,1] = 1.0
        hidden_layer.weights[2,2] = 1.0
        hidden_layer.weights[3,3] = 1.0

        input_data = [1,2,3]
        output = network.calculate(input_data)
        print("Output")
        print(output)

        self.assertEqual(1.0,output[0])
        self.assertEqual(3.0,output[1])
        self.assertEqual(2.0,output[2])
        self.assertEqual(0.0,output[3])
        self.assertEqual(0.0,output[4])

        print("np.tanh(output)=", np.tanh(output))
        print("output / sum(output)=", output / sum(output))
        print("np.argmax(output)=", np.argmax(output))

    def test_zero_input(self):
        layer = Layer(3,4)
        layer.weights[0,0] = 1.0
        layer.weights[0,1] = 1.0
        layer.weights[1,1] = 1.0
        layer.weights[1,2] = 1.0

        input_data = [0,0,0]
        
        print("Input:")
        print(input)
        print("Output:")
        output = layer.forward_propagation(input_data)
        print(output)

        self.assertEqual(0.0,output[0])
        self.assertEqual(0.0,output[1])
        self.assertEqual(0.0,output[2])
        self.assertEqual(0.0,output[3])
