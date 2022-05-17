
from csv import reader
import graphviz
from argparse import ArgumentParser
import logging

class GrampsObject:
    def __init__(self,id:str):
        self.id = id

class Place(GrampsObject):

    def __init__(self,id:str):
        super().__init__(id)
        self.name:str = None
        self.short_name:str = None
    
    def __repr__(self):
        return f"{self.short_name}"

class Person(GrampsObject):
    def __init__(self,id:str):
        super().__init__(id)
        self.given_name:str     = None
        self.last_name:str      = None
        self.call_name:str      = None
        self.prefix:str         = None
        self.suffix:str         = None
        self.birth_date:str     = None
        self.birth_place:Place  = None
        self.death_date:str     = None
        self.death_place:Place  = None
        self.origin_family:'Family' = None
        self.marriage_family:'Family'  = None

    def __repr__(self) -> str:
        given_names = self.given_name.split(' ')
        first_name = given_names[0]
        if self.call_name is not None and self.call_name != '':
            first_name = self.call_name
        return f"{first_name} {self.prefix} {self.last_name} {self.suffix}"
    
    def get_origin_families(self): 
        result:set['Family'] = set()
        if self.origin_family is not None:
            result.add(self.origin_family)
            if self.origin_family.husband is not None:
                result = result.union(self.origin_family.husband.get_origin_families())
            if self.origin_family.wife is not None:
                result = result.union(self.origin_family.wife.get_origin_families())
        return result

class Family(GrampsObject):

    def __init__(self,id:str):
        super().__init__(id)
        self.husband:Person         = None
        self.wife:Person            = None
        self.date:str               = None
        self.place:Place            = None
        self.children:list[Person]  = []

    def __repr__(self) -> str:
        return f"{self.id}"

class HelperFunctions:
    def strip_id(input_id:str) -> str:
        if len(input_id) > 2:
            return input_id[1:-1]
        else:
            raise ValueError(f'Error: Unable to parse id {input_id}')


class GrampsCsvParser:
    
    def __init__(self,filename:str):
        self.input_file = filename
        self.persons:dict[str,Person] = dict()
        self.places:dict[str,Place] = dict()
        self.families:dict[str,Family] = dict()
        self.separator = ','

    def read(self):
        self.state = None
        with open(self.input_file) as source:
            for line in source:
                self.parse(line)
    
    def print_stats(self):
        print(f'Nr of persons: {len(self.persons)}')
        print(f'Nr of places: {len(self.places)}')
        print(f'Nr of families: {len(self.families)}')

    def parse(self,line:str):
        if line is None or line == '' or line.find(self.separator) == -1:
            return

        for state in ['Person','Family','Marriage','Place']:
            self.parse_state(line,state)
        
        if self.header:
            self.header = False
            return
        #fields = line.split(self.separator)
        rows = list(reader([line],dialect='excel'))
        
        if len(rows) != 1:
            print(rows)
            raise ValueError('Unexpected line')
        fields = rows[0]
        self.check_nr_of_fields(fields)
        if self.state == 'Person':
            self.parse_person_fields(fields)
        if self.state == 'Place':
            self.parse_place_fields(fields)
        if self.state == 'Marriage':
            self.parse_marriage_fields(fields)
        if self.state == 'Family':
            self.parse_family_fields(fields)

    def parse_place_fields(self,fields:list[str]):
        id = HelperFunctions.strip_id(fields[0])
        place = Place(id)
        place.name = fields[1]
        place.short_name = place.name.split(',')[0]
        self.places[id] = place
    
    def parse_marriage_fields(self,fields:list[str]):
        id = HelperFunctions.strip_id(fields[0])
        family = Family(id)
        family.date = fields[3]
        if fields[4] != '':
            family.place = self.get_place(HelperFunctions.strip_id(fields[4]))
        if fields[1] != '':
            family.husband = self.get_person(HelperFunctions.strip_id(fields[1]))
            family.husband.marriage_family = family
        if fields[2] != '':
            family.wife = self.get_person(HelperFunctions.strip_id(fields[2]))
            family.wife.marriage_family = family
        
        
        
        self.families[id] = family

    def parse_family_fields(self,fields:list[str]):
        fam_id   = HelperFunctions.strip_id(fields[0])
        child_id = HelperFunctions.strip_id(fields[1])
        
        child = self.get_person(child_id)
        fam = self.get_family(fam_id)
        child.origin_family = fam
        fam.children.append(child)
    
    def get_person(self,id:str):
        if id not in self.persons:
            ValueError(f'Person [{id}] not found!')
        return self.persons[id]
    
    def get_family(self,id:str):
        if id not in self.families:
            ValueError(f'Family [{id}] not found!')
        return self.families[id]

    def get_place(self,id:str):
        if id not in self.places:
            ValueError(f'Place [{id}] not found!')
        return self.places[id]

    def check_nr_of_fields(self,fields:list[str]):
        if len(fields)!= self.nr_fields:
            print(fields)
            raise ValueError(f'Unexpected number of fields expected {self.nr_fields} found {len(fields)} ')

    def parse_person_fields(self,fields:list[str]):
        id = HelperFunctions.strip_id(fields[0])    
        person = Person(id)
        person.last_name = fields[1]
        person.given_name = fields[2]
        person.call_name = fields[3]
        person.prefix = fields[5]
        person.suffix = fields[4]
        person.birth_date = fields[8]
        if fields[9] != '':
            person.birth_place = self.get_place(HelperFunctions.strip_id(fields[9]))
        person.death_date  = fields[14]
        if fields[15] != '':
            person.death_place  = self.get_place(HelperFunctions.strip_id(fields[15]))
        self.persons[id] = person

    def parse_state(self,line:str,state:str):
        if line.startswith(state):
            self.state = state
            self.header = True
            self.nr_fields = len(line.split(self.separator))
            print(f'Loading {state}')

