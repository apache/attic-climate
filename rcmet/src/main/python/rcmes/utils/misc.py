"""Module with a collection of helper functions"""


import ConfigParser
import datetime
import glob
import json
import os
import sys

import numpy as np
import numpy.ma as ma
import netCDF

import classes

from fortranfile import FortranFile

def reshapeMonthlyData(dataset1):
    """
    Purpose::
       Returns a view of an array with shape (nMonth, ...)
       reshaped to (nYR, 12, ...) in order to assist in monthly
       calculations
    Input::
       dataset1 - an input array with the first dimension corresponding
       to the number of months, which must be a multiple of 12
    Output::
       data - A view of dataset1 but with shape (nYR, 12, ...).
    """
    
    # Create a view of dataset1. This lets us change the shape
    # without copying or modifying the original array.
    data = dataset1[:]
    ishape = data.shape
    nMonth = ishape[0]
    nshape = nMonth/12, 12
    
    # Combine the number of years / months (nshape) with other dimensions
    data.shape = tuple(list(nshape) + list(ishape[1:]))
    return data

def configToDict(config):
    """
    Helper function to parse a configuration input and return a python dictionary
    
    Input::  
        config - list of ('key', 'value') tuples from ConfigParser.
            key01 - string i.e. 'value01'
            key-2 - string i.e. 'value02'
    Output::
        configDict - Dictionary of Key/Value pairs
    """
    configDict = {}
    for entry in config:
        configDict[entry[0]] = entry[1]

    return configDict


def readSubRegionsFile(regionsFile):
    """
    Input::
        regionsFile - Path to a subRegion configuration file
        
    Output::
        Ordered List of SubRegion Objects decoded from regionsFile
    """
    if os.path.exists(regionsFile):
        regionsConfig = ConfigParser.SafeConfigParser()
        regionsConfig.optionxform = str
        regionsConfig.read(regionsFile)
        regions = generateSubRegions(regionsConfig.items('REGIONS'))

        return regions
    else:
        raise IOError

def getSubRegionsInteractively(counts, workdir):
    """
    Purpose::
        This function provides a commandline Q&A session to help users define 
        SubRegion Objects.
    Input::
        counts - dictionary with int counts of various metric inputs
            i.e. {'observations': 3,
                  'models'      : 1,
                  'times'       : 120}
        workdir - string of the current working directory where auxillary files
        can be found.  In this case the directory will be used to locate an 
        existing sub_regions.txt file.

    Output:: 
        subRegions = List of Parsed SubRegion Objects based on User inputs 
    """
    do_timeseries = None
    yes_no_list = ['y', 'n', '']
    
    while do_timeseries not in yes_no_list:
        do_timeseries = raw_input('Calculate area-mean timeseries for subregions? y/n: [n] \n>>>')
        if do_timeseries not in yes_no_list:
            print("'%s' is not a valid answer please try again" % do_timeseries)

    if do_timeseries == 'y':
        interactive_subregions = None
        while interactive_subregions not in yes_no_list:
            interactive_subregions = raw_input('Input Sub Region info interactively? y/n: [n] \n>>>')
            if interactive_subregions not in yes_no_list:
                print("'%s' is not a valid answer please try again" % interactive_subregions)
            
        if interactive_subregions == 'y':
            while interactive_subregions == 'y':
                regions = []
                region = createSubRegionObjectInteractively()
                regions.append(region)
                anotherRegion = None
                while anotherRegion == None:
                    another = raw_input("Would you like to add another sub region? y/n [n] \n>>>")
                    if another not in yes_no_list:
                        print("'%s' is not a valid answer please try again" % another)
                    elif another in ['', 'n']:
                        anotherRegion = 'n'
                        interactive_subregions = 'n'
                    else:
                        anotherRegion = 'y'

        else:
            subRegionFilename = None
            while subRegionFilename == None:
                readDefault = raw_input('Read from a default file (workdir + "/sub_regions.txt")? y/n: [y] \n>>>')

                if readDefault == 'y' or readDefault == '':
                    subRegionFilename = workdir + "/sub_regions.txt"
                    print("Attempting to parse %s..." % subRegionFilename)
                    regions = readSubRegionsFile(subRegionFilename)

                elif readDefault == 'n':
                    while subRegionFilename == None:
                        # ask about using a non default filename
                        subRegionFilename = raw_input('Enter the full path to the Sub Region file to read from:\n>>>')
                        print("Attempting to parse %s..." % subRegionFilename)
                        regions = readSubRegionsFile(subRegionFilename)

                elif readDefault == 'NONE':
                    subRegionFilename = 'NONE'
                    regions = []
            
                else:
                    print("'%'s is not a valid selection.  Please try again.  To proceed without Sub Regions defined enter NONE at the prompt" % readDefault)

        return regions

def generateSubRegions(regions):
    """ Takes in a list of ConfigParser tuples and returns a list of SubRegion objects
    
    Input::
        regions - Config Tuple: [('Region01', '["R01", 36.5, 29, 0.0, -10]'), ('Region02',....]

    Output::
        subRegions - list of SubRegion objects
    """
    subRegions = []
    for region in regions:
        name, latMax, latMin, lonMax, lonMin = json.loads(region[1])
        subRegion = classes.SubRegion(name, latMin, lonMin, latMax, lonMax)
        subRegions.append(subRegion)

    return subRegions

def parseSubRegions(subRegionConfig):
    """
    Input::
        subRegionConfig - ConfigParser object
    
    Output::
        subRegions - List of SubRegion Objects.  This could return an empty List if unable to parse subRegionConfig
    """
    subRegions = []
    try:
        if os.path.exists(subRegionConfig['subRegionFile']):
            subRegions = readSubRegionsFile(subRegionConfig['subRegionFile'])
            
        else:
            print "SubRegion Filepath: [%s] does not exist.  Check your configuration file, or comment out the SUB_REGION Section." % (subRegionConfig['subRegionFile'],)
            print "Processing without SubRegion support"


    except IOError:
        print "Unable to open %s.  Running without SubRegions" % (subRegionConfig['subRegionFile'],)
    except KeyError:
        print "subRegionFile parameter was not provided.  Processing without SubRegion support"

    return subRegions


