import hashlib
import hashlib

from portalflask.models.database import db_session
from portalflask.models.user import User
from portalflask.models.usergroup import UserGroup
from portalflask import oid
from portalflask.core.group_extension import GroupExtension, GROUPS_KEY

import os

from flask import Blueprint
from flask import request
from werkzeug.utils import secure_filename

portal_upload = Blueprint('portal_upload', __name__)

@portal_upload.route('/shapefile_upload', methods=['POST'])
def shapefile_upload():
    print(request.files)
    shapefile = request.files.getlist('shapefile[]')
    print(shapefile)
    for file in shapefile:
        print(file)
        filename = secure_filename(file.filename)
        file.save(os.path.join('/home/thomass/temp/', filename))

    return "200"
