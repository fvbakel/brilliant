import unittest
from genetic_nn import *

class TestSimParameters(unittest.TestCase):

    def test_load_and_save(self):
        SimParameters.write_sample_parameters()

        SimParameters.load_parameters('./example_config.json')