def decode_wrf_times(xtimes, base_time):
    '''
      Routine to convert from WRF time ('minutes since simulation start....') 
      into a python datetime structure
    
      Input:
          xtimes - list of wrf 'XTIME' in units of 'minutes since simulation start'
          base_time - a python datetime object describing simulation start date/time
    
      Output:
          times  - list of python datetime objects describing model data times
    
    
         Peter Lean August 2010
    
    '''
    times = []
    for xtime in xtimes:
        dt = datetime.timedelta(minutes=xtime)
        times.append(base_time + dt)
    
    return times

def calc_base_time_wrf(filename):
    '''
      Routine to calculate base_time (i.e. model initialization time)
       for wrf files with timestamp in their filenames.
      
        NB. Only works if includes a timestamp in format 'YYYY-MM-DD_HH:MM:SS'
        TODO: work out a more general way of doing this...
      Input:
          filename - full path to WRF netCDF file.
    
      Output:
          base_time  - a python datetime object describing model start time
    
         Peter Lean August 2010
    
    '''
    
    # Extract time from netCDF file (in units of 'minutes since beginning of simulation')
    f = netCDF4.Dataset(filename, mode='r')
    timesraw = f.variables["XTIME"]
    model_time = timesraw[0]
    
    dt = datetime.timedelta(minutes=int(model_time))
           
    # Extract and decode timestamp from filename
    
    filename = os.path.basename(filename)  # strip off the filepath
    
    timestamp_string = filename[11:30]   # cut out the date time stamp
    DATE_FORMAT = '%Y-%m-%d_%H:%M:%S'  
    
    timestamp = datetime.datetime(*time.strptime(timestamp_string, DATE_FORMAT)[:6])
    
    # Base Time = timestamp - 'minutes since beginning of simulation'
    base_time = timestamp - dt
    
    print 'Base Time calculated as: ', base_time
    
    return base_time

def calc_period_precip_from_running_tot(running_precip):
    '''
     WRF precipitation accumulations are stored as running totals from the start of the model run
     To find out values during each output time period, you must subtract the previous total
    
       e.g. running tot = 0,0,1,1,1,2,2,4,7,9,9,11 
            period accu = 0,0,1,0,0,1,0,2,3,2,0,2
    
      Input: 
         running_precip   - numpy array containing precipitation data at more than one time level
                             NB. assumes time dimension is the first one precip[time, lat, lon, level] 
    
      Output:
         acc_precip       - numpy array of same dimensions as input, 
                            but with period accumulations instead of running total.
    
    
        Peter Lean August 2010
    
    '''
    
    print 'Calculating period precip accumulations from running total'
    shifted_running_precip = np.roll(running_precip, -1, axis=0)
    nt = running_precip.shape[0]
    # avoid wrapping from the end time to the start time by forcing the accumulation at final time=0
    shifted_running_precip[nt - 1, :, :] = running_precip[nt - 1, :, :]
    acc_precip = shifted_running_precip - running_precip 

    # NB. sometimes rounding errors in the model lead to very small negative period accumulations
    #     These are removed and set to zero here.
    acc_precip = np.maximum(acc_precip, 0)

    return acc_precip

def decode_eraint_surf_times(xtimes):
    '''
      Routine to convert from ERA-Interim time ('hours since 1900...') 
      into a python datetime structure
    
      Input:
          xtimes - list of ERA-Interim times in units of 'hours since 1900'
    
      Output:
          times  - list of python datetime objects describing model data times
    
    
         Peter Lean August 2010
    
    '''
    base_time = datetime.datetime(1900, 1, 1, 0, 0, 0, 0)
    times = []
    
    for xtime in xtimes:
        dt = datetime.timedelta(hours=xtime)
        times.append(base_time + dt)
    
    return times

def read_total_precip_from_filelist(myfilelist):
    '''
     WRF outputs precipitation data under several variables:
     
         **RAINC** =  convective total precip
         
         **RAINNC** = large scale total precip  ("no convective")
         
         **SNOWC** =  convective snow
         
         **SNOWNC** = large scale snow  ("no convective")
     
     Therefore: 
         real rain = (rainc+rainnc)-(snowc+snownc)
         total precip = rainc+rainnc+snowc+snownc
         
     Input:
         myfilelist - a list of filename (including full path)
           
     Output:
         precip - a numpy array of total precip values
         lat, lon - 2D array of latitude and longitude values
         times    - list of times
     
     NB. THIS ROUTINE IS NO LONGER NEEDED... I HAD MISUNDERSTOOD HOW PRECIP DATA WAS STORED IN WRF
     TOTAL PRECIP  = RAINNC
     **A SIMILAR ROUTINE MAY BE REQUIRED TO FIND THE INDIVIDUAL COMPONENTS THOUGH..**
    
    '''
    myfilelist.sort()

    print 'Calculating total precipitation from individual rain/snow, convective/ls components'
    lat, lon, times, rainnc = read_data_from_file_list(myfilelist, 'RAINC')
    lat, lon, times, rainc = read_data_from_file_list(myfilelist, 'RAINNC')
    precip = rainnc + rainc
    # reset negative values to zero
    precip[precip < 0] = 0.0

    return lat, lon, times, precip


def isDirGood(directory):
    """
    Purpose::
        This function will check if a directory exists and is writeable.  If the directory doesn't exist it is created.
    Input::
        directory - Path we need to check 
    Output::
        directoryStatus - Boolean
    """
    directoryStatus = False
    
    if os.path.exists(directory):
        directoryStatus = os.access(directory, os.W_OK | os.X_OK)
        if directoryStatus:
            pass
        else:
            raise OSError("Unable to access the directory: %s.  Check that you have the proper permissions to read and write to that directory." % directory)
            #directoryStatus = False
    else:
        try:
            os.mkdir(directory)
            directoryStatus = True
        except OSError:
            raise

    return directoryStatus
    

