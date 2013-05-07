#!/usr/local/bin/python
"""
    Small command line utility to find what the time variable is called in a model file.
    
    Background::  
        Model output files tend not to follow any defined standard in terms of 
        variable naming conventions.  One model may call the time "time", 
        another one may call it "t".  This script looks for the existence of 
        any of a predefined list of synonyms for time.
    
    This script should be run from the command line (i.e. not called from within python)
    
    Input::
        -filename
    
    Output::
        -success flag (1 or 0): were both latitude and longitude variable names found in the file?
        
        if successful:
            -name of time variable
            -(TODO) modelStartTime -descriptions of time ranges in data files
            -(TODO) modelEndTime
        if unsuccessful:
            -list of variable names in file
    
    (NB. all printed to standar output)
"""

import sys
import bottle
from bottle import request
import Nio
import json
import decode_model_times as dmt


#filename = sys.argv[1]


@bottle.route('/list/time/:filename#".*"#')
def list_time(filename):
    filename = filename.strip('"')
    success = 0
    f = Nio.open_file(filename)
    var_name_list = f.variables.keys()
    # convert all variable names into lower case
    var_name_list_lower = [x.lower() for x in var_name_list]
    # create a "set" from this list of names
    varset = set(var_name_list_lower)
    # Use "set" types for finding common variable name from in the file and from the list of possibilities
    time_possible_names = set(['time','t','times','date','dates','julian'])
    # Search for common latitude name variants:
    # Find the intersection of two sets, i.e. find what latitude is called in this file.
    try:
      time_var_name = list(varset & time_possible_names)[0]
      success = 1
      index = 0
      for i in var_name_list_lower:
       if i==time_var_name:
            wh = index
       index += 1
      timename = var_name_list[wh]
      
    except:
      timename = 'not_found'
      success = 0
    
    if success:
        print 'timename is '+timename
        times = dmt.decode_model_times([filename],timename)
        start_time = str(min(times))
        end_time = str(max(times))
        time_var = json.dumps({'success':success,'timename':timename,
                               'start_time':start_time,'end_time':end_time})
        #return time_var
        if (request.query.callback):
            return "%s(%s)" % (request.query.callback, time_var)
        return time_var
        
    if success==0:
        json_output = json.dumps({'success':success,'variables':var_name_list })
    if (request.query.callback):
        return "%s(%s)" % (request.query.callback, json_output)
    return json_output
       
    #print success, var_name_list

