from beampy import jpy
import numpy as np


def get_bounding_box(polygon):
    x = np.array(polygon)[range(0, len(polygon) - 1, 2)]
    y = np.array(polygon)[range(1, len(polygon), 2)]
    return [(np.min(x)), (np.min(y)), (np.max(x)), (np.max(y))]


def get_shape(polygon):
    GeometryFactory = jpy.get_type('com.vividsolutions.jts.geom.GeometryFactory')
    LiteShape = jpy.get_type('org.geotools.geometry.jts.LiteShape')
    Coordinate = jpy.get_type('com.vividsolutions.jts.geom.Coordinate')

    gf = GeometryFactory()
    coordinates = []

    x = np.array(polygon)[range(0, len(polygon) - 1, 2)]
    y = np.array(polygon)[range(1, len(polygon), 2)]

    for i in range(0, len(x)):
        coordinates.append(Coordinate(x[i], y[i]))
    coordinates.append(Coordinate(x[0], y[0]))

    linear_ring = gf.createLinearRing(coordinates)
    polygon = gf.createPolygon(linear_ring, None)
    return LiteShape(polygon, None, False)


def create_mask(product, polygon):
    VectorDataNode = jpy.get_type('org.esa.beam.framework.datamodel.VectorDataNode')
    Color = jpy.get_type('java.awt.Color')
    DefaultFeatureCollection = jpy.get_type('org.geotools.feature.DefaultFeatureCollection')
    SimpleFeatureTypeBuilder = jpy.get_type('org.geotools.feature.simple.SimpleFeatureTypeBuilder')
    SimpleFeatureBuilder = jpy.get_type('org.geotools.feature.simple.SimpleFeatureBuilder')
    GeometryFactory = jpy.get_type('com.vividsolutions.jts.geom.GeometryFactory')
    DefaultGeographicCRS = jpy.get_type('org.geotools.referencing.crs.DefaultGeographicCRS')

    sftb = SimpleFeatureTypeBuilder()
    sftb.setName('default_feature_type')
    sftb.setDefaultGeometry('geometry')
    sftb.add('geometry', GeometryFactory().createPolygon(None, None).getClass(), DefaultGeographicCRS.WGS84)
    sft = sftb.buildFeatureType()

    sfb = SimpleFeatureBuilder(sft)
    sfb.set('geometry', get_shape(polygon).getGeometry())
    feature = sfb.buildFeature('geom')

    fc = DefaultFeatureCollection('name', sft)
    fc.add(feature)

    vdn = VectorDataNode('vdn', fc)
    product.getVectorDataGroup().add(vdn)

    return product.addMask('valid', vdn, 'desc', Color.black, 0.0)