def read_trmm_3b42_files(filelist, latMin, latMax, lonMin, lonMax):
    '''
     ** Alternate method of getting TRMM data from local repository if DB not available **
     Reads TRMM gridded precipitation data from netCDF files in local repository.
    
     Input:
        filelist - list of filenames (including path)
        latMin,latMax,lonMin,lonMax - define region to extract (in degrees)
     Output:
        lat, lon   - 1D array of latitude and longitude values
        timestore  - list of python datetime objects
        mdata      - numpy masked array containing data from all files    
    
      NB. written specific for TRMM netCDF output files
    
       Peter Lean June 2010 
    '''
    filelist.sort()

    # Crash nicely if 'filelist' is zero length
    if len(filelist) == 0:
        print 'Error: no files have been passed to read_data_from_file_list()'
        sys.exit()
    
    # Open the first file in the list to:
    #    i) read in lats, lons
    #    ii) find out how many timesteps in the file 
    #        (assume same ntimes in each file in list)
    #     -allows you to create an empty array to store variable data for all times
    tmp = netCDF4.Dataset(filelist[0], mode='r')
    latsraw = tmp.variables["latitude"]
    lonsraw = tmp.variables["longitude"]
    lat = latsraw[:]
    lon = lonsraw[:]
    print 'Lats and lons read in for first file in filelist'

    # Find out how many times there are in the file (should always be 1 for these TRMM files)
    timesraw = tmp.variables["time"]
    ntimes = len(timesraw)
    
    
    # Convert specified longitudes into 0-360 format if required
    if(lonMin < 0):
        lonMin = lonMin + 360
    if(lonMax < 0):
        lonMax = lonMax + 360

    # Create mask to extract required region only
    #  NB. longitude is slightly more complicated as can wrap the prime meridion
    print 'Extracting for :- lats:', latMin, latMax, ' lons: ', lonMin, lonMax
    wh_lat = np.logical_and((lat > latMin), (lat < latMax))
    if(lonMin <= lonMax):
        wh_lon = np.logical_and((lon > lonMin), (lon < lonMax))
    if(lonMin > lonMax):
        wh_lon = np.logical_or((lon > lonMin), (lon < lonMax))
    
    sublat = lat[wh_lat]
    sublon = lon[wh_lon]
    
    wh_true1, wh_true2 = np.meshgrid(wh_lon, wh_lat)
    wh = np.logical_and(wh_true1, wh_true2)
    
    # Create empty array to store data
    t2store = np.empty((ntimes * len(filelist), sublat.size, sublon.size))
    timestore = []

    # Now load in the data for real
    #  NB. no need to reload in the latitudes and longitudes -assume invariant
    i = 0
    timesaccu = 0 # a counter for number of times stored so far in t2store 
    #  NB. this method allows for missing times in data files 
    #      as no assumption made that same number of times in each file...
    for ifile in filelist:
        print 'Loading data from file: ', filelist[i]
        f = netCDF4.Dataset(ifile, mode='r')
        t2raw = f.variables['hrf']
        
        # Read time from filename (NB. 'time' variable in netCDF always set to zero)
        filename = os.path.basename(ifile)  # strip off the filepath
        timestamp_string = filename[11:23]   # cut out the date time stamp
        DATE_FORMAT = '%Y.%m.%d.%H'  
        mytime = datetime.datetime(*time.strptime(timestamp_string, DATE_FORMAT)[:4])
        ntimes = 1
        t2tmp = t2raw[0, :, :]
        sub = t2tmp[wh].reshape(sublat.size, sublon.size)
        t2store[timesaccu, :, :] = sub
        timestore.append(mytime)
        timesaccu = timesaccu + ntimes
        i += 1 
    
    print 'Data read in successfully with dimensions: ', t2store.shape
    
    # Create masked array using missing value flag from file
    mdi = f.variables['hrf'].missing_value[0]
    mdata = ma.masked_array(t2store, mask=(t2store == mdi))
    
    return sublat, sublon, timestore, mdata

def read_airs_lev3_files(filelist, myvar, latMin, latMax, lonMin, lonMax):
    '''
     ** For testing work before database was ready. **
     Reads AIRS level III gridded data from netCDF files.
    
     Input:
        filelist - list of filenames (including path)
        myvar    - name of variable to load
        latMin,latMax,lonMin,lonMax - define region to extract (in degrees)
     Output:
        lat, lon   - 1D array of latitude and longitude values
        timestore  - list of python datetime objects
        mdata      - numpy masked array containing data from all files    
    
      NB. written specific for AIRS level III netCDF output files
    
      NB. Ascending passes have local time of 1:30pm
      NB. Descending passes have local time of 1:30am
    
       Peter Lean June 2010 
    '''
    
    filelist.sort()
    
    # Crash nicely if 'filelist' is zero length
    if len(filelist) == 0:
        print 'Error: no files have been passed to read_data_from_file_list()'
        sys.exit()

    # Open the first file in the list to:
    #    i) read in lats, lons
    #    ii) find out how many timesteps in the file 
    #        (assume same ntimes in each file in list)
    #     -allows you to create an empty array to store variable data for all times
    tmp = netCDF4.Dataset(filelist[0], mode='r')
    latsraw = tmp.variables["lat"]
    lonsraw = tmp.variables["lon"]
    lat = latsraw[:]
    lon = lonsraw[:]
    print 'Lats and lons read in for first file in filelist'

    # Only one time per file in AIRS level III data
    ntimes = 1
    
    # Create mask to extract required region only
    #  NB. longitude is slightly more complicated as can wrap the prime meridion
    print 'Extracting for :- lats:', latMin, latMax, ' lons: ', lonMin, lonMax
    wh_lat = np.logical_and((lat >= latMin), (lat <= latMax))
    if(lonMin < lonMax):
        wh_lon = np.logical_and((lon >= lonMin), (lon <= lonMax))
    if(lonMin > lonMax):
        wh_lon = np.logical_or((lon >= lonMin), (lon <= lonMax))
    
    sublat = lat[wh_lat]
    sublon = lon[wh_lon]
    
    wh_true1, wh_true2 = np.meshgrid(wh_lon, wh_lat)
    wh = np.logical_and(wh_true1, wh_true2)
    
    # Create empty array to store data
    t2store = np.empty((ntimes * len(filelist), sublat.size, sublon.size))
    timestore = []

    # Now load in the data for real
    #  NB. no need to reload in the latitudes and longitudes -assume invariant
    i = 0
    timesaccu = 0 # a counter for number of times stored so far in t2store 
    #  NB. this method allows for missing times in data files 
    #      as no assumption made that same number of times in each file...
    for ifile in filelist:
        print 'Loading data from file: ', filelist[i]
        f = netCDF4.open_file(ifile, mode='r')
        t2raw = f.variables[myvar]
        
        # Read time from filename (NB. 'time' variable in netCDF always set to zero)
        filename = os.path.basename(ifile)  # strip off the filepath
        timestamp_string = filename[5:15]   # cut out the date time stamp
        DATE_FORMAT = '%Y.%m.%d'  
        mytime = datetime.datetime(*time.strptime(timestamp_string, DATE_FORMAT)[:4])
        print mytime
        ntimes = 1
        t2tmp = t2raw[:, :]
        sub = t2tmp[wh].reshape(sublat.size, sublon.size)
        t2store[timesaccu, :, :] = sub
        timestore.append(mytime)
        timesaccu = timesaccu + ntimes
        i += 1 


    print 'Data read in successfully with dimensions: ', t2store.shape

    # Create masked array using missing value flag from file
    mdi = f.variables[myvar]._FillValue[0]
    mdata = ma.masked_array(t2store, mask=(t2store == mdi))
    # Rearrange array so data match lat lon values
    mdata = np.flipud(mdata[:, ::-1])

    return sublat, sublon, timestore, mdata

