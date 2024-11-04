from genetic_nn.simulation import DnaColorMap,ColorScheme
from minimal_nn import *
from genetic_nn import *

import unittest

class TestColor(unittest.TestCase):

    def test_color_map(self):
        
        dna = [bytes.fromhex("010f0100"),
               bytes.fromhex("0f150300")]
        creature = Creature(dna)
        map = DnaColorMap(color_scheme=ColorScheme.NEURON)
        color_1 = map.get_color(creature.gens)
        color_2 = map.get_color(creature.gens)
        print(color_1)

        graph = Gen2Graphviz(creature=creature)
        graph.makeSimpleClusterGraph()
        graph.render(filename='cluster-color-test',directory='./tmp')

        self.assertEqual(color_1,color_2)

        dna_2 = [bytes.fromhex("010f1100"),
               bytes.fromhex("0f150300")]
        creature_2 = Creature(dna_2)

        graph = Gen2Graphviz(creature=creature_2)
        graph.makeSimpleClusterGraph()
        graph.render(filename='cluster-color-test_2',directory='./tmp')

        map = DnaColorMap(color_scheme=ColorScheme.NEURON)
        color_1 = map.get_color(creature.gens)
        color_2 = map.get_color(creature_2.gens)
        print(color_1)
        self.assertEqual(color_1,color_2)

        map = DnaColorMap(color_scheme=ColorScheme.SIMPLE)
        color_1 = map.get_color(creature.gens)
        color_2 = map.get_color(creature_2.gens)
        print(color_1)
        self.assertNotEqual(color_1,color_2)
