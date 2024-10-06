import unittest
from minimal_nn import *
from genetic_nn import *

class TestDNA(unittest.TestCase):

    def test_dna_to_net(self):
        dna = [bytes.fromhex("01040100"),
               bytes.fromhex("040f0300")]
        creature = Creature(dna)
        self.assertTrue(creature.has_valid_network)
        network = creature.network
        print(network.layers[0].weights)

        self.assertEqual(1.0, network.layers[0].weights[0,0]) 