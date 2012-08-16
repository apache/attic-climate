#!/usr/local/bin/python
"""
 Small command line utility to find what the latitude and longitude variables are called in a model file.
 Background:  model output files tend not to follow any defined standard in terms of variable naming conventions.
              One model may call the latitude "lat", another one may call it "Latitudes"
              This script looks for the existence of any of a predefined list of synonyms for lat and long.

  This script should be run from the command line (i.e. not called from within python)

       Input: 
               -filename

       Output: 
               -success flag (1 or 0): were both latitude and longitude variable names found in the file?
            if successful:
               -name of latitude variable
               -name of longitude variable
               -latMin -descriptions of lat/lon ranges in data files
               -latMax
               -lonMin
               -lonMax
            if unsuccessful:
               -list of variable names in file

       (NB. all printed to standar output)

       Peter Lean   February 2011
"""

import sys
import Nio
import bottle
import json

#filename = sys.argv[1]

@bottle.route('/list/latlon/:filename#".*"#')
def find_latlon(filename):
  success = 0
  filename = filename.strip('"')
  f = Nio.open_file(filename)
  var_name_list = f.variables.keys()

  # convert all variable names into lower case
  var_name_list_lower = [x.lower() for x in var_name_list]

  # create a "set" from this list of names
  varset = set(var_name_list_lower)

  # Use "set" types for finding common variable name from in the file and from the list of possibilities
  lat_possible_names = set(['latitude','lat','lats','latitudes'])
  lon_possible_names = set(['longitude','lon','lons','longitudes'])

  # Search for common latitude name variants:
  # Find the intersection of two sets, i.e. find what latitude is called in this file.
  
  try:
    print 'hello from inside try block'
    lat_var_name = list(varset & lat_possible_names)[0]
    successlat = 1
    index = 0
    for i in var_name_list_lower: 
     if i==lat_var_name:
          whlat = index
     index += 1
    latname = var_name_list[whlat]

    lats = f.variables[latname][:]
    latMin = lats.min()
    latMax = lats.max()

  except:
    print 'exception happens'
    latname = 'not_found'
    successlat = 0

  # Search for common longitude name variants:
  # Find the intersection of two sets, i.e. find what longitude
  # is called in this file.
  try:
    lon_var_name = list(varset & lon_possible_names)[0]
    successlon = 1
    index = 0
    for i in var_name_list_lower:
     if i==lon_var_name:
          whlon = index
     index += 1
    lonname = var_name_list[whlon]

    lons = f.variables[lonname][:]
    #this will correct all lons to -180 , 180
    lons[lons>180]=lons[lons>180]-360
    
    lonMin = lons.min()
    lonMax = lons.max()

  except:
    lonname = 'not_found'
    successlon = 0

  
  if(successlat & successlon): 
     success = 1
  
  
  if success:
    print success, latname, lonname, latMin, latMax, lonMin, lonMax
    val_types= [int,str,str,str,str,str,str]
    success_values = [success, latname, lonname, latMin, latMax, lonMin, lonMax]
    value_names = ['success','latname','lonname','latMin','latMax','lonMin','lonMax']
    values = [vtypes(svalues) for vtypes,svalues in zip(val_types,success_values)]
    print values
    output = dict(zip(value_names,values))
    #json_output = json.dumps({'success':success,'latname':latname, \
    #                          'lonname':lonname,'latMin':latMin, \
    #                           'latMax':latMax,'lonMin':lonMin, \
    #                           'lonMax':lonMax }, sort_keys=True, indent=4)
    return output
    

  if success==0:
    json_output = json.dumps({'success':success,
                                 'variables':var_name_list }, \
                                sort_keys=True, indent=4)
    return json_output
    #print success, var_name_list