def read_urd_files(filelist, latMin, latMax, lonMin, lonMax):
    '''
     Routine to load in NCEP Unified Raingauge Database binary files
    
      Input:
         filelist - a list of URD data files
    
    
      Output:
         sublats, sublons: 2d arrays of latitude and longitude values for user selected region.
         times - a list of python datetime objects
         subdata - precipitation data for user selected region
    
      Peter Lean  August 2010
    '''
    
    repository_path = '/nas/share1-hp/jinwonki/data/obs/pr25urd/daily/'
    
    # NB. Domain: 140W - 60W; 20N - 60N; Resolution: 0.25x0.25 degrees.
    #     The grids are arranged such that
    #     longitude is from 140W eastward to 60W and latitude from 20N northward
    #     to 60N, so that the first grid is (140W,20N), the second is 
    #     (139.75W,20N)......
    
    # Parameters specific to the URD dataset
    nlat = 161
    nlon = 321
    
    # Calculate the latitude and longitude arrays
    lat = np.arange(20, 60.25, 0.25)  # Hard wired lat,lon extent values for URD data files
    lon = np.arange(-140, -59.75, 0.25)
    
    lons, lats = np.meshgrid(lon, lat)

    # Define sub-region mask 
    #  NB. longitude is slightly more complicated as can wrap the prime meridion
    print 'Extracting for :- lats:', latMin, latMax, ' lons: ', lonMin, lonMax
    wh_lat = np.logical_and((lats >= latMin), (lats <= latMax))
    if(lonMin < lonMax):
        wh_lon = np.logical_and((lons >= lonMin), (lons <= lonMax))
    if(lonMin > lonMax):
        wh_lon = np.logical_or((lons >= lonMin), (lons <= lonMax))
    
    # count number of latitude values in subselection (for redimensioning array)
    wh_true = np.logical_and(wh_lat, wh_lon)
    nsublat = np.where(np.logical_and((lat >= latMin), (lat <= latMax)))[0].size
    
    sublats = lats[wh_true].reshape(nsublat, -1)  # infers longitude dimension given latitude dimension
    sublons = lons[wh_true].reshape(nsublat, -1)  # infers longitude dimension given latitude dimension
    nsublon = sublats.shape[1]

    # Load in the daily data
    datastore = []
    for myfile in filelist:
        f = FortranFile(repository_path + myfile)
    
        # Extract month and year from filename
        yearmonth = int(myfile[7:13])
        year = int(str(yearmonth)[0:4])
        month = int(str(yearmonth)[4:6])
        
        # Find out how many days there are in that month
        nt = calendar.monthrange(year, month)[1]
        
        data = np.zeros((nt, nsublat, nsublon))
        for t in np.arange(nt):
            precip = f.readReals()
            precip.shape = [nlat, nlon]
            data[t, :, :] = precip[wh_true].reshape(nsublat, nsublon) 
        
        datastore.append(data)

    # Make a single 3d numpy array out of my list of numpy arrays
    nt = 0
    for i in range(len(datastore)):
        nt = nt + datastore[i].shape[0]
    
    final_data = np.zeros((nt, nsublat, nsublon))
    t = 0
    for i in range(len(datastore)):
        nt = datastore[i].shape[0]
        final_data[t:t + nt, :, :] = datastore[i]
        t = t + nt

    # Load in land/sea mask
    ls = np.fromfile("/nas/share1-hp/jinwonki/data/obs/pr25urd/s/d/lsm25.usa", sep=" ")
    ls.shape = [nlat, nlon]
    # Extract subregion from land/sea mask
    subls = np.ones(final_data.shape)
    for t in np.arange(final_data.shape[0]):
        subls[t, :, :] = ls[wh_true].reshape(nsublat, nsublon) 
    
    # Construct a masked array of data i.e. only using data from land points
    mdi = -1
    mdata = ma.masked_array(final_data, mask=(subls == mdi))

    # Construct datetime list from dates in filenames.
    yearmonth = np.zeros(len(filelist))
    i = 0
    for filename in filelist:
        # Extract month and year from filename
        yearmonth[i] = int(filename[7:13])
        i += 1
    
    # Construct a list of datetimes between the earliest and latest yearmonth
    firstyear = int(str(yearmonth.min())[0:4])
    firstmonth = int(str(yearmonth.min())[4:6])
    times = []

    cur_time = datetime.datetime(firstyear, firstmonth, 1, 0, 0, 0, 0)
    
    for i in range(final_data.shape[0]):
        times.append(cur_time)
        dt = datetime.timedelta(days=1)
        cur_time = cur_time + dt
    
    return sublats, sublons, times, mdata

