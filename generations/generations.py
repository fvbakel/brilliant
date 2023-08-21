from abc import abstractmethod
from enum import Enum

import logging
import random
import graphviz
from os import PathLike

class Couple: pass

class Sex(Enum):
    MALE = 'm'
    FEMALE = 'f'

class Singleton:

    instance = None

    def __new__(cls):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
        return cls.instance

class Cycle(Singleton):

    def __init__(self):
        self.cycle_nr = 1
    
    def increase(self):
        self.cycle_nr += 0
    
    def reset(self):
        self.cycle_nr = 0

class Creature:
    LAST_ID = 0

    def __init__(self, parents:Couple,sex:Sex):
        self.parents = parents
        self.sex = sex
        self.couples:list[Couple] = []
        self.cycle_born = Cycle().cycle_nr
        self.cycle_dead = None

        Creature.LAST_ID += 1
        self.id = str(Creature.LAST_ID) 

    def die(self):
        self.cycle_dead = Cycle().cycle_nr

    def is_alive(self):
        if not self.cycle_dead:
            return True
        else:
            return False

    def get_age(self):
        if not self.cycle_dead:
            return Cycle().cycle_nr - self.cycle_born
        else:
            return Cycle().cycle_dead - self.cycle_born

class Couple:
    def __init__(self, father:Creature,mother:Creature):
        if mother.sex != Sex.FEMALE:
            logging.error("Mother must be female")
            return
        if father.sex != Sex.MALE:
            logging.error("Father must be male")
            return

        for couple in mother.couples:
            if couple.father == father:
                logging.error(f"Already a couple {couple.get_id()}")
                return

        self.mother = mother
        self.father = father
        self.children:list[Creature] = []

    def init_members(self):
        self.mother.couples.append(self)
        self.father.couples.append(self)

    def make_child(self):
        sex = random.choice((Sex.MALE,Sex.FEMALE))
        child = Creature(self,sex)
        self.children.append(child)
        return child
    
    def get_id(self):
        return f"{self.father.id}-{self.mother.id}"

#
#
# Rules
class ChildRule:

    def can_have_child(self,couple:Couple) -> bool:
        return True
    
class MaxChildRule:
    def set_max(self,max:int):
        self.max = max

    def can_have_child(self,couple:Couple):
        return len(couple.children) < self.max
    
class RandomMaxChildRule:
    def set_max(self,max:int):
        self.max = max

    def can_have_child(self,couple:Couple):
        if len(couple.children) < self.max:
            return random.choice((True,False))

class CoupleRule:

    def is_allowed(self,couple:Couple) -> bool:
        return True

class NoSiblingsCoupleRule(CoupleRule):

    def is_allowed(self,couple:Couple) -> bool:
        if couple.father.parents is None:
            return True
        if couple.mother.parents is None:
            return True
        
        if couple.mother.parents == couple.father.parents:
            logging.debug(f"Couple {couple.get_id()} not allowed, these are siblings from {couple.mother.parents.get_id()}")
            return False
        
        return True


class NotDeadRule:
    def is_allowed(self,couple:Couple) -> bool:
        return couple.father.is_alive() and couple.mother.is_alive()


class Population:

    def __init__(self):
        self.creatures:list[Creature] = []
        self.couples:list[Couple] = []

class PopulationGenerator:

    def __init__(self):
        self.population:Population = Population()
        self.child_rules:list[ChildRule] = []
        self.couple_rules:list[CoupleRule] = []

    def make_even_root_couples(self,nr_of_couples:int):
        for i in range(0,nr_of_couples):
            father = Creature(None,Sex.MALE)
            mother = Creature(None,Sex.FEMALE)
            self.population.creatures.append(father)
            self.population.creatures.append(mother)
            c = Couple(father=father,mother=mother)
            c.init_members()
            self.population.couples.append(c)

    def make_random_root(self,nr:int):
        for i in range(0,nr):
            self._make_random_root_creature()
    
    def _make_random_root_creature(self):
        sex = random.choice((Sex.MALE,Sex.FEMALE))
        c = Creature(None,sex)
        self.population.creatures.append(c)
        return c
    
    def make_couples(self):
        free_males:list[Creature] = []
        free_females:list[Creature] = []

        for creature in self.population.creatures:
            if len(creature.couples) == 0:
                if creature.sex == Sex.MALE:
                    free_males.append(creature)
                else:
                    free_females.append(creature)
        
        random.shuffle(free_males)
        random.shuffle(free_females)

        while (len(free_males) > 0) and (len(free_females) > 0):
            f = free_males.pop()
            m = free_females.pop()
            c = Couple(mother=m,father=f)
            allowed =True
            for rule in self.couple_rules:
                if not rule.is_allowed(c):
                    allowed = False
            if allowed:
                self.population.couples.append(c)
                c.init_members()
    
    def make_children(self):
        for couple in self.population.couples:
            allowed =True
            for rule in self.child_rules:
                if not rule.can_have_child(couple):
                    allowed = False
            if allowed:
                child = couple.make_child()
                self.population.creatures.append(child)


class Population2Dot:

    def __init__(self,population:Population):
        self.population = population
        self._refresh()

    def _refresh(self):
        self.dot = graphviz.Digraph()
        self.dot.attr(rankdir='TD')

        for creature in self.population.creatures:
            self._add_creature(creature)

        for couple in self.population.couples:
            self._add_couple(couple)

    def _add_creature(self,creature:Creature):
        node_details = '{ <label> '
        node_details += creature.id
        node_details += ' |{ <sex> '
        node_details += str(creature.sex.value)
        node_details += ' } }'
        self.dot.node(name=creature.id,label=node_details,shape='record')

    # TODO: Keep Children in subgraph
    def _add_couple(self,couple:Couple):
        couple_id = couple.get_id()
        self.dot.node(name=couple_id,shape='circle',label='')
        self.dot.edge(couple.father.id,couple_id)
        self.dot.edge(couple.mother.id,couple_id)
        for child in couple.children:
            self.dot.edge(couple_id,child.id)

    def render(self,filename:PathLike | str,directory:PathLike | str, format='svg'):
        self.dot.render(filename=filename,directory=directory, format=format)



