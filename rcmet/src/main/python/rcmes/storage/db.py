"""Collection of functions used to interface with the database and to create netCDF file
"""
import os
import urllib2
import re
import csv
import numpy as np
import numpy.ma as ma
import json
import Nio

from classes import RCMED
from toolkit import process
from datetime import timedelta ,datetime

def reorderXYT(lons, lats, times, values):
    # Re-order values in values array such that when reshaped everywhere is where it should be
    #  (as DB doesn't necessarily return everything in order)
    order = np.lexsort((lons, lats, times))
    counter = 0
    sortedValues = np.zeros_like(values)
    sortedLats = np.zeros_like(lats)
    sortedLons = np.zeros_like(lons)
    for i in order:
        sortedValues[counter] = values[i]
        sortedLats[counter] = lats[i]
        sortedLons[counter] = lons[i]
        counter += 1
    
    return sortedValues, sortedLats, sortedLons

def findUnique(seq, idfun=None):
    """
     Function to find unique values (used in construction of unique datetime list)
     NB. order preserving
     Input: seq  - a list of randomly ordered values
     Output: result - list of ordered values
    """
    if idfun is None:
        def idfun(x): 
            return x

    seen = {};
    result = []
    
    for item in seq:
        marker = idfun(item)
        # in old Python versions:
        # if seen.has_key(marker)
        # but in new ones:
        if marker in seen: continue
        seen[marker] = 1
        result.append(item)
    return result

def extractData(datasetID, paramID, latMin, latMax, lonMin, lonMax, startTime, endTime, cachedir, timestep):
    """
    Main function to extract data from DB into numpy masked arrays
    
    Input::
        datasetID, paramID: required identifiers of data in database
        latMin, latMax, lonMin, lonMax: location range to extract data for
        startTime, endTime: python datetime objects describing required time range to extract
        cachedir: directory path used to store temporary cache files
        timestep: "daily" | "monthly" so we can be sure to query the RCMED properly
    Output:
        uniqueLatitudes,uniqueLongitudes: 1d-numpy array of latitude and longitude grid values
        uniqueLevels:	1d-numpy array of vertical level values
        timesUnique: list of python datetime objects describing times of returned data
        mdata: masked numpy arrays of data values
    
    """
    
    url = RCMED.jplUrl(datasetID, paramID, latMin, latMax, lonMin, lonMax, startTime, endTime, cachedir, timestep) 

    # To get the parameter's information from parameter table
    database,timestep,realm,instrument,start_date,end_date,unit=get_param_info(url)
    
    # Create a directory inside the cachedir folder
    name=[]
    # activity is a fix value
    activity="obs4cmip5"
    name.append(activity)
    # product is a fix value
    product="observations"
    name.append(product)
    # realm, variable,frequency and instrument will be get from parameter table
    realm=realm
    name.append(realm)
    variable=database
    name.append(variable)
    frequency=timestep
    name.append(frequency)
    data_structure="grid"
    name.append(data_structure)
    institution="NASA"
    name.append(institution)
    project="RCMES"
    name.append(project)
    instrument=instrument
    name.append(instrument)
    version="v1"
    name.append(version)
    
    # Check to see whether the folder is already created for netCDF or not, then it will be created
    os.chdir(cachedir)
    path=os.getcwd()
    for n in name:
        if os.path.exists(path+"/"+n):
            os.chdir(path+"/"+n)
            path=os.getcwd()
        else:
            os.mkdir(n)
            os.chdir(path+"/"+n)
            path=os.getcwd()

    # To establish the netCDF file name
    processing_level='L3'
    processing_version="processing_version"  # the processing version is still unknown
    start_date=str(startTime)[0:4]+str(startTime)[5:7]+str(startTime)[8:10]
    end_date=str(endTime)[0:4]+str(endTime)[5:7]+str(endTime)[8:10]
    netCD_fileName=variable + '_' + project + '_' + processing_level + '_' + processing_version + '_' + str(latMin) + '_' + str(latMax) + '_' + str(lonMin) + '_' + str(lonMax) + '_' + start_date + '_' + end_date + '.nc'

    # To check if netCDF file  exists, then use it
    if os.path.exists(path+"/"+netCD_fileName):
        latitudes, longitudes, uniqueLevels, timesUnique, mdata=read_netcdf(path+"/"+netCD_fileName,timestep)
    # If the netCDF file does not exists, then create one.
    else:
        latitudes, longitudes, uniqueLevels, timesUnique, mdata=create_netCDF(url, database, latMin, latMax, lonMin, lonMax, startTime, endTime, unit, path+"/"+netCD_fileName,timestep)

    return latitudes, longitudes, uniqueLevels, timesUnique, mdata

