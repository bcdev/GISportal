import shutil
import sys
import os

if len(sys.argv) != 2:
    print('Usage:\n'
          '    python distribute.py <path_to_directory>')
    sys.exit(-1)

path = sys.argv[1]

for f in [f for f in os.listdir(path) if f.endswith('nc')]:
    source_filename = path + f

    if 'bas' in f:
        region = 'bas'
    elif 'nos' in f:
        region = 'nos'
    elif 'est' in f:
        region = 'est'
    else:
        print('Invalid filename: ' + source_filename)
        exit(-1)

    var_name = os.path.basename(source_filename)[18:21].replace('_', '')

    target_path = path + '/' + region + '/' + var_name
    if not os.path.exists(target_path):
        os.makedirs(target_path)

    print('Moving file \'' + source_filename + '\' to ' + target_path)
    shutil.move(source_filename, target_path + '/' + f)