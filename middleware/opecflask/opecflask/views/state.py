from flask import Blueprint, abort, request, jsonify, g, current_app
from opecflask.models.database import db_session
from opecflask.models.state import State
from opecflask.models.graph import Graph
from opecflask.models.quickregions import QuickRegions
from opecflask.models.roi import ROI
from opecflask.models.layergroup import LayerGroup
from opecflask.models.user import User
from opecflask.core import short_url
import datetime
import sqlite3 as sqlite

portal_state = Blueprint('portal_state', __name__)

@portal_state.route('/state/<stateUrl>', methods = ['GET'])     
def getState(stateUrl):
   # Decode url into a number to match to a state
   stateID = short_url.decode_url(stateUrl)
   output = {}
        
   if stateID is not None:      
      state = State.query.filter(stateID == State.id).first()
      if state != None:
         state.views += 1
         state.last_used = datetime.datetime.now()
         db_session.commit()
         
         output = stateToJSON(state)
         output['status'] = '200'
      else:
         output['error'] = 'Failed to find a state matching that url'  
         output['status'] = '404'           
      
   else:
      output['error'] = 'You must enter a valid state url'
      output['status'] = '400'
      
   try:
      jsonData = jsonify(output = output)
      #current_app.logger.debug('Request complete, Sending results') # DEBUG
      return jsonData
   except TypeError as e:
      g.error = "Request aborted, exception encountered: %s" % e
      abort(500) # If we fail to jsonify the data return 500
      
@portal_state.route('/state/<stateUrl>', methods = ['DELETE'])
def removeState(stateUrl):
   # Check if the user is logged in.
   if g.user is None:
      abort(401)
  
   email = g.user.email
   # Decode url into a number to match to a state
   stateID = short_url.decode_url(stateUrl)
   
   output = {}
   
   if email is None or stateID is None:
      output['status'] = 'Failed to remove state'
      output['email'] = email
      output['stateID'] = stateID
   else:
      # Might be able to use 'g.user' instead. Only reason I havn't is I'm not 
      # sure on the reliability of it.
      user = User.query.filter(User.email == email).first()
      
      if user is None: 
         # Create new user
         user = User(email)
         db_session.add(user)
         db_session.commit()
      
      state = user.states.filter(State.id == stateID).first()
      
      if state != None:
         db_session.delete(state)
         db_session.commit()
         
         output['message'] = 'Successfully removed state.'
         output['status'] = '200'
         
      else:
         output['message'] = 'Failed to remove state as no state with that ID could be found.'
         output['status'] = '404'
         
   try:
      jsonData = jsonify(output = output)
      #current_app.logger.debug('Request complete, Sending results') # DEBUG
      return jsonData
   except TypeError as e:
      g.error = "Request aborted, exception encountered: %s" % e
      abort(500) # If we fail to jsonify the data return 500
      
@portal_state.route('/state', methods = ['GET'])     
def getStates():
   # Check if the user is logged in.
   if g.user is None:
      abort(401)
      
   #TODO: Return available states filtered by email or other provided parameters.
   email = g.user.email
   
   output = {}
   
   if email is None:  
      output['message'] = 'You need to enter an email'
      output['status'] = '400'
   else: 
      user = User.query.filter(User.email == email).first()
      if user is None:
         output['message'] = 'No user with that email.'
         output['status'] = '400'
      else:
         states = user.states.all()
    
         for state in states:
            output[short_url.encode_url(state.id)] = stateToJSON(state)

   try:
      jsonData = jsonify(output = output)
      #current_app.logger.debug('Request complete, Sending results') # DEBUG
      return jsonData
   except TypeError as e:
      g.error = "Request aborted, exception encountered: %s" % e
      abort(500) # If we fail to jsonify the data return 500
   
     
@portal_state.route('/state', methods = ['POST'])      
def setState():
   # Check if the user is logged in.
   if g.user is None:
      abort(401)
   
   email = g.user.email
   state = request.values.get('state', None)
   
   output = {}
   
   if email is None or state is None:
      output['message'] = 'failed to store state'
      output['email'] = email
      output['state'] = state
      output['status'] = '404'
   else:
      # Might be able to use 'g.user' instead. Only reason I havn't is I'm not 
      # sure on the reliability of it.
      user = User.query.filter(User.email == email).first() 
      
      if user is None: 
         # Create new user
         user = User(email)
         db_session.add(user)
         db_session.commit()
              
      s = State(user.id, state)
      checksumMatch = user.states.filter(State.checksum == s.checksum).first()
      if checksumMatch == None:
         db_session.add(s)
         db_session.commit()
          
         output['url'] = short_url.encode_url(s.id)
         output['message'] = 'state stored'
         output['status'] = '200'
      else:
         output['url'] = short_url.encode_url(checksumMatch.id)
         output['message'] = 'Failed to add state as state already exists'
         output['status'] = '400'
   
   try:
      jsonData = jsonify(output = output)
      #current_app.logger.debug('Request complete, Sending results') # DEBUG
      return jsonData
   except TypeError as e:
      g.error = "Request aborted, exception encountered: %s" % e
      abort(500) # If we fail to jsonify the data return 500
   
def compareChecksum(hexdigest1, hexdigest2):
   return hexdigest1 == hexdigest2
   
      
def stateToJSON(state):
   output = {}
   output['url'] = short_url.encode_url(state.id)
   output['user_id'] = state.user_id
   output['state'] = state.state
   output['version'] = state.version
   output['views'] = state.views
   output['lastUsed'] = str(state.last_used)
   return output
