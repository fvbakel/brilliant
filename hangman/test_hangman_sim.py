import unittest
import hangman      as hm
import hangman_sim  as sim

class TestHangManStrategy(unittest.TestCase):

    def test_get_available_words(self):
        word_list= hm.WordList()
        word_list.read_wordlist()
        round = hm.GameRound("lol")
        strategy = sim.HangManStrategy(word_list)
        strategy.set_current_round(round)
        all = strategy.current_list
        self.assertGreater(len(all),10)
        self.assertTrue('lol' in all)
        self.assertTrue('aap' in all)
        letter = 'a'
        result = round.guess_letter(letter)
        strategy.update_current_wordlist(letter,result)

        after_a = strategy.current_list
        self.assertFalse('aap' in after_a)

    def test_guessing(self):
        word_list= hm.WordList()
        word_list.read_wordlist()
        round = hm.GameRound("woord")
        strategy = sim.HangManStrategy(word_list)
        strategy.set_current_round(round)
        
        all = strategy.current_list
        self.assertGreater(len(all),100)

        letter = "w"
        is_found = round.guess_letter(letter)
        strategy.update_current_wordlist(letter,is_found)
        w_all = strategy.current_list
        self.assertGreater(len(all),len(w_all))

        letter = "o"
        is_found = round.guess_letter(letter)
        strategy.update_current_wordlist(letter,is_found)
        wo_all = strategy.current_list
        self.assertGreater(len(w_all),len(wo_all))

        letter = "r"
        is_found = round.guess_letter(letter)
        strategy.update_current_wordlist(letter,is_found)

        letter = "d"
        is_found = round.guess_letter(letter)
        strategy.update_current_wordlist(letter,is_found)

        one = strategy.current_list
        self.assertEqual(len(one),1)
        self.assertEqual(one[0],"woord")

    def test_get_letter_frequency(self):
        word_list= hm.WordList()
        word_list.read_wordlist()
        round = hm.GameRound("woord")
        strategy = sim.HangManStrategy(word_list)
        strategy.set_current_round(round)
        freq = strategy.get_letter_frequency()
        print(freq)
        print(freq.order_by_frequency())
        self.assertGreater(len(freq.stats),0)

    def test_HangManStrategyFreq(self):
        word_list= hm.WordList()
        word_list.read_wordlist()
        round = hm.GameRound("woord")
        strategy = sim.HangManStrategyFreq(word_list)
        strategy.set_current_round(round)

        next,result = strategy.guess_next()
        self.assertEqual(next,"e")

        next,result = strategy.guess_next()
        self.assertEqual(next,"a")

        next,result = strategy.guess_next()
        self.assertEqual(next,"o")

        next,result = strategy.guess_next()
        self.assertEqual(next,"r")

        next,result = strategy.guess_next()
        self.assertEqual(next,"d")

        next,result = strategy.guess_next()
        self.assertEqual(next,"b")

        next,result = strategy.guess_next()
        self.assertEqual(next,"k")

        next,result = strategy.guess_next()
        self.assertEqual(next,"m")

        next,result = strategy.guess_next()
        self.assertEqual(next,"n")

        next,result = strategy.guess_next()
        self.assertEqual(next,"v")

        next,result = strategy.guess_next()
        self.assertEqual(next,"w")

        with self.assertRaises(ValueError):
            next,result = strategy.guess_next()
