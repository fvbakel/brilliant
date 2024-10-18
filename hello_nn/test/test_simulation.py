import unittest
from minimal_nn import *
from genetic_nn import *

class TestDNA2NetworkSimulation(unittest.TestCase):

    def test_simulation_statistics(self):

        param = SimParameters()
        param.max_nr_of_cycles          = 5002
        param.report_initial_cycles     = 5
        param.report_interval_cycles    = 50
        param.nr_of_initial_gens        = 10
        param.population_size           = 500
        param.nr_of_steps_per_cycle     = 150
        param.nr_of_cols                = 100
        param.nr_of_rows                = 150
        param.mutation_probability      = 0.05

        print('')
        sim = DNA2NetworkSimulation(param)
        sim.run_simulation()