def read_tmp_watershed(myfile, dom_num):
    '''
     Routine to read watershed weighting file mapped onto WRF model grids.
      NB.this will be superceded by proper routines to read shape files and regrid onto any model grid.
    
      Input:
         myfile - file name of the watershed ascii file to load
         dom_num - WRF domain number (specific to this experiment)
    
      Output:
         mymask - boolean mask array saying where the watershed is
    
       Peter Lean    September 2010
    '''
    
    # Parameters specific to WRF domain setup required for these files
    if(dom_num == 1):
        nx = 190
        ny = 130
    
    if(dom_num == 2):
        nx = 192
        ny = 180
      
    # Create an empty array to store the weights
    myweights = np.zeros((ny, nx))
    
    # Load in data from the mask file
    i, j, w = np.loadtxt("/home/plean/demo/rcmes/watersheds/" + myfile, unpack=True)
    
    for q in np.arange(len(i)):
        myweights[j[q], i[q]] = w[q]
    
    mymask = np.empty((ny, nx))
    mymask[:] = True
    mymask[(myweights > 0.5)] = False
    
    return mymask

def read_eraint_surf_files(filelist, myvar, latMin, latMax, lonMin, lonMax):
    '''
     ** For testing work before database was ready. **
     Reads ERA-Interim surface netCDF files.
    
     Input:
        filelist - list of filenames (including path)
        myvar    - name of variable to load
        latMin,latMax,lonMin,lonMax - define region to extract (in degrees)
     Output:
        lat, lon   - 1D array of latitude and longitude values
        timestore  - list of python datetime objects
        mdata      - numpy masked array containing data from all files    
    
       Peter Lean September 2010 
    '''
    
    
    # Crash nicely if 'filelist' is zero length
    if len(filelist) == 0:
        print 'Error: no files have been passed to read_data_from_file_list()'
        sys.exit()

    # Open the first file in the list to:
    #    i) read in lats, lons
    #    ii) find out how many timesteps in the file 
    #        (assume same ntimes in each file in list)
    #     -allows you to create an empty array to store variable data for all times
    tmp = netCDF4.Dataset(filelist[0],mode='r')
    latsraw = tmp.variables["latitude"]
    lonsraw = tmp.variables["longitude"]
    lat = latsraw[:]
    lon = lonsraw[:]
    print 'Lats and lons read in for first file in filelist'
    
    # Create mask to extract required region only
    #  NB. longitude is slightly more complicated as can wrap the prime meridion
    print 'Extracting for :- lats:', latMin, latMax, ' lons: ', lonMin, lonMax
    wh_lat = np.logical_and((lat >= latMin), (lat <= latMax))
    if(lonMin < lonMax):
        wh_lon = np.logical_and((lon >= lonMin), (lon <= lonMax))
    if(lonMin > lonMax):
        wh_lon = np.logical_or((lon >= lonMin), (lon <= lonMax))
    
    sublat = lat[wh_lat]
    sublon = lon[wh_lon]
    
    wh_true1, wh_true2 = np.meshgrid(wh_lon, wh_lat)
    wh = np.logical_and(wh_true1, wh_true2)
    
    # Create storage lists
    datastore = []
    timestore = []

    # Now load in the data for real
    #  NB. no need to reload in the latitudes and longitudes -assume invariant
    i = 0
    timesaccu = 0 # a counter for number of times stored so far in t2store 
    #  NB. this method allows for missing times in data files 
    #      as no assumption made that same number of times in each file...
    for ifile in filelist:
        print 'Loading data from file: ', filelist[i]
        f = netCDF4.Dataset(ifile, mode='r')
        data = f.variables[myvar][:]
        scale = f.variables[myvar].scale_factor
        offset = f.variables[myvar].add_offset
        data = data * scale + offset
        times = f.variables["time"][:]
        ntimes = times.size
        # Decode times into python datetime object
        sub = data[:, wh].reshape(ntimes, sublat.size, sublon.size)
        datastore.append(sub)
        timestore.append(times)
        timesaccu = timesaccu + ntimes
        i += 1 

    # move data from lists into correctly dimensioned arrays
    final_data = np.zeros((timesaccu, sublat.size, sublon.size))
    t = 0
    for i in range(len(datastore)):
        nt = datastore[i].shape[0]
        final_data[t:t + nt, :, :] = datastore[i]
        t = t + nt
    
    times = np.zeros((timesaccu))
    t = 0
    for i in range(len(timestore)):
        nt = timestore[i].shape[0]
        times[t:t + nt] = timestore[i]
        t = t + nt
  
    # Decode times into python datetime objects
    times = rcmes.process.decode_eraint_surf_times(times)
    
    print 'Data read in successfully with dimensions: ', final_data.shape
    
    # Create masked array using missing value flag from file
    mdi = f.variables[myvar]._FillValue[0]
    mdata = ma.masked_array(final_data, mask=(final_data == mdi))

    # Rearrange array so data match lat lon values
    mdata = np.flipud(mdata[:, ::-1])
    
    return sublat, sublon, times, mdata

def make_list_of_wrf_files(firstTime, lastTime, ident):
    '''
     Routine to make list of WRF filenames given time period.
    
      Input:
          firstTime - datetime object specifying start time
          lastTime  - datetime object specifying end time
          ident     - identifier for model run, e.g. 'd01'
    
      Output:
          filelist  - list of standard format WRF filenames
    
          Peter Lean
    '''

    dt = datetime.timedelta(hours=6)
    filenamelist = []
    curTime = firstTime

    while curTime <= lastTime:
        curTimeString = curTime.strftime("%Y-%m-%d_%H:%M:%S")
        filenamelist.append('wrfout_' + ident + '_' + curTimeString)
        curTime += dt
    
    return filenamelist