def get_param_info(url):

    '''
    This function will get the general information by given URL from the parameter table.
    '''
    url=url + "&info=yes"
    result = urllib2.urlopen(url)
    datastring = result.read()
    datastring=json.loads(datastring)
    database=datastring["database"]
    timestep=datastring["timestep"]
    realm=datastring["realm"]
    instrument=datastring["instrument"]
    start_date=datastring["start_date"]
    end_date=datastring["end_date"]
    unit=datastring["units"]
    
    return database,timestep,realm,instrument,start_date,end_date,unit


def create_netCDF(url, database, latMin, latMax, lonMin, lonMax, startTime, endTime, unit, netCD_fileName, timestep):


        print 'Starting retrieval from DB (this may take several minutes)'
        result = urllib2.urlopen(url)
        datastring = result.read()    
        d = re.search('data: \r\n', datastring)
        datacsv = datastring[d.end():len(datastring)]
        
        # To create a list of all datapoints
        datacsv=datacsv.split('\r\n')    
                
        latitudes = []
        longitudes = []
        levels = []
        values = []
        timestamps = []
        
        # To make a series of lists from datapoints
        for i in range(len(datacsv)-1):  # Because the last row is empty, "len(datacsv)-1" is used.
            row=datacsv[i].split(',')
            latitudes.append(np.float32(row[0]))
            longitudes.append(np.float32(row[1]))
            levels.append(np.float32(row[2]))
            # timestamps are strings so we will leave them alone for now
            timestamps.append(row[3])
            values.append(np.float32(row[4]))
       
        hours=[]
        timeFormat = "%Y-%m-%d %H:%M:%S"
        base_date=datetime.strptime(timestamps[0], timeFormat)
        # To convert the date to hours 
        for t in timestamps:
            date=datetime.strptime(t, timeFormat)
            dif=date-base_date
            hours.append(dif.days*24)        

        
        # To generate netCDF file from database
        print "Generating netCDF file in the cache directory...."
        netcdf =  Nio.open_file(netCD_fileName,'w')
        string="The netCDF file for parameter: " + database + ", latMin: " + str(latMin) + ", latMax: " + str(latMax) + ", lonMin: " + str(lonMin) + ", lonMax: " + str(lonMax) + " startTime: " + str(timestamps[0]) + " and endTime: " + str(timestamps[len(timestamps)-1]) + "."
        netcdf.globalAttName = str(string)
        netcdf.create_dimension('dim', len(latitudes))
        latitude = netcdf.create_variable('lat', 'd', ('dim',))
        longitude = netcdf.create_variable('lon', 'd', ('dim',))
        level = netcdf.create_variable('lev', 'd', ('dim',))
        time = netcdf.create_variable('time', 'd', ('dim',))
        value = netcdf.create_variable('value', 'd', ('dim',))
        
        netcdf.variables['lat'].varAttName = 'latitude'
        netcdf.variables['lat'].units = 'degrees_north'
        netcdf.variables['lon'].varAttName = 'longitude'
        netcdf.variables['lon'].units = 'degrees_east'
        netcdf.variables['time'].varAttName = 'time'
        netcdf.variables['time'].units = 'hours since ' + str(timestamps[0])
        netcdf.variables['value'].varAttName = 'value'
        netcdf.variables['value'].units = str(unit)
        netcdf.variables['lev'].varAttName = 'level'
        netcdf.variables['lev'].units = 'hPa'
        latitude[:]=latitudes[:]
        longitude[:]=longitudes[:]
        level[:]=levels[:]
        time[:]=hours[:]
        value[:]=values[:]
        netcdf.close()
        
        latitudes, longitudes, uniqueLevels, timesUnique, mdata = read_netcdf(netCD_fileName,timestep)
        
        return latitudes, longitudes, uniqueLevels, timesUnique, mdata
    
