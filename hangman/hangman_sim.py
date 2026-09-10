import hangman as hm
from argparse import ArgumentParser
from pathlib import Path
import re
from timeit import default_timer as timer

class HangmanSim():

    def __init__(self):
        self.wordlist = hm.WordList()
        self.wordlist.read_wordlist()
        self.min_lenght = 3
        self.strategy = HangManStrategyFreq(self.wordlist) 

    def solve_word(self,word:str,verbose=False):
        round = hm.GameRound(word)
        i = 0
        self.strategy.set_current_round(round)
        while not round.is_ready():
            next = self.strategy.guess_next()
            round.guess_letter(next)
            if verbose:
                i += 1
                print(f"{i:02d}, {next} : {round.get_word_view()}")
        return round

    def solve_all(self,lenght:int=0):
        input_file = Path(self.wordlist.file)
        output_file = f"{input_file.parent}/{input_file.stem}_sim.txt"
        print(f"Writing output file: {output_file}")
        with open(output_file, "w") as output: 
            if lenght == 0:
                for nr_of_letters,words in self.wordlist.words.items():
                    if nr_of_letters < self.min_lenght:
                        continue
                    self._process_words(output, nr_of_letters, words)
            else:
                self._process_words(output, lenght, self.wordlist.words[lenght])
        print("Ready")

    def _process_words(self, output, nr_of_letters, words):
        print(f"Processing {len(words)} words of lenght {nr_of_letters}")
        start = timer()
        for word in words:
            round = self.solve_word(word)
            output.write(f"{word},{nr_of_letters},{round.nr_of_wrong_guesses}\n")
        end = timer()
        duration = end - start
        speed = len(words) / duration
        print(f"Ready processing {len(words)} words of lenght {nr_of_letters}. duration: {duration:.2f} sec Speed: {speed:.2f} words per second")

class HangManStrategy():

    def __init__(self,wordlist:hm.WordList):
        self.wordlist = wordlist
        self.current_list:list[str] = list()
        self.current_round:hm.GameRound

    def set_current_round(self,round:hm.GameRound):
        self.current_round = round
        self.current_list = self.wordlist.words[self.current_round.size]

    def get_available_words(self):
        if self.current_round.nr_of_guesses() == 0:
            return self.current_list
        
        reg_ex = self.current_round.get_regular_expression()
        result:list[str] = list()
        for word in filter(reg_ex.match,self.current_list):
            if len(self.current_round.guessed_wrong.intersection(word)) == 0:
                result.append(word)
        self.current_list = result
        return self.current_list

    def get_letter_frequency(self):
        return hm.LetterFrequency(self.get_available_words())

    def guess_next(self)->str:
        return "a"

class HangManStrategyFreq(HangManStrategy):

    def __init__(self,wordlist:hm.WordList):
        super().__init__(wordlist)

    def guess_next(self,round = hm.GameRound)->str:
        if self.current_round.is_ready():
            raise ValueError("Round is ready, nothing to guess")
            
        freq = self.get_letter_frequency()
        for letter in freq.order_by_frequency():
            if letter not in self.current_round.guessed:
                return letter
        return ""

"""
Basic idea for this stratey is to try to cut the list 
of possible words in two equal halfs with the next guess
"""
class HangManStrategyHalf(HangManStrategy):

    def __init__(self,wordlist:hm.WordList):
        super().__init__(wordlist)

    def guess_next(self,round = hm.GameRound)->str:
        if self.current_round.is_ready():
            raise ValueError("Round is ready, nothing to guess")
        words = self.get_available_words()
        nr_of_words = len(words)
        half = nr_of_words // 2
        freq = hm.LetterFrequency(words)
        choosen_letter = ""
        best_diff = nr_of_words + 1
        for letter,count in freq.order_by_frequency().items():
            if letter not in self.current_round.guessed:
                diff = abs(half - count)
                if diff < best_diff:
                    best_diff = diff
                    choosen_letter = letter
        return choosen_letter

def main():
    parser = ArgumentParser(description=
            """Simulate hangman.
            """
        )
    parser.add_argument("-w","--word", help="Simulate the game on a single word and output the guesses", type=str, required=False, default=None)
    parser.add_argument("-p","--pattern", help="Search the wordlist based on a pattern, example .a. where . is an unknown letter", type=str, required=False, default=None)
    parser.add_argument("-l","--lenght", help="Simulate the game only for letters of given lenght", type=int, required=False, default=0)
    args = parser.parse_args()

    sim = HangmanSim()
    if args.word is not None:
        sim.solve_word(args.word,True)
    elif args.pattern is not None:
        search_pattern(args)
    elif args.lenght is not None and args.lenght > 0:
        sim.solve_all(args.lenght)
    else:
        sim.solve_all()

def search_pattern(args):
    wordlist = hm.WordList()
    wordlist.read_wordlist()
    size = len(args.pattern)
    reg_ex = re.compile(args.pattern)
    print(list(filter(reg_ex.match,wordlist.words[size])))


if __name__ == "__main__":
    main()