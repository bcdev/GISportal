import netCDF4
import shutil
import sys
import numpy as np
import datetime
import os


def add_time_dimension(dataset):
    temp_file = dataset + '_temp'

    print('Adding time dimension to file ' + dataset)

    source = netCDF4.Dataset(dataset, 'r')
    target = netCDF4.Dataset(temp_file, 'w')

    for dim in source.dimensions:
        target.createDimension(dim, len(source.dimensions[dim]))

    target.createDimension('time', 1)

    for global_attribute_name in source.ncattrs():
        target.setncattr(global_attribute_name, source.__getattribute__(global_attribute_name))

    for var_name in source.variables:
        var = source.variables[var_name]
        dimensions = var.dimensions
        if 'lat' in dimensions and 'lon' in dimensions and len(dimensions) == 2:
            dimensions = ['time', dimensions[0], dimensions[1]]
        target_var = target.createVariable(var_name, var.dtype, dimensions, zlib=True)

        for attribute_name in var.ncattrs():
            attribute_value = var.__getattribute__(attribute_name)
            if 'coordinates' in attribute_name and attribute_value == 'lat lon':
                target_var.setncattr(attribute_name, 'time lat lon')
            else:
                target_var.setncattr(attribute_name, attribute_value)

        if 'lat' in dimensions and 'lon' in dimensions and len(dimensions) == 2:
            lat_dim_length = len(source.dimensions[var.dimensions[0]])
            lon_dim_length = len(source.dimensions[var.dimensions[1]])
            target_var[:] = var[:].reshape(1, lat_dim_length, lon_dim_length)
        else:
            target_var[:] = var[:]

    time_var = target.createVariable('time', np.int32, dimensions=('time'))
    time_var.setncattr('units', 'seconds since 1970-01-01')
    time_var.setncattr('standard_name', 'time')
    epoch = datetime.datetime.strptime('1970-01-01', '%Y-%m-%d')

    if 'waqss_archive' in os.path.basename(dataset):
        time = datetime.datetime.strptime(os.path.basename(dataset)[0:8], '%Y%m%d')
    elif 'weekly' in os.path.basename(dataset):
        time = datetime.datetime.strptime(os.path.basename(dataset)[14:24], '%Y-%m-%d')
    else:
        time = datetime.datetime.strptime(os.path.basename(dataset)[3:13], '%Y-%m-%d')
    delta = (time - epoch)
    seconds_since_epoch = delta.days * (24*60*60) + delta.seconds
    time_var[0] = seconds_since_epoch

    target.close()

    target_file = dataset
    if not target_file.endswith('.nc'):
        target_file = target_file + '.nc'
        target_file = target_file.replace('.pre', '')
        os.remove(dataset)

    shutil.move(temp_file, target_file)

if __name__ == 'main':
    # dataset name pattern: /path/to/L3_2013-03-22_2013-03-22.nc
    add_time_dimension(sys.argv[1])