class PathFinder:

    def __init__(self,recent_person:Person,past_person:Person):
        self.path:list[Person] = []
        self.recent_person = recent_person
        self.past_person = past_person
        self.path_found = self.find_past_person(recent_person)

    def find_past_person(self,current_person:Person):
        if current_person is None:
            return False
        self.path.append(current_person)
        if current_person == self.past_person:
            return True
        if current_person.origin_family is not None:
            if self.find_past_person(current_person.origin_family.husband):
                return True
            if self.find_past_person(current_person.origin_family.wife):
                return True
        self.path.pop()
        return False


class CommonFinder:

    def __init__(self,personA:Person,personB:Person):
        self.personA = personA
        self.personB = personB
        self.compute_common()
        
    def _discard_origin_family(self,person:Person):
        if person is not None:
            if person.origin_family is not None:
                self.common.discard(person.origin_family)

    def compute_common(self):
        familiesA = self.personA.get_origin_families()
        familiesB = self.personB.get_origin_families()
        
        commonAll = familiesA.intersection(familiesB)
        self.common = commonAll.copy()
        for family in commonAll:
            self._discard_origin_family(family.husband)
            self._discard_origin_family(family.wife)
            




class GrampsGraph:
    left_newline = '&#92;l'
    newline = '&#92;n'
    def __init__(self):
        self.dot = graphviz.Graph()       
        self.dot.attr(rankdir='LR')
        
    
    def makePlainGraph(self,persons:set[Person]):
        families: set[Family] = set()
        for person in persons:
            families = families.union(person.get_origin_families())
            if person.marriage_family is not None:
                families.add(person.marriage_family)

        persons_todo = persons.copy()
        
        for family in families:
            if  family.husband is not None and \
                family.husband in persons_todo:
                    persons_todo.remove(family.husband)
            if  family.wife is not None and \
                family.wife in persons_todo:
                    persons_todo.remove(family.wife)

        for family in families:
            self.add_family_node(family=family)
        
        for person in persons_todo:
            self.add_person_node(person)

        for person in persons_todo:
            self.add_person_to_fam(person)
        
        for family in families:
            self.add_parent_to_fam(False,family)
            self.add_parent_to_fam(True,family)
    
    def add_parent_to_fam(self,use_wife:bool,family:Family):
        parent = family.husband
        role = 'husband'
        if use_wife:
            parent = family.wife
            role = 'wife'

        if  parent is not None and \
            parent.origin_family is not None:
            from_id = f"{family.id}:{role}"
            to_id = f"{parent.origin_family.id}:mariage"
            self.dot.edge(from_id,to_id)

    def add_person_to_fam(self,person:Person):
        if person.origin_family is not None:
            self.dot.edge(person.id,person.origin_family.id)
        
    def add_family_node(self,family:Family):
        fam_label = '<husband> '
        fam_label += self.get_person_label(family.husband)
        fam_label += ' | <mariage>'
        fam_label += self.get_marriage_label(family)
        fam_label += ' | <wife> '
        fam_label += self.get_person_label(family.wife)
        self.dot.node(name=family.id,label=fam_label,shape='record')

    def add_person_node(self,person:Person):
        label = self.get_person_label(person)
        self.dot.node(name=person.id,label=label,shape='box')

    def get_person_label(self,person:Person):
        if  person is None:
            return 'LEEG'
        birth_place = '-'
        if person.birth_place:
            birth_place = person.birth_place
        death_place = '-'
        if person.death_place:
            death_place = person.death_place
        return f"{person}{GrampsGraph.left_newline}* {person.birth_date} {birth_place}{GrampsGraph.left_newline}† {person.death_date} {death_place}{GrampsGraph.left_newline}"
    
    def get_marriage_label(self,family:Family):
        if  family is None:
            return 'LEEG'
        
        date = '-'
        if family.date:
            date = family.date
        place = '-'
        if family.place: 
            place = family.place

        
        label = f"⚭{GrampsGraph.newline}{date} {place}{GrampsGraph.newline}"
        return label

    def render(self,filename:str,directory:str, format='svg'):
        self.dot.render(filename=filename,directory=directory, format=format)

