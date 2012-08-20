"""
Module for handling data input files.  Requires PyNIO and Numpy be 
installed.

This module can easily open NetCDF, HDF and Grib files.  Search the PyNIO
documentation for a complete list of supported formats.
"""

try:
    import Nio
except ImportError:
    import nio

import numpy as np
import numpy.ma as ma
import sys
import os

# Appending rcmes via relative path
sys.path.append(os.path.abspath('../.'))
import rcmes.toolkit.process

def findunique(seq):
    keys = {}
    for e in seq:
        keys[e] = 1
    return keys.keys()

def find_time_var_name_from_file(filelist):
   """ 
    Function to find what the time variable is called in a model file.
    
    Background:  model output files tend not to follow any defined standard in
    terms of variable naming conventions.  One model may call the time "time",
    another one may call it "t" and this script looks for the existence of 
    any of a predefined list of synonyms for time. 
       
    Input:: 
        filelist -list of filenames
   
    Output:: 
        success - flag (1 or 0): were both latitude and longitude variable names found in the file?
        timename - name of time variable
        var_name_list - list of variable names in file
    """
   filename = filelist[0]

   success = 0

   f = Nio.open_file(filename)
   var_name_list = f.variables.keys()

   # convert all variable names into lower case
   var_name_list_lower = [x.lower() for x in var_name_list]

   # create a "set" from this list of names
   varset = set(var_name_list_lower)

   # Use "set" types for finding common variable name from in the file and from the list of possibilities
   time_possible_names = set(['time','times','date','dates','julian'])


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

   if success==0:
      timename = ''

   return success, timename, var_name_list

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
     lons[lons>180]=lons[lons>180]-360.
     lonMin = lons.min()
     lonMax = lons.max()

     return latMin, latMax, lonMin, lonMax

   except:
     print 'Error: there was a problem with finding the latitude and longitude ranges in the file'
     print '       Please check that you specified the filename, and variable names correctly.'
 
     return 0,0,0,0

def find_latlon_var_from_file(filelist):
   """ 
   Function to find what the latitude and longitude variables are called in a model file.
    
   Background:
    
       Model output files tend not to follow any defined standard in terms of 
       variable naming conventions. One model may call the latitude "lat", 
       another one may call it "Latitudes" and this script looks for the 
       existence of any of a predefined list of synonyms for lat and long.
   
   Input:: 
       filename 
   
   Output::
       success - success flag (1 or 0): were both latitude and longitude variable names found in the file?
       latname - name of latitude variable
       lonname - name of longitude variable
       latMin -descriptions of lat/lon ranges in data files
       latMax
       lonMin
       lonMax
       var_name_list - list of variable names in file 
               
   **NB.** if unsuccessful then all variables will be empty except the final list of variable names.
   """
   filename = filelist[0]
   success = 0
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
     latname = 'not_found'
     successlat = 0

   # Search for common longitude name variants:
   # Find the intersection of two sets, i.e. find what longitude is called in this file.
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
     lons[lons>180]=lons[lons>180]-360.
     lonMin = lons.min()
     lonMax = lons.max()

   except:
     lonname = 'not_found'
     successlon = 0

   if(successlat & successlon): 
      success = 1

   if success==0:
      latname = lonname = latMin = lonMin = latMax = lonMax = ''

   return success, latname, lonname, latMin, latMax, lonMin, lonMax, var_name_list

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
   if len(filelist)==0:
      print 'Error: no files have been passed to read_data_from_file_list()'
      return -1,-1,-1,-1

   # Open the first file in the list to:
   #    i) read in lats, lons
   #    ii) find out how many timesteps in the file 
   #        (assume same ntimes in each file in list)
   #     -allows you to create an empty array to store variable data for all times
   tmp=Nio.open_file(filelist[0], format='nc')
   latsraw = tmp.variables[latVarName][:]
   lonsraw = tmp.variables[lonVarName][:]
   lonsraw[lonsraw>180] = lonsraw[lonsraw>180]-360.  # convert to -180,180 if necessary

   """TODO:  Guard against case where latsraw and lonsraw are not the same dim?"""
   
   if(latsraw.ndim == 1):
     lon,lat = np.meshgrid(lonsraw,latsraw)
   if(latsraw.ndim == 2):
     lon = lonsraw
     lat = latsraw

   timesraw = tmp.variables[timeVarName]
   ntimes=len(timesraw)

   print 'Lats and lons read in for first file in filelist'

   # Create a single empty masked array to store model data from all files
   t2store = ma.zeros((ntimes*len(filelist),len(lat[:,0]),len(lon[0,:])))
   timestore=np.empty((ntimes*len(filelist))) 
  

   # Now load in the data for real
   #  NB. no need to reload in the latitudes and longitudes -assume invariant
   i=0
   timesaccu=0 # a counter for number of times stored so far in t2store 
               #  NB. this method allows for missing times in data files 
               #      as no assumption made that same number of times in each file...


   for ifile in filelist:
     print 'Loading data from file: ',filelist[i]
     f=Nio.open_file(ifile)
     t2raw = f.variables[myvar][:]

     timesraw = f.variables[timeVarName]
     time=timesraw[:]
     ntimes=len(time)

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
     if t2tmp.ndim==2:
        t2tmp = np.expand_dims(t2tmp,0)

     t2store[timesaccu+np.arange(ntimes),:,:]=t2tmp[:,:,:]
     timestore[timesaccu+np.arange(ntimes)]=time
     timesaccu=timesaccu+ntimes
     f.close()
     i += 1 
     

   print 'Data read in successfully with dimensions: ',t2store.shape

   # TODO: search for duplicated entries (same time) and remove duplicates.
   # Check to see if number of unique times == number of times, if so then no problem

   if(len(np.unique(timestore))!=len(np.where(timestore!=0)[0].view())):
     print 'WARNING: Possible duplicated times'

   # Decode model times into python datetime objects
   timestore = rcmes.process.decode_model_times(filelist, timeVarName)

   data_dict = {}
   data_dict['lats'] = lat
   data_dict['lons'] = lon
   data_dict['times'] = timestore
   data_dict['data'] = t2store
   #return lat, lon, timestore, t2store
   return data_dict

def select_var_from_file(myfile,fmt='not set'):
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

   if fmt=='not set':
       f = Nio.open_file(myfile)

   if fmt!='not set':
       f = Nio.open_file(myfile,format=fmt)

   keylist = f.variables.keys()

   i = 0
   for v in keylist:
       print '[',i,'] ',f.variables[v].long_name,' (',v,')'
       i += 1

   user_selection = raw_input('Please select variable : [0 -'+str(i-1)+']  ')

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

   f = Nio.open_file(myfile,format='nc')

   keylist = f.variables.keys()

   i = 0
   for v in keylist:
       try:
         print '[',i,'] ',f.variables[v].description,' (',v,')'
       except:
         print ''

       i += 1

   user_selection = raw_input('Please select WRF variable : [0 -'+str(i-1)+']  ')

   mywrfvar = keylist[int(user_selection)]

   return mywrfvar
