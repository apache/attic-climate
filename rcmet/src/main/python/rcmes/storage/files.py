"""
Module for handling data input files.  Requires PyNIO and Numpy be 
installed.

This module can easily open NetCDF, HDF and Grib files.  Search the PyNIO
documentation for a complete list of supported formats.
"""

from os import path

try:
    import Nio
except ImportError:
    import nio as Nio

import numpy as np
import numpy.ma as ma
import sys

from toolkit import process
from utils import fortranfile


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

def getVariableRange(filename, variableName):
    """
    Function to return the min and max values of the given variable in
    the supplied filename.
   
    Input::
        filename - absolute path to a file
        variableName - variable whose min and max values should be returned

    Output::
        variableRange - tuple of order (variableMin, variableMax)
    """
    try:
        f = Nio.open_file(filename)
    except:
        #print 'PyNio had an issue opening the filename (%s) you provided' % filename
        print "NIOError:", sys.exc_info()[0]
        raise
    
    varArray = f.variables[variableName][:]
    return (varArray.min(), varArray.max())


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
    filename = filelist[0]
    # Crash nicely if 'filelist' is zero length
    """TODO:  Throw Error instead via try Except"""
    if len(filelist) == 0:
        print 'Error: no files have been passed to read_data_from_file_list()'
        sys.exit()

    # Open the first file in the list to:
    #    i) read in lats, lons
    #    ii) find out how many timesteps in the file 
    #        (assume same ntimes in each file in list)
    #     -allows you to create an empty array to store variable data for all times
    tmp = Nio.open_file(filename)
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
    timestore = ma.zeros((ntimes * len(filelist))) 
    
    # Now load in the data for real
    #  NB. no need to reload in the latitudes and longitudes -assume invariant
    i = 0
    timesaccu = 0 # a counter for number of times stored so far in t2store 
    #  NB. this method allows for missing times in data files 
    #      as no assumption made that same number of times in each file...


    for ifile in filelist:

        #print 'Loading data from file: ',filelist[i]
        f = Nio.open_file(ifile)
        t2raw = f.variables[myvar][:]
        timesraw = f.variables[timeVarName]
        time = timesraw[:]
        ntimes = len(time)
        print 'file= ', i, 'ntimes= ', ntimes, filelist[i]
        
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

    # Decode model times into python datetime objects. Note: timestore becomes a list (no more an array) here
    timestore, _ = process.getModelTimes(filename, timeVarName)
    
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

def read_lolaT_from_file(filename, latVarName, lonVarName, timeVarName, file_type):
    """
    Function that will return lat, lon, and time arrays
    
    Input::
        filename - the file to inspect
        latVarName - name of the Latitude Variable
        lonVarName - name of the Longitude Variable
        timeVarName - name of the Time Variable
        fileType = type of file we are trying to parse
    
    Output::
        lat - MESH GRID of Latitude values with shape (nx, ny)
        lon - MESH GRID of Longitude values with shape (nx, ny)
        timestore - Python list of Datetime objects
        
        MESHGRID docs: http://docs.scipy.org/doc/numpy/reference/generated/numpy.meshgrid.html
        
    """

    tmp = Nio.open_file(filename, format=file_type)
    lonsraw = tmp.variables[lonVarName][:]
    latsraw = tmp.variables[latVarName][:]
    lonsraw[lonsraw > 180] = lonsraw[lonsraw > 180] - 360.  # convert to -180,180 if necessary
    if(latsraw.ndim == 1):
        lon, lat = np.meshgrid(lonsraw, latsraw)
    if(latsraw.ndim == 2):
        lon = lonsraw
        lat = latsraw
    timestore, _ = process.getModelTimes(filename, timeVarName)
    print '  read_lolaT_from_file: Lats, lons and times read in for the model domain'
    return lat, lon, timestore

