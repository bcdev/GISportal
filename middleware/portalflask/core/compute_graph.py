import beampy
import shapefile
from beampy import jpy
from netCDF4 import num2date
import numpy as np

def get_name_index(fields):
    for index, f in enumerate(fields):
        if f[0].lower() == 'name':
            return index
    print('Warning: cannot find name column. Falling back to column \'' + str(fields[1]) + '\'')
    return 1


def get_record(record_name, shapefile):
    index = get_name_index(shapefile.fields)
    records = shapefile.shapeRecords()
    for rec in records:
        if rec.record[index - 1] == record_name:
            return rec
    raise ValueError('Cannot find record with name \'' + record_name + '\'')


def get_shape(record):
    GeneralPath = jpy.get_type('java.awt.geom.GeneralPath')
    path = GeneralPath()
    start_point = record.shape.points[0]
    path.moveTo(start_point[0], start_point[1])
    for point in record.shape.points[1:]:
        # lon lat
        path.lineTo(point[0], point[1])
    path.lineTo(start_point[0], start_point[1])

    path = GeneralPath()
    path.moveTo(18.40625, 33.43555)
    path.lineTo(23.67969, 33.43555)
    path.lineTo(23.67969, 36.95117)
    path.lineTo(18.40625, 36.95117)
    path.lineTo(18.40625, 33.43555)
    return path


def get_axis_root(product, axis):
    variable_metadata_root = product.getMetadataRoot().getElement('Variable_Attributes')
    axis_root = variable_metadata_root.getElement(axis)
    return axis_root


def get_coordinate_variable(product, axis):
    axis_root = get_axis_root(product, axis)
    if axis_root is None:
        return None

    axis_element_attribute = axis_root.getElement('_CoordinateAxisType').getData().toString()
    if axis_element_attribute == axis:
        return np.array(axis_root.getElement('Values').getAttributes()[0].getData().getElems())
    return None


def getUnits(product, axis):
    axis_root = get_axis_root(product, axis)
    units_attribute = axis_root.getAttribute('units')
    if units_attribute is not None:
        return units_attribute.getData().toString()
    return None


def get_output(ncfile_name, variable_name, shapefile_path, record_name):

    sf = shapefile.Reader(shapefile_path)
    record = get_record(record_name, sf)
    shape = get_shape(record)
    product = beampy.ProductIO.readProduct(ncfile_name)

    output = {}

    times = get_coordinate_variable(product, 'Time')
    if times is None:
        raise ValueError('No time variable found')

    time_units = getUnits(product, 'Time')
    if time_units:
        start = (num2date(times[0], time_units, calendar='standard')).isoformat()
    else:
        start = ''.join(times[0])

    output['global'] = {'time': start}

    units = getUnits(dataset.variables[variable_name])
    output['units'] = units

    output['data'] = {}
    factory = jpy.get_type('org.esa.beam.framework.datamodel.StxFactory')().withRoiShape(shape)
    pm = jpy.get_type('com.bc.ceres.core.ProgressMonitor')
    for time_index, band in enumerate(product.getBands()):
        if time_units:
            date = num2date(time[time_index], time_units, calendar='standard').isoformat()
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
