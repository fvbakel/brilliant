import unittest
from minimal_nn import *
from genetic_nn import *

import os

class TestDNA2NetworkSimulation(unittest.TestCase):

    def test_simulation_statistics(self):

        param = SimParameters()
        param.max_nr_of_cycles          = 102
        param.report_initial_cycles     = 5
        param.report_interval_cycles    = 25
        param.nr_of_initial_gens        = 10
        param.population_size           = 500
        param.nr_of_always_random       = 0
        param.nr_of_steps_per_cycle     = 200
        param.start_energy              = 150
        param.nr_of_cols                = 100
        param.nr_of_rows                = 75
        param.mutation_probability      = 0.03
        param.survivor_threshold        = 180
        param.mix_probability           = 0.8
        param.gen_energy_cost           = 1/param.nr_of_initial_gens
        param.sexual_reproduce          = False
        param.competition_reproduce     = False
        param.negative_sensors          = True
        param.wall_mode                 = 'bucket'

        param.save_parameters(f'{param.sim_dir}/sim_parmams.txt')
        print('')
        sim = DNA2NetworkSimulation(param)
        sim.run_simulation()

    def test_simulation_loop(self):

        param = SimParameters()
        param.max_nr_of_cycles          = 52
        param.report_initial_cycles     = 5
        param.report_interval_cycles    = 25
        param.nr_of_initial_gens        = 10
        param.population_size           = 500
        param.nr_of_always_random       = 0
        param.nr_of_steps_per_cycle     = 200
        param.start_energy              = 150
        param.nr_of_cols                = 100
        param.nr_of_rows                = 75
        param.mutation_probability      = 0.03
        param.survivor_threshold        = 180
        param.mix_probability           = 0.8
        param.gen_energy_cost           = 1/param.nr_of_initial_gens
        param.sexual_reproduce          = False
        param.competition_reproduce     = False
        param.negative_sensors          = True
        param.wall_mode                 = 'bucket'

        for i in range(0,20):
            param.sim_dir = f'./tmp/comp/{i}'
            os.makedirs(param.sim_dir) 
            param.save_parameters(f'{param.sim_dir}/sim_parmams.txt')
            print(f'Running simulation {i}')
            sim = DNA2NetworkSimulation(param)
            sim.run_simulation()

    def test_wrong_wall_mode(self):
        param = SimParameters()
        param.wall_mode = 'does not exists'
        sim = DNA2NetworkSimulation(param)
        with self.assertRaises(ValueError):
            sim.run_simulation()


