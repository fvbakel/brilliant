from basegrid.route import *
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

        first = route.pop(0)
        self.assertEqual(route.length,1,"After pop(0) Route has length 1")
        self.assertEqual(first,start,"Pop(0) returns start")

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

    def test_get_sub_route(self):
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

        sub_route = route.get_sub_route(test_positions[0][0],test_positions[4][4])
        self.assertIsNone(sub_route,"Sub route 0-0 -> 4,4 is not possible")

        sub_route = route.get_sub_route(test_positions[0][0],test_positions[1][3])
        logging.debug(f"Sub route 0-0 -> 1-3 is: {str(sub_route)}")
        self.assertIsNotNone(sub_route,"Sub route 0-0 -> 1,3 is possible")
        if not sub_route is None:
            self.assertEqual(sub_route.start,test_positions[0][0],"Sub route 0-0 -> 1,3 starts with 0-0")
            self.assertEqual(sub_route.end,test_positions[1][3],"Sub route 0-0 -> 1,3 ends with 1-3")

        sub_route = route.get_sub_route(test_positions[1][3],test_positions[1][0])
        logging.debug(f"Sub route 1-3 -> 1-0 is: {str(sub_route)}")
        self.assertIsNotNone(sub_route,"Sub route 1-3 -> 1-0 is possible")
        if not sub_route is None:
            self.assertEqual(sub_route.start,test_positions[1][3],"Sub route 1-3 -> 1-0 starts with 1-3")
            self.assertEqual(sub_route.end,test_positions[1][0],"Sub route 1-3 -> 1-0 ends with 1-0")
    
    def test_route_valid(self):
        test_positions = self.get_test_positions(nr=5)
        route = Route()
        
        route.append(test_positions[0][0])
        route.append(test_positions[1][0])
        route.append(test_positions[2][0])
        route.append(test_positions[2][1])
        self.assertTrue(route.is_valid())

        route.append(test_positions[3][3])
        self.assertFalse(route.is_valid())

    def test_route_add(self):
        test_positions = self.get_test_positions(nr=5)
        route_1 = Route()
        route_2 = Route()
        self.assertTrue(route_1.add_route(route_2),"Two empty routes can be added")

        route_2.append(test_positions[0][0])
        self.assertTrue(route_1.add_route(route_2),"None empty route can be added to empty route")

        route_1 = Route()
        route_2 = Route()
        route_1.append(test_positions[0][0])
        self.assertTrue(route_1.add_route(route_2),"Empty route can be added to non empty route")

        route_1 = Route()
        route_2 = Route()
        route_1.append(test_positions[0][0])
        route_1.append(test_positions[1][0])
        route_1.append(test_positions[1][1])
        route_2.append(test_positions[1][1])
        route_2.append(test_positions[1][2])
        route_2.append(test_positions[1][3])
        self.assertTrue(route_1.add_route(route_2),"Route can be added is end 1 is start 2")

        route_1 = Route()
        route_2 = Route()

        route_1.append(test_positions[1][1])
        route_1.append(test_positions[1][0])
        route_1.append(test_positions[0][0])
        
        route_2.append(test_positions[1][3])
        route_2.append(test_positions[1][2])
        route_2.append(test_positions[1][1])
        self.assertTrue(route_1.add_route(route_2),"Route can be added is start 1 is end 2")

        route_1 = Route()
        route_2 = Route()
        route_1.append(test_positions[0][0])
        route_1.append(test_positions[1][0])
        route_1.append(test_positions[1][1])
        route_2.append(test_positions[1][2])
        route_2.append(test_positions[1][3])
        self.assertTrue(route_1.add_route(route_2),"Route can be added when it starts with a neighbor")

        route_1 = Route()
        route_2 = Route()
        route_1.append(test_positions[1][1])
        route_1.append(test_positions[1][0])
        route_1.append(test_positions[0][0])
        route_2.append(test_positions[1][3])
        route_2.append(test_positions[1][2])
        self.assertTrue(route_1.add_route(route_2),"Route can be added when it ends with a neighbor")


    def test_get_route_to_route(self):
        test_positions = self.get_test_positions(nr=5)
        route_1 = Route()
        route_2 = Route()

        self.assertIsNone(
            route_1.get_route_to_route(
                test_positions[0][0],route_2
            ),
            "Two empty routes result in no route"
        )
        
        route_1.append(test_positions[0][0])
        route_1.append(test_positions[1][0])
        route_1.append(test_positions[1][1])
        route_1.append(test_positions[1][2])
        route_1.append(test_positions[1][3])

        route_2.append(test_positions[2][0])
        route_2.append(test_positions[2][1])
        route_2.append(test_positions[2][2])

        self.assertIsNone(
            route_1.get_route_to_route(
                test_positions[0][0],route_2
            ),
            "Two disconnected routes result in no route"
        )

        route_1.append(test_positions[0][0])
        route_1.append(test_positions[1][0])
        route_1.append(test_positions[1][1])
        route_1.append(test_positions[1][2])
        route_1.append(test_positions[1][3])

        route_2.append(test_positions[1][1])
        route_2.append(test_positions[2][1])
        route_2.append(test_positions[2][2])
        route_2.append(test_positions[3][2])

        new_route = route_1.get_route_to_route(
            test_positions[0][0],
            route_2
        )

        self.assertIsNotNone(
            new_route,
            "New route can be found"
        )
        if not new_route is None:
            self.assertEquals(
                new_route.length,
                6,
                "New route is expected 6 long"
            )

        new_route = route_1.get_route_to_route(
            test_positions[1][3],
            route_2
        )

        self.assertIsNotNone(
            new_route,
            "New route can be found backwards"
        )
        if not new_route is None:
            self.assertEquals(
                new_route.length,
                7,
                "New route is expected 7 long"
            )

    def test_compare_and_copy_route(self):
        test_positions = self.get_test_positions(nr=5)
        route_1 = Route()
        route_2 = Route()

        self.assertEqual(route_1,route_2,"Two empty routes are equal")

        route_1 = Route()
        route_2 = Route()
        route_1.append(test_positions[0][0])
        self.assertNotEqual(route_1,route_2,"Empty routes is not equal to non-empty route")
        self.assertNotEqual(route_2,None,"Empty routes is not equal to None ")
        self.assertNotEqual(route_1,None,"Non-empty routes is not equal to None ")

        route_1 = Route()
        route_2 = Route()
        route_1.append(test_positions[0][0])
        route_1.append(test_positions[1][0])
        route_1.append(test_positions[2][0])

        route_2.append(test_positions[0][0])
        route_2.append(test_positions[1][0])
        route_2.append(test_positions[2][0])

        self.assertEqual(route_1,route_2,"Same positions in same order is equal")
        route_2.reverse()
        self.assertNotEqual(route_1,route_2,"Same positions in reverse order is not equal")

        route_2 = Route()
        route_2.append(test_positions[0][0])
        route_2.append(test_positions[1][0])
        route_2.append(test_positions[2][0])
        route_2.append(test_positions[3][0])
        self.assertNotEqual(route_1,route_2,"One more position is not equal")

        route_2 = route_1.copy()
        self.assertEqual(route_1,route_2,"Copies are equal")

        route_2.pop()
        self.assertNotEqual(route_1,route_2,"After a pop of one copies are not equal")



