import Nio 
import numpy as np
import numpy.ma as ma
import toolkit.process as process
import toolkit.process_v12 as process_v12
import math


def findunique(seq):
    keys = {}
    for e in seq:
        keys[e] = 1
    return keys.keys()


def read_lolaT_from_file(ifile,latVarName,lonVarName,timeVarName,file_type):
   ##################################################################################
   # Read in the long & lat of model grid
   ##################################################################################

   tmp=Nio.open_file(ifile,format=file_type)
   lonsraw = tmp.variables[lonVarName][:]
   latsraw = tmp.variables[latVarName][:]
   lonsraw[lonsraw>180] = lonsraw[lonsraw>180]-360.  # convert to -180,180 if necessary
   if(latsraw.ndim == 1):
     lon,lat = np.meshgrid(lonsraw,latsraw)
   if(latsraw.ndim == 2):
     lon = lonsraw; lat = latsraw
   timestore = process.getModelTimes(ifile,timeVarName)
   print '  read_lolaT_from_file: Lats, lons and times read in for the model domain'
   return lat,lon,timestore

def read_data_from_one_file(ifile,myvar,timeVarName,lat,file_type):
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
   tmp=Nio.open_file(ifile,format=file_type)
   timesraw = tmp.variables[timeVarName]
   ntimes=len(timesraw); nygrd=len(lat[:,0]); nxgrd=len(lat[0,:])
    # Create a single empty masked array to store model data from all files
   t2store = ma.zeros((ntimes,nygrd,nxgrd))
    # Now load in the data for real
   print '  read_data_from_one_file: Loading data from file: ',ifile
   f=Nio.open_file(ifile)
   t2raw = f.variables[myvar][:]
   timesraw = f.variables[timeVarName]
   time=timesraw[0:ntimes]
   t2tmp = t2raw.squeeze()
   if t2tmp.ndim==2:
      t2tmp = np.expand_dims(t2tmp,0)
   t2store=t2tmp
   f.close()
   print '  read_data_from_one_file: Data read in successfully with dimensions: ',t2store.shape
   timestore = process.getModelTimes(ifile,timeVarName)
   return timestore, t2store

def read_data_from_file_list_K(filelist,myvar,timeVarName,latVarName,lonVarName,file_type):
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
   nfiles=len(filelist)
    # Crash nicely if 'filelist' is zero length
   if nfiles==0:
     print 'Error: no files have been passed to read_data_from_file_list(): Exit'
     return -1,-1,-1,-1

   # Open the first file in the list to:
   #    i)  read in lats, lons
   #    ii) find out how many timesteps in the file (assume same ntimes in each file in list)
   #     -allows you to create an empty array to store variable data for all times
   tmp=Nio.open_file(filelist[0],format=file_type)
   latsraw = tmp.variables[latVarName][:]
   lonsraw = tmp.variables[lonVarName][:]
   lonsraw[lonsraw>180] = lonsraw[lonsraw>180]-360.  # convert to -180,180 if necessary
   if(latsraw.ndim == 1):
     lon,lat = np.meshgrid(lonsraw,latsraw)
   if(latsraw.ndim == 2):
     lon = lonsraw; lat = latsraw

   timesraw = tmp.variables[timeVarName]
   ntimes=len(timesraw); nygrd=len(lat[:,0]); nxgrd=len(lon[0,:])

   print 'Lats and lons read in for first file in filelist'

   # Create a single empty masked array to store model data from all files
   #t2store = ma.zeros((ntimes*nfiles,nygrd,nxgrd))
   t2store = ma.zeros((nfiles,ntimes,nygrd,nxgrd))
   #timestore=ma.zeros((ntimes*nfiles)) 

    ## Now load in the data for real
    ##  NB. no need to reload in the latitudes and longitudes -assume invariant
   #timesaccu=0 # a counter for number of times stored so far in t2store 
               #  NB. this method allows for missing times in data files 
               #      as no assumption made that same number of times in each file...
   i=0
   for ifile in filelist:
     #print 'Loading data from file: ',filelist[i]
     f=Nio.open_file(ifile)
     t2raw = f.variables[myvar][:]
     timesraw = f.variables[timeVarName]
     time=timesraw[0:ntimes]
     #ntimes=len(time)
     #print 'file= ',i,'ntimes= ',ntimes,filelist[i]
      ## Flatten dimensions which needn't exist, i.e. level 
      ##   e.g. if for single level then often data have 4 dimensions, when 3 dimensions will do.
      ##  Code requires data to have dimensions, (time,lat,lon)
      ##    i.e. remove level dimensions
     t2tmp = t2raw.squeeze()
      ## Nb. if data happen to be for a single time, we flattened it by accident; lets put it back... 
     if t2tmp.ndim==2:
        t2tmp = np.expand_dims(t2tmp,0)
     #t2store[timesaccu+np.arange(ntimes),:,:]=t2tmp[0:ntimes,:,:]
     t2store[i,0:ntimes,:,:]=t2tmp[0:ntimes,:,:]
     #timestore[timesaccu+np.arange(ntimes)]=time
     #timesaccu=timesaccu+ntimes
     f.close()
     i += 1 
     
   print 'Data read in successfully with dimensions: ',t2store.shape

    # Decode model times into python datetime objects. Note: timestore becomes a list (no more an array) here
   ifile=filelist[0]
   timestore = process.getModelTimes(ifile,timeVarName)

   return lat, lon, timestore, t2store

