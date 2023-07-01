import unittest
from generations import *
from testconfig import *

class TestGenerations(unittest.TestCase):

    def test_basic_classes(self):
        f = Creature(None,Sex.MALE)
        m = Creature(None,Sex.FEMALE)
        c = Couple(mother=m,father=f)
        c.make_child()

        self.assertEqual(len(c.children),1,"Make one child")

    def test_population2Dot(self):
        population = Population()
        f = Creature(None,Sex.MALE)
        m = Creature(None,Sex.FEMALE)
        c = Couple(mother=m,father=f)
        child_1 = c.make_child()
        population.couples.append(c)
        population.creatures.append(f)
        population.creatures.append(m)
        population.creatures.append(child_1)

        r = Population2Dot(population)
        r.render(self._testMethodName + "001" + ".dot",TEST_TMP_DIR)

    def test_nosiblings_rule(self):
        population = Population()
        couple_rule = NoSiblingsCoupleRule()

        f = Creature(None,Sex.MALE)
        m = Creature(None,Sex.FEMALE)
        c = Couple(mother=m,father=f)
        self.assertIsNotNone(c,"Possible to create main couple")
        self.assertTrue(couple_rule.is_allowed(c),"Two root parents are allowed")
        c.init_members()
        population.couples.append(c)

        child_1 = c.make_child()
        child_1.sex = Sex.MALE
        child_2 = c.make_child()
        child_2.sex = Sex.FEMALE

        c_2 = Couple(father=child_1,mother=child_2)
        self.assertIsNotNone(c_2,"Possible to create couple 2")
        self.assertFalse(couple_rule.is_allowed(c_2),"Siblings couple is not allowed")
        

        f_2 = Creature(None,Sex.MALE)
        m_2 = Creature(None,Sex.FEMALE)
        c_3 = Couple(mother=m_2,father=f_2)
        self.assertIsNotNone(c_3,"Possible to create main couple 3")
        self.assertTrue(couple_rule.is_allowed(c_3),"Two root parents are allowed")
        c_3.init_members()
        population.couples.append(c_3)

        child_3 = c_3.make_child()
        child_3.sex = Sex.MALE
        child_4 = c_3.make_child()
        child_4.sex = Sex.FEMALE
        c_4 = Couple(father=child_1,mother=child_4)
             
        population.couples.append(c_4)
        r = Population2Dot(population)
        r.render(self._testMethodName + "c_4" + ".dot",TEST_TMP_DIR)

        self.assertIsNotNone(c_4,"Possible to create couple 4")
        self.assertTrue(couple_rule.is_allowed(c_4),"Cousins couple is allowed")

    def test_population_generator(self):
        max_4 = MaxChildRule()
        max_4.set_max(4)

        couple_rule = NoSiblingsCoupleRule()

        generator = PopulationGenerator(child_rule=max_4,couple_rule=couple_rule)
        generator.make_even_root_couples(2)

        r = Population2Dot(generator.population)
        r.render(self._testMethodName + "001" + ".dot",TEST_TMP_DIR)

        
        generator.make_children()
        r = Population2Dot(generator.population)
        r.render(self._testMethodName + "002" + ".dot",TEST_TMP_DIR)

        generator.make_children()
        generator.make_couples()
        generator.make_children()
        generator.make_children()

        r = Population2Dot(generator.population)
        r.render(self._testMethodName + "003" + ".dot",TEST_TMP_DIR)