"""Module with a collection of helper functions"""

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
   import datetime
   times=[]
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
   import numpy
   import Nio
   import datetime
   import time
   import os

   # Extract time from netCDF file (in units of 'minutes since beginning of simulation')
   f=Nio.open_file(filename, format='nc')
   timesraw = f.variables["XTIME"]
   model_time=timesraw[0]

   dt = datetime.timedelta(minutes=int(model_time))
          
   # Extract and decode timestamp from filename

   filename=os.path.basename(filename)  # strip off the filepath

   timestamp_string = filename[11:30]   # cut out the date time stamp
   format='%Y-%m-%d_%H:%M:%S'  

   timestamp = datetime.datetime(*time.strptime(timestamp_string,format)[:6])

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
   import numpy

   print 'Calculating period precip accumulations from running total'

   shifted_running_precip = numpy.roll(running_precip,-1,axis=0)
   nt = running_precip.shape[0]

   # avoid wrapping from the end time to the start time by forcing the accumulation at final time=0
   shifted_running_precip[nt-1,:,:]=running_precip[nt-1,:,:]

   acc_precip = shifted_running_precip - running_precip 

   # NB. sometimes rounding errors in the model lead to very small negative period accumulations
   #     These are removed and set to zero here.
   acc_precip = numpy.maximum(acc_precip,0)

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
   import datetime
   import numpy

   base_time = datetime.datetime(1900,1,1,0,0,0,0)

   times=[]
   for xtime in xtimes:
      dt = datetime.timedelta(hours=xtime)
      times.append(base_time + dt)

   return times

def read_total_precip_from_filelist(myfilelist):
   '''
     WRF outputs precipitation data under several variables:
      RAINC=  convective total precip
      RAINNC= large scale total precip  ("no convective")
      SNOWC=  convective snow
      SNOWNC= large scale snow  ("no convective")
   
     Therefore, real rain = (rainc+rainnc)-(snowc+snownc)
                total precip = rainc+rainnc+snowc+snownc
     Input:
            myfilelist - a list of filename (including full path)
           
     Output:
            precip - a numpy array of total precip values
            lat, lon - 2D array of latitude and longitude values
            times    - list of times
   
     Peter Lean August 2010
   
     NB. THIS ROUTINE IS NO LONGER NEEDED... I HAD MISUNDERSTOOD HOW PRECIP DATA WAS STORED IN WRF
         TOTAL PRECIP  = RAINNC
     -A SIMILAR ROUTINE MAY BE REQUIRED TO FIND THE INDIVIDUAL COMPONENTS THOUGH..
   '''

   myfilelist.sort()

   print 'Calculating total precipitation from individual rain/snow, convective/ls components'
   lat,lon,times,rainnc = read_data_from_file_list(myfilelist,'RAINC')
   lat,lon,times,rainc = read_data_from_file_list(myfilelist,'RAINNC')
   #lat,lon,times,snowc = read_data_from_file_list(myfilelist,'SNOWC')
   #lat,lon,times,snownc = read_data_from_file_list(myfilelist,'SNOWNC')

   #precip = rainc+rainnc+snowc+snownc
   precip = rainnc+rainc

   # reset negative values to zero
   precip[precip<0]=0.0

   return lat, lon, times, precip


