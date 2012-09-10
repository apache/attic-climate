"""
Module for handling data input files.  Requires PyNIO and Numpy be 
installed.

This module can easily open NetCDF, HDF and Grib files.  Search the PyNIO
documentation for a complete list of supported formats.
"""

try:
    import Nio
except ImportError:
    import nio as Nio

import numpy as np
import numpy.ma as ma
import sys

import toolkit.process as process


VARIABLE_NAMES = {'time': ['time', 'times', 'date', 'dates', 'julian'],
                  'latitude': ['latitude', 'lat', 'lats', 'latitudes'],
                  'longitude': ['longitude', 'lon', 'lons', 'longitudes']
                  }


def findunique(seq):
    keys = {}
    for e in seq:
        keys[e] = 1
    return keys.keys()

def getVariableByType(filename, variableType):
    """
    Function that will try to return the variable from a file based on a provided
    parameter type.
    
    Input::
        filename - the file to inspect
        variableType - time | latitude | longitude
    
    Output::
        variable name OR list of all variables in the file if a single variable
        name match cannot be found.
    """
    try:
        f = Nio.open_file(filename)
    except:
        #print 'PyNio had an issue opening the filename (%s) you provided' % filename
        print "NIOError:", sys.exc_info()[0]
        raise
    
    variableKeys = f.variables.keys()
    f.close()
    variableKeys = [variable.lower() for variable in variableKeys]
    variableMatch = VARIABLE_NAMES[variableType]

    commonVariables = list(set(variableKeys).intersection(variableMatch)) 

    if len(commonVariables) == 1:
        return str(commonVariables[0])
    
    else:
        return variableKeys


def find_latlon_ranges(filelist, lat_var_name, lon_var_name):
   """
    Function to return the latitude and longitude ranges of the data in a file,
    given the identifying variable names.
   
       Input:
               filelist - list of filenames (data is read in from first file only)
               lat_var_name - variable name of the 'latitude' variable
               lon_var_name - variable name of the 'longitude' variable
   
       Output:
               latMin, latMax, lonMin, lonMax - self explanatory
   
                       Peter Lean      March 2011
   """
   filename = filelist[0]

   try:
     f = Nio.open_file(filename)

     lats = f.variables[lat_var_name][:]
     latMin = lats.min()
     latMax = lats.max()

     lons = f.variables[lon_var_name][:]
     lons[lons > 180] = lons[lons > 180] - 360.
     lonMin = lons.min()
     lonMax = lons.max()

     return latMin, latMax, lonMin, lonMax

   except:
     print 'Error: there was a problem with finding the latitude and longitude ranges in the file'
     print '       Please check that you specified the filename, and variable names correctly.'
 
     return 0, 0, 0, 0

