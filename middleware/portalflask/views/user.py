import hashlib

from portalflask.models.database import db_session
from portalflask.models.user import User
from portalflask import oid


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
   #if request.method == 'POST':
      #openid = request.form.get('openid')
      #if openid:
         #return oid.try_login(openid, ask_for=['email'])

   if provider is not None and provider in COMMON_PROVIDERS:
      session['provider'] = provider
      return oid.try_login(COMMON_PROVIDERS[provider], ask_for=['email', 'fullname', 'nickname'])

   return redirect(url_for('portal_user.index'))

@oid.after_login
def create_or_login(resp):
   print('in create or login')

   print(str(resp))

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
       print('logged in user ' + user.openid)
       flash(u'Successfully signed in')
       return redirect(url_for('portal_user.index'))
   return redirect(url_for('portal_user.create_user', next=oid.get_next_url(),
                           email=resp.email))
                           
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
         print('Profile successfully created')
         db_session.add(User(email, session['openid'], 'username')) # todo!
         db_session.commit()
         return redirect(oid.get_next_url())
   elif request.method == 'GET':
      print('in get')
      email = request.args.get('email', None)
      if '@' not in email:
          print(u'Error: you have to enter a valid email address')
      else:
         print('Profile successfully created')
         db_session.add(User(email, session['openid'], 'username')) # todo!
         db_session.commit()
         # The index has a script that closes popup when logged in
         #return redirect(oid.get_next_url()) 
         return redirect(url_for('portal_user.index'))
   print('returning')
   return redirect(url_for('portal_user.index'))
   
#@portal_user.route('/profile', methods=['GET', 'POST'])
#def edit_profile():
   #if g.user is None:
      #abort(401)
   #form = dict(email=g.user.email)
   #if request.method == 'POST':
      #if 'delete' in request.form:
         #pass
      #form['email'] = request.form['email']
      #if '@' not in form['email']:
         #flash(u'Error: you have to enter a valid email address')
      #else:
         #flash(u'Profile successfully created')
         #g.user.email = form['email']
         #db_session.commit()
         #return redirect(url_for('portal_user.edit_profile'))
   #return render_template('edit_profile.html', form=form)

@portal_user.route('/get_user', methods=['POST'])
def get_user():
    print('in get user')
    if g.user is not None:
        print('return ' + g.user.openid)
        return jsonify(username=g.user.openid)
    return jsonify(username=None)


@portal_user.route('/logout', methods=['GET','POST'])
def logout():
   print('signing out user ' + session['openid'])
   session.pop('openid', None)
   g.user = None
   return "200", 200