def read_trmm_3b42_files(filelist,latMin,latMax,lonMin,lonMax):
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
   import Nio
   import numpy as np
   import numpy.ma as ma
   import os
   import datetime
   import time

   filelist.sort()

   # Crash nicely if 'filelist' is zero length
   if len(filelist)==0:
      print 'Error: no files have been passed to read_data_from_file_list()'
      return -1,-1,-1,-1

   # Open the first file in the list to:
   #    i) read in lats, lons
   #    ii) find out how many timesteps in the file 
   #        (assume same ntimes in each file in list)
   #     -allows you to create an empty array to store variable data for all times
   tmp=Nio.open_file(filelist[0], format='nc')
   latsraw = tmp.variables["latitude"]
   lonsraw = tmp.variables["longitude"]
   lat = latsraw[:]
   lon = lonsraw[:]
   print 'Lats and lons read in for first file in filelist'

   # Find out how many times there are in the file (should always be 1 for these TRMM files)
   timesraw = tmp.variables["time"]
   ntimes=len(timesraw)


   # Convert specified longitudes into 0-360 format if required
   if(lonMin<0):
     lonMin=lonMin+360
   if(lonMax<0):
     lonMax=lonMax+360

   # Create mask to extract required region only
   #  NB. longitude is slightly more complicated as can wrap the prime meridion
   print 'Extracting for :- lats:',latMin, latMax,' lons: ',lonMin, lonMax
   wh_lat = np.logical_and((lat>latMin),(lat<latMax))
   if(lonMin<=lonMax):
     wh_lon = np.logical_and((lon>lonMin), (lon<lonMax))
   if(lonMin>lonMax):
     wh_lon = np.logical_or((lon>lonMin), (lon<lonMax))

   sublat = lat[wh_lat]
   sublon = lon[wh_lon]

   wh_true1,wh_true2 = np.meshgrid(wh_lon,wh_lat)
   wh = np.logical_and(wh_true1,wh_true2)

   # Create empty array to store data
   t2store=np.empty((ntimes*len(filelist),sublat.size,sublon.size))
   timestore = []

   # Now load in the data for real
   #  NB. no need to reload in the latitudes and longitudes -assume invariant
   i=0
   timesaccu=0 # a counter for number of times stored so far in t2store 
               #  NB. this method allows for missing times in data files 
               #      as no assumption made that same number of times in each file...
   for ifile in filelist:
     print 'Loading data from file: ',filelist[i]
     f=Nio.open_file(ifile, format='nc')
     t2raw = f.variables['hrf']

     # Read time from filename (NB. 'time' variable in netCDF always set to zero)
     filename=os.path.basename(ifile)  # strip off the filepath
     timestamp_string = filename[11:23]   # cut out the date time stamp
     format='%Y.%m.%d.%H'  
     mytime = datetime.datetime(*time.strptime(timestamp_string,format)[:4])
     ntimes=1
     t2tmp=t2raw[0,:,:]
     sub=t2tmp[wh].reshape(sublat.size,sublon.size)
     t2store[timesaccu,:,:]=sub
     timestore.append(mytime)
     timesaccu=timesaccu+ntimes
     i += 1 

   print 'Data read in successfully with dimensions: ',t2store.shape

   # Create masked array using missing value flag from file
   mdi = f.variables['hrf'].missing_value[0]
   mdata = ma.masked_array(t2store,mask=(t2store==mdi))

   return sublat, sublon, timestore, mdata



def read_airs_lev3_files(filelist,myvar,latMin,latMax,lonMin,lonMax):
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
   import Nio
   import numpy as np
   import numpy.ma as ma
   import os
   import datetime
   import time

   filelist.sort()

   # Crash nicely if 'filelist' is zero length
   if len(filelist)==0:
      print 'Error: no files have been passed to read_data_from_file_list()'
      return -1,-1,-1,-1

   # Open the first file in the list to:
   #    i) read in lats, lons
   #    ii) find out how many timesteps in the file 
   #        (assume same ntimes in each file in list)
   #     -allows you to create an empty array to store variable data for all times
   tmp=Nio.open_file(filelist[0], format='nc')
   latsraw = tmp.variables["lat"]
   lonsraw = tmp.variables["lon"]
   lat = latsraw[:]
   lon = lonsraw[:]
   print 'Lats and lons read in for first file in filelist'

   # Only one time per file in AIRS level III data
   ntimes=1

   # Create mask to extract required region only
   #  NB. longitude is slightly more complicated as can wrap the prime meridion
   print 'Extracting for :- lats:',latMin, latMax,' lons: ',lonMin, lonMax
   wh_lat = np.logical_and((lat>=latMin),(lat<=latMax))
   if(lonMin<lonMax):
     wh_lon = np.logical_and((lon>=lonMin), (lon<=lonMax))
   if(lonMin>lonMax):
     wh_lon = np.logical_or((lon>=lonMin), (lon<=lonMax))

   sublat = lat[wh_lat]
   sublon = lon[wh_lon]

   wh_true1,wh_true2 = np.meshgrid(wh_lon,wh_lat)
   wh = np.logical_and(wh_true1,wh_true2)

   # Create empty array to store data
   t2store=np.empty((ntimes*len(filelist),sublat.size,sublon.size))
   timestore = []

   # Now load in the data for real
   #  NB. no need to reload in the latitudes and longitudes -assume invariant
   i=0
   timesaccu=0 # a counter for number of times stored so far in t2store 
               #  NB. this method allows for missing times in data files 
               #      as no assumption made that same number of times in each file...
   for ifile in filelist:
     print 'Loading data from file: ',filelist[i]
     f=Nio.open_file(ifile, format='nc')
     t2raw = f.variables[myvar]

     # Read time from filename (NB. 'time' variable in netCDF always set to zero)
     filename=os.path.basename(ifile)  # strip off the filepath
     timestamp_string = filename[5:15]   # cut out the date time stamp
     format='%Y.%m.%d'  
     mytime = datetime.datetime(*time.strptime(timestamp_string,format)[:4])
     print mytime
     ntimes=1
     t2tmp=t2raw[:,:]
     sub=t2tmp[wh].reshape(sublat.size,sublon.size)
     t2store[timesaccu,:,:]=sub
     timestore.append(mytime)
     timesaccu=timesaccu+ntimes
     i += 1 


   print 'Data read in successfully with dimensions: ',t2store.shape

   # Create masked array using missing value flag from file
   mdi = f.variables[myvar]._FillValue[0]
   mdata = ma.masked_array(t2store,mask=(t2store==mdi))

   # Rearrange array so data match lat lon values
   mdata=np.flipud(mdata[:,::-1])

   return sublat, sublon, timestore, mdata


