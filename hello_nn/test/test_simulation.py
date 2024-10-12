import unittest
from minimal_nn import *
from genetic_nn import *
from basegrid import Size

class TestDNA2NetworkSimulation(unittest.TestCase):

    def test_simulation_statistics(self):
        sim = DNA2NetworkSimulation()
        
        sim.max_nr_of_cycles = 5002
        sim.report_initial_cycles = 5
        sim.report_interval_cycles = 50
        sim.nr_of_initial_gens = 8
        sim.population_size = 500
        sim.nr_of_steps_per_cycle = 150

        sim.make_random_population()
        print('')
        print(sim.report())


        sim.run_simulation()

