import unittest
from minimal_nn import *
from genetic_nn import *

class TestDNA2NetworkSimulation(unittest.TestCase):

    def test_simulation_statistics(self):
        sim = DNA2NetworkSimulation()
        sim.make_random_population()
        print('')
        print(sim.statistics())

        sim.do_one_cycle()
        print(sim.statistics())
        for i in range(0,100):
            sim.do_one_cycle()
        print(sim.statistics())

        for i in range(0,1000):
            sim.do_one_cycle()
        print(sim.statistics())
        

