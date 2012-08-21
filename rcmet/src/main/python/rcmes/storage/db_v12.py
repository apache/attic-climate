# Collection of functions used to interface with the database

def findUnique(seq, idfun=None): 
    # Function to find unique values (used in construction of unique datetime list)
    # NB. order preserving
    # Input: seq  - a list of randomly ordered values
    # Output: result - list of ordered values
    #
    if idfun is None:
      def idfun(x): return x
    seen = {}; result = []
    for item in seq:
        marker = idfun(item)
        # in old Python versions:
        # if seen.has_key(marker)
        # but in new ones:
        if marker in seen: continue
        seen[marker] = 1
        result.append(item)
    return result

def extract_data_from_db(datasetID, paramID, latMin, latMax, lonMin, lonMax, startTime, endTime, cachedir):
   # Main function to extract data from DB into numpy masked arrays
   # Input:
   #       datasetID, paramID  : 		required identifiers of data in database
   #       latMin, latMax, lonMin, lonMax:  	location range to extract data for
   #       startTime, endTime:  		python datetime objects describing required time range to extract
   #       cachedir:                            directory path used to store temporary cache files
   # Output:
   #	   lats_unique,lons_unique:		1d-numpy array of latitude and longitude grid values
   #       levs_unique:				1d-numpy array of vertical level values
   #       times_unique:			list of python datetime objects describing times of returned data
   #       mdata:				masked numpy arrays of data values
   #   Peter Lean August 2010
   import os
   import urllib2
   import re
   import csv
   import numpy
   import numpy.ma as ma
   import time, datetime
   import pickle

   ##########################################################
   # 1. fetch the data from the database using url query api
   ########################################################## 
   '''CGOODALE - One cosmetic improvement would be to handle the parsing of the date
   time objects into RCMES ISOFormatted strings better.  Just define a 
   function to turn a properly formed string'''

   # Construct appropriate URL using input parameters
   url_base='http://argo.jpl.nasa.gov/query-api/query.php?'

   url_request = 'datasetId='+str(datasetID)+'&parameterId='+str(paramID)+'&latMin='+str(latMin)+'&latMax='+str(latMax)+'&lonMin='+str(lonMin)+'&lonMax='+str(lonMax)+'&timeStart='+str(startTime.year)+str('%(#)02d' % { '#' : startTime.month })+str('%(#)02d' % { '#' : startTime.day })+'T'+str('%(#)02d' % { '#' : startTime.hour })+str('%(#)02d' % { '#' : startTime.minute })+'Z&timeEnd='+str(endTime.year)+str('%(#)02d' % { '#' : endTime.month })+str('%(#)02d' % { '#' : endTime.day })+'T'+str('%(#)02d' % { '#' : endTime.hour })+str('%(#)02d' % { '#' : endTime.minute })+'Z'

