import os
import unittest

from numpy.testing import assert_array_equal
import numpy as np

import beampy

import portalflask.core.graph_support as graph_support


class GraphSupportTest(unittest.TestCase):

    def setUp(self):
        test_product_path = os.path.join(os.path.dirname(__file__), 'test.nc')
        self.product = beampy.ProductIO.readProduct(test_product_path)


    def test_get_coordinate_variable(self):
        time_var = graph_support.get_coordinate_variable(self.product, 'Time')
        assert_array_equal(np.array([1.63965594E9], dtype=np.float32), time_var)

        none_var = graph_support.get_coordinate_variable(self.product, 'Kaputtnick')
        self.assertIsNone(none_var)


    def test_get_axis_units(self):
        self.assertEqual('meters', graph_support.get_axis_units(self.product, 'depth'))
        self.assertEqual('degrees_north', graph_support.get_axis_units(self.product, 'latitude'))
        self.assertIsNone(graph_support.get_axis_units(self.product, 'Godot'))


    def test_get_depth(self):
        self.assertAlmostEqual(1.4721018, graph_support.get_depth(self.product))

if __name__ == '__main__':
    unittest.main()