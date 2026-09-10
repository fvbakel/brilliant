import unittest
import hangman      as hm
import hangman_sim  as sim

class TestHangManStrategy(unittest.TestCase):

    def test_get_available_words(self):
        word_list= hm.WordList()
        word_list.read_wordlist()
        round = hm.GameRound("woord")
        strategy = sim.HangManStrategy(word_list)
        all = strategy.get_available_words(round)
        self.assertGreater(len(all),100)

        round.guess_letter("w")
        w_all = strategy.get_available_words(round)
        self.assertGreater(len(all),len(w_all))

        round.guess_letter("o")
        wo_all = strategy.get_available_words(round)
        self.assertGreater(len(w_all),len(wo_all))

        round.guess_letter("r")
        round.guess_letter("d")

        one = strategy.get_available_words(round)
        self.assertEqual(len(one),1)
        self.assertEqual(one[0],"woord")

    def test_get_letter_frequency(self):
        word_list= hm.WordList()
        word_list.read_wordlist()
        round = hm.GameRound("woord")
        strategy = sim.HangManStrategy(word_list)
        freq = strategy.get_letter_frequency(round)
        print(freq)
        print(freq.order_by_frequency())
        self.assertGreater(len(freq.stats),0)

    def test_HangManStrategyFreq(self):
        word_list= hm.WordList()
        word_list.read_wordlist()
        round = hm.GameRound("woord")
        strategy = sim.HangManStrategyFreq(word_list)
        next = strategy.guess_next(round)
        self.assertEqual(next,"e")
        round.guess_letter(next)

        next = strategy.guess_next(round)
        self.assertEqual(next,"a")
        round.guess_letter(next)

        next = strategy.guess_next(round)
        self.assertEqual(next,"o")
        round.guess_letter(next)

        next = strategy.guess_next(round)
        self.assertEqual(next,"r")
        round.guess_letter(next)

        next = strategy.guess_next(round)
        self.assertEqual(next,"d")
        round.guess_letter(next)

        next = strategy.guess_next(round)
        self.assertEqual(next,"b")
        round.guess_letter(next)

        next = strategy.guess_next(round)
        self.assertEqual(next,"k")
        round.guess_letter(next)

        next = strategy.guess_next(round)
        self.assertEqual(next,"m")
        round.guess_letter(next)

        next = strategy.guess_next(round)
        self.assertEqual(next,"n")
        round.guess_letter(next)

        next = strategy.guess_next(round)
        self.assertEqual(next,"v")
        round.guess_letter(next)

        next = strategy.guess_next(round)
        self.assertEqual(next,"w")
        round.guess_letter(next)

        with self.assertRaises(ValueError):
            strategy.guess_next(round)