def make_list_of_trmm_files(firstTime, lastTime):
    '''
     Routine to make list of TRMM filenames given time period.
    
      Input:
          firstTime - datetime object specifying start time
          lastTime  - datetime object specifying end time
    
      Output:
          filelist  - list of standard format WRF filenames
    
          Peter Lean
    '''
    trmm_repository = '/nas/share4-cf/plean/TRMM/'
    dt = datetime.timedelta(hours=24)
    filenamelist = []
    curTime = firstTime
    while curTime <= lastTime:
        curTimeString = curTime.strftime("%Y.%m.%d")
        filenamelist.append(trmm_repository + '3B42_daily.' + curTimeString + '.6.nc')
        
        curTime += dt
    
    return filenamelist

def make_list_of_airs_files(firstTime, lastTime):
    '''
     Routine to make list of AIRS filenames given time period.
    
      Input:
          firstTime - datetime object specifying start time
          lastTime  - datetime object specifying end time
    
      Output:
          filelist  - list of standard format WRF filenames
    
          Peter Lean
    '''


    airs_repository = '/nas/share4-cf/plean/AIRX3STD/'
    dt = datetime.timedelta(hours=24)
    filenamelist = []
    curTime = firstTime
    while curTime <= lastTime:
        curTimeString = curTime.strftime("%Y.%m.%d")
        filenamelist.append(glob.glob(airs_repository + 'AIRS.' + curTimeString + '.L3.*.nc')[0])
        
        curTime += dt
    
    return filenamelist

def make_list_of_urd_files(firstTime, lastTime):
    '''
     Routine to make list of URD filenames given time period.
    
      Input:
          firstTime - datetime object specifying start time
          lastTime  - datetime object specifying end time
    
      Output:
          filelist  - list of standard format WRF filenames
    
          Peter Lean
    '''
    
    dt = datetime.timedelta(days=30)
    filenamelist = []
    newfirstTime = datetime.datetime(firstTime.year, firstTime.month, 15, 0, 0, 0)
    newlastTime = datetime.datetime(lastTime.year, lastTime.month, 15, 0, 0, 0)
    
    curTime = newfirstTime
    while curTime <= newlastTime:
        curTimeString = curTime.strftime("%Y%m")
        filenamelist.append('pr_ncep' + curTimeString)
        if(curTime.month == 1):
            curTime = datetime.datetime(curTime.year, curTime.month, 15, 00, 00, 00, 00)
        
        curTime += dt
    
    return filenamelist

def make_list_of_era_surf_files(firstTime, lastTime):
    '''
     Routine to make list of ERA-Interim surface filenames given time period.
    
      Input:
          firstTime - datetime object specifying start time
          lastTime  - datetime object specifying end time
    
      Output:
          filelist  - list of standard format WRF filenames
    
          Peter Lean
    '''

    import datetime
    eraint_repository = '/data/plean/era-int/surf/'
    filenamelist = []
    dt = datetime.timedelta(days=30)
    newfirstTime = datetime.datetime(firstTime.year, firstTime.month, 15, 0, 0, 0)
    newlastTime = datetime.datetime(lastTime.year, lastTime.month, 15, 0, 0, 0)
    curTime = newfirstTime

    while curTime <= newlastTime:
        curTimeString = curTime.strftime("%b%Y")
        filenamelist.append(eraint_repository + 'sfc.' + curTimeString.lower() + '.nc')
        if(curTime.month == 1):
            curTime = datetime.datetime(curTime.year, curTime.month, 15, 00, 00, 00, 00)
        
        curTime += dt
    
    return filenamelist


#

def assign_subRgns_from_a_text_file(infile):
    # Read pre-fabricated sugregion information from a text file
    # Note: python indexing includes the beginning point but excludes the ending point
    f = open(infile, 'r')
    for i in np.arange(8):
        string = f.readline()
        print 'Line ', i, ': Content ', string
    string = f.readline()
    numSubRgn = int(string[20:22])
    print 'numSubRgn = ', numSubRgn
    for i in np.arange(3):
        string = f.readline()
    # Read input string and extract subRegion info (name, longs, lats) from the string
    subRgnName = []
    subRgnLon0 = ma.zeros((numSubRgn))
    subRgnLon1 = ma.zeros((numSubRgn))
    subRgnLat0 = ma.zeros((numSubRgn))
    subRgnLat1 = ma.zeros((numSubRgn))
    for i in np.arange(numSubRgn):
        string = f.readline()
        subRgnName.append(string[0:19])
        subRgnLon0[i] = float(string[30:37])
        subRgnLon1[i] = float(string[40:47])
        subRgnLat0[i] = float(string[50:55])
        subRgnLat1[i] = float(string[60:65])
    f.close()
    print 'subRgnName: ', subRgnName
    print 'subRgnLon0: ', subRgnLon0
    print 'subRgnLon1: ', subRgnLon1
    print 'subRgnLat0: ', subRgnLat0
    print 'subRgnLat1: ', subRgnLat1
    return numSubRgn, subRgnName, subRgnLon0, subRgnLon1, subRgnLat0, subRgnLat1

def createSubRegionObjectInteractively():
    """
    Purpose::
        Mini command line program to enable users to enter SubRegion Information
    Input::
        None
    Output::
        SubRegion Object
    """
    rawInput = None
    while rawInput == None:
        userMessage = ("Enter information for 1 Sub Region using the following "
                       "pipe '|' separated format: \n"
                       "RegionName | Degrees North | Degrees South | Degrees East | Degrees West \n>>>")
        userInput = raw_input(userMessage)
        inputList = userInput.split('|')
        if len(inputList) != 5:
            badLengthMessage = ("Unable to parse %s.  You should have 5 inputs "
                                "separated by 4 pipe characters. \n"
                                "Example:  Region Name | 85 | 80 | 10 | -30" % userInput)
            print(badLengthMessage)
        else:
            name = str(inputList[0]).strip()
            latMax = str(inputList[1]).strip()
            latMin = str(inputList[2]).strip()
            lonMax = str(inputList[3]).strip()
            lonMin = str(inputList[4]).strip()
            subRegion = classes.SubRegion(name, latMin, lonMin, latMax, lonMax)
            rawInput = True

    return subRegion