class GrampsCommand:
    def __init__(self):
        self._parser = ArgumentParser(description=
            """Make different reports based on a Gramps CVS export
            """
        )
        self._parser.set_defaults(func=self._no_args)
        self._parser.add_argument("-f","--file", help="Filename Gramps csv export", type=str, required=True, default='export-gramps.csv')

        sub_parsers = self._parser.add_subparsers()
        parser = sub_parsers.add_parser('path',help='Find a path between two wiki persons')
        parser.add_argument("start", help="Start the search from this most recent person",type=str,default=None)
        parser.add_argument("end", help="The person to find the path to", type=str,default=None)
        parser.set_defaults(func=self._path)

        parser = sub_parsers.add_parser('graph',help="Make a family graph")
        parser.add_argument("-o","--output", help="Filename to output", type=str, required=False, default='export-gramps')
        parser.add_argument("persons", help="Comma separated list of persons to use, based on id", type=str,default=None)
        parser.set_defaults(func=self._graph)

        parser = sub_parsers.add_parser('stats',help="Print the statistics")
        parser.set_defaults(func=self._stats)

        parser = sub_parsers.add_parser('common',help='Find the common family between two persons')
        parser.add_argument("personA", help="The first person",type=str,default=None)
        parser.add_argument("personB", help="The second person", type=str,default=None)
        parser.set_defaults(func=self._common)

        parser = sub_parsers.add_parser('find_person',help='Find a persons')
        parser.add_argument("person_name", help="Part of the person",type=str,default=None)
        parser.set_defaults(func=self._find_person)

        self._args = self._parser.parse_args()
        self.read_gramps()
        

    def _no_args(self):
        self._parser.print_help()

    def run(self):
        self._args.func()

    def read_gramps(self):
        self.gramps = GrampsCsvParser(filename=self._args.file)
        self.gramps.read()
    
    def _stats(self):
        self.gramps.print_stats()
    
    def _path(self):
        if self._args.start not in self.gramps.persons:
            print(f'Start person not found: {person_id}')
            return
        if self._args.end not in self.gramps.persons:
            print(f'End person not found: {person_id}')
            return

        finder = PathFinder(recent_person=self.gramps.persons[self._args.start],past_person=self.gramps.persons[self._args.end])
        if finder.path_found:
            print("Path found:")
            for person in finder.path:
                print(person)
        else:
            print("Path not found.")
    
    def _common(self):
        if self._args.personA not in self.gramps.persons:
            print(f'PersonA not found: {person_id}')
            return
        if self._args.personB not in self.gramps.persons:
            print(f'PersonB not found: {person_id}')
            return

        finder = CommonFinder(personA=self.gramps.persons[self._args.personA],personB=self.gramps.persons[self._args.personB])
        if len(finder.common) > 0:
            print(f"Common family found for [{self.gramps.persons[self._args.personA]}] and [{self.gramps.persons[self._args.personB]}]")
            for family in finder.common:
                print(f"{family}: {family.husband} -- {family.date} {family.place}-- {family.wife}")
        else:
            print("No common family found.")

    def _find_person(self):
        name = self._args.person_name.upper()
        for id,person in self.gramps.persons.items():
            label = person.__repr__().upper()
            if label.find(name) >= 0:
                print(f"{id} {person}")
    
    def _graph(self):
        person_ids = self._args.persons.split(',')
        persons:set[Person] = set()
        
        for person_id in person_ids:
            if person_id in self.gramps.persons:
                persons.add(self.gramps.persons[person_id])
            else:
                print(f'Person not found: {person_id}')

        if len(persons) == 0:
            return
        graph = GrampsGraph()
        graph.makePlainGraph(persons=persons)
        graph.render(filename=self._args.output,directory='./',format='svg')
        logging.basicConfig(level=logging.DEBUG)
        logging.debug(graph.dot)

def main():
    command = GrampsCommand()
    command.run()





if __name__ == '__main__':
    main()