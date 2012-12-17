"""Collection of functions used to interface with the database
"""
import os
import urllib2
import re
import cPickle
import csv
import numpy as np
import numpy.ma as ma
import datetime
import pickle

from classes import RCMED

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

def extractData(datasetID, paramID, latMin, latMax, lonMin, lonMax, startTime, endTime, cachedir):
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
    
    # 0. Setup local variables to be used later
    url = RCMED.jplUrl(datasetID, paramID, latMin, latMax, lonMin, lonMax, startTime, endTime, cachedir)
    urlRequest = url.split('?')[1]

    pickleFilePath = os.path.abspath(cachedir + '/' + urlRequest + '.pic')

    if os.path.exists(pickleFilePath):
        print 'Retrieving data from cache (pickle file)'
        f = open(pickleFilePath, 'rb')
        store = cPickle.load(f)
        f.close()
        latitudes = store[0]
        longitudes = store[1]
        uniqueLevels = store[2]
        timesUnique = store[3]
        mdata = store[4]

        return latitudes, longitudes, uniqueLevels, timesUnique, mdata

    else:
        # 1. fetch the data from the database using url query api
        print 'Starting retrieval from DB (this may take several minutes)'
        
        '''TODO: - THIS IS WHERE WE NEED TO WORK ON SUPPORTING THE DOWNLOAD AND UNZIPPING
        OF THE DATABASE RETRIEVALS and converting them into pickle files for faster 
        read access'''
        cacheFilePath = os.path.abspath(cachedir + '/' + urlRequest + ".txt")
        result = urllib2.urlopen(url)
        datastring = result.read()
        #print datastring[-200:]
        # 2. Strip out data from returned string
        # Separate data and metadata sections from string returned by API
        # m = re.search('meta:', datastring)
        d = re.search('data: \r\n', datastring)
        #header = datastring[m.end():d.start()]
        datacsv = datastring[d.end():len(datastring)]
        # Strip out unnecessary '\r' from delimiters
        datacsv = re.sub('\r', '', datacsv)
        # Write data to temporary file ready to be read in by csv module (since problems with multi-line strings)
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
            values.append(np.float32(row[4]))
            # timestamps are strings so we will leave them alone for now
            timestamps.append(row[3])
        
        myfile.close()
        os.remove(cacheFilePath)
        # Make arrays of unique latitudes, longitudes, levels and times
        uniqueLatitudes = np.unique(latitudes)
        uniqueLongitudes = np.unique(longitudes)
        uniqueLevels = np.unique(levels)
        uniqueTimestamps = np.unique(timestamps)
        
        # Calculate nx and ny
        uniqueLongitudeCount = len(uniqueLongitudes)
        uniqueLatitudeCount = len(uniqueLatitudes)
        uniqueLevelCount = len(np.unique(levels))
        uniqueTimeCount = len(np.unique(timestamps))

        values, latitudes, longitudes = reorderXYT(latitudes, longitudes, timestamps, values)

        # Convert each unique time from strings into list of Python datetime objects
        # TODO - LIST COMPS!
        timeFormat = "%Y-%m-%d %H:%M:%S"
        timesUnique = [datetime.datetime.strptime(t, timeFormat) for t in uniqueTimestamps]
        timesUnique.sort()

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
        #msk = mdata.mask
        #print 'extract_from_db: after masking ',mdata[0,50,:]
        #print 'mask values: ',msk[0,50,:]; return -1
        
        # Save 'pickles' files (=direct memory dump to file) of data variables
        # for faster retrieval than txt cache files.
        f = open(pickleFilePath, 'wb')
        pickle.dump([latitudes, longitudes, uniqueLevels, timesUnique, mdata], f)
        f.close()
        return latitudes, longitudes, uniqueLevels, timesUnique, mdata
