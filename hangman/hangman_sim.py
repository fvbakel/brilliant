import hangman as hm
from argparse import ArgumentParser
from pathlib import Path

class HangmanSim():

    def __init__(self):
        self.wordlist = hm.WordList()
        self.wordlist.read_wordlist()
        self.min_lenght = 3
        self.strategy = HangManStrategyFreq(self.wordlist) 

    def solve_word(self,word:str,verbose=False):
        round = hm.GameRound(word)
        
        while not round.is_ready():
            next = self.strategy.guess_next(round)
            round.guess_letter(next)
            if verbose:
                print(f"{next} : {round.get_word_view()}")
        return round

    def solve_all(self):
        input_file = Path(self.wordlist.file)
        output_file = f"{input_file.parent}/{input_file.stem}_sim.txt"
        print(f"Writing output file: {output_file}")
        with open(output_file, "w") as output: 
            for nr_of_letters,words in self.wordlist.words.items():
                if nr_of_letters < self.min_lenght:
                    continue
                print(f"Processing {len(words)} words of lenght {nr_of_letters}")
                for word in words:
                    round = self.solve_word(word)
                    output.write(f"{word},{nr_of_letters},{round.nr_of_wrong_guesses}\n")
        print("Ready")


class HangManStrategy():

    def __init__(self,wordlist:hm.WordList):
        self.wordlist = wordlist

    def get_available_words(self,round:hm.GameRound):
        reg_ex = round.get_regular_expression()
        return list(filter(reg_ex.match,self.wordlist.words[round.size]))

    def get_letter_frequency(self,round:hm.GameRound):
        return hm.LetterFrequency(self.get_available_words(round))

    def guess_next(self,round:hm.GameRound)->str:
        return "a"

class HangManStrategyFreq(HangManStrategy):

    def __init__(self,wordlist:hm.WordList):
        super().__init__(wordlist)

    def guess_next(self,round = hm.GameRound)->str:
        if round.is_ready():
            raise ValueError("Round is ready, nothing to guess")
        freq = self.get_letter_frequency(round)
        for letter in freq.order_by_frequency():
            if letter not in round.guessed:
                return letter
        return ""

def main():
    parser = ArgumentParser(description=
            """Simulate hangman.
            """
        )
    parser.add_argument("-w","--word", help="simulate the game on a single word and output the guesses", type=str, required=False, default=None)
    args = parser.parse_args()

    sim = HangmanSim()
    if args.word is None:
        sim.solve_all()
    else:
        sim.solve_word(args.word,True)


if __name__ == "__main__":
    main()