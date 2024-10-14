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
    
    def test_creature_from_dna_string(self):
        #dna_string = '161b4d75 141b3198 0e197efe 0a198a26 000d5544 171c2306 0a1d77da 111a3ef7'
        dna_string = '01109e0b 081301a4 171c9915 000a6038 0a1956f8 15164f8b 09101a3c 0111e98f'
        creature = Creature.from_hex_string(dna_string=dna_string)
        graph = Gen2Graphviz(creature=creature)
        graph.makePlainGraph()
        graph.render(filename='plain',directory='./tmp')

        graph.reset()
        graph.makeSimpleClusterGraph()
        graph.render(filename='cluster',directory='./tmp')