import hangman as hm
from hangman_pics import HANGMANPICS

class HangmanGameTextUI:

    def __init__(self):
        self.wordlist = hm.WordList()
        self.wordlist.read_wordlist()
        word = self.wordlist.random_word()
        self.round = hm.GameRound(word)
        self.state = 0
        self.alive = True
        self.max_wrong_guesses = len(HANGMANPICS)-1

    def update_state(self):
        if self.alive:
            self.state = self.round.nr_of_wrong_guesses
            if self.state == self.max_wrong_guesses:
                self.alive = False

    def update_display(self):
        self.clear_screen()
        print("Hangman")
        print("\n")
        print(HANGMANPICS[self.state])
        print("\n")
        print("Letters guessed:")
        print(", ".join(self.round.guessed_ordered))
        print("\n")
        print(self.round.get_word_view())
        print("\n")

    def clear_screen(self):
        print(chr(27) + "[2J")

    def ask_next(self):
        while True:
            user_input = input('Enter a single letter: ')

            if len(user_input) == 1 and user_input.isalpha():
                return user_input.lower()
            else:
                print('Enter a single letter to continue.')
                continue

    def run(self):
        while self.alive:
            self.update_state()
            self.update_display()
            if self.alive:
                if not self.round.is_ready():
                    self.round.guess_letter(self.ask_next())
                else:
                    print(f"You won!")
                    break
            else:
                print(f"You are dead the correct word was: {self.round.solution}")

def main():
    ui = HangmanGameTextUI()
    ui.run()

if __name__ == "__main__":
    main()