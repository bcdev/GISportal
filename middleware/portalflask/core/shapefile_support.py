import os

import shapefile as sf
from beampy import jpy
import numpy as np


def get_shape(shapefile_name, shape_name):
    shapefile = sf.Reader('/home/thomass/temp/' + shapefile_name) # todo replace hard-coded dir
    record = get_record(shape_name, shapefile)
    return get_shape_for_record(record)


def get_shape_names(shapefile_name):
    # todo - replace hard-coded path
    if not os.path.exists('/home/thomass/temp/' + shapefile_name):
        return None
    shapefile = sf.Reader('/home/thomass/temp/' + shapefile_name)
    index = get_name_index(shapefile.fields) - 1 # '- 1' because fields count a deletion flag, which is not present in records
    shape_names = []
    for shape_record in shapefile.shapeRecords():
        shape_names.append(shape_record.record[index])
    return shape_names


def get_bounding_box(shapefile_name, shape_name):
    # todo - replace hard-coded path
    if not os.path.exists('/home/thomass/temp/' + shapefile_name):
        return None
    shapefile = sf.Reader('/home/thomass/temp/' + shapefile_name)
    record = get_record(shape_name, shapefile)
    shape_bbox = record.shape.bbox
    result_bbox = ''
    for i, component in enumerate(shape_bbox):
        result_bbox += str(component)
        if i < len(shape_bbox) - 1:
            result_bbox += ','

    return result_bbox


def get_shape_geometry(shapefile_name, shape_name):
    if not os.path.exists('/home/thomass/temp/' + shapefile_name):
        return None
    shapefile = sf.Reader('/home/thomass/temp/' + shapefile_name)
    name_index = get_name_index(shapefile.fields) - 1

    for index, shape_record in enumerate(shapefile.shapeRecords()):
        if shape_record.record[name_index] == shape_name:
            break

    points = np.array(shape_record.shape.points).tolist()
    parts = shape_record.shape.parts

    shape = []
    start_index = 0

    for index, part in enumerate(parts):
        subshape = []
        end_index = len(points) if index == len(parts) - 1 else parts[index + 1]

        for x in range(start_index, end_index):
            subshape.append(points[x])

        shape.append(subshape)
        start_index = end_index

    return shape


def get_name_index(fields):
    for index, field in enumerate(fields):
        identifier_index = 0
        if field[identifier_index].lower() == 'name':  # indexing is correct, don't worry
            return index
    print('Warning: cannot find name column. Falling back to column \'' + str(fields[1]) + '\'')
    return 1


def get_record(shape_name, shapefile):
    index = get_name_index(shapefile.fields) - 1 # '- 1' because fields count a deletion flag, which is not present in records
    records = shapefile.shapeRecords()
    for rec in records:
        if rec.record[index] == shape_name:
            return rec
    raise ValueError('Cannot find record with name \'' + shape_name + '\'')


def get_shape_for_record(record):
    GeometryCollectionShape = jpy.get_type('com.vividsolutions.jts.awt.GeometryCollectionShape')
    GeneralPath = jpy.get_type('java.awt.geom.GeneralPath')
    shape = GeometryCollectionShape()
    start_index = 1
    for point_count in record.shape.parts[1:]:
        end_index = start_index + point_count
        path = GeneralPath()
        start_point = record.shape.points[0]
        path.moveTo(start_point[0], start_point[1])
        for point in record.shape.points[start_index:end_index]:
            # lon lat
            path.lineTo(point[0], point[1])
        path.closePath()
        shape.add(path)
        start_index = end_index

    return shape


def create_mask(shapefile_name, shape_name, product):
    FeatureUtils = jpy.get_type('org.esa.beam.util.FeatureUtils')
    File = jpy.get_type('java.io.File')
    Util = jpy.get_type('org.esa.beam.statistics.output.Util')
    DefaultFeatureCollection = jpy.get_type('org.geotools.feature.DefaultFeatureCollection')
    VectorDataNode = jpy.get_type('org.esa.beam.framework.datamodel.VectorDataNode')
    ProgressMonitor = jpy.get_type('com.bc.ceres.core.ProgressMonitor')
    Color = jpy.get_type('java.awt.Color')

    shapefile_path = '/home/thomass/temp/' + shapefile_name
    shapefile = File(shapefile_path)
    features = FeatureUtils.loadFeatureCollectionFromShapefile(shapefile)
    feature_iterator = features.features()
    while feature_iterator.hasNext():
        simple_feature = feature_iterator.next()
        name = Util.getFeatureName(simple_feature)
        if name == shape_name:
            break

    feature_iterator.close()
    fc = DefaultFeatureCollection(simple_feature.getIdentifier().getID(), simple_feature.getType())
    fc.add(simple_feature)

    product_features = FeatureUtils.clipFeatureCollectionToProductBounds(fc, product, None, ProgressMonitor.NULL)

    vdn = VectorDataNode(shape_name, product_features)
    product.getVectorDataGroup().add(vdn)
    return product.addMask('valid', vdn, 'desc', Color.black, 0.0)