def read_data_from_one_file(ifile, myvar, timeVarName, lat, file_type):
    ##################################################################################
    # Read in data from one file at a time
    # Input:   filelist - list of filenames (including path)
    #          myvar    - string containing name of variable to load in (as it appears in file)
    # Output:  lat, lon - 2D array of latitude and longitude values
    #          times    - list of times
    #          t2store  - numpy array containing data from all files    
    # Modified from read_data_from_file_list to read data from multiple models into a 4-D array
    # 1. The code now processes model data that completely covers the 20-yr period. Thus,
    #    all model data must have the same time levels (ntimes). Unlike in the oroginal, ntimes
    #    is fixed here.
    # 2. Because one of the model data exceeds 240 mos (243 mos), the model data must be
    #    truncated to the 240 mons using the ntimes determined from the first file.
    ##################################################################################
    f = Nio.open_file(ifile)
    try:
        varUnit = f.variables[myvar].units.upper()
    except:
        varUnit = raw_input('Enter the model variable unit: \n> ').upper()
    t2raw = f.variables[myvar][:]
    t2tmp = t2raw.squeeze()
    if t2tmp.ndim == 2:
        t2tmp = np.expand_dims(t2tmp, 0)
    t2tmp = t2tmp
    f.close()
    print '  success read_data_from_one_file: VarName=', myvar, ' Shape(Full)= ', t2tmp.shape, ' Unit= ', varUnit
    timestore = process.decode_model_timesK(ifile, timeVarName, file_type)
    return timestore, t2tmp, varUnit

def find_time_var_name_from_file(filename, timename, file_type):
    # Function to find what the time variable is called in a model file.
    #       Input: 
    #               filelist -list of filenames
    #       Output: 
    #               -success flag (1 or 0): were both latitude and longitude variable names found in the file?
    #       Peter Lean   February 2011
    f = Nio.open_file(filename)
    var_name_list = f.variables.keys()

    # convert all variable names into lower case
    var_name_list_lower = [x.lower() for x in var_name_list]

    # create a "set" from this list of names
    varset = set(var_name_list_lower)

    # Use "set" types for finding common variable name from in the file and from the list of possibilities
    time_possible_names = set(['time', 'times', 'date', 'dates', 'julian'])


    # Search for common latitude name variants:
    # Find the intersection of two sets, i.e. find what latitude is called in this file.
    try:
        time_var_name = list(varset & time_possible_names)[0]
        success = 1
        index = 0
        for i in var_name_list_lower:
            if i == time_var_name:
                wh = index
            index += 1
        timename = var_name_list[wh]

    except:
        timename = 'not_found'
        success = 0

    if success == 0:
        timename = ''

    return success, timename, var_name_list

def find_latlon_var_from_file(filename, file_type, latname, lonname):
    # Function to find what the latitude and longitude variables are called in a model file.
    #       Input: 
    #               -filename 
    #       Output: 
    #               -success flag (1 or 0): were both latitude and longitude variable names found in the file?
    #               -latMin -descriptions of lat/lon ranges in data files
    #               -latMax
    #               -lonMin
    #               -lonMax
    #       Peter Lean   February 2011

    f = Nio.open_file(filename, mode='r', options=None, format=file_type)
    var_name_list = f.variables.keys()
    # convert all variable names into lower case
    var_name_list_lower = [x.lower() for x in var_name_list]
    # create a "set" from this list of names
    varset = set(var_name_list_lower)

    # Use "set" types for finding common variable name from in the file and from the list of possibilities
    lat_possible_names = set(['latitude', 'lat', 'lats', 'latitudes'])
    lon_possible_names = set(['longitude', 'lon', 'lons', 'longitudes'])
    
    # Search for common latitude name variants:
    # Find the intersection of two sets, i.e. find what latitude is called in this file.
    try:
        lats = f.variables[latname][:]
        successlat = 1
        latMin = lats.min()
        latMax = lats.max()
    
    except:
        latname = 'not_found'
        successlat = 0
    
    # Search for common longitude name variants:
    # Find the intersection of two sets, i.e. find what longitude is called in this file.
    try:
        lons = f.variables[lonname][:]
        successlon = 1
        lons[lons > 180] = lons[lons > 180] - 360.
        lonMin = lons.min()
        lonMax = lons.max()

    except:
        successlon = 0

    # check if both longs and lats are successfully read from the data file (send message only if unsuccessful).
    success = 0
    if(successlat == successlon == 1): success = 1
    #if success==1: print 'in rcmes_v12.find_latlon_var_from_file: both long/lat found'
    if success == 0:
        latname = lonname = latMin = lonMin = latMax = lonMax = ''
        print 'rcmes_v12.find_latlon_var_from_file: either/both long or/& lat corresponding'
        print '  to the provided var names are not found. Check your var names or data files: Exit'
        return -1, -1, -1, -1
    return success, latMin, latMax, lonMin, lonMax


