import unittest

import portalflask.core.shapefile_support as shapefile_support

class ShapefileSupportTest(unittest.TestCase):


    def test_get_shape_geometry(self):
        shape = shapefile_support.get_shape_geometry('countries.shp', 'Afghanistan')
        self.assertEqual(list, type(shape))
        self.assertEqual(1, len(shape))

        self.assertEqual(list, type(shape[0]))
        self.assertEqual(list, type(shape[0][0]))
        self.assertEqual([65.6272964477539, 37.33319854736328], shape[0][0])


    def test_get_shape_geometry_2(self):
        shape = shapefile_support.get_shape_geometry('countries.shp', 'Spain')
        self.assertEqual(list, type(shape))
        self.assertEqual(9, len(shape))

        first_part = shape[0]
        first_point = first_part[0]
        self.assertEqual(list, type(first_point))
        self.assertEqual([-14.333060264587402, 28.0444393157959], first_point)


        last_part = shape[8]
        last_point = last_part[321]
        self.assertEqual(list, type(last_point))
        self.assertEqual([1.4352469444274902, 42.59714889526367], last_point)



if __name__ == '__main__':
    unittest.main()