def read_urd_files(filelist,latMin,latMax,lonMin,lonMax):
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
   import numpy
   import numpy.ma as ma
   import datetime
   import calendar
   from fortranfile import FortranFile

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
   lat =numpy.arange(20,60.25,0.25)  # Hard wired lat,lon extent values for URD data files
   lon =numpy.arange(-140,-59.75,0.25)

   lons,lats = numpy.meshgrid(lon,lat)

   # Define sub-region mask 
   #  NB. longitude is slightly more complicated as can wrap the prime meridion
   print 'Extracting for :- lats:',latMin, latMax,' lons: ',lonMin, lonMax
   wh_lat = numpy.logical_and((lats>=latMin),(lats<=latMax))
   if(lonMin<lonMax):
     wh_lon = numpy.logical_and((lons>=lonMin), (lons<=lonMax))
   if(lonMin>lonMax):
     wh_lon = numpy.logical_or((lons>=lonMin), (lons<=lonMax))

   # count number of latitude values in subselection (for redimensioning array)
   wh_true = numpy.logical_and(wh_lat, wh_lon)
   nsublat = numpy.where(numpy.logical_and((lat>=latMin),(lat<=latMax)))[0].size

   sublats = lats[wh_true].reshape(nsublat,-1)  # infers longitude dimension given latitude dimension
   sublons = lons[wh_true].reshape(nsublat,-1)  # infers longitude dimension given latitude dimension
   nsublon = sublats.shape[1]

   # Load in the daily data
   datastore = []
   for myfile in filelist:

      f = FortranFile(repository_path+myfile)

      # Extract month and year from filename
      yearmonth = int(myfile[7:13])
      year      = int(str(yearmonth)[0:4])
      month     = int(str(yearmonth)[4:6])

      # Find out how many days there are in that month
      nt = calendar.monthrange(year, month)[1]

      data = numpy.zeros((nt,nsublat,nsublon))
      for t in numpy.arange(nt):
          precip = f.readReals()
          precip.shape = [nlat,nlon]
          data[t,:,:] = precip[wh_true].reshape(nsublat,nsublon) 

      datastore.append(data)

   # Make a single 3d numpy array out of my list of numpy arrays
   nt = 0
   for i in range(len(datastore)):
	nt = nt + datastore[i].shape[0]

   final_data = numpy.zeros((nt,nsublat,nsublon))
   t=0
   for i in range(len(datastore)):
	nt = datastore[i].shape[0]
        final_data[t:t+nt,:,:] = datastore[i]
        t=t+nt

   # Load in land/sea mask
   ls = numpy.fromfile("/nas/share1-hp/jinwonki/data/obs/pr25urd/s/d/lsm25.usa",sep=" ")
   ls.shape = [nlat,nlon]
   # Extract subregion from land/sea mask
   subls = numpy.ones(final_data.shape)
   for t in numpy.arange(final_data.shape[0]):
      subls[t,:,:] = ls[wh_true].reshape(nsublat,nsublon) 

   # Construct a masked array of data i.e. only using data from land points
   mdi = -1
   mdata = ma.masked_array(final_data,mask=(subls==mdi))

   # Construct datetime list from dates in filenames.
   yearmonth=numpy.zeros(len(filelist))
   i=0
   for filename in filelist:
       # Extract month and year from filename
       yearmonth[i] = int(filename[7:13])
       i += 1

   # Construct a list of datetimes between the earliest and latest yearmonth
   firstyear = int(str(yearmonth.min())[0:4])
   firstmonth = int(str(yearmonth.min())[4:6])
   times=[]

   cur_time = datetime.datetime(firstyear,firstmonth,1,0,0,0,0)

   for i in range(final_data.shape[0]):
      times.append(cur_time)
      dt = datetime.timedelta(days=1)
      cur_time = cur_time + dt

   return sublats,sublons,times,mdata


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

   import numpy
   import numpy.ma as ma

   # Parameters specific to WRF domain setup required for these files
   if(dom_num == 1):
      nx = 190
      ny = 130

   if(dom_num == 2):
      nx = 192
      ny = 180
     
   # Create an empty array to store the weights
   myweights = numpy.zeros((ny,nx))
   mymask = numpy.ones((ny,nx))
   
   # Load in data from the mask file
   i,j,w = numpy.loadtxt("/home/plean/demo/rcmes/watersheds/"+myfile, unpack=True)

   for q in numpy.arange(len(i)):
      myweights[j[q],i[q]] = w[q]

   mymask = numpy.empty((ny,nx))
   mymask[:] = True
   mymask[(myweights>0.5)] = False

   return mymask


