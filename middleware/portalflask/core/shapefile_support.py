import os

import beampy
import shapefile
from beampy import jpy
from netCDF4 import num2date
import numpy as np


def get_output(ncfile_name, variable_name, shapefile_name, shape_name):
    sf = shapefile.Reader('/home/thomass/temp/' + shapefile_name) # todo replace hard-coded dir
    record = get_record(shape_name, sf)
    shape = get_shape(record)
    product = beampy.ProductIO.readProduct(ncfile_name)

    output = {}

    times = get_coordinate_variable(product, 'Time')
    if times is None:
        raise ValueError('No time variable found')

    time_units = get_axis_units(product, 'Time')
    if time_units:
        start = (num2date(times[0], time_units, calendar='standard')).isoformat()
    else:
        start = ''.join(times[0])

    output['global'] = {'time': start}

    units = get_axis_units(product, str(variable_name))
    output['units'] = units

    output['data'] = {}
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
            output['data'][date] = {'mean': mean, 'median': median,'std': std, 'min': minimum, 'max': maximum}

    return output


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