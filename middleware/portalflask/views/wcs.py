from flask import Blueprint, abort, request, jsonify, g, current_app
from portalflask.core.param import Param
from portalflask.core import error_handler
import portalflask.core.geometry_support as geometry_support
import portalflask.core.graph_support as graph_support

import urllib
import urllib2
import os
import tempfile
import numpy as np

portal_wcs = Blueprint('portal_wcs', __name__)

"""
Gets wcs data from a specified server, then performs a requested function
on the received data, before jsonifying the output and returning it.
"""
@portal_wcs.route('/wcs', methods=['POST'])
def getWcsData():

   graph_to_method = {
        'histogram': get_histogram,
        'timeseries': get_timeseries,
        'hovmollerLon': get_hovmoller,
        'hovmollerLat': get_hovmoller
   }

   wkt = request.headers['wkt']

   g.graphError = ""

   params = getParams(wkt)  # Gets any parameters
   params = checkParams(params)  # Checks what parameters where entered

   params['url'] = createURL(params)
   current_app.logger.debug('Processing request...')  # DEBUG
   current_app.logger.debug(params['url'].value)
   graph_type = params['graphType'].value

   method = graph_to_method[graph_type]
   output = getDataSafe(params, method)

   current_app.logger.debug('Jsonifying response...')  # DEBUG
   
   try:
      jsonData = jsonify(output=output, type=params['graphType'].value, coverage=params['coverage'].value, error=g.graphError)
   except TypeError as e:
      g.error = "Request aborted, exception encountered: %s" % e
      error_handler.setError('2-06', None, g.user.id, "views/wcs.py:getWcsData - Type erro, returning 400 to user. Exception %s" % e, request)
      abort(400) # If we fail to jsonify the data return 400
      
   current_app.logger.debug('Request complete, Sending results') # DEBUG
   
   return jsonData


def get_histogram(params):
    import beampy  # import here, because importing may take a while
    ncfile_name = params['file_name']
    variable_name = params['coverage'].value
    wkt = params['wkt'].value

    product = beampy.ProductIO.readProduct(ncfile_name)
    mask = geometry_support.create_mask(product, wkt)
    data = graph_support.get_band_data_as_array(variable_name, product, mask)
    product.dispose()
    return {'histogram': histogram(data)}


def get_hovmoller(params):
    import beampy  # import here, because importing may take a while
    ncfile_name = params['file_name']
    variable_name = params['graphZAxis'].value
    wkt = params['wkt'].value

    product = beampy.ProductIO.readProduct(ncfile_name)
    mask = geometry_support.create_mask(product, wkt)
    hovmoller = graph_support.get_hovmoller(product, variable_name, mask, params['graphXAxis'].value,
                                            params['graphYAxis'].value)
    product.dispose()
    return hovmoller


def get_timeseries(params):
    import beampy  # import here, because importing may take a while

    ncfile_name = params['file_name']
    variable_name = params['coverage'].value
    wkt = params['wkt'].value

    shape = geometry_support.get_shape(wkt)
    product = beampy.ProductIO.readProduct(ncfile_name)

    timeseries = graph_support.get_timeseries(product, variable_name, shape)
    product.dispose()
    return timeseries


"""
Gets any parameters.
"""
def getParams(wkt):
   # Required for url
   nameToParam = {}
   nameToParam["baseURL"] = Param("baseURL", False, False, request.args.get('baseurl'))
   nameToParam["service"] = Param("service", False, True, 'WCS')
   nameToParam["request"] = Param("request", False, True, 'GetCoverage')
   nameToParam["version"] = Param("version", False, True, request.args.get('version', '1.0.0'))
   nameToParam["format"] = Param("format", False, True, request.args.get('format', 'NetCDF3'))
   nameToParam["coverage"] = Param("coverage", False, True, request.args.get('coverage'))
   nameToParam["crs"] = Param("crs", False, True, 'OGC:CRS84')
   
   # Optional extras
   nameToParam["time"] = Param("time", True, True, request.args.get('time', None))
   nameToParam["vertical"] = Param("vertical", True, True, request.args.get('depth', None))
   
   # Geometry spec
   nameToParam["wkt"] = Param("wkt", True, False, wkt)
   nameToParam["bbox"] = Param("bbox", False, True, geometry_support.get_bounding_box(nameToParam['wkt'].value))

   # Custom
   nameToParam["graphType"] = Param("graphType", False, False, request.args.get('graphType'))
   nameToParam["graphXAxis"] = Param("graphXAxis", True, False, request.args.get('graphXAxis'))
   nameToParam["graphYAxis"] = Param("graphYAxis", True, False, request.args.get('graphYAxis'))
   nameToParam["graphZAxis"] = Param("graphZAxis", True, False, request.args.get('graphZAxis'))
   
   nameToParam["graphXFunc"] = Param("graphXFunc", True, False, request.args.get('graphXFunc'))
   nameToParam["graphYFunc"] = Param("graphYFunc", True, False, request.args.get('graphYFunc'))
   nameToParam["graphZFunc"] = Param("graphZFunc", True, False, request.args.get('graphZFunc'))
   
   return nameToParam


"""
Check the parameters to see if they are valid.
"""
def checkParams(params):    
   checkedParams = {}
   
   for key in params.iterkeys():
      if params[key].value is None or len(params[key].value) == 0:
         if not params[key].isOptional():            
            error = 'required parameter "%s" is missing or is set to an invalid value' % key
            g.error = error
            print(error)
            user_id = g.user.id if g.user is not None else ''
            error_handler.setError('2-06', None, user_id, "views/wcs.py:checkParams - Parameter is missing or invalid, returning 400 to user. Parameter %s" % key, request)
            abort(400)
      else:
         checkedParams[key] = params[key]
         
   return checkedParams


