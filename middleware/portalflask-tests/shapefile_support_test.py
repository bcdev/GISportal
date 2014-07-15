import os

import unittest
import beampy

import portalflask.core.shapefile_support as shapefile_support
from numpy.testing import assert_array_equal
import numpy as np

class ShapefileSupportTest(unittest.TestCase):

    def setUp(self):
        test_product_path = os.path.join(os.path.dirname(__file__), 'test.nc')
        self.product = beampy.ProductIO.readProduct(test_product_path)


    def test_get_coordinate_variable(self):
        time_var = shapefile_support.get_coordinate_variable(self.product, 'Time')
        assert_array_equal(np.array([1.63965594E9], dtype=np.float32), time_var)

        none_var = shapefile_support.get_coordinate_variable(self.product, 'Kaputtnick')
        self.assertIsNone(none_var)


    def test_get_axis_units(self):
        self.assertEqual('meters', shapefile_support.get_axis_units(self.product, 'depth'))
        self.assertEqual('degrees_north', shapefile_support.get_axis_units(self.product, 'latitude'))
        self.assertIsNone(shapefile_support.get_axis_units(self.product, 'Godot'))


    def test_get_depth(self):
        self.assertAlmostEqual(1.4721018, shapefile_support.get_depth(self.product))


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