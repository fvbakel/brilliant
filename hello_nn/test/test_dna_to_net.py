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
        #dna_string = '01109e0b 081301a4 171c9915 000a6038 0a1956f8 15164f8b 09101a3c 0111e98f'
        #dna_string = '010f5c74 0d1b1e6e 0d1a64a9 131d9f44 5019a0f6 0417b833 0714a565 120d07c9'
        #dna_string = '010f5c74 0d1b1e6e 0d1a64a9 131d9f44 5019a0f6 0417b833 0714a565 120d07c9'
        #dna_string = '0b0dc338 040ced5c 0a0ee8e4 0a0dca5b 040bbd3b 0c0d97d2 040c986e 070cd1d4 020b93a7 050a1ee8 0b0fe0d6 070c6b40 0a115ae5 0c1198e0 0a0dfac3 040cf0cd'
        dna_string = '0c0cc545 0a1040c1 0b0dcb16 0a11f440 0a101abf 0a1d1f47 020b25e4 0f0fffc7 0a0dd8f0 0a10ca20'
        creature = Creature.from_hex_string(dna_string=dna_string)
        graph = Gen2Graphviz(creature=creature)
        graph.makePlainGraph()
        graph.render(filename='plain',directory='./tmp')

        graph.reset()
        graph.makeSimpleClusterGraph()
        graph.render(filename='cluster',directory='./tmp')

        print('Network weights')
        print('Network weights layer 0')
        print(creature.network.layers[0].weights)
        print('Network weights layer 1')
        print(creature.network.layers[1].weights)
