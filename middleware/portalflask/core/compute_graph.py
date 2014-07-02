import beampy
import shapefile
from beampy import jpy
from netCDF4 import Dataset, num2date
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


def get_output():
    nc_file = '/home/thomass/OPATMBFM3_OGS_HC_Med_19990101_20111231_Totalchlorophyll.nc'
    variable_name = 'Totchl'
    shapefile_path = '/home/thomass/temp/countries.shp'
    record_name = 'Colombia'

    dataset = Dataset(nc_file, 'r')

    sf = shapefile.Reader(shapefile_path)
    record = get_record(record_name, sf)
    shape = get_shape(record)
    product = beampy.ProductIO.readProduct(nc_file)

    output = {}

    time = getCoordinateVariable(dataset, 'Time')
    if time is None:
        raise ValueError('No time variable found')
    times = np.array(time)

    timeUnits = getUnits(time)
    if timeUnits:
        start = (num2date(times[0], time.units, calendar='standard')).isoformat()
    else:
        start = ''.join(times[0])

    output['global'] = {'time': start}

    units = getUnits(dataset.variables[variable_name])
    output['units'] = units

    output['data'] = {}
    for time_index, band in enumerate(product.getBands()):
        if timeUnits:
            date = num2date(time[time_index], time.units, calendar='standard').isoformat()
        else:
            date = ''.join(times[time_index])

        factory = beampy.StxFactory()
        stx = factory.withROIShape(shape).create(band, beampy.ProgressMonitor.NULL)
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


def getCoordinateVariable(dataset, axis):
    for i, key in enumerate(dataset.variables):
        var = dataset.variables[key]
        for name in var.ncattrs():
            if name == "_CoordinateAxisType" and var._CoordinateAxisType == axis:
                return var

    return None



def getUnits(variable):
    for name in variable.ncattrs():
        if name == "units":
            return variable.units

    return ''