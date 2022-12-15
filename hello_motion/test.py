import unittest
from motion import *

class TestDimensionScale(unittest.TestCase):

    def test_converts(self):
        dim_scale = DimensionScale((10,20),(100,100))
        self.assertEqual(dim_scale.result_dim,(100,50))
        self.assertEqual(dim_scale.scale_org_to_result,(10,2.5))

        point_1 = (20,5)
        point_1_org = dim_scale.res_to_org(point_1)
        self.assertEqual(point_1_org,(2,2))

if __name__ == "__main__":
    unittest.main()