def selectSubRegion(subRegions):
    # interactively select the sub-region ID for area-mean time-series evaluation
    print '-'*59
    columnTemplate = "|{0:2}|{1:10}|{2:10}|{3:10}|{4:10}|{5:10}|"
    print columnTemplate.format("ID", "Name", "LonMin", "LonMax", "LatMin", "LatMax")
    counter = 0
    for subRegion in subRegions:
        print columnTemplate.format(counter, subRegion.name, subRegion.lonMin, subRegion.lonMax, subRegion.latMin, subRegion.latMax)
        counter += 1

    print '-'*59
    ask = 'Enter the sub-region ID to be evaluated. -9 for all sub-regions (-9 is not active yet): \n'
    rgnSelect = int(raw_input(ask))
    if rgnSelect >= len(subRegions):
        print 'sub-region ID out of range. Max = %s' % len(subRegions)
        sys.exit()
    return rgnSelect

def getStartEndTimes(status, startOverLapTime, endOverLapTime):
    '''
    This function will get the start and end time from user.
    It also check whether or not user enters the proper time for both start and end.
    If user leaves the start and end time empty, it will get the largest time range as default (overlap).
    '''

    if status == "start":
        try:
            time = raw_input("Please Enter a Start Date [%s]: " % startOverLapTime.strftime('%Y-%m-%d'))
            if not time:
                time = startOverLapTime
                print "Your time starts from [%s] " % time.strftime('%Y-%m-%d')
                return time
            time = datetime.datetime.strptime(time, '%Y-%m-%d')
            if time < startOverLapTime:
                print "WARNING: The time you inputted [%s] " % time.strftime('%Y-%m-%d') + " is before the minimum start time [%s]."  % startOverLapTime.strftime('%Y-%m-%d')
                time = getStartEndTimes("start", startOverLapTime, endOverLapTime)
                return time
            elif time > endOverLapTime:
                print "WARNING: The time you inputted [%s] " % time.strftime('%Y-%m-%d') + " is after the maximum end time [%s]. " % endOverLapTime.strftime('%Y-%m-%d')
                time = getStartEndTimes("start", startOverLapTime, endOverLapTime)
                return time
            else:
                return time
        except ValueError:
            getStartEndTimes(status, startOverLapTime, endOverLapTime)
    
    if status == "end":
        try:
            time = raw_input("Please Enter an End Date [%s]: " % endOverLapTime.strftime('%Y-%m-%d'))
            if not time:
                time = endOverLapTime
                print "Your time ends by [%s] " % time.strftime('%Y-%m-%d')
                return time
            time = datetime.datetime.strptime(time, '%Y-%m-%d')
            if time > endOverLapTime:
                print "WARNING: The time you inputted [%s] " % time.strftime('%Y-%m-%d') + " is after the maximum end time [%s]. " % endOverLapTime.strftime('%Y-%m-%d')
                time = getStartEndTimes("end", startOverLapTime, endOverLapTime)
                return time
            elif time < startOverLapTime:
                print "WARNING: The time you inputted [%s] " % time.strftime('%Y-%m-%d') + " is before the minimum start time [%s]."  % startOverLapTime.strftime('%Y-%m-%d')
                time = getStartEndTimes("end", startOverLapTime, endOverLapTime)
                return time
            else:
                return time
        except ValueError:
            getStartEndTimes(status, startOverLapTime, endOverLapTime)


def getDirSettings():
    """
    This function will collect 2 parameters from the user about the RCMET run they have started.
    
    Output::
        dirs - Tuple of strings i.e. ('workDirPath', 'cacheDirPath')
    """
    workDir = os.path.abspath(raw_input('Please enter workDir:\n> '))
    if os.path.isdir(workDir):
        pass
    else:
        makeDirectory(workDir)
    
    cacheDir= os.path.abspath(raw_input('Please enter cacheDir:\n> '))
    if os.path.isdir(cacheDir):
        pass
    else:
        makeDirectory(cacheDir)
    
    return (workDir, cacheDir)

def getModelFiles():
    modelList = []
    while len(modelList) < 1:
        userInput = raw_input('Please enter model file (or specify multiple files using wildcard):\n> ')
        modelList = glob.glob(userInput)
        if len(modelList) == 0:
            print("Sorry we were unable to find any files at - %s" % userInput)
            print("Please try again, and use the asterisk * for the wildcard")
        
    return modelList

def getTemporalGrid():
    options = ['annual', 'monthly', 'daily']
    print("Please select one of the following Temporal Grid Options:\n")
    for key, option in enumerate(options):
        print("[%s] - %s" % (key, option))
    choice = int(raw_input(">>>"))
    try:
        temporalGrid = options[choice]
    except IndexError:
        getTemporalGrid()
    else:
        return temporalGrid

def getSpatialGrid():
    options = ['obs', 'model', 'user']
    print("Please select one of the following Spatial Grid Options:\n")
    for key, option in enumerate(options):
        print("[%s] - %s" % (key, option))

    choice = int(raw_input(">>>"))
    try:
        spatialGrid = options[choice]
    except IndexError:
        getSpatialGrid()

    return spatialGrid

def askUserForVariableName(variableNames, targetName):
    if targetName == "analysis":
        print("Select the variable you want to use for analysis/metrics:")
    else:
        print("Select the variable that corresponds to %s:" % targetName)

    for idx, variable in enumerate(variableNames):
        print("[%s] - %s" % (idx, variable))
    userChoice = int(raw_input(">>>"))
    try:
        variableName = variableNames[userChoice]
    except IndexError:
        askUserForVariableName(variableNames, targetName)
    
    return variableName
        
        

def getLatLonStep(settings):
    pass

def getSpatialBounds(settings):
    pass


def getUserSpatialSettings(settings):
    getLatLonStep(settings)
    getSpatialBounds(settings)