def read_eraint_surf_files(filelist,myvar,latMin,latMax,lonMin,lonMax):
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
   import os
   import datetime
   import time

   import Nio
   import numpy as np
   import numpy.ma as ma
   import rcmes.process

   #filelist.sort()

   # Crash nicely if 'filelist' is zero length
   if len(filelist)==0:
      print 'Error: no files have been passed to read_data_from_file_list()'
      return -1,-1,-1,-1

   # Open the first file in the list to:
   #    i) read in lats, lons
   #    ii) find out how many timesteps in the file 
   #        (assume same ntimes in each file in list)
   #     -allows you to create an empty array to store variable data for all times
   tmp=Nio.open_file(filelist[0])
   latsraw = tmp.variables["latitude"]
   lonsraw = tmp.variables["longitude"]
   lat = latsraw[:]
   lon = lonsraw[:]
   print 'Lats and lons read in for first file in filelist'

   # Create mask to extract required region only
   #  NB. longitude is slightly more complicated as can wrap the prime meridion
   print 'Extracting for :- lats:',latMin, latMax,' lons: ',lonMin, lonMax
   wh_lat = np.logical_and((lat>=latMin),(lat<=latMax))
   if(lonMin<lonMax):
     wh_lon = np.logical_and((lon>=lonMin), (lon<=lonMax))
   if(lonMin>lonMax):
     wh_lon = np.logical_or((lon>=lonMin), (lon<=lonMax))

   sublat = lat[wh_lat]
   sublon = lon[wh_lon]

   wh_true1,wh_true2 = np.meshgrid(wh_lon,wh_lat)
   wh = np.logical_and(wh_true1,wh_true2)

   # Create storage lists
   datastore = []
   timestore = []

   # Now load in the data for real
   #  NB. no need to reload in the latitudes and longitudes -assume invariant
   i=0
   timesaccu=0 # a counter for number of times stored so far in t2store 
               #  NB. this method allows for missing times in data files 
               #      as no assumption made that same number of times in each file...
   for ifile in filelist:
     print 'Loading data from file: ',filelist[i]
     f=Nio.open_file(ifile, format='nc')
     data = f.variables[myvar][:]
     scale = f.variables[myvar].scale_factor
     offset = f.variables[myvar].add_offset

     data = data*scale+offset

     times = f.variables["time"][:]
     ntimes = times.size
     # Decode times into python datetime object

     sub=data[:,wh].reshape(ntimes,sublat.size,sublon.size)
     datastore.append(sub)

     timestore.append(times)

     timesaccu=timesaccu+ntimes
     i += 1 


   # move data from lists into correctly dimensioned arrays
   final_data = np.zeros((timesaccu,sublat.size,sublon.size))
   t=0
   for i in range(len(datastore)):
	nt = datastore[i].shape[0]
        final_data[t:t+nt,:,:] = datastore[i]
        t=t+nt

   times = np.zeros((timesaccu))
   t=0
   for i in range(len(timestore)):
	nt = timestore[i].shape[0]
        times[t:t+nt] = timestore[i]
        t=t+nt
  
   # Decode times into python datetime objects
   times = rcmes.process.decode_eraint_surf_times(times)

   print 'Data read in successfully with dimensions: ',final_data.shape

   # Create masked array using missing value flag from file
   mdi = f.variables[myvar]._FillValue[0]
   mdata = ma.masked_array(final_data,mask=(final_data==mdi))

   # Rearrange array so data match lat lon values
   mdata=np.flipud(mdata[:,::-1])

   return sublat, sublon, times, mdata


