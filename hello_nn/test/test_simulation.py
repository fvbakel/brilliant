import unittest
from minimal_nn import *
from genetic_nn import *

class TestDNA2NetworkSimulation(unittest.TestCase):

    def test_simulation_statistics(self):
        sim = DNA2NetworkSimulation()
        sim.make_random_population()
        print('')
        print(sim.report())

        sim.max_nr_of_cycles = 100
        sim.run_simulation()

