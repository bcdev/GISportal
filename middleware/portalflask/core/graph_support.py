from netCDF4 import num2date

import jpy
import numpy as np


def get_timeseries(product, variable_name, shape):
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


def get_band_data_as_array(variable_name, product, mask):
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


def get_hovmoller(product, variable_name, mask, x_axis_var, y_axis_var):
    x_arr = get_coordinate_variable(product, x_axis_var)
    y_arr = get_coordinate_variable(product, y_axis_var)
    z_arr = np.zeros(product.getSceneRasterWidth() * product.getSceneRasterHeight())
    mask_pixels = np.zeros(product.getSceneRasterWidth() * product.getSceneRasterHeight())

    if x_arr is None:
        # g.graphError = "could not find %s dimension" % x_axis_var
        print('could not find %s dimension' % x_axis_var)
        return
    if y_arr is None:
        # g.graphError = "could not find %s dimension" % y_axis_var
        print('could not find %s dimension' % y_axis_var)
        return

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

    output['depth'] = get_depth(product)

    bands = [b for b in product.getBands() if b.getName().startswith(variable_name)]

    if direction == 'lat':
        height = product.getSceneRasterHeight()
        for y in range(height):
            for time_index in range(len(bands)):
                date = num2date(time[time_index], time_units, calendar='standard').isoformat() if time_units else ''.join(times[time_index])
                bands[time_index].readPixels(0, y, product.getSceneRasterWidth(), 1, z_arr)
                mask.readPixels(0, y, product.getSceneRasterWidth(), 1, mask_pixels)
                ma_array = np.ma.array(np.ma.masked_invalid(z_arr), mask=mask_pixels)
                mean = float(np.mean(ma_array))
                lat_value = float(lat[height - 1 - y])  # lat is stored in reversed order
                output['data'].append([date, lat_value, mean])
    elif direction == "lon":
        width = product.getSceneRasterWidth()
        for x in range(width):
            for time_index in range(len(bands)):
                date = num2date(time[time_index], time_units, calendar='standard').isoformat() if time_units else ''.join(times[time_index])
                bands[time_index].readPixels(x, 0, 1, product.getSceneRasterHeight(), z_arr)
                mask.readPixels(x, 0, 1, product.getSceneRasterHeight(), mask_pixels)
                ma_array = np.ma.array(np.ma.masked_invalid(z_arr), mask=mask_pixels)
                mean = float(np.mean(ma_array))
                lon_value = float(lon[x])
                output['data'].append([date, lon_value, mean])

    if len(output['data']) < 1:
        # g.graphError = "no valid data available to use"
        # error_handler.setError('2-07', None, g.user.id, "views/wcs.py:hovmoller - No valid data available to use.")
        print('no valid data available to use')
        return output

    return output


def get_depth(product):
    axis_root = get_axis_root(product, 'depth')
    has_axis_root = axis_root is not None
    is_height_type = axis_root.getAttribute('_CoordinateAxisType').getData().getElemString() == 'Height'
    is_positive_Z_coordinate = axis_root.getAttribute('_CoordinateZisPositive') is not None
    if has_axis_root and is_height_type and is_positive_Z_coordinate:
        return axis_root.getElement('Values').getAttributes()[0].getData().getElems()[0]
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


def get_coordinate_variable(product, axis):
    for element in product.getMetadataRoot().getElement('Variable_Attributes').getElements():
        coordinate_axis_attribute = element.getAttribute('_CoordinateAxisType')
        if coordinate_axis_attribute is not None:
            axis_element_attribute = coordinate_axis_attribute.getData().toString()
            if axis_element_attribute == axis:
                return np.array(element.getElement('Values').getAttributes()[0].getData().getElems())
    return None