def make_list_of_urd_files(startTime, endTime):
   '''
    Routine to make a list of URD file names (for use with local repository)
    
     Input:
        startTime: datetime object of start time
        endTime:   datetime object of end time
   
     Output:
        filenamelist - list of filename strings
   
       Peter Lean  September 2010
   '''

   import datetime

   # NB. timedelta has no months functionality as months are variable length and so it is ambiguous
   #		-to get around this here, I set the day to the middle of the month and add 30 days
   #		-each January I reset the day to the 15th so that there is no drift in long time series.
   dt = datetime.timedelta(days=30)

   newstartTime = datetime.datetime(startTime.year,startTime.month,15,00,00,00,00)

   
   filenamelist = []

   curTime = newstartTime
   while curTime <= endTime:
      filenamelist.append('pr_ncep'+str(curTime.year)+str("%.2i"% curTime.month))
      curTime += dt
      if(curTime.month==1):
         curTime = datetime.datetime(curTime.year,curTime.month,15,00,00,00,00)

   return filenamelist


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

   import datetime

   dt = datetime.timedelta(hours=6)

   filenamelist = []

   curTime = firstTime
   while curTime <= lastTime:
      curTimeString = curTime.strftime("%Y-%m-%d_%H:%M:%S")
      filenamelist.append('wrfout_'+ident+'_'+curTimeString)

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

   import datetime
 
   trmm_repository = '/nas/share4-cf/plean/TRMM/'

   dt = datetime.timedelta(hours=24)

   filenamelist = []

   curTime = firstTime
   while curTime <= lastTime:
      curTimeString = curTime.strftime("%Y.%m.%d")
      filenamelist.append(trmm_repository+'3B42_daily.'+curTimeString+'.6.nc')

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

   import datetime
   import glob

   airs_repository = '/nas/share4-cf/plean/AIRX3STD/'

   dt = datetime.timedelta(hours=24)

   filenamelist = []

   curTime = firstTime
   while curTime <= lastTime:
      curTimeString = curTime.strftime("%Y.%m.%d")
      filenamelist.append(glob.glob(airs_repository+'AIRS.'+curTimeString+'.L3.*.nc')[0])

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

   import datetime
 
   dt = datetime.timedelta(days=30)

   filenamelist = []

   newfirstTime = datetime.datetime(firstTime.year,firstTime.month,15,0,0,0)
   newlastTime = datetime.datetime(lastTime.year,lastTime.month,15,0,0,0)

   curTime = newfirstTime
   while curTime <= newlastTime:
      curTimeString = curTime.strftime("%Y%m")
      filenamelist.append('pr_ncep'+curTimeString)
      if(curTime.month==1):
         curTime = datetime.datetime(curTime.year,curTime.month,15,00,00,00,00)

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
   newfirstTime = datetime.datetime(firstTime.year,firstTime.month,15,0,0,0)
   newlastTime = datetime.datetime(lastTime.year,lastTime.month,15,0,0,0)

   curTime = newfirstTime
   while curTime <= newlastTime:
      curTimeString = curTime.strftime("%b%Y")
      filenamelist.append(eraint_repository+'sfc.'+curTimeString.lower()+'.nc')
      if(curTime.month==1):
         curTime = datetime.datetime(curTime.year,curTime.month,15,00,00,00,00)

      curTime += dt
   
   return filenamelist
