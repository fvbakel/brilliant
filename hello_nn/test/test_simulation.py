import unittest
from minimal_nn import *
from genetic_nn import *

class TestDNA2NetworkSimulation(unittest.TestCase):

    def test_simulation_statistics(self):

        param = SimParameters()
        param.max_nr_of_cycles          = 202
        param.report_initial_cycles     = 5
        param.report_interval_cycles    = 20
        param.nr_of_initial_gens        = 3
        param.population_size           = 500
        param.nr_of_steps_per_cycle     = 150
        param.nr_of_cols                = 100
        param.nr_of_rows                = 75
        param.mutation_probability      = 0.01
        param.survivor_threshold        = 100
        param.mix_probability           = 0.3
        param.sexual_reproduce          = True
        param.wall_mode                 = 'random'

        param.save_parameters(f'{param.sim_dir}/sim_parmams.txt')
        print('')
        sim = DNA2NetworkSimulation(param)
        sim.run_simulation()

    def test_wrong_wall_mode(self):
        param = SimParameters()
        param.wall_mode = 'does not exists'
        sim = DNA2NetworkSimulation(param)
        with self.assertRaises(ValueError):
            sim.run_simulation()


