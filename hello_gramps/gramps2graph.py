
from csv import reader

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
        self.prefix:str         = None
        self.suffix:str         = None
        self.birth_date:str     = None
        self.birth_place:Place  = None
        self.death_date:str     = None
        self.death_place:Place  = None
        self.origin_family:'Family' = None
        self.child_family:'Family'  = None

    def __repr__(self) -> str:
        return f"{self.id} {self.given_name} {self.prefix} {self.last_name} {self.suffix}"

class Family(GrampsObject):

    def __init__(self,id:str):
        super().__init__(id)
        self.husband:Person          = None
        self.wife:Person          = None
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
            family.husband.child_family = family
        if fields[2] != '':
            family.wife = self.get_person(HelperFunctions.strip_id(fields[2]))
            family.wife.child_family = family
        
        
        
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

from argparse import ArgumentParser

def main():
    parser = ArgumentParser(description=
        """Convert a Gramps csv export to a graph
        """
    )
        
    parser.add_argument("-f","--file", help="Filename Gramps csv export", type=str, required=True, default='export-gramps.csv')
    args = parser.parse_args()

    gramps = GrampsCsvParser(filename=args.file)
    gramps.read()
    gramps.print_stats()
    if 'I0000' in gramps.persons:
        print(gramps.persons)
    #for id,place in parser.places.items():
    #    print(place)

if __name__ == '__main__':
    main()