import re
import random

reg_ex_letter = re.compile('^[a-z]$')

class GameRound:

    def __init__(self,solution:str):
        self.solution = solution

        self.guessed:set[str] = set()
        self.guessed_ordered:list[str] = list()
        self.nr_of_wrong_guesses = 0
        self.size = len(self.solution)

    def get_word_view(self):
        return " ".join(letter if letter in self.guessed else "_" for letter in self.solution)

    def nr_of_guesses(self):
        return len(self.guessed_ordered)

    def is_ready(self):
        for letter in self.solution:
            if letter not in self.guessed:
                return False
        return True

    def guess_word(self,word:str):
        return word == self.solution

    def guess_letter(self,letter:str):
        if not reg_ex_letter.fullmatch(letter):
            raise ValueError(f"Expected one lower case letter in range [a-z], got {letter}")
        self.guessed.add(letter)
        self.guessed_ordered.append(letter)
        if letter in self.solution:
            return True
        else:
            self.nr_of_wrong_guesses +=1
            return False

class WordList:

    def __init__(self,file:str = ''):
        self.file = file
        self.words:dict[int,list[str]] = dict()

    def read_wordlist(self):
        if len(self.file) == 0:
            self.file = "/home/fvbakel/tmp/basiswoorden-gekeurd-filtered.txt"
        
        with open(self.file, "r") as input:
            for line in input:
                if line is None:
                    continue
                word = line.strip()
                l = len(word)
                if l not in self.words:
                    self.words[l] = []
                self.words[l].append(word)

    def random_word(self,lenght:int = 0,min_lenght=3,max_lenght=10):
        if lenght == 0:
            l = random.choice([l for l in self.words.keys() if l >= min_lenght and l < max_lenght ])
        elif lenght in self.words:
            l = lenght
        else:
            raise ValueError(f"Words with lenght {lenght} do not occur in word list.")

        return random.choice(self.words[l])

    def get_available_lenghts(self):
        return self.words.keys()

    


    
