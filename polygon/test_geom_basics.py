import unittest
import geom_basics as gb

class TestGeomBasics(unittest.TestCase):

    def test_distance(self):
        p1 = (0,0)
        p2 = (0,1)
        self.assertEqual(gb.distance(p1,p2),1)

        p1 = (5, 6)
        p2 = (5, 4)
        self.assertEqual(gb.distance(p1,p2),2)

        p1 = (5, 6)
        p2 = (5, 6)
        self.assertEqual(gb.distance(p1,p2),0)

    def test_is_on_circle(self):
        center = (0,0)
        radius = 1
        p = (0,1)
        self.assertTrue(gb.is_on_circle(center,radius,p))

        center = (0,0)
        radius = 1
        p = (0,2)
        self.assertFalse(gb.is_on_circle(center,radius,p))

        center = (0,0)
        radius = 1
        p = (0.5,0)
        self.assertFalse(gb.is_on_circle(center,radius,p))


    def test_is_in_circle(self):
        center = (0,0)
        radius = 1
        p = (0,1)
        self.assertTrue(gb.is_in_circle(center,radius,p))

        center = (0,0)
        radius = 1
        p = (0,2)
        self.assertFalse(gb.is_in_circle(center,radius,p))

        center = (0,0)
        radius = 1
        p = (0.5,0)
        self.assertTrue(gb.is_in_circle(center,radius,p))

    def test_get_angle_counter_clockwise(self):
        self.assertEqual(gb.get_angle_counter_clockwise(( 1, 0)),  0)
        self.assertEqual(gb.get_angle_counter_clockwise(( 0, 1)), 90)
        self.assertEqual(gb.get_angle_counter_clockwise((-1, 0)), 180)
        self.assertEqual(gb.get_angle_counter_clockwise(( 0,-1)), 270)

        self.assertEqual(gb.get_angle_counter_clockwise(( 0, 0)),  0)

        self.assertEqual(gb.get_angle_counter_clockwise(( 1, 1)),  45)
        self.assertEqual(gb.get_angle_counter_clockwise((-1, 1)), 135)
        self.assertEqual(gb.get_angle_counter_clockwise((-1,-1)), 225)
        self.assertEqual(gb.get_angle_counter_clockwise(( 1,-1)), 315)

        self.assertEqual(round(gb.get_angle_counter_clockwise(( 4, 3))),  37)
        self.assertEqual(round(gb.get_angle_counter_clockwise(( -3, 4))),  37+90)
        self.assertEqual(round(gb.get_angle_counter_clockwise(( -4, 3))),  180-37)
        self.assertEqual(round(gb.get_angle_counter_clockwise(( -4, -3))),  37+180)
        self.assertEqual(round(gb.get_angle_counter_clockwise(( -3, -4))),  270-37)
        self.assertEqual(round(gb.get_angle_counter_clockwise(( 3, -4))),   270+37)
        self.assertEqual(round(gb.get_angle_counter_clockwise(( 4, -3))),   360-37)

def test_caculate_angle_counter_clockwise(self):
    p1 = (0,0)
    p2 = (1,0)
    p3 = (1,1)
    self.assertEqual(gb.caculate_angle_counter_clockwise(p1,p2,p3),45)

    p1 = (0,0)
    p2 = (1,0)
    p3 = (-1,-1)
    self.assertEqual(gb.caculate_angle_counter_clockwise(p1,p2,p3),360-45)

    p1 = (0,0)
    p2 = (1,0)
    p3 = (-1,-1)
    self.assertEqual(gb.caculate_angle_counter_clockwise(p1,p2,p3),360-45)