def read_data_from_file_list(filelist, myvar, timeVarName, latVarName, lonVarName):
   '''
    Read in data from a list of model files into a single data structure
   
    Input:
       filelist - list of filenames (including path)
       myvar    - string containing name of variable to load in (as it appears in file)
    Output:
       lat, lon - 2D array of latitude and longitude values
       timestore    - list of times
       t2store  - numpy array containing data from all files    
   
     NB. originally written specific for WRF netCDF output files
         modified to make more general (Feb 2011)
   
      Peter Lean July 2010 
   '''

   filelist.sort()

   # Crash nicely if 'filelist' is zero length
   """TODO:  Throw Error instead via try Except"""
   if len(filelist) == 0:
      print 'Error: no files have been passed to read_data_from_file_list()'
      return -1, -1, -1, -1

   # Open the first file in the list to:
   #    i) read in lats, lons
   #    ii) find out how many timesteps in the file 
   #        (assume same ntimes in each file in list)
   #     -allows you to create an empty array to store variable data for all times
   tmp = Nio.open_file(filelist[0], format='nc')
   latsraw = tmp.variables[latVarName][:]
   lonsraw = tmp.variables[lonVarName][:]
   lonsraw[lonsraw > 180] = lonsraw[lonsraw > 180] - 360.  # convert to -180,180 if necessary

   """TODO:  Guard against case where latsraw and lonsraw are not the same dim?"""
   
   if(latsraw.ndim == 1):
     lon, lat = np.meshgrid(lonsraw, latsraw)
   if(latsraw.ndim == 2):
     lon = lonsraw
     lat = latsraw

   timesraw = tmp.variables[timeVarName]
   ntimes = len(timesraw)

   print 'Lats and lons read in for first file in filelist'

   # Create a single empty masked array to store model data from all files
   t2store = ma.zeros((ntimes * len(filelist), len(lat[:, 0]), len(lon[0, :])))
   timestore = np.empty((ntimes * len(filelist))) 
  

   # Now load in the data for real
   #  NB. no need to reload in the latitudes and longitudes -assume invariant
   i = 0
   timesaccu = 0 # a counter for number of times stored so far in t2store 
               #  NB. this method allows for missing times in data files 
               #      as no assumption made that same number of times in each file...


   for ifile in filelist:
     print 'Loading data from file: ', filelist[i]
     f = Nio.open_file(ifile)
     t2raw = f.variables[myvar][:]

     timesraw = f.variables[timeVarName]
     time = timesraw[:]
     ntimes = len(time)

     # Flatten dimensions which needn't exist, i.e. level 
     #   e.g. if for single level then often data have 4 dimensions, when 3 dimensions will do.
     #  Code requires data to have dimensions, (time,lat,lon)
     #    i.e. remove level dimensions
     # Remove 1d axis from the t2raw array
     # Example: t2raw.shape == (365, 180, 360 1) <maps to (time, lat, lon, height)>
     # After the squeeze you will be left with (365, 180, 360) instead
     t2tmp = t2raw.squeeze()
     # Nb. if this happens to be data for a single time only, then we just flattened it by accident
     #     lets put it back... 
     if t2tmp.ndim == 2:
        t2tmp = np.expand_dims(t2tmp, 0)

     t2store[timesaccu + np.arange(ntimes), :, :] = t2tmp[:, :, :]
     timestore[timesaccu + np.arange(ntimes)] = time
     timesaccu = timesaccu + ntimes
     f.close()
     i += 1 
     

   print 'Data read in successfully with dimensions: ', t2store.shape

   # TODO: search for duplicated entries (same time) and remove duplicates.
   # Check to see if number of unique times == number of times, if so then no problem

   if(len(np.unique(timestore)) != len(np.where(timestore != 0)[0].view())):
     print 'WARNING: Possible duplicated times'

   # Decode model times into python datetime objects
   timestore = process.decode_model_times(filelist, timeVarName)

   data_dict = {}
   data_dict['lats'] = lat
   data_dict['lons'] = lon
   data_dict['times'] = timestore
   data_dict['data'] = t2store
   #return lat, lon, timestore, t2store
   return data_dict

def select_var_from_file(myfile, fmt='not set'):
   '''
    Routine to act as user interface to allow users to select variable of interest from a file.
    
     Input:
        myfile - filename
        fmt - (optional) specify fileformat for PyNIO if filename suffix is non-standard
   
     Output:
        myvar - variable name in file
   
       Peter Lean  September 2010
   '''

   print fmt

   if fmt == 'not set':
       f = Nio.open_file(myfile)

   if fmt != 'not set':
       f = Nio.open_file(myfile, format=fmt)

   keylist = f.variables.keys()

   i = 0
   for v in keylist:
       print '[', i, '] ', f.variables[v].long_name, ' (', v, ')'
       i += 1

   user_selection = raw_input('Please select variable : [0 -' + str(i - 1) + ']  ')

   myvar = keylist[int(user_selection)]

   return myvar

def select_var_from_wrf_file(myfile):
   '''
    Routine to act as user interface to allow users to select variable of interest from a wrf netCDF file.
    
     Input:
        myfile - filename
   
     Output:
        mywrfvar - variable name in wrf file
   
       Peter Lean  September 2010
   '''

   f = Nio.open_file(myfile, format='nc')

   keylist = f.variables.keys()

   i = 0
   for v in keylist:
       try:
         print '[', i, '] ', f.variables[v].description, ' (', v, ')'
       except:
         print ''

       i += 1

   user_selection = raw_input('Please select WRF variable : [0 -' + str(i - 1) + ']  ')

   mywrfvar = keylist[int(user_selection)]

   return mywrfvar