def read_data_from_file_list(filelist,myvar,timeVarName,latVarName,lonVarName,file_type):
   '''
   ##################################################################################
   # Read in data from a list of model files into a single data structure
   #
   # Input:
   #    filelist - list of filenames (including path)
   #    myvar    - string containing name of variable to load in (as it appears in file)
   # Output:
   #    lat, lon - 2D array of latitude and longitude values
   #    times    - list of times
   #    t2store  - numpy array containing data from all files    
   #
   #  NB. originally written specific for WRF netCDF output files
   #      modified to make more general (Feb 2011)
   #
   #   Peter Lean July 2010 
   ##################################################################################
   '''

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
   tmp=Nio.open_file(filelist[0],format=file_type)
   latsraw = tmp.variables[latVarName][:]
   lonsraw = tmp.variables[lonVarName][:]
   lonsraw[lonsraw>180] = lonsraw[lonsraw>180]-360.  # convert to -180,180 if necessary

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
   timestore=ma.zeros((ntimes*len(filelist))) 

   # Now load in the data for real
   #  NB. no need to reload in the latitudes and longitudes -assume invariant
   i=0
   timesaccu=0 # a counter for number of times stored so far in t2store 
               #  NB. this method allows for missing times in data files 
               #      as no assumption made that same number of times in each file...


   for ifile in filelist:

     #print 'Loading data from file: ',filelist[i]
     f=Nio.open_file(ifile)
     t2raw = f.variables[myvar][:]
     timesraw = f.variables[timeVarName]
     time=timesraw[:]
     ntimes=len(time)
     print 'file= ',i,'ntimes= ',ntimes,filelist[i]

     # Flatten dimensions which needn't exist, i.e. level 
     #   e.g. if for single level then often data have 4 dimensions, when 3 dimensions will do.
     #  Code requires data to have dimensions, (time,lat,lon)
     #    i.e. remove level dimensions
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
   #print timestore[0:240]

    # TODO: search for duplicated entries (same time) and remove duplicates.
    # Check to see if number of unique times == number of times, if so then no problem
   #print 'np.unique(timestore)= ',np.unique(timestore)
   #if(len(np.unique(timestore))!=len(np.where(timestore!=0)[0].view())):
   #  print 'WARNING: Possible duplicated times'

    # Decode model times into python datetime objects. Note: timestore becomes a list (no more an array) here
   ifile=filelist[0]
   timestore = rcmes.processK.decode_model_times(ifile,timeVarName,file_type)

   return lat, lon, timestore, t2store