#   url_request = 'datasetId='+str(datasetID)+'&parameterId='+str(paramID)+'&latMin='+str(latMin)+'&latMax='+str(latMax)+'&lonMin='+str(lonMin)+'&lonMax='+str(lonMax)+'&timeStart='+str(startTime.year)+str('%(#)02d' % { '#' : startTime.month })+'Z&timeEnd='+str(endTime.year)+str('%(#)02d' % { '#' : endTime.month })+'Z'

   cache_filename = cachedir+'/'+url_request +".txt"
   pickle_filename = cachedir+'/'+url_request + '.pic'

   url = url_base + url_request

   # Check if data has already been downloaded and stored in a cache pickle file 
   # If so load the data from the picke file and return.
   #   NB. pickle files are raw binary memory dumps and hence are faster to load in than txt files.
   # TODO: now that pickles files are used as the cache, no need to store all old txt cache files.
   #            -only need to save latest one and can keep overwriting for each new DB retrieval.
   if(os.path.exists(pickle_filename)==True):
      print 'Retrieving data from cache (pickle file)'
      f = open(pickle_filename,'rb')
      store = pickle.load(f)
      f.close()
      lats = store[0]; lons = store[1]; levs_unique = store[2]; times_unique = store[3]
      mdata = store[4]
      #print times_unique
      return lats,lons,levs_unique,times_unique,mdata


   '''CGOODALE - We need to test this out and see if we can clean
   this up and instead rely entirely on the *.pic pickle file
   instead of trying to juggle the *pic and *txt files'''
   # Check if data has already been downloaded and stored in a cache txt file
   #  If it hasn't already been downloaded then first download the data + store in cache
   if(os.path.exists(cache_filename)==False):
      # Retrieve the data from the database API
     print 'Starting retrieval from DB (this may take several minutes)'
     '''CGOODALE - THIS IS WHERE WE NEED TO WORK ON SUPPORTING THE DOWNLOAD AND UNZIPPING
     OF THE DATABASE RETRIEVALS and converting them into pickle files for faster 
     read access'''
     result = urllib2.urlopen(url); datastring = result.read()
     print datastring[-200:]
      # 2. Strip out data from returned string
      # Separate data and metadata sections from string returned by API
     m = re.search('meta:',datastring)
     d = re.search('data: \r\n',datastring)
     header = datastring[m.end():d.start()]
     datacsv = datastring[d.end():len(datastring)]
      # Strip out unnecessary '\r' from delimiters
     datacsv = re.sub('\r','',datacsv)
      # Write data to temporary file ready to be read in by csv module (since problems with multi-line strings)
     myfile = open(cache_filename, "w")
     myfile.write(datacsv)
     myfile.close()
     print 'Saved retrieved data to cache file: '+cache_filename

    # Create blank lists
   latitudes=[]; longitudes=[]; levels=[]; timestmp=[]; values=[]

    # Open data from cache
   myfile = open(cache_filename,"r"); print 'Reading obs from cache file'
   csv_reader = csv.reader(myfile)
   for row in csv_reader:
      latitudes.append(row[0]); longitudes.append(row[1]); levels.append(row[2]); timestmp.append(row[3])
      values.append(row[4])

    # Calculate nx and ny
   nlon = len(numpy.unique(longitudes)); nlat = len(numpy.unique(latitudes))
   nlevs = len(numpy.unique(levels))   ; nt = len(numpy.unique(timestmp))

    # Convert from strings to correct types 
   lats = numpy.float32(latitudes); lons = numpy.float32(longitudes); levs = numpy.float32(levels)
   data = numpy.float32(values)

    # For now store times as a numpy array of strings
   timestamps = numpy.array(timestmp)
   #print 'timestamps = ',timestamps

    # Make arrays of unique lats, lons, levs and times
   lats_unique = numpy.unique(lats); lons_unique = numpy.unique(lons); levs_unique = numpy.unique(levs)

   times_unique_np = numpy.unique(timestamps)

   # Convert longitudes to standard format i.e. from 0->360 to -180 -> 180 (if necessary)
   # NB. should be redundant after db changes.
   #lons_unique[lons_unique>180] = lons_unique[lons_unique>180]-360

   # Re-order data in data array such that when reshaped everywhere is where it should be
   #  (as DB doesn't necessarily return everything in order)
   order = numpy.lexsort((lons,lats,timestamps))
   counter = 0
   data2 = numpy.zeros_like(data); lats2 = numpy.zeros_like(lats); lons2 = numpy.zeros_like(lons)
   for i in order:
      data2[counter] = data[i]; lats2[counter] = lats[i]; lons2[counter] = lons[i]
      counter += 1
   data = data2; data2 = 0
   lats = lats2; lats2 = 0
   lons = lons2; lons2 = 0

    # Convert each unique time from strings into list of Python datetime objects
   times_unique = []; timestamps = []; time_format = "%Y-%m-%d %H:%M:%S"
   for mytime in times_unique_np:
      times_unique.append(datetime.datetime.fromtimestamp(time.mktime(time.strptime(mytime, time_format))))

    # Re-order datetime list (data has already been sorted into datetime order, but date list has not yet)
   times_unique.sort()

    # Reshape arrays
   lats = lats.reshape(nt,nlat,nlon,nlevs)
   lons = lons.reshape(nt,nlat,nlon,nlevs)
   levs = levs.reshape(nt,nlat,nlon,nlevs)
   data = data.reshape(nt,nlat,nlon,nlevs)
   #print 'extract_from_db: raw data ',data[0,50,:,0]

    # Flatten dimension if only single level
   if nlevs==1:
      data = data[:,:,:,0]; lats = lats[0,:,:,0]; lons = lons[0,:,:,0]
    # Created masked array to deal with missing data
    #  -these make functions like data.mean(), data.max() etc ignore missing data
   mdi=-9999  # TODO: extract this value from the DB retrieval meta data
   mdata = ma.masked_array(data,mask=(data==mdi))
   #msk = mdata.mask
   #print 'extract_from_db: after masking ',mdata[0,50,:]
   #print 'mask values: ',msk[0,50,:]; return -1
    # If pickle file not yet created then create one now for next time.
    # Save 'pickles' files (=direct memory dump to file) of data variables
    # for faster retrieval than txt cache files.
   if(os.path.exists(pickle_filename)==False):
      f = open(pickle_filename,'wb')
      status = pickle.dump([lats,lons,levs_unique,times_unique,mdata],f)
      f.close()
   return lats,lons,levs_unique,times_unique,mdata

class dataset:
    def __init__(self):
       self.name = []
       self.ID = []
       self.parameters = []
       self.parameterIDs = []
