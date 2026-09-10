from abc import abstractmethod

import hangman as hm

class HangmanSim():

    def __init__(self):
        self.wordlist = hm.WordList()
        self.wordlist.read_wordlist()    

    def one_word(self,word:str):
        word = self.wordlist.random_word()
        round = hm.GameRound(word)

        pass

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
    pass

if __name__ == "__main__":
    main()