def select_var_from_file(myfile,fmt='not set'):
   '''
   # Routine to act as user interface to allow users to select variable of interest from a file.
   # 
   #  Input:
   #     myfile - filename
   #     fmt - (optional) specify fileformat for PyNIO if filename suffix is non-standard
   #
   #  Output:
   #     myvar - variable name in file
   #
   #    Peter Lean  September 2010
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
   # Routine to act as user interface to allow users to select variable of interest from a wrf netCDF file.
   # 
   #  Input:
   #     myfile - filename
   #
   #  Output:
   #     mywrfvar - variable name in wrf file
   #
   #    Peter Lean  September 2010
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

def writeBN_lola(fileName,lons,lats):
  # write a binary data file that include longitude (1-d) and latitude (1-d) values
 import rcmes.fortranfile

 F=rcmes.fortranfile.FortranFile(fileName,mode='w')
 ngrdY=lons.shape[0]; ngrdX=lons.shape[1]
 tmpDat=ma.zeros(ngrdX); tmpDat[:]=lons[0,:]; F.writeReals(tmpDat)
 tmpDat=ma.zeros(ngrdY); tmpDat[:]=lats[:,0]; F.writeReals(tmpDat)
  # release temporary arrays
 tmpDat=0
 F.close()

def writeBNdata       \
   (fileName,maskOption,numOBSs,numMDLs,nT,ngrdX,ngrdY,numSubRgn,obsData,mdlData,obsRgnAvg,mdlRgnAvg):
 import rcmes.fortranfile

  # write spatially- and regionally regridded data into a binary data file
 missing=-1.e26
 F=rcmes.fortranfile.FortranFile(fileName,mode='w')
  # construct a data array to replace mask flag with a missing value (missing=-1.e12) for printing
 data=ma.zeros((nT,ngrdY,ngrdX))
 for m in np.arange(numOBSs):
   data[:,:,:]=obsData[m,:,:,:]; msk=data.mask
   for n in np.arange(nT):
     for j in np.arange(ngrdY):
       for i in np.arange(ngrdX):
         if msk[n,j,i]: data[n,j,i]=missing
    # write observed data. allowed to write only one row at a time
   tmpDat=ma.zeros(ngrdX)
   for n in np.arange(nT):
     for j in np.arange(ngrdY):
       tmpDat[:]=data[n,j,:]
       F.writeReals(tmpDat)
  # write model data (dep. on the number of models).
 for m in np.arange(numMDLs):
   data[:,:,:]=mdlData[m,:,:,:]; msk=data.mask
   for n in np.arange(nT):
     for j in np.arange(ngrdY):
       for i in np.arange(ngrdX):
         if msk[n,j,i]: data[n,j,i]=missing
   for n in np.arange(nT):
     for j in np.arange(ngrdY):
       tmpDat[:]=data[n,j,:]
       F.writeReals(tmpDat)
 data=0     # release the array allocated for data
  # write data in subregions
 if maskOption:
   print 'Also included are the time series of the means over ',numSubRgn,' areas from obs and model data'
   tmpDat=ma.zeros(nT); print numSubRgn
   for m in np.arange(numOBSs):
     for n in np.arange(numSubRgn):
       tmpDat[:]=obsRgnAvg[m,n,:]
       F.writeReals(tmpDat)
   for m in np.arange(numMDLs):
     for n in np.arange(numSubRgn):
       tmpDat[:]=mdlRgnAvg[m,n,:]
       F.writeReals(tmpDat)
 tmpDat=0     # release the array allocated for tmpDat
 F.close()

def writeNCfile(fileName,lons,lats,obsData,mdlData,obsRgnAvg,mdlRgnAvg):
  # write an output file of variables up to 3 dimensions
  # fileName: the name of the output data file
  # lons[ngrdX]: longitude
  # lats[ngrdY]: latitudes
  # obsData[nT,ngrdY,ngrdX]: the obs time series of the entire model domain
  # mdlData[numMDLs,nT,ngrdY,ngrdX]: the mdltime series of the entire model domain
  # obsRgnAvg[numSubRgn,nT]: the obs time series for the all subregions
  # mdlRgnAvg[numMDLs,numSubRgn,nT]: the mdl time series for the all subregions

 dimO=obsData.shape[0]
 dimM=mdlData.shape[0]
 dimT=mdlData.shape[1]
 dimY=mdlData.shape[2]
 dimX=mdlData.shape[3]
 dimR=obsRgnAvg.shape[1]
 f = Nio.open_file(fileName,mode='w',format='nc')
 print mdlRgnAvg.shape,dimM,dimR,dimT
  #create global attributes
 f.globalAttName = ''
  # create dimensions
 f.create_dimension('unity',1)
 f.create_dimension('time',dimT)
 f.create_dimension('west_east',dimX)
 f.create_dimension('south_north',dimY)
 f.create_dimension('obss',dimO)
 f.create_dimension('mdls',dimM)
 f.create_dimension('rgns',dimR)
  # create the variable (real*4) to be written in the file
 var = f.create_variable('lon','d',('south_north','west_east'))
 var = f.create_variable('lat','d',('south_north','west_east'))
 var = f.create_variable('oDat','d',('obss','time','south_north','west_east'))
 var = f.create_variable('mDat','d',('mdls','time','south_north','west_east'))
 var = f.create_variable('oRgn','d',('rgns','time'))
 var = f.create_variable('mRgn','d',('mdls','rgns','time'))
  # create attributes and units for the variable
 f.variables['lon'].varAttName = 'Longitudes'; f.variables['lon'].varUnit = 'degrees East'
 f.variables['lat'].varAttName = 'Latitudes'; f.variables['lat'].varUnit = 'degrees North'
 f.variables['oDat'].varAttName = 'Obseration time series: entire domain'
 f.variables['mDat'].varAttName = 'Model time series: entire domain'
 f.variables['oRgn'].varAttName = 'Obseration time series: Subregions'
 f.variables['mRgn'].varAttName = 'Model time series: Subregions'
  # assign the values to the variable and write it
 #print 'lons in writeFile'; print lons
 f.variables['lon'][:,:] = lons
 f.variables['lat'][:,:] = lats
 f.variables['oDat'][:,:,:,:] = obsData
 f.variables['mDat'][:,:,:,:] = mdlData
 f.variables['oRgn'][:,:,:] = obsRgnAvg
 f.variables['mRgn'][:,:,:] = mdlRgnAvg
 #print f
 f.close()
