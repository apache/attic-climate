#!/usr/local/bin/python

def prep_data(cachedir,workdir,                                                                                                    \
              obsList,obsDatasetId,obsParameterId,                                                                                 \
              startTime,endTime,                                                                                                   \
              latMin,latMax,lonMin,lonMax,dLat,dLon,naLats,naLons,                                                                 \
              mdlList,                                                                                                             \
              numSubRgn,subRgnLon0,subRgnLon1,subRgnLat0,subRgnLat1,subRgnName,                                                    \
              modelVarName,precipFlag,modelTimeVarName,modelLatVarName,modelLonVarName,                                            \
              regridOption,timeRegridOption,maskOption,FoutOption):

 ##################################################################################################################
 # Routine to read-in and re-grid both obs and mdl datasets.
 # Processes both single and multiple files of obs and mdl or combinations in a general way.
 #       i)    retrieve observations from the database
 #       ii)   load in model data
 #       iii)  temporal regridding
 #       iv)   spatial regridding
 #       v)    area-averaging
 #       Input:
 #               cachedir 	- string describing directory path
 #               workdir 	- string describing directory path
 #               obsList        - string describing the observation data files
 #               obsDatasetId 	- int, db dataset id
 #               obsParameterId	- int, db parameter id 
 #               startTime	- datetime object, the starting time of evaluation
 #               endTime	- datetime object, the ending time of evaluation
 #               latMin, latMax, lonMin, lonMax, dLat, dLon, naLats, naLons: define the evaluation/analysis domain/grid system
 #	         latMin		- float
 #               latMax		- float
 #               lonMin		- float
 #               lonMax		- float
 #               dLat  		- float
 #               dLon  		- float
 #               naLats		- integer
 #               naLons		- integer
 #               mdlList	- string describing model file name + path
 #               modelVarName	- string describing name of variable to evaluate (as written in model file)
 #	         precipFlag	- bool  (is this precipitation data? True/False)
 #               modelTimeVarName - string describing name of time variable in model file 	
 #               modelLatVarName  - string describing name of latitude variable in model file 
 #               modelLonVarName  - string describing name of longitude variable in model file 
 #               regridOption 	 - string: 'obs'|'model'|'regular'
 #               timeRegridOption -string: 'full'|'annual'|'monthly'|'daily'
 #               maskOption - int (=1 if set)
 #               maskLatMin - float (only used if maskOption=1)
 #               maskLatMax - float (only used if maskOption=1)
 #	         maskLonMin - float (only used if maskOption=1)
 #               maskLonMax - float (only used if maskOption=1)
 #       Output: image files of plots + possibly data
 #       Jinwon Kim, 7/11/2012
 ##################################################################################################################
 import sys
 import os
 import math
 import subprocess
 import datetime
 import pickle
 import numpy; import numpy as np; import numpy.ma as ma; import Nio
 import rcmes.db_v12; import rcmes.files_20; import rcmes.process_v12

  # assign parameters that must be preserved throughout the process
 T00=273.16    # the triple-point temperature
 yymm0=startTime.strftime("%Y%m"); yymm1=endTime.strftime("%Y%m"); print 'start & end eval period = ',yymm0,yymm1
  # check the number of obs & model data files
 numOBSs=len(obsList)
 numMDLs=len(mdlList)
 if numMDLs < 1: print 'No input model data file. EXIT'; return -1         # no input mdl data file
 if numOBSs < 1: print 'No input observation data file. EXIT'; return -1   # no input obs data file

  ##################################################################################################################
  ## Part 1: retrieve observation data from the database and regrid them
  ##       NB. automatically uses local cache if already retrieved.
  ##################################################################################################################
 print 'the number of observation datasets: ',numOBSs
 print obsList,obsDatasetId,obsParameterId,latMin,latMax,lonMin,lonMax,startTime,endTime,cachedir

  # prepararation for spatial regridding: define the size of horizontal array of the target interpolation grid system (ngrdX and ngrdY)
 if regridOption=='model':
   ifile=mdlList[0]; typeF='nc'
   modelLats,modelLons,mTimes = rcmes.files_20.read_lolaT_from_file(ifile,modelLatVarName,modelLonVarName,modelTimeVarName,typeF)
   lats=modelLats; lons=modelLons
 if regridOption=='regular':
   lat = np.arange(naLats)*dLat+latMin; lon = np.arange(naLons)*dLon+lonMin; lons,lats = np.meshgrid(lon,lat); lon=0.; lat=0.
 ngrdY=lats.shape[0]; ngrdX=lats.shape[1]

 regObsData=[]
 for n in np.arange(numOBSs):
    # spatial regridding
   oLats,oLons,oLevs,oTimes,oData =  \
     rcmes.db_v12.extract_data_from_db(obsDatasetId[n],obsParameterId[n],latMin,latMax,lonMin,lonMax,startTime,endTime,cachedir)
    # TODO: modify this if block with new metadata usage.
   if (precipFlag==True) & (obsList[n][0:3] == 'CRU'):
     oData = 86400.*oData
   #print 'Raw data ',oData[10,100,51:150]# return -1,-1,-1,-1  # missing data are read-in ok.
   nstOBSs=oData.shape[0]         # note that the length of obs data can vary for different obs intervals (e.g., daily vs. monthly)
   print 'Regrid OBS dataset onto the ',regridOption,' grid system: ngrdY, ngrdX, nstOBSs= ',ngrdY,ngrdX,nstOBSs
   tmpOBS=ma.zeros((nstOBSs,ngrdY,ngrdX))
   for t in np.arange(nstOBSs):
     tmpOBS[t,:,:] = rcmes.process_v12.do_regrid(oData[t,:,:],oLats,oLons,lats,lons)
   #if n==0: print 'Spatial regridding ',tmpOBS[10,100,50:100]# return -1,-1,-1,-1# spatial interpolation preserves the missing data flag ok
   oLats=0.; oLons=0.       # release the memory occupied by the temporary variables oLats and oLons.
    # temporally regrid the spatially regridded obs data
   oData,newObsTimes = rcmes.process_v12.calc_average_on_new_time_unit_K(tmpOBS,oTimes,unit=timeRegridOption); tmpOBS=0.
   #if n==0: print 'Temporal regridding ',oData[10,100,50:100]# return -1,-1,-1,-1# temporal regridding preserves the missing data flag ok
    # check the consistency of temporally regridded obs data
   if n == 0:
     oldObsTimes = newObsTimes
   else:
     if oldObsTimes != newObsTimes:
       print 'temporally regridded obs data time levels do not match at ',n-1,n
       return -1,-1,-1,-1
     else:
       oldObsTimes = newObsTimes
    # if everything's fine, append the spatially and temporally regridded data in the obs data array (obsData)
   regObsData.append(oData)
  # all obs datasets have been read-in and regridded. convert the regridded obs data from 'list' to 'array'
  # also finalize 'obsTimes', the time cooridnate values of the regridded obs data.
  # NOTE: using 'list_to_array' assigns values to the missing points; this has become a problem in handling the CRU data.
  #       this problem disappears by using 'ma.array'.
 obsData = ma.array(regObsData); obsTimes=newObsTimes; regObsData=0; oldObsTimes=0
 nT=len(obsTimes)
 #obsData = list_to_array(regObsData); obsTimes=newObsTimes; regObsData=0; oldObsTimes=0
  # compute the simple multi-obs ensemble if multiple obs are used
 if numOBSs > 1:
   oData=obsData
   obsData=ma.zeros((numOBSs+1,nT,ngrdY,ngrdX))
   avg=ma.zeros((nT,ngrdY,ngrdX))
   for i in np.arange(numOBSs):
     obsData[i,:,:,:]=oData[i,:,:,:]
     avg[:,:,:]=avg[:,:,:]+oData[i,:,:,:]
   avg=avg/float(numOBSs)
   obsData[numOBSs,:,:,:]=avg[:,:,:]     # store the model-ensemble data
   numOBSs=numOBSs+1                     # update the number of obs data to include the model ensemble
   obsList.append('ENS-OBS')
 print 'OBS regridded: ',obsData.shape
 #print obsData[0,10,100,50:100]; return -1,-1,-1,-1

  ##################################################################################################################
  ## Part 2: load in and regrid model data from file(s)
  ## NOTE: tthe wo parameters, numMDLs and numMOmx are defined to represent the number of models (w/ all 240 mos) &
  ##       the total number of months, respectively, in later multi-model calculations.
  ##################################################################################################################
 typeF='nc'; mdlName=[]; regridMdlData=[]
  # extract the model names and store them in the list 'mdlName'
 for n in np.arange(numMDLs):
   name=mdlList[n][46:60]; ii=3; i=0; print 'Input model name= ',name
   for i in np.arange(ii):
     if(name[i]=='-'): ii=i
   name=name[0:ii]; mdlName.append(name)
    # read model grid info, then model data
   ifile=mdlList[n]; print 'ifile= ',ifile
   modelLats,modelLons,mTimes = rcmes.files_20.read_lolaT_from_file(ifile,modelLatVarName,modelLonVarName,modelTimeVarName,typeF)
   mTime,mdlDat = rcmes.files_20.read_data_from_one_file(ifile,modelVarName,modelTimeVarName,modelLats,typeF)
   mdlT=[]; mStep=len(mTimes)
   for i in np.arange(mStep):
     mdlT.append(mTimes[i].strftime("%Y%m"))
   wh = (np.array(mdlT)>=yymm0) & (np.array(mdlT)<=yymm1)
   modelTimes = list(np.array(mTimes)[wh])
   mData=mdlDat[wh,:,:]
    # determine the dimension size from the model time and latitude data.
   nT=len(modelTimes); nmdlY=modelLats.shape[0]; nmdlX=modelLats.shape[1]; print 'nT, ngrdY, ngrdX = ',nT,ngrdY, ngrdX,min(modelTimes),max(modelTimes)
    # spatial regridding of the modl data
   tmpMDL=ma.zeros((nT,ngrdY,ngrdX))
   for t in np.arange(nT):
     tmpMDL[t,:,:] = rcmes.process_v12.do_regrid(mData[t,:,:],modelLats,modelLons,lats,lons)
    # temporally regrid the model data
   mData,newMdlTimes = rcmes.process_v12.calc_average_on_new_time_unit_K(tmpMDL,modelTimes,unit=timeRegridOption); tmpMDL=0.
    # check data consistency for all models 
   if n == 0:
     oldMdlTimes = newMdlTimes
   else:
     if oldMdlTimes != newMdlTimes:
       print 'temporally regridded mdl data time levels do not match at ',n-1,n
       print len(oldMdlTimes),len(newMdlTimes)
       return -1,-1,-1,-1
     else:
       oldMdlTimes = newMdlTimes
    # if everything's fine, append the spatially and temporally regridded data in the obs data array (obsData)
   regridMdlData.append(mData)
 modelData=ma.array(regridMdlData); modelTimes =newMdlTimes;  regridMdlData=0; oldMdlTimes = 0; newMdlTimes = 0
 #modelData=list_to_array(regridMdlData); modelTimes =newMdlTimes;  regridMdlData=0; oldMdlTimes = 0; newMdlTimes = 0

  # check consistency between the time levels of the model and obs data
  #   this is the final update of time levels: 'Times' and 'nT'
 if obsTimes != modelTimes:
   print 'time levels of the obs and model data are not consistent. EXIT'
   print 'obsTimes'; print obsTimes; print 'modelTimes'; print modelTimes; return -1, -1, -1, -1
  #  'Times = modelTimes = obsTimes' has been established and modelTimes and obsTimes will not be used hereafter. (de-allocated)
 Times=modelTimes; nT=len(modelTimes); modelTimes=0; obsTimes=0

 print 'Reading and regridding model data are completed'; print 'numMDLs, modelData.shape= ',numMDLs,modelData.shape
  # compute the simple multi-model ensemble if multiple modles are evaluated
 if numMDLs > 1:
   mdlData=modelData
   modelData=ma.zeros((numMDLs+1,nT,ngrdY,ngrdX))
   avg=ma.zeros((nT,ngrdY,ngrdX))
   for i in np.arange(numMDLs):
     modelData[i,:,:,:]=mdlData[i,:,:,:]
     avg[:,:,:]=avg[:,:,:]+mdlData[i,:,:,:]
   avg=avg/float(numMDLs)
   modelData[numMDLs,:,:,:]=avg[:,:,:]     # store the model-ensemble data
   i0mdl=0; i1mdl=numMDLs
   numMDLs=numMDLs+1 
   mdlName.append('ENS')
   print 'Eval mdl-mean timeseries for the obs periods: modelData.shape= ',modelData.shape

  # convert model precip unit from mm/s to mm/d: Note that only applies to CORDEX for now
  #* Looks like cru3.1 is in mm/sec & TRMM is mm/day. Need to check and must be fixed as a part of the metadata plan.
  # TODO: get rid of this if block with new metadata usage
 if precipFlag==True:
   modelData = modelData*86400.  # convert from kg/m^2/s into mm/day
 #print modelData[0,10,100,100],obsData[0,10,100,100]#obsData[1,10,100,100]; return -1
 #print 'before area averaging ',obsData[0,10,100,50:100]

  ##################################################################################################################
  # (Optional) Part 5: area-averaging
  #      RCMET calculate metrics either at grid point or for area-means over a defined (masked) region.
  #      If area-averaging is selected, then a user have also selected how to define the area to average over.
  #      The options were:
  #              -define masked region using regular lat/lon bounding box parameters
  #              -read in masked region from file
  #         either i) Load in the mask file (if required)
  #             or ii) Create the mask using latlonbox  
  #           then iii) Do the area-averaging
  ##################################################################################################################
 obsRgnAvg=ma.zeros((numOBSs,numSubRgn,nT)); mdlRgnAvg=ma.zeros((numMDLs,numSubRgn,nT))
 if maskOption==1:  # i.e. define regular lat/lon box for area-averaging
   print 'Enter area-averaging: modelData.shape, obsData.shape ',modelData.shape,obsData.shape
   print 'Using Latitude/Longitude Mask for Area Averaging'
   for n in np.arange(numSubRgn):
      # Define mask using regular lat/lon box specified by users (i.e. ignore regions where mask = True)
     maskLonMin=subRgnLon0[n]; maskLonMax=subRgnLon1[n]; maskLatMin=subRgnLat0[n]; maskLatMax=subRgnLat1[n]
     mask = np.logical_or( np.logical_or(lats<=maskLatMin,lats>=maskLatMax), np.logical_or(lons<=maskLonMin,lons>=maskLonMax) )
      # Calculate area-weighted averages within this region and store in new lists: first average obs data (single time series)
     for k in np.arange(numOBSs):
       obsStore=[]
       for t in np.arange(nT):
         obsStore.append(rcmes.process.calc_area_mean(obsData[k,t,:,:],lats,lons,mymask=mask))
       obsRgnAvg[k,n,:]=ma.array(obsStore[:])
     for k in np.arange(numMDLs):
       mdlStore=[]
       for t in np.arange(nT):
         mdlStore.append(rcmes.process.calc_area_mean(modelData[k,t,:,:],lats,lons,mymask=mask))
       mdlRgnAvg[k,n,:]=ma.array(mdlStore)
   obsStore=[]; mdlStore=[]
   #print 'mask option = 1: obs & mdl shapes ',obsRgnAvg.shape,mdlRgnAvg.shape
   #for k in np.arange(nT):
   #  print obsRgnAvg[0,3,k],mdlRgnAvg[0,3,k]; k+=12
 else:       # no sub-regions. return 'null' variables for the regional mean timeseries
   obsRgnAvg=0.; mdlRgnAvg=0.

  ##################################################################################################################
  # Output according to the output method options
  # Create a binary file of raw obs & model data and exit. If maskOption==1, also write area-averaged time series
  #   in the same data file.
  ##################################################################################################################
 if FoutOption==1:
    # write 1-d long and lat values
   fileName=workdir+'/lonlat'+ '.bn'
    # clean up old file
   if(os.path.exists(fileName)==False):
     rcmes.files_20.writeBN_lola(fileName,lons,lats)
    # write obs/model data values
   fileName=workdir+'/Tseries_' + modelVarName + '.bn'
   print 'Created monthly data file ',fileName,' for user"s own processing'
   print 'The file includes monthly time series of ',numOBSs,' obs and ',numMDLs,' models ',nT,' steps ',ngrdX,'x',ngrdY,' grids'
   if(os.path.exists(fileName)==True):
     cmnd='rm -f ' + fileName; subprocess.call(cmnd,shell=True)
   rcmes.files_20.writeBNdata(fileName,maskOption,numOBSs,numMDLs,nT,ngrdX,ngrdY,numSubRgn,obsData,modelData,obsRgnAvg,mdlRgnAvg)
 if FoutOption==2:                    # print a netCDF file
   foName=workdir+'/Tseries'
   tempName = foName + '.' + 'nc'
    # if the file already exists, delete it before writing. otherwise, the process below will add values to the existing file.
   if(os.path.exists(tempName)==True):
     print "removing %s from the local filesystem, so it can be replaced..." % (tempName, )
     cmnd='rm -f ' + tempName; subprocess.call(cmnd,shell=True)
   rcmes.files_20.writeNCfile(foName,lons,lats,obsData,modelData,obsRgnAvg,mdlRgnAvg)

  # Processing complete
 print 'data_prep is completed: both obs and mdl data are re-gridded to a common analysis grid'

  # return regridded variables
 return numOBSs,numMDLs,nT,ngrdY,ngrdX,Times,obsData,mdlData,obsRgnAvg,mdlRgnAvg,obsList,mdlName
