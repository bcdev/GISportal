from portalflask.models.database import db_session

from portalflask.models.shapefile import Shapefile
from portalflask.models.shape import Shape
from portalflask.models.user import User
from flask import current_app, g
import portalflask.core.shapefile_support as shapefile_support

import os

from flask import Blueprint
from flask import request
from werkzeug.utils import secure_filename

from actions import check_for_permission

portal_upload = Blueprint('portal_upload', __name__)

@portal_upload.route('/shapefile_upload', methods=['POST'])
@check_for_permission(['admins'])
def shapefile_upload():
    shapefiles = request.files.getlist('shapefile[]')
    if len(shapefiles) == 0:
        print('Apparently uploaded empty list of files...?')
        return '200'

    shapefile_name = secure_filename(shapefiles[0].filename)
    shapefile_name = shapefile_name[:shapefile_name.index('.')] + '.shp'
    path = str(os.path.join(shapefile_support.get_shape_path(), shapefile_name))
    print(path)
    already_registered = Shapefile.query.filter(Shapefile.path == path).count() > 0
    if already_registered:
        print('Shapefile \''+  shapefile_name + '\' has already been uploaded before.')
        return '200'

    if not os.path.exists(shapefile_support.get_shape_path()):
        os.makedirs(shapefile_support.get_shape_path())

    for file in shapefiles:
        filename = secure_filename(file.filename)
        target = os.path.join(shapefile_support.get_shape_path(), filename)
        file.save(target)
        print('successfully saved file \'' + target + '\'')
    persist(shapefile_name, path)

    return '200'


def persist(shapefile_name, path):
    shape_names = shapefile_support.get_shape_names(shapefile_name)
    persistent_shapes = []
    for shape_name in shape_names:
        shape = Shape(shape_name)
        persistent_shapes.append(shape)
        db_session.add(shape)
    db_session.add(Shapefile(name=shapefile_name, path=path, children=persistent_shapes))
    db_session.commit()