import hashlib
import os

from portalflask.models.database import db_session
from portalflask.models.user import User
from portalflask.models.usergroup import UserGroup
from portalflask import oid, shapefile_support
from portalflask.core.group_extension import GroupExtension, GROUPS_KEY

from actions import check_for_permission
from flask import Blueprint, render_template, redirect, url_for, g, session, request, jsonify, current_app

from openid.extensions.sreg import SRegResponse

portal_user = Blueprint('portal_user', __name__)

@portal_user.route('/')
def index():
   return render_template('index.html')


@portal_user.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def login():
   # if we are already logged in, go back to were we came from
   if g.user is not None:
      return redirect(url_for('portal_user.index'))

   openid_identity = current_app.config.get('OPENID_RP_URL')
   print openid_identity
   return oid.try_login(openid_identity, ask_for=['email', 'fullname', 'nickname'], extensions=[GroupExtension()])


@oid.after_login
def create_or_login(resp):
   generic_identity = resp.identity_url
   nickname = resp.nickname
   user_identity = generic_identity + '?id=' + hashlib.md5(nickname).hexdigest()
   session['openid'] = user_identity
   user = User.query.filter_by(openid=user_identity).first()

   if user is not None:
       g.user = user
       return redirect(url_for('portal_user.index'))
   group_extension = resp.extensions[GroupExtension.ns_alias]
   sreg_extension = resp.extensions[SRegResponse.ns_alias]
   return redirect(url_for('portal_user.create_user', next=oid.get_next_url(),
                           email=resp.email, groups=group_extension[GROUPS_KEY],
                           username=sreg_extension['nickname'],
                           full_name=sreg_extension['fullname']))


@portal_user.route('/create-user', methods=['GET', 'POST'])
def create_user():
   if g.user is not None or 'openid' not in session:
      raise ValueError('should never come here')
   if request.method == 'POST':
      print ('in post')
      email = request.form['email']
      group_names = request.form['groups'].split()
      username = request.form['username'].split()
      full_name = request.args.get('full_name', None)
      add_user_to_db(email, username, full_name, group_names)
      db_session.commit()
      print('Profile successfully created')
      return redirect(oid.get_next_url())
   elif request.method == 'GET':
      print('in get')
      email = request.args.get('email', None)
      group_names = request.args.get('groups', None).split()
      username = request.args.get('username', None)
      full_name = request.args.get('full_name', None)
      add_user_to_db(email, username, full_name, group_names)
      db_session.commit()
      print('Profile successfully created')
      return redirect(url_for('portal_user.index'))
   return redirect(url_for('portal_user.index'))


@portal_user.route('/get_user', methods=['POST'])
@check_for_permission(['bc'])
def get_user():
    if g.user is not None:
        groupstring = ''
        for i, group in enumerate(g.user.groups):
            groupstring += group.group_name
            if i < len(g.user.groups) - 1:
                groupstring += ','
        return jsonify(username=g.user.username, usergroups=groupstring, fullname=g.user.full_name, email=g.user.email, openid=g.user.openid)
    return jsonify(username=None, usergroups=None, fullname=None, email=None, openid=None)


@portal_user.route('/permissions/<allowed_user_groups>', methods=['POST'])
def permissions(allowed_user_groups):
    if g.user is not None:
        for group in g.user.groups:
            if group.group_name in allowed_user_groups:
                return jsonify(is_accessible=True)
    return jsonify(is_accessible=False)


@portal_user.route('/get_shapefile_names', methods=['POST'])
@check_for_permission(['bc', 'coastcolour', 'waqss_users'])
def get_shapefile_names():
    if not os.path.exists(get_shape_path()):
        return jsonify(shapefiles=[])
    files = [f for f in os.listdir(get_shape_path()) if os.path.basename(f).endswith('.shp')]
    return jsonify(shapefiles=files)


@portal_user.route('/get_shape_names/<shapefile_name>', methods=['POST'])
@check_for_permission(['bc', 'coastcolour', 'waqss_users'])
def get_shape_names(shapefile_name):
    shapefile_path = get_shape_path() + shapefile_name
    shape_names = shapefile_support.get_shape_names(shapefile_path)
    return jsonify(shape_names=shape_names)


@portal_user.route('/get_shapefile_geometry/<shapefile_name>/<shape_name>', methods=['POST'])
@check_for_permission(['bc', 'coastcolour', 'waqss_users'])
def get_shapefile_geometry(shapefile_name, shape_name):
    shapefile_path = get_shape_path() + shapefile_name
    return jsonify(geometry=shapefile_support.get_shape_geometry(shapefile_path, shape_name), bounds=shapefile_support.get_bounding_box(shapefile_path, shape_name))


@portal_user.route('/logout', methods=['GET','POST'])
def logout():
   session.pop('openid', None)
   g.user = None
   return "200", 200


@portal_user.route('/is_logged_in', methods=['GET'])
def is_logged_in():
   return jsonify(logged_in=g.user is not None)


def add_user_to_db(email, username, full_name, group_names):
    db_groups = UserGroup.query.all()
    for group_name in group_names:
        group_is_already_in_db = group_name in [db_group.group_name for db_group in db_groups]
        if not group_is_already_in_db:
            db_session.add(UserGroup(group_name))
    db_session.commit()
    user_groups = UserGroup.query.filter(UserGroup.group_name.in_(group_names)).all()
    db_session.add(User(email=email, openid=session['openid'], username=username, full_name=full_name, groups=user_groups))


def get_shape_path():
    return str(current_app.config.get('SHAPEFILE_PATH')) + str(g.user.username) + "/"