import unittest
import difflib

class TestDiffLibBytes(unittest.TestCase):

    def test_bytes_similarity(self):

        ratio = difflib.SequenceMatcher(a="abc",b="abc").ratio()
        print("Identical ratio abc vs abc:", ratio)

        four_bytes_1 = bytes.fromhex("FF FF FF FF")
        four_bytes_2 = bytes.fromhex("FF FF FF FF")
        ratio = difflib.SequenceMatcher(a=four_bytes_1,b=four_bytes_2).ratio()
        print("Identical ratio:", ratio)

        four_bytes_2 = bytes.fromhex("EF FF FF FF")
        ratio = difflib.SequenceMatcher(a=four_bytes_1,b=four_bytes_2).ratio()
        print("Identical ratio:", ratio)

        four_bytes_2 = bytes.fromhex("0F FF FF FF")
        ratio = difflib.SequenceMatcher(a=four_bytes_1,b=four_bytes_2).ratio()
        print("Identical ratio:", ratio)

        list_1 = [
            bytes.fromhex("FF FF FF FF"),
            bytes.fromhex("FF FF FF FF"),
            bytes.fromhex("FF FF FF FF")
        ]
        list_2 = [
            bytes.fromhex("FF FF FF FF"),
            bytes.fromhex("FF FF FF FF"),
            bytes.fromhex("0F FF FF FF")
        ]
        ratio = difflib.SequenceMatcher(a=list_1,b=list_2).ratio()
        print("Identical ratio:", ratio)