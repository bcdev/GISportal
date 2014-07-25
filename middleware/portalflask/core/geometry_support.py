from beampy import jpy
from pygeoif import geometry


def get_bounding_box(wkt):
    geom = geometry.from_wkt(wkt)
    minx = geom.bounds[0]
    miny = geom.bounds[1]
    maxx = geom.bounds[2]
    maxy = geom.bounds[3]
    return str(minx) + ',' + str(miny) + ',' + str(maxx) + ',' + str(maxy)


def get_shape(wkt):
    LiteShape = jpy.get_type('org.geotools.geometry.jts.LiteShape')
    WKTReader = jpy.get_type('com.vividsolutions.jts.io.WKTReader')

    wktReader = WKTReader()
    geom = wktReader.read(wkt)

    return LiteShape(geom, None, False)


def create_mask(product, wkt):
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
    sfb.set('geometry', get_shape(wkt).getGeometry())
    feature = sfb.buildFeature('geom')

    fc = DefaultFeatureCollection('name', sft)
    fc.add(feature)

    vdn = VectorDataNode('vdn', fc)
    product.getVectorDataGroup().add(vdn)

    return product.addMask('valid', vdn, 'desc', Color.black, 0.0)