def read_data_from_file_list_K(filelist, myvar, timeVarName, latVarName, lonVarName, file_type):
    ##################################################################################
    # Read in data from a list of model files into a single data structure
    # Input:   filelist - list of filenames (including path)
    #          myvar    - string containing name of variable to load in (as it appears in file)
    # Output:  lat, lon - 2D array of latitude and longitude values
    #          times    - list of times
    #          t2store  - numpy array containing data from all files    
    # Modified from read_data_from_file_list to read data from multiple models into a 4-D array
    # 1. The code now processes model data that completely covers the 20-yr period. Thus,
    #    all model data must have the same time levels (ntimes). Unlike in the oroginal, ntimes
    #    is fixed here.
    # 2. Because one of the model data exceeds 240 mos (243 mos), the model data must be
    #    truncated to the 240 mons using the ntimes determined from the first file.
    ##################################################################################
    filelist.sort()
    nfiles = len(filelist)
    # Crash nicely if 'filelist' is zero length
    if nfiles == 0:
        print 'Error: no files have been passed to read_data_from_file_list(): Exit'
        sys.exit()

    # Open the first file in the list to:
    #    i)  read in lats, lons
    #    ii) find out how many timesteps in the file (assume same ntimes in each file in list)
    #     -allows you to create an empty array to store variable data for all times
    tmp = Nio.open_file(filelist[0], format=file_type)
    latsraw = tmp.variables[latVarName][:]
    lonsraw = tmp.variables[lonVarName][:]
    lonsraw[lonsraw > 180] = lonsraw[lonsraw > 180] - 360.  # convert to -180,180 if necessary
    if(latsraw.ndim == 1):
        lon, lat = np.meshgrid(lonsraw, latsraw)
    if(latsraw.ndim == 2):
        lon = lonsraw; lat = latsraw
    
    timesraw = tmp.variables[timeVarName]
    ntimes = len(timesraw); nygrd = len(lat[:, 0]); nxgrd = len(lon[0, :])
    
    print 'Lats and lons read in for first file in filelist'

    # Create a single empty masked array to store model data from all files
    #t2store = ma.zeros((ntimes*nfiles,nygrd,nxgrd))
    t2store = ma.zeros((nfiles, ntimes, nygrd, nxgrd))
    #timestore=ma.zeros((ntimes*nfiles)) 
    
    ## Now load in the data for real
    ##  NB. no need to reload in the latitudes and longitudes -assume invariant
    #timesaccu=0 # a counter for number of times stored so far in t2store 
    #  NB. this method allows for missing times in data files 
    #      as no assumption made that same number of times in each file...

    i = 0
    for ifile in filelist:
        #print 'Loading data from file: ',filelist[i]
        f = Nio.open_file(ifile)
        t2raw = f.variables[myvar][:]
        timesraw = f.variables[timeVarName]
        time = timesraw[0:ntimes]
        #ntimes=len(time)
        #print 'file= ',i,'ntimes= ',ntimes,filelist[i]
        ## Flatten dimensions which needn't exist, i.e. level 
        ##   e.g. if for single level then often data have 4 dimensions, when 3 dimensions will do.
        ##  Code requires data to have dimensions, (time,lat,lon)
        ##    i.e. remove level dimensions
        t2tmp = t2raw.squeeze()
        ## Nb. if data happen to be for a single time, we flattened it by accident; lets put it back... 
        if t2tmp.ndim == 2:
            t2tmp = np.expand_dims(t2tmp, 0)
        #t2store[timesaccu+np.arange(ntimes),:,:]=t2tmp[0:ntimes,:,:]
        t2store[i, 0:ntimes, :, :] = t2tmp[0:ntimes, :, :]
        #timestore[timesaccu+np.arange(ntimes)]=time
        #timesaccu=timesaccu+ntimes
        f.close()
        i += 1 

    print 'Data read in successfully with dimensions: ', t2store.shape
    
    # Decode model times into python datetime objects. Note: timestore becomes a list (no more an array) here
    ifile = filelist[0]
    timestore, _ = process.getModelTimes(ifile, timeVarName)
    
    return lat, lon, timestore, t2store

