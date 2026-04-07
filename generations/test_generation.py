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

    def test_Cycle(self):
        cycle_1 = Cycle.cycle
        cycle_2 = Cycle.cycle
        self.assertEqual(cycle_1,cycle_2)

        Cycle.cycle.increase()
        self.assertEqual(cycle_1.cycle_nr,2)

        Cycle.cycle.increase()
        self.assertEqual(cycle_1.cycle_nr,3)
        
        self.assertEqual(Cycle.cycle.cycle_nr,3)

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

    def test_population_simulator(self):
        max = MaxChildRule()
        max.set_max(3)

        simulator = PopulationSimulation()
        simulator.child_rules.append(max)
        simulator.child_rules.append(NotDeadRule())
        #simulator.child_rules.append(AgeCoupleRule())
        simulator.couple_rules.append(NoSiblingsCoupleRule())
        simulator.couple_rules.append(NotDeadRule())
        
        simulator.population.make_even_root_couples(2)

        r = Population2Dot(simulator.population)
        r.render(self._testMethodName + "001" + ".dot",TEST_TMP_DIR)
        
        simulator.make_children()
        Cycle.cycle.increase()
        r = Population2Dot(simulator.population)
        r.render(self._testMethodName + "002" + ".dot",TEST_TMP_DIR)

        simulator.make_children()
        simulator.make_couples()
        simulator.make_children()
        Cycle.cycle.increase()
        simulator.make_children()
        Cycle.cycle.increase()

        r = Population2Dot(simulator.population)
        r.render(self._testMethodName + "003" + ".dot",TEST_TMP_DIR)

        for i in range(0,8):
            Cycle.cycle.increase()
            simulator.die_old_creatures()
            simulator.make_couples()
            for i in range(0,max.max):
                simulator.make_children()
                Cycle.cycle.increase()

        r = Population2Dot(simulator.population)
        r.render(self._testMethodName + "004" + ".dot",TEST_TMP_DIR)

    def test_max_3(self):
        max = MaxChildRule()
        max.set_max(3)

        simulator = PopulationSimulation()
        simulator.child_rules.append(max)
        simulator.child_rules.append(NotDeadRule())
        #simulator.child_rules.append(AgeCoupleRule())
        simulator.couple_rules.append(NoSiblingsCoupleRule())
        simulator.couple_rules.append(NotDeadRule())
        
        simulator.population.make_even_root_couples(3)

        self.run_simulation(simulator,max,20)

    def test_max_2(self):
        max = MaxChildRule()
        max.set_max(2)

        simulator = PopulationSimulation()
        simulator.child_rules.append(max)
        simulator.child_rules.append(NotDeadRule())
        simulator.child_rules.append(AgeCoupleRule())
        simulator.couple_rules.append(NoSiblingsCoupleRule())
        simulator.couple_rules.append(NotDeadRule())
        
        simulator.population.make_even_root_couples(3)

        self.run_simulation(simulator,max,20)

    def test_random_max(self):
        max = RandomMaxChildRule()
        max.set_max(5)

        age_rule = AgeCoupleRule()
        age_rule.set_min(2)
        age_rule.set_max(8)

        simulator = PopulationSimulation()
        simulator.child_rules.append(max)
        simulator.child_rules.append(NotDeadRule())
        simulator.child_rules.append(age_rule)
        simulator.couple_rules.append(NoSiblingsCoupleRule())
        simulator.couple_rules.append(NotDeadRule())
        
        simulator.population.make_even_root_couples(3)

        self.run_simulation(simulator,max,50)

    def run_simulation(self,simulator:PopulationSimulation,max:MaxChildRule,nr_of_cycles:int):
        r = Population2Dot(simulator.population)
        r.render(f"{self._testMethodName}_{0}.dot",TEST_TMP_DIR)
                
        for i in range(1,nr_of_cycles):
            Cycle.cycle.increase()
            simulator.die_old_creatures()
            simulator.make_couples()
            simulator.make_children()

        r = Population2Dot(simulator.population)
        r.render(f"{self._testMethodName}_{i:02d}.dot",TEST_TMP_DIR)
        