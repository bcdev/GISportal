import os
import unittest
import random

from numpy.testing import assert_array_equal
import numpy as np

import beampy

import portalflask.core.graph_support as graph_support
import portalflask.core.shapefile_support as shapefile_support
import portalflask.core.geometry_support as geometry_support
import portalflask.views.wcs as wcs


class PortalTests(unittest.TestCase):

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


    def test_get_bounding_box_from_wkt(self):
        bb = geometry_support.get_bounding_box('POLYGON ((-1 2, 1.5 5, 4 1.5, 4 -1.5, 1.5 -2))')
        self.assertEqual('-1.0,-2.0,4.0,5.0', bb)


    def test_get_shape_from_geometry(self):
        shape = geometry_support.get_shape('POLYGON ((-1 2, 1.5 5, 4 1.5, 4 -1.5, 1.5 -2, -1 2))')
        geom = shape.getGeometry()

        self.assertEqual(6, geom.getNumPoints())

        self.assertEqual(-1, geom.getCoordinates()[0].x)
        self.assertEqual(2, geom.getCoordinates()[0].y)

        self.assertEqual(1.5, geom.getCoordinates()[4].x)
        self.assertEqual(-2, geom.getCoordinates()[4].y)

        self.assertEqual(-1, geom.getCoordinates()[5].x)
        self.assertEqual(2, geom.getCoordinates()[5].y)


    def test_get_mask_rectangular(self):
        test_product_path = os.path.join(os.path.dirname(__file__), 'test.nc')
        product = beampy.ProductIO.readProduct(test_product_path)
        geometry = 'POLYGON ((-10 45, -10 40, 10 40, 10 45, -10 45))'
        mask = geometry_support.create_mask(product, geometry)
        mask_pixel = np.ones(1, np.int32)

        self.assertIsNotNone(mask)

        for i in range(1000):
            x = random.randrange(product.getSceneRasterWidth())  # any x
            y = random.randrange(30)  # index of first line that is not masked
            mask.readPixels(x, y, 1, 1, mask_pixel)
            self.assertEqual(255, mask_pixel[0])

        for i in range(1000):
            x = random.randrange(product.getSceneRasterWidth())  # any x
            y = random.randrange(31, product.getSceneRasterHeight() - 1)
            mask.readPixels(x, y, 1, 1, mask_pixel)
            self.assertEqual(0, mask_pixel[0])


    def test_get_mask_polygonal(self):
        test_product_path = os.path.join(os.path.dirname(__file__), 'test.nc')
        product = beampy.ProductIO.readProduct(test_product_path)
        polygon = 'POLYGON ((-3.53125 40.28125, -0.78125 42.53125, 1.59375 39.15625, -3.53125 40.28125))'
        mask = geometry_support.create_mask(product, polygon)
        self.assertIsNotNone(mask)

        mask_pixels = np.zeros(product.getSceneRasterWidth(), np.int32)

        for y in range(product.getSceneRasterHeight()):
            mask.readPixels(0, y, product.getSceneRasterWidth(), 1, mask_pixels)
            if y < 10 or y > 37:
                self.assertEqual(0, np.sum(mask_pixels))
            self.assertEqual(0, np.sum(mask_pixels[:12]))
            self.assertEqual(0, np.sum(mask_pixels[54:]))

            if y == 20:
                self.assertEqual(0, mask_pixels[22])
                for x in range(23, 43):
                    self.assertEqual(255, mask_pixels[x])
                self.assertEqual(0, np.sum(mask_pixels[43:]))


if __name__ == '__main__':
    unittest.main()