import os

import shapefile as sf
import beampy
from beampy import jpy
from netCDF4 import num2date
import numpy as np

from portalflask.views.actions import check_for_permission


@check_for_permission(['admins'])
def get_timeseries(ncfile_name, variable_name, shapefile_name, shape_name):
    shapefile = sf.Reader('/home/thomass/temp/' + shapefile_name) # todo replace hard-coded dir
    record = get_record(shape_name, shapefile)
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
    ProgressMonitor = jpy.get_type('com.bc.ceres.core.ProgressMonitor')

    for time_index, band in enumerate(product.getBands()):
        print (str(time_index) + ': ' + band.getName())
        if time_units:
            date = num2date(times[time_index], time_units, calendar='standard').isoformat()
        else:
            date = ''.join(times[time_index])

        stx = factory.create(band, ProgressMonitor.NULL)
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
def get_hovmoller(ncfile_name, variable_name, shapefile_name, shape_name, x_axis_var, y_axis_var):
    shapefile = sf.Reader('/home/thomass/temp/' + shapefile_name) # todo replace hard-coded dir
    record = get_record(shape_name, shapefile)
    shape = get_shape(record)
    product = beampy.ProductIO.readProduct(ncfile_name)

    x_arr = get_coordinate_variable(product, x_axis_var)
    y_arr = get_coordinate_variable(product, y_axis_var)
    z_arr = np.zeros(product.getSceneRasterWidth() * product.getSceneRasterHeight())  # np.array(dataset.variables[z_axis_var])

    if x_arr is None:
        # g.graphError = "could not find %s dimension" % x_axis_var
        print('could not find %s dimension' % x_axis_var)
        return
    if y_arr is None:
        # g.graphError = "could not find %s dimension" % y_axis_var
        print('could not find %s dimension' % y_axis_var)
        return

    # Create a masked array ignoring nan's
    # z_masked_array = np.ma.masked_invalid(z_arr)

    lat = None
    lon = None

    if x_axis_var == 'Time':
        times = x_arr
        time = get_coordinate_variable(product, x_axis_var)
        lat = y_arr
    else:
        lon = x_arr
        times = y_arr
        time = get_coordinate_variable(product, y_axis_var)

    time_units = get_axis_units(product, 'Time')
    start = (num2date(times[0], time_units, calendar='standard')).isoformat() if time_units else ''.join(times[0])

    output = {
        'global': {'time': start},
        'data': []
    }

    direction = None
    if lat is not None:
        direction = 'lat'
    elif lon is not None:
        direction = 'lon'
        # z_arr = z_arr.swapaxes(1, 2)  # Make it use Lon instead of Lat

    output['depth'] = get_depth(product)

    bands = [b for b in product.getBands() if b.getName().startswith(variable_name)]
    for time_index in len(bands):
        date = num2date(time[time_index], time_units, calendar='standard').isoformat() if time_units else ''.join(times[time_index])

        if direction == 'lat':
            for y in product.getSceneRasterHeight():
                bands[time_index].readPixels(0, y, product.getSceneRasterWidth(), 1, z_arr)
                valid_pixels = []
                # mask.readPixels(0, y, width, 1, mask_pixels)
                for x, p in enumerate(z_arr):
                    # if mask_pixels[x] == 0:
                        valid_pixels.append(p)

                mean = float(np.mean(valid_pixels))

                if np.isnan(mean):
                    mean = 0

            output['data'].append([date, float(lat[y]), mean])
        elif direction == "lon":
            pass

    if len(output['data']) < 1:
        # g.graphError = "no valid data available to use"
        # error_handler.setError('2-07', None, g.user.id, "views/wcs.py:hovmoller - No valid data available to use.")
        print('no valid data available to use')
        return output

    return output


@check_for_permission(['admins'])
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


@check_for_permission(['admins'])
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
    for element in product.getMetadataRoot().getElement('Variable_Attributes').getElements():
        coordinate_axis_attribute = element.getAttribute('_CoordinateAxisType')
        if coordinate_axis_attribute is not None:
            axis_element_attribute = coordinate_axis_attribute.getData().toString()
            if axis_element_attribute == axis:
                return np.array(element.getElement('Values').getAttributes()[0].getData().getElems())
    return None


def get_axis_units(product, axis):
    axis_root = get_axis_root(product, axis)
    if axis_root is None:
        return None
    units_attribute = axis_root.getAttribute('units')
    if units_attribute is not None:
        return units_attribute.getData().toString()
    return None


def get_axis_root(product, axis):
    variable_metadata_root = product.getMetadataRoot().getElement('Variable_Attributes')
    axis_root = variable_metadata_root.getElement(axis)
    return axis_root


def get_depth(product):
    axis_root = get_axis_root(product, 'depth')
    has_axis_root = axis_root is not None
    is_height_type = axis_root.getAttribute('_CoordinateAxisType').getData().getElemString() == 'Height'
    is_positive_Z_coordinate = axis_root.getAttribute('_CoordinateZisPositive') is not None
    print(has_axis_root)
    print(is_height_type)
    print(is_positive_Z_coordinate)
    if has_axis_root and is_height_type and is_positive_Z_coordinate:
        return axis_root.getElement('Values').getAttributes()[0].getData().getElems()[0]
    return None

