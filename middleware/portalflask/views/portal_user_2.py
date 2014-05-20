from flask import Blueprint, request, jsonify, g, current_app
from sqlalchemy import desc
from portalflask.models.database import db_session
from portalflask.models.state import State
from portalflask.models.graph import Graph
from portalflask.models.quickregions import QuickRegions
from portalflask.models.roi import ROI
from portalflask.models.layergroup import LayerGroup
from portalflask.models.user import User
from portalflask.core import short_url, error_handler
import datetime
import sqlite3 as sqlite

portal_user_2 = Blueprint('portal_user_2', __name__)

@portal_user_2.route('/user', methods = ['GET'])
def get_user():
    current_app.logger.debug("starting to log request")
    current_app.logger.debug(str(request.args))
    current_app.logger.debug("end logging request")

    import random

    rand = random.random()
    if rand > 0.7:
        return jsonify(username='a')
    if rand > 0.5:
        return jsonify(username='b')
    if rand > 0.3:
        return jsonify(username='c')
    return jsonify(username='d')