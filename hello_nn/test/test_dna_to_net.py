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
        #dna_string = '000a0100 0a100100'
        # below is for move left, else up, else down, else right in case NR_OF_HIDDEN_NEURONS = 6
        # dna_string = '000a0400 0a100400 020b0300 0b120300 030c0200 0c130200 010d0100 0d110100' 
        #dna_string = '000a0400 0a100400 420b0300 0b320300 030c0200 0c130200 010d0100 0d110110' # 101
        # dna_string = '000a0400 0a100420 020b0300 0b320300 030c0200 0c130200 050d0100 0d110110' # 151
        # below is a symbiose of two
        #dna_string = '0b110b60 070ec37c 020dc945 0e1698f3 050a2dfd 0c102530 000c0a7a 002da6a8 0a134d0e 0e132e79'
        # dna_string = '0a13e422 050e55ac 000a6862 180df66e 0d106b47 0f175932 030a9e37 050d0d9e 0b126b3e 4f13fc03'
        # left top
        dna_string = '464d2ff8 000cf796 050a4e16 0a115b87 0c108980 010aa74f 024dae7b 0e123dee 010bc178 0e14ac97'
        creature = Creature.from_hex_string(dna_string=dna_string)
        graph = Gen2Graphviz(creature=creature)
        graph.makePlainGraph()
        graph.render(filename='plain',directory='./tmp')

        graph.reset()
        graph.makeSimpleClusterGraph()
        graph.render(filename='cluster',directory='./tmp')

        print('Network weights')
        for index,layer in enumerate(creature.network.layers):
            print(f'Network weights layer {index}')
            print(layer.weights)

    def test_creature_decision(self):
        # below is for move left, else up, else down, else right in case NR_OF_HIDDEN_NEURONS = 6
        dna_string = '000a0400 0a100400 020b0300 0b120300 030c0200 0c130200 010d0100 0d110100' 
        creature = Creature.from_hex_string(dna_string=dna_string)
        graph = Gen2Graphviz(creature=creature)
        graph.makePlainGraph()
        graph.render(filename='plain',directory='./tmp')

        graph.reset()
        graph.makeSimpleClusterGraph()
        graph.render(filename='cluster',directory='./tmp')

        print('Network weights')
        for index,layer in enumerate(creature.network.layers):
            print(f'Network weights layer {index}')
            print(layer.weights)
        
        creature.sensors[0].current_value = 2
        creature.sensors[1].current_value = 2
        creature.sensors[2].current_value = 2
        creature.sensors[3].current_value = 2
        action = creature.decide_action()
        print(action)