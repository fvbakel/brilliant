import unittest
from generations import *
from testconfig import *

class TestGenerations(unittest.TestCase):

    def test_basic_classes(self):
        f = Creature(None,Sex.MALE)
        m = Creature(None,Sex.FEMALE)
        c = Couple(m,f)
        c.make_child()

        self.assertEqual(len(c.children),1,"Make one child")

    def test_population2Dot(self):
        population = Population()
        f = Creature(None,Sex.MALE)
        m = Creature(None,Sex.FEMALE)
        c = Couple(m,f)
        child_1 = c.make_child()
        population.couples.append(c)
        population.creatures.append(f)
        population.creatures.append(m)
        population.creatures.append(child_1)

        r = Population2Dot(population)
        r.render(self._testMethodName + "001" + ".dot",TEST_TMP_DIR)