def find_latlon_ranges(filelist, lat_var_name, lon_var_name):
    # Function to return the latitude and longitude ranges of the data in a file,
    # given the identifying variable names.
    #
    #    Input:
    #            filelist - list of filenames (data is read in from first file only)
    #            lat_var_name - variable name of the 'latitude' variable
    #            lon_var_name - variable name of the 'longitude' variable
    #
    #    Output:
    #            latMin, latMax, lonMin, lonMax - self explanatory
    #
    #                    Peter Lean      March 2011
    
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
        
        sys.exit()

def writeBN_lola(fileName, lons, lats):
    # write a binary data file that include longitude (1-d) and latitude (1-d) values
    
    F = fortranfile.FortranFile(fileName, mode='w')
    ngrdY = lons.shape[0]; ngrdX = lons.shape[1]
    tmpDat = ma.zeros(ngrdX); tmpDat[:] = lons[0, :]; F.writeReals(tmpDat)
    tmpDat = ma.zeros(ngrdY); tmpDat[:] = lats[:, 0]; F.writeReals(tmpDat)
    # release temporary arrays
    tmpDat = 0
    F.close()

def writeBNdata(fileName, numOBSs, numMDLs, nT, ngrdX, ngrdY, numSubRgn, obsData, mdlData, obsRgnAvg, mdlRgnAvg):
    #(fileName,maskOption,numOBSs,numMDLs,nT,ngrdX,ngrdY,numSubRgn,obsData,mdlData,obsRgnAvg,mdlRgnAvg):
    # write spatially- and regionally regridded data into a binary data file
    missing = -1.e26
    F = fortranfile.FortranFile(fileName, mode='w')
    # construct a data array to replace mask flag with a missing value (missing=-1.e12) for printing
    data = ma.zeros((nT, ngrdY, ngrdX))
    for m in np.arange(numOBSs):
        data[:, :, :] = obsData[m, :, :, :]; msk = data.mask
        for n in np.arange(nT):
            for j in np.arange(ngrdY):
                for i in np.arange(ngrdX):
                    if msk[n, j, i]: data[n, j, i] = missing

        # write observed data. allowed to write only one row at a time
        tmpDat = ma.zeros(ngrdX)
        for n in np.arange(nT):
            for j in np.arange(ngrdY):
                tmpDat[:] = data[n, j, :]
                F.writeReals(tmpDat)

    # write model data (dep. on the number of models).
    for m in np.arange(numMDLs):
        data[:, :, :] = mdlData[m, :, :, :]
        msk = data.mask
        for n in np.arange(nT):
            for j in np.arange(ngrdY):
                for i in np.arange(ngrdX):
                    if msk[n, j, i]:
                        data[n, j, i] = missing

        for n in np.arange(nT):
            for j in np.arange(ngrdY):
                tmpDat[:] = data[n, j, :]
                F.writeReals(tmpDat)

    data = 0     # release the array allocated for data
    # write data in subregions
    if numSubRgn > 0:
        print 'Also included are the time series of the means over ', numSubRgn, ' areas from obs and model data'
        tmpDat = ma.zeros(nT); print numSubRgn
        for m in np.arange(numOBSs):
            for n in np.arange(numSubRgn):
                tmpDat[:] = obsRgnAvg[m, n, :]
                F.writeReals(tmpDat)
        for m in np.arange(numMDLs):
            for n in np.arange(numSubRgn):
                tmpDat[:] = mdlRgnAvg[m, n, :]
                F.writeReals(tmpDat)
    tmpDat = 0     # release the array allocated for tmpDat
    F.close()

