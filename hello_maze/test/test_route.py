from maze.route import *
from test.test_config import *
import logging
import unittest

class TestRoute(unittest.TestCase):

    def get_test_positions(self,nr:int=5):
        test_positions:list[list[Position]] = []
        for col in range(0,nr):
            test_positions.append([])
            for row in range(0,nr):
                test_positions[col].append(Position(col,row))
        
        return test_positions

    def test_route_basics(self):
        route = Route()

        self.assertEqual(route.length,0,"At the start the route has length 0")
        self.assertIsNone(route.start,"empty route has no start")
        self.assertIsNone(route.end,"empty route has no end")

        start = Position(0,0)
        route.append(start)
        self.assertEqual(route.length,1,"Route has length 1")
        self.assertEqual(route.start,start,"Route starts with start")
        self.assertEqual(route.end,start,"End is start with one position")

        next = Position(1,0)
        route.append(next)
        self.assertEqual(route.length,2,"Route has length 2")
        self.assertEqual(route.start,start,"Route starts with start")
        self.assertEqual(route.end,next,"Route ends with last")

        next = Position(2,0)
        route.append(next)
        self.assertEqual(route.length,3,"Route has length 3")
        self.assertEqual(route.start,start,"Route starts with start")
        self.assertEqual(route.end,next,"Route ends with last")

        self.assertTrue(route.has_position(start),"Start is a position")
        self.assertFalse(route.has_position(Position(4,0)),"4-0 is not in route")

        route.optimize()
        self.assertEqual(route.length,3,"After optimize still Route has length 3")
        self.assertEqual(route.start,start,"After optimize still Route starts with start")
        self.assertEqual(route.end,next,"After optimize still Route ends with last")

        cur_path = route.path
        route.reverse()
        self.assertEqual(route.length,3,"After reverse still Route has length 3")
        self.assertEqual(route.start,next,"After reverse still Route starts with last")
        self.assertEqual(route.end,start,"After reverse still Route ends with start")
        print(cur_path)

        route.reverse()
        last = route.pop()
        self.assertEqual(route.length,2,"After pop Route has length 2")
        self.assertEqual(last,next,"Pop returns end")

        route.reset_path()
        self.assertEqual(route.length,0,"After reset the route has length 0")

    def test_optimize(self):
        test_positions = self.get_test_positions(nr=5)
        route = Route()
        
        route.append(test_positions[0][0])
        route.append(test_positions[1][0])
        route.append(test_positions[2][0])
        route.append(test_positions[3][0])
        route.append(test_positions[2][0])
        route.append(test_positions[1][0])
        route.append(test_positions[1][1])
        route.append(test_positions[1][2])
        route.append(test_positions[1][2])
        route.append(test_positions[1][2])
        route.append(test_positions[1][3])
        route.append(test_positions[1][4])
        route.append(test_positions[1][3])
        route.append(test_positions[1][2])

        route.optimize()
        logging.debug(f"Route after optimize: {str(route)}")

        self.assertEqual(route.end,test_positions[1][2],"After optimize still Route ends with 1-2")
        self.assertEqual(route.start,test_positions[0][0],"After optimize still Route starts with 0-0")
        self.assertEqual(route.length,4,"After optimize Route has length 4")

