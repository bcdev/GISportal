from flask import Flask, g, session, make_response
try:
   from flask_openid import OpenID
except:
   from flaskext.openid import OpenID

from core.group_extension import GroupExtension
from openid.extensions.sreg import SRegResponse

import sys
import os
import settings as settings

def create_app(path):
   app = Flask(__name__)
   app.config.update(SECRET_KEY=settings.SECRET_KEY, DEBUG=settings.DEBUG)
   print path
   
   setup_version(app)
   
   #=== SETUP LOGGING ===#
   setup_logging(app, path)
   
   #=== SETUP CONFIG ===#
   setup_config(app)
   
   #=== SETUP DATABASE ===#
   app.config['DATABASE_URI'] = settings.DATABASE_URI

   #=== ROUTES ===#
   @app.before_request
   def before_request():
      g.user = None
      if 'openid' in session:
         g.user = User.query.filter_by(openid = session['openid']).first()
         
   @app.after_request
   def after_request(response):
      db_session.remove()
      return response
   
   @app.errorhandler(400)
   def badRequest(error):
      if hasattr(g, 'error'):
         resp = make_response(g.error, 400)
         resp.headers['MESSAGE'] = g.error
         return resp
      else:
         resp = make_response("Bad request", 400)
         resp.headers['MESSAGE'] = "Bad request"
         return resp
   
   return app


def setup_version(app):
   app.config['MAJOR_VERSION'] = '0'
   app.config['MINOR_VERSION'] = '3'
   app.config['API_VERSION'] = '0.1'


"""
Setup logging for the application. If no path is provided, is empty, or does
not exist, the app instance path is used.
"""
def setup_logging(app, path):
   if settings.LOG_PATH != None:
      if len(settings.LOG_PATH) == 0:
         settings.LOG_PATH = path
           
      try:  
         import logging
         import os
         from logging.handlers import RotatingFileHandler
      
         if settings.LOG_PATH and len(settings.LOG_PATH) != 0 and os.path.exists(settings.LOG_PATH):
            f_handler = RotatingFileHandler(os.path.join(settings.LOG_PATH, 'python-flask.log'))
         else:
            f_handler = RotatingFileHandler(os.path.join(app.instance_path, 'python-flask.log'))
            
         f_handler.setLevel(logging.DEBUG)
         f_handler.setFormatter(logging.Formatter(
             '[%(asctime)s] [%(levelname)s]: %(message)s'
             '[in %(filename)s:%(lineno)d]'
         ))
         app.logger.addHandler(f_handler)
         app.logger.setLevel(settings.LOG_LEVEL)
      except:
         print 'Failed to setup logging'
         
# Use settings as a config object
def setup_config(app):
   app.config.from_object(settings)
   app.logger.debug("In debug mode: %s" % app.debug)
   os.environ['JAVA_HOME'] = settings.JAVA_HOME
   os.environ['JDK_HOME'] = settings.JDK_HOME
   os.environ['PATH'] = settings.PATH_extension + ':' + os.getenv('PATH', '')
   os.environ['LD_LIBRARY_PATH'] = settings.LD_LIBRARY_PATH_extension + ':' + os.getenv('LD_LIBRARY_PATH', '')
   os.environ['BEAM_HOME'] = settings.BEAM_HOME


# Alternative method to using 'setup_routing' above
def setup_blueprints(app):
   from views.user import portal_user
   from views.state import portal_state
   from views.graph import portal_graph
   #from views.quickregions import portal_quickRegions
   #from views.roi import portal_roi
   #from views.layergroup import portal_layerGroup
   from views.proxy import portal_proxy
   from views.wfs import portal_wfs
   from views.wcs import portal_wcs
   from views.actions import portal_actions
   from views.upload import portal_upload

   app.register_blueprint(portal_user)
   app.register_blueprint(portal_state)
   app.register_blueprint(portal_graph)
   app.register_blueprint(portal_proxy)
   app.register_blueprint(portal_wfs)
   app.register_blueprint(portal_wcs)
   app.register_blueprint(portal_actions)
   app.register_blueprint(portal_upload)

path = sys.path[0]
app = create_app(path)

oid = OpenID(app, settings.OPENID_FOLDER, extension_responses=[GroupExtension, SRegResponse])
print path

# register application views and blueprints  
setup_blueprints(app)

from portalflask.models.database import db_session
from portalflask.models.user import User
