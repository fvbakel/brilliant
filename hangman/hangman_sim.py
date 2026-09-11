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
            next,result = self.strategy.guess_next()
            if verbose:
                i += 1
                nr = len(self.strategy.current_list)
                first = self.strategy.current_list[:7]
                print(f"{i:02d},{str(result)[0]}, {next} : {round.get_word_view()}, {nr:06d},{first}")
        return round

    def solve_all(self,lenght:int=0):
        input_file = Path(self.wordlist.file)
        output_file = f"{input_file.parent}/{input_file.stem}_sim_{lenght}.txt"
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
        self.first_freq_cache:dict[int,hm.LetterFrequency] = dict()
        self.current_freq:hm.LetterFrequency
        self.word_list_cache:dict[int,dict[int,list[str]]] = dict()
        

    def set_current_round(self,round:hm.GameRound):
        self.current_round = round
        self.current_list = self.wordlist.words[self.current_round.size]
        if self.current_round.size not in self.first_freq_cache:
            self.first_freq_cache[self.current_round.size] = hm.LetterFrequency(self.current_list)
        self.current_freq = self.first_freq_cache[self.current_round.size]

    def update_current_wordlist(self,last_letter:str,last_result:bool):
        if last_result:
            self._filter_for_correct_guess(last_letter)
        else:
            nr_of_guesses = self.current_round.nr_of_guesses()
            if  nr_of_guesses == self.current_round.nr_of_wrong_guesses:
                self._filter_wrong_guess_from_cache(last_letter, nr_of_guesses)
            else:
                self._filter_for_wrong_guess(last_letter)
        self.current_freq = hm.LetterFrequency(self.current_list)

    def _filter_wrong_guess_from_cache(self, last_letter, nr_of_guesses):
        if self.current_round.size not in self.word_list_cache:
            self.word_list_cache[self.current_round.size] = dict()
        if nr_of_guesses not in self.word_list_cache[self.current_round.size]:
            self.word_list_cache[self.current_round.size] = dict()
            self._filter_for_wrong_guess(last_letter)
            self.word_list_cache[self.current_round.size][nr_of_guesses] = self.current_list
        else:
            self.current_list = self.word_list_cache[self.current_round.size][nr_of_guesses]

    def _filter_for_correct_guess(self, last_letter):
        pattern = self.current_round.get_pattern()

        known_index:list[int] = list()
        unknown_index:list[int] = list()
        for i,letter in enumerate(pattern):
            if letter == last_letter:
                known_index.append(i)
            if letter == '.':
                unknown_index.append(i)

        result:list[str] = list()

        for word in self.current_list:
            skip = False
            for index in known_index:
                if word[index] != last_letter:
                    skip = True
                    break
            if skip:
                continue
            
            for index in unknown_index:
                if word[index] == last_letter:
                    skip = True
                    break
            if skip:
                continue

            result.append(word)

        self.current_list = result

    def _filter_for_wrong_guess(self, last_letter):
        result:list[str] = list()
        for word in self.current_list:
            if last_letter not in set(word):
                result.append(word)
        self.current_list = result

    def get_letter_frequency(self):
        return self.current_freq

    def get_next_guess(self)->str:
        return "a"

    def guess_next(self):
        next = self.get_next_guess()
        result = self.current_round.guess_letter(next)
        self.update_current_wordlist(next,result)
        return next, result

class HangManStrategyFreq(HangManStrategy):

    def __init__(self,wordlist:hm.WordList):
        super().__init__(wordlist)

    def get_next_guess(self)->str:
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

    def get_next_guess(self)->str:
        if self.current_round.is_ready():
            raise ValueError("Round is ready, nothing to guess")
        words = self.current_list
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