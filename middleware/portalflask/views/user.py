import hashlib

from portalflask.models.database import db_session
from portalflask.models.user import User
from portalflask.models.usergroup import UserGroup
from portalflask import oid
from portalflask.core.group_extension import GroupExtension, GROUPS_KEY
from flask import Blueprint, render_template, redirect, url_for, g, session, request, jsonify

portal_user = Blueprint('portal_user', __name__)

COMMON_PROVIDERS = {'google': 'https://www.google.com/accounts/o8/id',
                    'yahoo': 'https://yahoo.com/',
                    'aol': 'http://aol.com/',
                    'bc': 'http://opec-portal-test:8585/openid-server/provider/discovery/gis-portal',
                    'steam': 'https://steamcommunity.com/openid/'
}

@portal_user.route('/')
def index():
   return render_template('index.html')


@portal_user.route('/login')
@oid.loginhandler
def login_with_google():
   print('in login with google')
   # if we are already logged in, go back to were we came from
   if g.user is not None:
      return redirect(url_for('state_user.getStates'))
   return oid.try_login(COMMON_PROVIDERS['google'], ask_for=['email', 'fullname', 'nickname'])


@portal_user.route('/login/<provider>', methods=['GET', 'POST'])
@oid.loginhandler
def login(provider):
   print('in login')
   # if we are already logged in, go back to were we came from
   if g.user is not None:
      return redirect(url_for('portal_user.index'))

   if provider is not None and provider in COMMON_PROVIDERS:
      session['provider'] = provider
      return oid.try_login(COMMON_PROVIDERS[provider], ask_for=['email', 'fullname', 'nickname'], extensions=[GroupExtension()])

   return redirect(url_for('portal_user.index'))


@oid.after_login
def create_or_login(resp):
   print('in create or login')

   if session['provider'] == 'bc':
      generic_identity = resp.identity_url
      email = resp.email
      user_identity = generic_identity + '?id=' + hashlib.md5(email).hexdigest()
   else:
      user_identity = resp.identity_url

   session['openid'] = user_identity
   user = User.query.filter_by(openid=user_identity).first()

   if user is not None:
       g.user = user
       print('logged in user ' + str(user) + ' who is in groups: ' + str(user.groups))
       return redirect(url_for('portal_user.index'))
   extension = resp.extensions[GroupExtension.ns_alias]
   return redirect(url_for('portal_user.create_user', next=oid.get_next_url(),
                           email=resp.email, groups=extension[GROUPS_KEY]))


@portal_user.route('/create-user', methods=['GET', 'POST'])
def create_user():
   print('in create user')
   if g.user is not None or 'openid' not in session:
      return redirect(url_for('portal_user.index'))
   if request.method == 'POST':
      print ('in post')
      email = request.form['email']
      if '@' not in email:
         print('Error: invalid email address')
      else:
         groups = request.form['groups'].split()
         add_user_to_db(email, 'username', groups)  # todo !!
         db_session.commit()
         print('Profile successfully created')
         return redirect(oid.get_next_url())
   elif request.method == 'GET':
      print('in get')
      email = request.args.get('email', None)
      if '@' not in email:
          print(u'Error: you have to enter a valid email address')
      else:
         groups = request.args.get('groups', None).split()
         add_user_to_db(email, 'username', groups)  # todo !!
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

        return jsonify(username=g.user.openid, usergroups=groupstring)
    return jsonify(username=None)


@portal_user.route('/logout', methods=['GET','POST'])
def logout():
   print('signing out user ' + session['openid'])
   session.pop('openid', None)
   g.user = None
   return "200", 200


def add_user_to_db(username, email, groups):
    db_groups = UserGroup.query.all()
    for group in groups:
        if not group in db_groups:
            db_session.add(UserGroup(group))
    db_session.commit()
    user_groups = UserGroup.query.all()
    db_session.add(User(email, session['openid'], username, user_groups))