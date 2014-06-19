import hashlib

from portalflask.models.database import db_session
from portalflask.models.user import User
from portalflask.models.usergroup import UserGroup
from portalflask import oid
from portalflask.core.group_extension import GroupExtension, GROUPS_KEY
from flask import Blueprint, render_template, redirect, url_for, g, session, request, jsonify, current_app

from openid.extensions.sreg import SRegResponse

portal_user = Blueprint('portal_user', __name__)

@portal_user.route('/')
def index():
   return render_template('index.html')


@portal_user.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def login():
   print('in login')
   # if we are already logged in, go back to were we came from
   if g.user is not None:
      return redirect(url_for('portal_user.index'))

   openid_identity = current_app.config.get('OPENID_RP_URL')
   return oid.try_login(openid_identity, ask_for=['email', 'fullname', 'nickname'], extensions=[GroupExtension()])


@oid.after_login
def create_or_login(resp):
   print('in create or login')

   generic_identity = resp.identity_url
   email = resp.email
   user_identity = generic_identity + '?id=' + hashlib.md5(email).hexdigest()
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
   print('in create user')
   if g.user is not None or 'openid' not in session:
      raise ValueError('should never come here')
   if request.method == 'POST':
      print ('in post')
      email = request.form['email']
      if '@' not in email:
         print('Error: invalid email address')
      else:
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
      if '@' not in email:
          print(u'Error: you have to enter a valid email address')
      else:
         group_names = request.args.get('groups', None).split()
         username = request.args.get('username', None)
         full_name = request.args.get('full_name', None)
         add_user_to_db(email, username, full_name, group_names)
         db_session.commit()
         print('Profile successfully created')
         return redirect(url_for('portal_user.index'))
   print('returning')
   return redirect(url_for('portal_user.index'))


@portal_user.route('/get_user', methods=['POST'])
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
                print('granted')
                return jsonify(is_accessible=True)
    print('declined')
    return jsonify(is_accessible=False)


@portal_user.route('/logout', methods=['GET','POST'])
def logout():
   session.pop('openid', None)
   g.user = None
   return "200", 200


def add_user_to_db(email, username, full_name, group_names):
    db_groups = UserGroup.query.all()
    for group_name in group_names:
        group_is_already_in_db = group_name in [db_group.group_name for db_group in db_groups]
        if not group_is_already_in_db:
            db_session.add(UserGroup(group_name))
    db_session.commit()
    user_groups = UserGroup.query.filter(UserGroup.group_name in group_names)
    db_session.add(User(email=email, openid=session['openid'], username=username, full_name=full_name, groups=user_groups))