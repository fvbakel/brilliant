from genetic_nn.simulation import DnaColorMap
from minimal_nn import *
from genetic_nn import *

import unittest

class TestColor(unittest.TestCase):

    def test_color_map(self):
        dna = [bytes.fromhex("01040100"),
               bytes.fromhex("040f0300")]
        creature = Creature(dna)
        map = DnaColorMap()
        color_1 = map.get_color(creature.gens)
        color_2 = map.get_color(creature.gens)
        print(color_1)
        self.assertEqual(color_1,color_2)
