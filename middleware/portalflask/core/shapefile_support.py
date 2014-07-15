import os

import beampy
import shapefile
from beampy import jpy
from netCDF4 import num2date
import numpy as np

from portalflask.views.actions import check_for_permission

@check_for_permission(['admins'])
def get_timeseries(ncfile_name, variable_name, shapefile_name, shape_name):
    sf = shapefile.Reader('/home/thomass/temp/' + shapefile_name) # todo replace hard-coded dir
    record = get_record(shape_name, sf)
    shape = get_shape(record)
    product = beampy.ProductIO.readProduct(ncfile_name)

    timeseries = {}

    times = get_coordinate_variable(product, 'Time')
    if times is None:
        raise ValueError('No time variable found')

    time_units = get_axis_units(product, 'Time')
    if time_units:
        start = (num2date(times[0], time_units, calendar='standard')).isoformat()
    else:
        start = ''.join(times[0])

    timeseries['global'] = {'time': start}

    units = get_axis_units(product, str(variable_name))
    timeseries['units'] = units

    timeseries['data'] = {}
    factory = jpy.get_type('org.esa.beam.framework.datamodel.StxFactory')().withRoiShape(shape)
    pm = jpy.get_type('com.bc.ceres.core.ProgressMonitor')

    for time_index, band in enumerate(product.getBands()):
        print (str(time_index) + ': ' + band.getName())
        if time_units:
            date = num2date(times[time_index], time_units, calendar='standard').isoformat()
        else:
            date = ''.join(times[time_index])

        stx = factory.create(band, pm.NULL)
        maximum = stx.getMaximum()
        minimum = stx.getMinimum()
        std = stx.getStandardDeviation()
        mean = stx.getMean()
        median = stx.getMedian()

        if np.isnan(maximum) or np.isnan(minimum) or np.isnan(std) or np.isnan(mean) or np.isnan(median):
            pass
        else:
            timeseries['data'][date] = {'mean': mean, 'median': median,'std': std, 'min': minimum, 'max': maximum}

    return timeseries

@check_for_permission(['admins'])
def get_shape_names(shapefile_name):
    # todo - replace hard-coded path
    if not os.path.exists('/home/thomass/temp/' + shapefile_name):
        return None
    sf = shapefile.Reader('/home/thomass/temp/' + shapefile_name)
    index = get_name_index(sf.fields) - 1 # '- 1' because fields count a deletion flag, which is not present in records
    shape_names = []
    for shape_record in sf.shapeRecords():
        shape_names.append(shape_record.record[index])
    return shape_names

@check_for_permission(['admins'])
def get_bounding_box(shapefile_name, shape_name):
    # todo - replace hard-coded path
    if not os.path.exists('/home/thomass/temp/' + shapefile_name):
        return None
    sf = shapefile.Reader('/home/thomass/temp/' + shapefile_name)
    record = get_record(shape_name, sf)
    shape_bbox = record.shape.bbox
    result_bbox = ''
    for i, component in enumerate(shape_bbox):
        result_bbox += str(component)
        if i < len(shape_bbox) - 1:
            result_bbox += ','

    return result_bbox


@check_for_permission(['admins'])
def get_shape_geometry(shapefile_name, shape_name):
    if not os.path.exists('/home/thomass/temp/' + shapefile_name):
        return None
    sf = shapefile.Reader('/home/thomass/temp/' + shapefile_name)


@check_for_permission(['admins'])
def get_band_data_as_array(ncfile_name, variable_name, shapefile_name, shape_name):
    FeatureUtils = jpy.get_type('org.esa.beam.util.FeatureUtils')
    File = jpy.get_type('java.io.File')
    Util = jpy.get_type('org.esa.beam.statistics.output.Util')
    DefaultFeatureCollection = jpy.get_type('org.geotools.feature.DefaultFeatureCollection')
    VectorDataNode = jpy.get_type('org.esa.beam.framework.datamodel.VectorDataNode')
    ProgressMonitor = jpy.get_type('com.bc.ceres.core.ProgressMonitor')
    Color = jpy.get_type('java.awt.Color')

    print('imported everything')
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

    print('reading product')
    product = beampy.ProductIO.readProduct(ncfile_name)
    product_features = FeatureUtils.clipFeatureCollectionToProductBounds(fc, product, None, ProgressMonitor.NULL)

    vdn = VectorDataNode(shape_name, product_features)
    product.getVectorDataGroup().add(vdn)
    mask = product.addMask('valid', vdn, 'desc', Color.black, 0.0)

    width = product.getSceneRasterWidth()
    height = product.getSceneRasterHeight()

    pixels = np.zeros(width, dtype=np.float32)
    mask_pixels = np.zeros(width, dtype=np.int32)
    result = []

    jpy.diag.flags = jpy.diag.F_ALL

    for band in product.getBands():
        if band.getName().startswith(variable_name):
            for y in range(height):
                band.readPixels(0, y, width, 1, pixels)
                mask.readPixels(0, y, width, 1, mask_pixels)
                for x, p in enumerate(pixels):
                    if mask_pixels[x] == 0:
                        result.append(p)

    return np.array(result)


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


def get_shape(record):
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
        path.lineTo(start_point[0], start_point[1])
        shape.add(path)
        start_index = end_index

    return shape


def get_coordinate_variable(product, axis):
    axis_root = get_axis_root(product, axis)
    if axis_root is None:
        return None

    axis_element_attribute = axis_root.getAttribute('_CoordinateAxisType').getData().toString()
    if axis_element_attribute == axis:
        return np.array(axis_root.getElement('Values').getAttributes()[0].getData().getElems())
    return None


def get_axis_units(product, axis):
    axis_root = get_axis_root(product, axis)
    units_attribute = axis_root.getAttribute('units')
    if units_attribute is not None:
        return units_attribute.getData().toString()
    return None


def get_axis_root(product, axis):
    variable_metadata_root = product.getMetadataRoot().getElement('Variable_Attributes')
    axis_root = variable_metadata_root.getElement(axis)
    return axis_root