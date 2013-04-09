"""
Collection of functions used to interface with the database and to create netCDF
"""
import os
import urllib2
import re
import csv
import numpy as np
import numpy.ma as ma
from datetime import timedelta ,datetime
from netCDF4 import Dataset
from classes import RCMED
import json
from toolkit import process



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

def extractData(datasetID, paramID, latMin, latMax, lonMin, lonMax, startTime, endTime, cachedir,timestep):
    """
    Main function to extract data from DB into numpy masked arrays
    
    Input::
        datasetID, paramID: required identifiers of data in database
        latMin, latMax, lonMin, lonMax: location range to extract data for
        startTime, endTime: python datetime objects describing required time range to extract
        cachedir: directory path used to store temporary cache files
    Output:
        uniqueLatitudes,uniqueLongitudes: 1d-numpy array of latitude and longitude grid values
        uniqueLevels:	1d-numpy array of vertical level values
        timesUnique: list of python datetime objects describing times of returned data
        mdata: masked numpy arrays of data values
    
    """
    url = RCMED.jplUrl(datasetID, paramID, latMin, latMax, lonMin, lonMax, startTime, endTime, cachedir,timestep)

    database,timestep,realm,instrument,start_date,end_date,unit=get_param_info(url)
    
    name=[]
    #create a directory inside the cachedir
    activity="obs4cmip5"
    name.append(activity)
    product="observations"
    name.append(product)
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
    
    #Satellite datasets filename
    processing_level='L3'
    processing_version="processing_version"
    start_date=str(startTime)[0:4]+str(startTime)[5:7]+str(startTime)[8:10]
    end_date=str(endTime)[0:4]+str(endTime)[5:7]+str(endTime)[8:10]
    netCD_fileName=variable + '_' + project + '_' + processing_level + '_' + processing_version + '_' + start_date + '_' + end_date + '.nc'
    
    if os.path.exists(path+"/"+netCD_fileName):
        latitudes, longitudes, uniqueLevels, timesUnique, mdata=read_netcdf(path+"/"+netCD_fileName,timestep)
    else:
        latitudes, longitudes, uniqueLevels, timesUnique, mdata=create_netCDF(url,cachedir,datasetID, paramID, latMin, latMax, lonMin, lonMax, startTime, endTime, unit, path+"/"+netCD_fileName,timestep)

    return latitudes, longitudes, uniqueLevels, timesUnique, mdata


def get_param_info(url):

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

    

def create_netCDF(url,cachedir,datasetID, paramID, latMin, latMax, lonMin, lonMax, startTime, endTime, unit,netCD_fileName,timestep):

        urlRequest = url.split('?')[1]
        urlRequest=urlRequest.replace('&','_')

        print 'Starting retrieval from DB (this may take several minutes)'
        cacheFilePath = os.path.abspath(cachedir + '/' + urlRequest + ".txt")
        result = urllib2.urlopen(url)
        datastring = result.read()
        d = re.search('data: \r\n', datastring)
        datacsv = datastring[d.end():len(datastring)]
        datacsv = re.sub('\r', '', datacsv)
        myfile = open(cacheFilePath, "w")
        myfile.write(datacsv)
        myfile.close()
        print 'Saved retrieved data to cache file: ' + cacheFilePath
        
        # Parse cache file csv data and close file
        myfile = open(cacheFilePath, "r")
        print 'Reading obs from cache file'
        csv_reader = csv.reader(myfile)
        
        latitudes = []
        longitudes = []
        levels = []
        values = []
        timestamps = []
        
        for row in csv_reader:
            latitudes.append(np.float32(row[0]))
            longitudes.append(np.float32(row[1]))
            levels.append(np.float32(row[2]))
            # timestamps are strings so we will leave them alone for now
            timestamps.append(row[3])
            values.append(np.float32(row[4]))
        
        myfile.close()
            
        lats=latitudes
        lons=longitudes
        lev=levels
        tim=timestamps
        val=values        
        hours=[]
        timeFormat = "%Y-%m-%d %H:%M:%S"
        base_time=datetime.strptime(tim[0], timeFormat)
        #Convert the date to hours 
        for t in tim:
            date=datetime.strptime(t, timeFormat)
            dif=date-base_time
            hours.append(dif.days*24)        
        os.remove(cacheFilePath)
        
        # Generate netCDF file from .txt file
        print "Generating netCDF file in the cache directory...."
        netcdf = Dataset(netCD_fileName, 'w') 
        netcdf.globalAttName = 'The netCDF file for dataset:',datasetID, ', parameter:',paramID, ', latMin: ',latMin, ', latMax: ',latMax, ', lonMin: ',lonMin, ', lonMax: ',lonMax,' startTime: ',tim[0],' and endTime: ',tim[len(tim)-1],'.' 
        netcdf.createDimension('dim', len(lats))
        latitude = netcdf.createVariable('lat', 'f4', ('dim'))
        longitude = netcdf.createVariable('lon', 'f4', ('dim'))
        level = netcdf.createVariable('lev', 'f4', ('dim'))
        time = netcdf.createVariable('time', 'd', ('dim'))
        value = netcdf.createVariable('value', 'f4', ('dim'))
        netcdf.variables['lat'].standard_name = 'latitude'
        latitude.units = 'degrees_north'
        netcdf.variables['lon'].standard_name = 'longitude'
        longitude.units = 'degrees_east'
        netcdf.variables['time'].standard_name = 'time'
        time.units= 'hours since ',tim[0]
        netcdf.variables['value'].standard_name = 'value'
        value.units = unit
        netcdf.variables['lev'].standard_name = 'level'
        level.units = 'hPa'
        latitude[:]=lats[:]
        longitude[:]=lons[:]
        level[:]=lev[:]
        time[:]=hours[:]
        value[:]=val[:]
        netcdf.close()
        latitudes, longitudes, uniqueLevels, timesUnique, mdata = read_netcdf(netCD_fileName,timestep)
        
        return latitudes, longitudes, uniqueLevels, timesUnique, mdata
    
def read_netcdf(netCD_fileName,timestep):
        # use the created netCDF file
        print 'Retrieving data from cache (netCDF file)'
        netcdf = Dataset(netCD_fileName, 'r')
        latitudes = netcdf.variables['lat'][:]
        longitudes = netcdf.variables['lon'][:]
        levels = netcdf.variables['lev'][:]
        hours = netcdf.variables['time'][:]
        values = netcdf.variables['value'][:]
        netcdf.close()
        
        # Because time in netCDF file is based on hours since a date, it needs to be converted to date
        times=[]
        t="2003-10-15 00:00:00"
        dt = datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
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
        timeFormat = "%Y-%m-%d %H:%M:%S"


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
    
