import unittest
import os
import random
import numpy as np

import beampy

import portalflask.core.polygon_support as polygon_support

class PolygonSupportTest(unittest.TestCase):

    def test_get_bounding_box(self):
        bb = polygon_support.get_bounding_box([-1, 2, 1.5, 5, 4, 1.5, 4, -1.5, 1.5, -2])
        self.assertEqual(4, len(bb))
        self.assertEqual([-1, -2, 4, 5], bb)


    def test_get_shape(self):
        shape = polygon_support.get_shape([-1, 2, 1.5, 5, 4, 1.5, 4, -1.5, 1.5, -2])
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
        polygon = [-10, 45, -10, 40, 10, 40, 10, 45]
        mask = polygon_support.create_mask(product, polygon)
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
        polygon = [-3.53125, 40.28125, -0.78125, 42.53125, 1.59375, 39.15625]
        mask = polygon_support.create_mask(product, polygon)
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