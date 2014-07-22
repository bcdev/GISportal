import hashlib

from portalflask.models.database import db_session
from portalflask.models.user import User
from portalflask.models.usergroup import UserGroup
from portalflask import oid
from portalflask.core.group_extension import GroupExtension, GROUPS_KEY
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
    shapefile = request.files.getlist('shapefile[]')
    if not os.path.exists(shapefile_support.get_shape_path()):
        os.makedirs(shapefile_support.get_shape_path())
    for file in shapefile:
        filename = secure_filename(file.filename)
        target = os.path.join(shapefile_support.get_shape_path(), filename)
        file.save(target)
        print('successfully saved file \'' + target + '\'')

    return "200"
