import json
from dataclasses import dataclass

@dataclass
class SimParameters:
    max_nr_of_cycles        : int  = 10
    nr_of_steps_per_cycle   : int  = 200
    start_energy            : int  = 200
    population_size         : int  = 800
    nr_of_initial_gens      : int  = 8
    mutation_probability    : float = 0.01
    nr_of_always_random     : int   = 1
    report_initial_cycles   : int  = 10
    report_interval_cycles  : int  = 10
    max_vision              : int  = 3
    initial_valid_gens      : bool = True
    nr_of_cols              : int  = 150
    nr_of_rows              : int  = 200
    survivor_threshold      : int  = 200
    mix_probability         : float = 0.3
    wall_mode               : str  = 'two'
    sexual_reproduce        : bool = False
    competition_reproduce   : bool = True
    sim_dir                 : str  = './tmp'

    def save_parameters(self,filename:str):
        with open(filename, 'w') as f:
            json.dump(self.__dict__, fp=f, indent=4)

    @classmethod
    def load_parameters(cls,configFilename):
        with open(configFilename, 'r') as f:
            config = json.load(f)
        return SimParameters(**config)

    @classmethod
    def write_sample_parameters(cls):
        param = SimParameters()
        param.save_parameters('example_config.json')
