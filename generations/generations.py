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

class Creature:
    LAST_ID = 0

    def __init__(self, parents:Couple,sex:Sex):
        self.parents = parents
        self.sex = sex
        self.couples:list[Couple] = []

        Creature.LAST_ID += 1
        self.id = str(Creature.LAST_ID) 

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

class ChildRule:

    def can_have_child(self,couple:Couple) -> bool:
        return True
    
class MaxChildRule:
    def set_max(self,max:int):
        self.max = max

    def can_have_child(self,couple:Couple):
        return len(couple.children) < self.max

class CoupleRule:

    def is_allowed(self,couple:Couple) -> bool:
        return True

class NoSiblingsCoupleRule:

    def is_allowed(self,couple:Couple) -> bool:
        if couple.father.parents is None:
            return True
        if couple.mother.parents is None:
            return True
        
        if couple.mother.parents == couple.father.parents:
            logging.debug(f"Couple {couple.get_id()} not allowed, these are siblings from {couple.mother.parents.get_id()}")
            return False
        
        return True


class Population:

    def __init__(self):
        self.creatures:list[Creature] = []
        self.couples:list[Couple] = []

class PopulationGenerator:

    def __init__(self,child_rule:ChildRule,couple_rule:CoupleRule):
        self.population:Population = Population()
        self.child_rule = child_rule
        self.couple_rule = couple_rule

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
        
        while (len(free_males) > 0) and (len(free_females) > 0):
            f = free_males.pop()
            m = free_females.pop()
            c = Couple(mother=m,father=f)
            if self.couple_rule.is_allowed(c):
                self.population.couples.append(c)
                c.init_members()
    
    def make_children(self):
        for couple in self.population.couples:
            if self.child_rule.can_have_child(couple):
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


    def _add_couple(self,couple:Couple):
        couple_id = couple.get_id()
        self.dot.node(name=couple_id,shape='circle',label='')
        self.dot.edge(couple.father.id,couple_id)
        self.dot.edge(couple.mother.id,couple_id)
        for child in couple.children:
            self.dot.edge(couple_id,child.id)

    def render(self,filename:PathLike | str,directory:PathLike | str, format='svg'):
        self.dot.render(filename=filename,directory=directory, format=format)



