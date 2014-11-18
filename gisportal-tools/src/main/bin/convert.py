from netCDF4 import Dataset
import numpy
import shutil
import sys
import os
import subprocess
import add_time_dimension

if len(sys.argv) != 2:
    print('Usage:\n'
          '    python convert.py <path_to_directory>')
    sys.exit(-1)

path = sys.argv[1]
cwd = os.getcwd()

for f in [f for f in os.listdir(path) if f.endswith('png')]:
    source_filename = path + '/' + f
    print('Converting file \'' + source_filename + '\'')
    returncode = subprocess.call([cwd + '/convert.sh', source_filename])
    if returncode == 101:
        continue

    var_name = os.path.basename(source_filename)[18:21].replace('_', '')

    if 'nos' in os.path.basename(source_filename):
        latmin = 49.0
        latmax = 63.0
        lonmin = -5.0
        lonmax = 13.0
    elif 'bas' in os.path.basename(source_filename):
        latmin = 53.0
        latmax = 66.0
        lonmin = 9.0
        lonmax = 31.0
    elif 'est' in os.path.basename(source_filename):
        latmin = 57.058884
        latmax = 60.57032
        lonmin = 21.702216
        lonmax = 30.225435

    d = Dataset(source_filename[:-4] + '_waqss_archive.nc', 'r')
    d_new = Dataset(source_filename[:-4] + '_waqss_archive.nc' + '_tmp', 'w')
    lon = d_new.createDimension('lon', len(d.dimensions['x']))
    lat = d_new.createDimension('lat', len(d.dimensions['y']))
    var_rgb = d_new.createVariable(var_name + '_rgb', numpy.int8, ('lat', 'lon'), fill_value=0.0)
    var_rgb.long_name = 'Weekly mean of ' + var_name + '. Caution: generated from RGB, no real geophysical values!'
    var_rgb.units = 'None'

    var_rgb[:] = 100 * (1 / numpy.max(d.variables['gray'][:])) * d.variables['gray'][:]

    lat = d_new.createVariable('lat', numpy.float32, 'lat')
    lat.long_name = "latitude"
    lat.standard_name = "latitude"
    lat.valid_min = latmin
    lat.valid_max = latmax
    lat[:] = numpy.linspace(latmax, latmin, num=len(d_new.dimensions['lat']))

    lon = d_new.createVariable('lon', numpy.float32, 'lon')
    lon.long_name = "longitude"
    lon.standard_name = "longitude"
    lon.valid_min = lonmin
    lon.valid_max = lonmax
    lon[:] = numpy.linspace(lonmin, lonmax, num=len(d_new.dimensions['lon']))
    d_new.close()
    d.close()

    shutil.move(source_filename[:-4] + '_waqss_archive.nc' + '_tmp', source_filename[:-4] + '_waqss_archive.nc')

    add_time_dimension.add_time_dimension(source_filename[:-4] + '_waqss_archive.nc')