def read_netcdf(netCD_fileName,timestep):
    
        # To use the created netCDF file
        print 'Retrieving data from cache (netCDF file)'
        netcdf = Nio.open_file(netCD_fileName , 'r')
        # To get all data from netCDF file
        latitudes = netcdf.variables['lat'][:]
        longitudes = netcdf.variables['lon'][:]
        levels = netcdf.variables['lev'][:]
        hours = netcdf.variables['time'][:]
        values = netcdf.variables['value'][:]
        
        # To get the base date
        time_unit=netcdf.variables['time'].units
        time_unit=time_unit.split(' ')
        base_data=time_unit[2] + " " + time_unit[3]
        
        netcdf.close()
        
        timeFormat = "%Y-%m-%d %H:%M:%S"
        
        # Because time in netCDF file is based on hours since a specific date, it needs to be converted to date format
        times=[]
        # To convert the base date to the python datetime format
        dt = datetime.strptime(base_data, timeFormat)
        for t in range(len(hours)):
            d=timedelta(hours[t]/24)    
            add=dt+d
            times.append(str(add.year) + '-' + str("%02d" % (add.month)) + '-' + str("%02d" % (add.day)) + ' ' + str("%02d" % (add.hour)) + ':' + str("%02d" % (add.minute)) + ':' + str("%02d" % (add.second)))
        
        # Make arrays of unique latitudes, longitudes, levels and times
        uniqueLatitudes = np.unique(latitudes)
        uniqueLongitudes = np.unique(longitudes)
        uniqueLevels = np.unique(levels)
        uniqueTimestamps = np.unique(times)
        
        # Calculate nx and ny
        uniqueLongitudeCount = len(uniqueLongitudes)
        uniqueLatitudeCount = len(uniqueLatitudes)
        uniqueLevelCount = len(uniqueLevels)
        uniqueTimeCount = len(uniqueTimestamps)

        values, latitudes, longitudes = reorderXYT(longitudes, latitudes, times, values)

        # Convert each unique time from strings into list of Python datetime objects
        # TODO - LIST COMPS!
        timesUnique = [datetime.strptime(t, timeFormat) for t in uniqueTimestamps]
        timesUnique.sort()
        timesUnique = process.normalizeDatetimes(timesUnique, timestep)

        # Reshape arrays
        latitudes = latitudes.reshape(uniqueTimeCount, uniqueLatitudeCount, uniqueLongitudeCount, uniqueLevelCount)
        longitudes = longitudes.reshape(uniqueTimeCount, uniqueLatitudeCount, uniqueLongitudeCount, uniqueLevelCount)
        levels = np.array(levels).reshape(uniqueTimeCount, uniqueLatitudeCount, uniqueLongitudeCount, uniqueLevelCount)
        values = values.reshape(uniqueTimeCount, uniqueLatitudeCount, uniqueLongitudeCount, uniqueLevelCount)

        # Flatten dimension if only single level
        if uniqueLevelCount == 1:
            values = values[:, :, :, 0]
            latitudes = latitudes[0, :, :, 0]
            longitudes = longitudes[0, :, :, 0]

        # Created masked array to deal with missing values
        #  -these make functions like values.mean(), values.max() etc ignore missing values
        mdi = -9999  # TODO: extract this value from the DB retrieval metadata
        mdata = ma.masked_array(values, mask=(values == mdi))
        
        return latitudes, longitudes, uniqueLevels, timesUnique, mdata
    