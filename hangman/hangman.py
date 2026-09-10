import re
import random

reg_ex_letter = re.compile('^[a-z]$')

class GameRound:

    def __init__(self,solution:str):
        self.solution = solution

        self.guessed:set[str] = set()
        self.guessed_ordered:list[str] = list()
        self.guessed_wrong:set[str] = set()
        self.nr_of_wrong_guesses = 0
        self.size = len(self.solution)

    def get_word_view(self):
        return " ".join(letter if letter in self.guessed else "_" for letter in self.solution)

    def get_regular_expression(self):
        regex_str = "".join(letter if letter in self.guessed else "." for letter in self.solution)
        return re.compile(regex_str)

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
            self.guessed_wrong.add(letter)
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

class LetterFrequency:

    def __init__(self,list_of_words:list[str]):
        self.list_of_words = list_of_words
        self.stats:dict[str,int] = dict()
        self.calculate()

    def calculate(self):
        for word in self.list_of_words:
            # below is a choice, we count letter frequency per word. If one
            # letters is multiple times in one word, this still counts as one
            for letter in set(word):
                if letter not in self.stats:
                    self.stats[letter] = 0
                self.stats[letter] += 1

    def order_by_frequency(self):
        return {k: v for k, v in sorted(self.stats.items(), key=lambda item: item[1],reverse=True)}

    def __str__(self)->str:
        result:list[str] = []
        keys = sorted(self.stats.keys())
        for key in keys:
            result.append(f"{key} = {self.stats[key]}")
        return "\n".join(result)

    