"""
Create the url that will be used to contact the wcs server.
"""
def createURL(params):
   urlParams = {}
   for param in params.itervalues():
      if param.neededInUrl():
         urlParams[param.getName()] = param.value

   query = urllib.urlencode(urlParams)
   url = params['baseURL'].value + query
   current_app.logger.debug('URL: ' + url) # DEBUG
   if "wcs2json/wcs" in params['baseURL'].value:
      g.error = 'possible infinite recursion detected, cancelled request'
      error_handler.setError('2-06', None, g.user.id, "views/wcs.py:createURL - Possible recursion detected, returning 400 to user.", request)
      abort(400)
   return Param("url", False, False, url)


def contactWCSServer(url):
   current_app.logger.debug('Contacting WCS Server with request...')
   current_app.logger.debug(url)
   resp = urllib2.urlopen(url)
   current_app.logger.debug('Request successful')
   return resp


def saveOutTempFile(resp):
   current_app.logger.debug('Saving out temporary file...')
   temp = tempfile.NamedTemporaryFile('w+b', delete=False, dir='/tmp')
   temp.write(resp.read())
   temp.close()
   resp.close()
   current_app.logger.debug('Temporary file saved successfully')
   return temp.name


def expandBbox(params):
   # TODO: try except for malformed bbox
   current_app.logger.debug('Expanding Bbox...')
   increment = 0.1
   values = params['bbox'].value.split(',')
   for i,v in enumerate(values):
      values[i] = float(values[i]) # Cast string to float
      if i == 0 or i == 1:
         values[i] -= increment
      elif i == 2 or i == 3:
         values[i] += increment
      values[i] = str(values[i])
   params['bbox'].value = ','.join(values)
   current_app.logger.debug(','.join(values))
   current_app.logger.debug('New Bbox %s' % params['bbox'].value)
   current_app.logger.debug('Bbox Expanded')
   # Recreate the url
   current_app.logger.debug('Recreating the url...')
   params['url'] = createURL(params)
   current_app.logger.debug('Url recreated')
   return params


"""
Generic method for getting data from a wcs server
"""
def getData(params, method):
   resp = contactWCSServer(params['url'].value)
   fileName = saveOutTempFile(resp)
   params['file_name'] = fileName
   output = method(params)
   os.remove(fileName)
   current_app.logger.debug('Process complete, returning data for transmission...')
   return output


"""
Tries to get a single point of data to return
"""      
def getPointData(params, method):
   current_app.logger.debug('Beginning try to get point data...')
   for x in range(10) :
      current_app.logger.debug('Attempt %s' % (x + 1))
      #expand box
      params = expandBbox(params)
      try:
         return getData(params, method)
      except urllib2.URLError as e:
         if hasattr(e, 'code'): # check for the code attribute from urllib2.urlopen
            current_app.logger.debug(e.code)
            if e.code != 400:
               g.graphError = "Failed to make a valid connection with the WCS server"
               return {}
            else:
               current_app.logger.debug('Made a bad request to the WCS server')
   
   # If we get here, then no point found
   g.graphError = "Could not retrieve a data point for that area"
   return {}


def getDataSafe(params, method):
   try:
      return getData(params, method)
   except urllib2.URLError as e:
      print(e)
      if hasattr(e, 'code'): # check for the code attribute from urllib2.urlopen
         if e.code == 400:
            g.error = "Failed to access url, make sure you have entered the correct parameters."
         if e.code == 500:
            g.error = "Sorry, looks like one of the servers you requested data from is having trouble at the moment. It returned a 500."
         abort(400)

      g.error = "Failed to access url, make sure you have entered the correct parameters"
      error_handler.setError('2-06', None, g.user.id, "views/wcs.py:getDataSafe - Failed to access url, returning 400 to user. Exception %s" % e, request)
      abort(400) # return 400 if we can't get an exact code


def histogram(arr):
    maskedarr = np.ma.masked_array(arr, [np.isnan(x) for x in arr])
    bins = request.args.get('bins', None) # TODO move to get params
    numbers = []
    current_app.logger.debug('before bins') # DEBUG

    if bins == None or not bins:
        bins = np.linspace(float(np.min(maskedarr)), float(np.max(maskedarr)), 11)  # Create ten evenly spaced bins
        current_app.logger.debug('bins generated') # DEBUG
        N, bins = np.histogram(maskedarr, bins) # Create the histogram
    else:
        values = bins.split(',')
        for i,v in enumerate(values):
            values[i] = float(values[i]) # Cast string to float
        bins = np.array(values)
        current_app.logger.debug('bins converted') # DEBUG
        N,bins = np.histogram(maskedarr, bins) # Create the histogram

    current_app.logger.debug('histogram created') # DEBUG
    for i in range(len(bins)-1): # Iter over the bins
        if np.isnan(bins[i]) or np.isnan(bins[i+1] or np.isnan(N[i])):
            g.graphError = 'no valid data available to use'
            return

        numbers.append((bins[i] + (bins[i+1] - bins[i])/2, float(N[i])))  # Get a number halfway between this bin and the next
    return {'Numbers': numbers, 'Bins': bins.tolist()}