def writeNCfile(fileName, numSubRgn, lons, lats, obsData, mdlData, obsRgnAvg, mdlRgnAvg, obsList, mdlList, subRegions):
    # write an output file of variables up to 3 dimensions
    # fileName: the name of the output data file
    # numSubRgn  : the number of subregions
    # lons[ngrdX]: longitude
    # lats[ngrdY]: latitudes
    # obsData[nT,ngrdY,ngrdX]: the obs time series of the entire model domain
    # mdlData[numMDLs,nT,ngrdY,ngrdX]: the mdltime series of the entire model domain
    # obsRgnAvg[numSubRgn,nT]: the obs time series for the all subregions
    # mdlRgnAvg[numMDLs,numSubRgn,nT]: the mdl time series for the all subregions
    dimO = obsData.shape[0]      # the number of obs data
    dimM = mdlData.shape[0]      # the number of mdl data
    dimT = mdlData.shape[1]      # the number of time levels
    dimY = mdlData.shape[2]      # y-dimension
    dimX = mdlData.shape[3]      # x-dimension
    dimR = obsRgnAvg.shape[1]    # the number of subregions
    f = Nio.open_file(fileName, mode='w', format='nc')
    print mdlRgnAvg.shape, dimM, dimR, dimT
    #create global attributes
    f.globalAttName = ''
    # create dimensions
    print 'Creating Dimensions within the NetCDF Object...'
    f.create_dimension('unity', 1)
    f.create_dimension('time', dimT)
    f.create_dimension('west_east', dimX)
    f.create_dimension('south_north', dimY)
    f.create_dimension('obs', dimO)
    f.create_dimension('models', dimM)
        
    # create the variable (real*4) to be written in the file
    print 'Creating Variables...'
    f.create_variable('lon', 'd', ('south_north', 'west_east'))
    f.create_variable('lat', 'd', ('south_north', 'west_east'))
    f.create_variable('oDat', 'd', ('obss', 'time', 'south_north', 'west_east'))
    f.create_variable('mDat', 'd', ('models', 'time', 'south_north', 'west_east'))
    
    if subRegions:
        f.create_dimension('regions', dimR)
        f.create_variable('oRgn', 'd', ('obss', 'regions', 'time'))
        f.create_variable('mRgn', 'd', ('models', 'regions', 'time'))
        f.variables['oRgn'].varAttName = 'Observation time series: Subregions'
        f.variables['mRgn'].varAttName = 'Model time series: Subregions'

    loadDataIntoNetCDF(f, obsList, obsData, 'Observation')
    print 'Loaded the Observations into the NetCDF'

    loadDataIntoNetCDF(f, mdlList, mdlData, 'Model')

    # create attributes and units for the variable
    print 'Creating Attributes and Units...'
    f.variables['lon'].varAttName = 'Longitudes'
    f.variables['lon'].varUnit = 'degrees East'
    f.variables['lat'].varAttName = 'Latitudes'
    f.variables['lat'].varUnit = 'degrees North'
    f.variables['oDat'].varAttName = 'Observation time series: entire domain'
    f.variables['mDat'].varAttName = 'Model time series: entire domain'

    # assign the values to the variable and write it
    f.variables['lon'][:, :] = lons
    f.variables['lat'][:, :] = lats
    if subRegions:
        f.variables['oRgn'][:, :, :] = obsRgnAvg
        f.variables['mRgn'][:, :, :] = mdlRgnAvg

    f.close()

def loadDataIntoNetCDF(fileObject, datasets, dataArray, dataType):
    """
    Input::
        fileObject - PyNIO file object data will be loaded into
        datasets - List of dataset names
        dataArray - Multi-dimensional array of data to be loaded into the NetCDF file
        dataType - String with value of either 'Model' or 'Observation'
    Output::
        No return value.  PyNIO file object is updated in place
    """
    datasetCount = 0
    for dataset in datasets:
        if dataType.lower() == 'observation':
            datasetName = dataset.replace(' ','')
        elif dataType.lower() == 'model':
            datasetName = path.splitext(path.basename(dataset))[0]
        print "Creating variable %s" % datasetName
        fileObject.create_variable(datasetName, 'd', ('time', 'south_north', 'west_east'))
        fileObject.variables[datasetName].varAttName = 'Obseration time series: entire domain'
        print 'Loading values into %s' % datasetName
        fileObject.variables[datasetName].assign_value(dataArray[datasetCount,:,:,:])
        datasetCount += 1