def makeDirectory(directory):
    print "%s doesn't exist.  Trying to create it now." % directory
    try:
        os.mkdir(directory)
        print("Created %s successfully" % directory)
    except OSError:
        print "This program cannot create dir: %s due to permission issues." % directory
        sys.exit()


def userDefinedStartEndTimes(obsList, modelList):
    """
    The function will interactively ask the user to select a start and end time based on the start/end times
    of the supplied observation and model objects
     
    Input::
        obsList - List of Observation Objects
        modelList - List of Model Objects
    
    Output::
        startTime - Python datetime object from User Input
        endTime - Python datetime object from User Input
    """
    startTimes = []
    endTimes = []
    print '='*94
    template = "|{0:60}|{1:15}|{2:15}|"
    print template.format('Dataset - NAME', 'START DATE', 'END DATE')
    for observation in obsList:
        startTimes.append(datetime.datetime.strptime(observation['start_date'],'%Y-%m-%d'))
        endTimes.append(datetime.datetime.strptime(observation['end_date'],'%Y-%m-%d'))
        print template.format(observation['longname'], observation['start_date'], observation['end_date'])
    print '-'*94
    for model in modelList:
        startTimes.append(model.minTime)
        endTimes.append(model.maxTime)
        print template.format(model.name, model.minTime.strftime('%Y-%m-%d'), model.maxTime.strftime('%Y-%m-%d'))
    print '='*94
    
    # Compute Overlap
    maxstartTimes=max(startTimes)
    minendTimes=min(endTimes)
    # TODO:  Do we need to start on JAN and end on DEC?  Do we know someone is doing ANNUAL analysis at this point?
#    if maxstartTimes.month != 1:
#        maxstartTimes = datetime.datetime(maxstartTimes.year+1,1,maxstartTimes.day)
#    if minendTimes.month != 12:
#        minendTimes = datetime.datetime(minendTimes.year-1,12,minendTimes.day)
    if minendTimes.year < maxstartTimes.year:
        print 'Not enough data for overlapping years'
        sys.exit()
    overLap = (maxstartTimes.strftime('%Y-%m-%d'), minendTimes.strftime('%Y-%m-%d'))
    # Present default overlap to user as default value
    print 'Standard Overlap in the selected datasets are %s through %s' % (overLap)

    startOverLapTime = datetime.datetime.strptime(overLap[0],'%Y-%m-%d')
    endOverLapTime = datetime.datetime.strptime(overLap[1],'%Y-%m-%d')

    # Enter Start Date
    startTime = getStartEndTimes("start", startOverLapTime, endOverLapTime)    
    # Enter End Date
    endTime = getStartEndTimes("end", startOverLapTime, endOverLapTime)
        
    if startTime > endTime:
        print "WARNING: The start time you entered [%s]" % startTime.strftime('%Y-%m-%d') + " is after the end time you entered [%s]." % endTime.strftime('%Y-%m-%d')
        startTime = getStartEndTimes("start", startOverLapTime, endOverLapTime)
        endTime = getStartEndTimes("end", startOverLapTime, endOverLapTime)

    return startTime, endTime


def select_timOpt():
    #---------------------------------------------
    # Interacrively select the time scale to be evaluated
    # e.g., the means over annual, seasonal, monthly, or a specified period (e.g., JJAS for Indian monsoon)
    #------------------------------------------------------------------------------------
    print 'Select the time-mean properties to be evaluated: Enter'
    timeOption = \
      int(raw_input('1=annual mean, 2=seasonal mean (define "season", e.g., JJAS for Indian monsoon), 3=monthly \n> '))
    return timeOption

def select_data(nDat, Times, List, sourceDat):
    #---------------------------------------------
    # Interacrively select a model or models for evaluation
    #----------------------------------------------------------------------------
    print '-----------------------------------------------'
    if sourceDat == 'mdl':
        print 'mdlID  mdlName numMOs  mdlStartTime mdlEndTime fileName'
    elif sourceDat == 'obs':
        print 'obsID  obsName obsMOs  obsStartTime obsEndTime fileName'
    else:
        print 'not valid data source: CRASH and restart'
        sys.exit()
    print '-----------------------------------------------'

    for n in np.arange(len(List)):
        print n, List[n], Times[0], Times[-1]
        n += 1
    print '-----------------------------------------------'
    if sourceDat == 'mdl':
        ask = 'Enter the model ID to be evaluated. -9 for all models (-9 is not active yet): \n'
    elif sourceDat == 'obs':
        ask = 'Enter the obs ID to be evaluated. -9 for all models (-9 is not active yet): \n'
    datSelect = int(raw_input(ask))
    if datSelect > nDat - 1:
        print 'Data ID out of range: CRASH'
        sys.exit()
    return datSelect

def select_metrics():
    #---------------------------------------------
    # Interacrively select an evaluation metric
    # Input : none
    # Output: metricOption, the indicator for selecting the metric to be calculated
    #------------------------------------------------------------------------------
    print 'Metric options'
    print '[0] Bias: mean bias across full time range'
    print '[1] Mean Absolute Error: across full time range'
    print '[2] Spatial Pattern Correlation: results in a time series of spatial correlation coeff'
    print '[3] Temporal Correlation: results in 2-d array of temporal correlation coefficient'
    print '[4] Spatial Pattern Correlation between averaged fields: results in a single correlation coeff'
    print '[5] RMSE in time: results in a 2-d array of RMSE over two time series'
    print '[6] TODO: Probability Distribution Function similarity score'
    choice = int(raw_input('Please make a selection from the options above\n> '))
    # assign the evaluation metric to be calculated
    if choice == 0:
        metricOption = 'BIAS'
    elif choice == 1:
        metricOption = 'MAE'
    elif choice == 2:
        metricOption = 'PCt'
    elif choice == 3:
        metricOption = 'TC'
    elif choice == 4:
        metricOption = 'PCC'
    elif choice == 5:
        metricOption = 'RMSt'
    elif choice == 6:
        metricOption = 'pdfSkillScore'
    print 'in subroutine metricOption = ', metricOption
    return metricOption

