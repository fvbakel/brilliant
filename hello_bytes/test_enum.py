import unittest
import enum

class Animal(enum.Enum):
    COW, CAT, DOG, FISH = range(4)

    @classmethod
    def list_values(cls):
        return list(map(lambda c: c.value, cls))
    
    @classmethod
    def list(cls):
        return list(map(lambda c: c, cls))

def get_cow() -> Animal:
    return Animal.COW

def get_me(animal:Animal) -> Animal:
    return animal


class TestEnum(unittest.TestCase):

    def test_enum_behavior(self):
        my_animal = Animal.DOG
        self.assertTrue(my_animal == Animal.DOG)

        my_animal = get_cow()
        self.assertTrue(my_animal == Animal.COW)

        animals = Animal.list_values()
        self.assertTrue(animals[1] == Animal.CAT.value)

        animals = Animal.list()
        self.assertTrue(animals[1] == Animal.CAT)

        animals = [animal for animal in Animal]
        self.assertTrue(animals[1] == Animal.CAT)
        

