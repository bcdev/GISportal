from flask import Blueprint, request, jsonify, g, current_app, session
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
    if 'username' in session:
        username = session['username']
        return jsonify(username=username)
    return jsonify(username='guest')