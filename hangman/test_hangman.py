import unittest
import hangman as hm

class TestGameRound(unittest.TestCase):

    def test_basics(self):
        round = hm.GameRound("woord")
        self.assertFalse(round.guess_word("wrong"))
        self.assertTrue(round.guess_word("woord"))
        self.assertFalse(round.is_ready())
        self.assertEqual(round.get_word_view(),"_ _ _ _ _")
        self.assertFalse(round.guess_letter("a"))
        self.assertTrue(round.guess_letter("o"))
        self.assertEqual(round.get_word_view(),"_ o o _ _")
        self.assertTrue(round.guess_letter("w"))
        self.assertTrue(round.guess_letter("r"))
        self.assertTrue(round.guess_letter("d"))
        self.assertEqual(round.get_word_view(),"w o o r d")
        self.assertTrue(round.is_ready())

class TestWordList(unittest.TestCase):

    def test_basics(self):
        word_list= hm.WordList()
        word_list.read_wordlist()
        word = word_list.random_word(3)
        print(word)
        self.assertEqual(len(word),3)