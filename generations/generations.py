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
        self.couples:list(Couple) = []

        Creature.LAST_ID += 1
        self.id = str(Creature.LAST_ID) 

class Couple:
    def __init__(self, mother:Creature, father:Creature):
        if mother.sex != Sex.FEMALE:
            logging.error("Mother must be female")
            return
        if father.sex != Sex.MALE:
            logging.error("Father must be male")
            return

        for couple in mother.couples:
            if couple.father == father:
                logging.error("Already a couple")
                return

        self.mother = mother
        self.father = father
        self.children:list(Creature) = []

        mother.couples.append(self)
        father.couples.append(self)

    def make_child(self):
        sex = random.choice((Sex.MALE,Sex.FEMALE))
        child = Creature(self,sex)
        self.children.append(child)
        return child
    
    def get_id(self):
        return f"{self.father.id}-{self.mother.id}"

class Population:

    def __init__(self):
        self.creatures = []
        self.couples = []

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



