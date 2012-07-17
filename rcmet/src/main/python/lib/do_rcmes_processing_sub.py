#!/usr/local/bin/python

def do_rcmes(cachedir, workdir, obsDatasetId, obsParameterId, startTime, endTime, latMin, latMax, lonMin, lonMax, filelist, modelVarName, precipFlag, modelTimeVarName, modelLatVarName, modelLonVarName, regridOption, timeRegridOption,seasonalCycleOption,metricOption,titleOption,plotFileNameOption,maskOption,maskLatMin,maskLatMax,maskLonMin,maskLonMax):
 '''
 ##################################################################################################################
 # Routine to perform full end-to-end RCMET processing.
 #
 #       i)    retrieve observations from the database
 #       ii)   load in model data
 #       iii)  temporal regridding
 #       iv)   spatial regridding
 #       v)    area-averaging
 #       vi)   seasonal cycle compositing
 #       vii)  metric calculation
 #       viii) plot production
 #
 #       Input: a huge argument list with all of the user options (which can be collected from the GUI)
 #               cachedir 	- string describing directory path
 #               workdir 	- string describing directory path
 #               obsDatasetId 	- int, db dataset id
 #               obsParameterId	- int, db parameter id 
 #               startTime	- datetime object (needs to change to string + decode)
 #               endTime		- datetime object (needs to change to string + decode)
 #	         latMin		- float
 #               latMax		- float
 #               lonMin		- float
 #               lonMax		- float
 #               filelist	- string describing model file name + path
 #               modelVarName	- string describing name of variable to evaluate (as written in model file)
 #	         precipFlag	- bool  (is this precipitation data? True/False)
 #               modelTimeVarName - string describing name of time variable in model file 	
 #               modelLatVarName  - string describing name of latitude variable in model file 
 #               modelLonVarName  - string describing name of longitude variable in model file 
 #               regridOption 	 - string: 'obs'|'model'|'regular'
 #               timeRegridOption -string: 'full'|'annual'|'monthly'|'daily'
 #               seasonalCycleOption - int (=1 if set) (probably should be bool longterm) 
 #	         metricOption - string: 'bias'|'mae'|'acc'|'pdf'|'patcor'|'rms'|'diff'
 #               titleOption - string describing title to use in plot graphic
 #               plotFileNameOption - string describing filename stub to use for plot graphic i.e. {stub}.png
 #               maskOption - int (=1 if set)
 #               maskLatMin - float (only used if maskOption=1)
 #               maskLatMax - float (only used if maskOption=1)
 #	         maskLonMin - float (only used if maskOption=1)
 #               maskLonMax - float (only used if maskOption=1)
 #
 #
 #
 #       Output: image files of plots + possibly data
 # 
 #       Peter Lean      February 2011
 #
 ##################################################################################################################
 '''

 import sys
 import os
 import math
 import subprocess
 import datetime
 import pickle
 import numpy; import numpy.ma as ma 
 # import Nio - NOT USED
 # import numpy as np - NOT USED 
 import rcmes.plots
 import rcmes.fortranfile
 import rcmes.db; import rcmes.files; import rcmes.process; import rcmes.metrics
 from rc_model import Model

 global modData
 global obData
 global mmt1
 global sigma_tt1
 ##################################################################################################################
 # Part 1: retrieve observation data from the database
 #       NB. automatically uses local cache if already retrieved.
 ##################################################################################################################
 obsLats,obsLons,obsLevs,obsTimes,obsData = rcmes.db.extract_data_from_db(obsDatasetId,obsParameterId,latMin,latMax,lonMin,lonMax,startTime,endTime,cachedir)
#extract climo data
 ##################################################################################################################
 # TEMPORARY INELEGANT UNIT CORRECTION TO CONVERT UNITS FOR CRU DATA WHICH WAS INGESTED INTO DB WITH WRONG UNITS
 # REMOVE THIS SECTION ONCE THE CRU DATA HAS BEEN RE-INGESTED CORRECTLY INTO DB
 ##################################################################################################################
 #if(obsParameterId==32):
 #       obsData = obsData / 30. # approx conversion from mm/month to mm/day (until we can reingest the data with correct units) 
 #if(obsParameterId==33):
 #       obsData = obsData + 273.15
 #if(obsParameterId==34):
 #       obsData = obsData + 273.15
 #if(obsParameterId==35):
 #       obsData = obsData + 273.15

  # assign parameters that must be preserved throughout the process
 if maskOption==1: seasonalCycleOption=1
 T00=273.16    # the triple-point temperature
 yymm0=startTime.strftime("%Y%m"); yymm1=endTime.strftime("%Y%m"); print 'start & end eval period = ',yymm0,yymm1
  # check the number of model data files
 numMDLs=len(filelist)
 if numMDLs < 1:         # no input data file
   print 'No input model data file. EXIT'; sys.exit()

  ##################################################################################################################
  ## Part 1: retrieve observation data from the database
  ##       NB. automatically uses local cache if already retrieved.
  ##################################################################################################################
 print obsDatasetId,obsParameterId,latMin,latMax,lonMin,lonMax,startTime,endTime,cachedir
 obsLats,obsLons,obsLevs,obsTimes,obsData =  \
   rcmes.db.extract_data_from_db(obsDatasetId,obsParameterId,latMin,latMax,lonMin,lonMax,startTime,endTime,cachedir)
 #print 'obsTimes= ',obsTimes; return 0

 ##################################################################################################################
 # Part 2: load in model data from file(s)
 ##################################################################################################################
 modelLats,modelLons,modelTimes,modelData = rcmes.files.read_data_from_file_list(filelist,modelVarName,modelTimeVarName, modelLatVarName, modelLonVarName)

 ##################################################################################################################
 # Deal with some precipitation specific options
 #      i.e. adjust units of model data and set plot color bars suitable for precip
 ##################################################################################################################
 colorbar = 'rainbow'
 if precipFlag==True:
    modelData = modelData*86400.  # convert from kgm-2s-1 into mm/day
    colorbar = 'precip2_17lev'

 # set color bar suitable for MODIS cloud data
 if obsParameterId==31:
    colorbar = 'gsdtol'

 ##################################################################################################################
 # Extract sub-selection of model data for required time range.
 #   e.g. a single model file may contain data for 20 years,
 #        but the user may have selected to only analyse data between 2003 and 2004.  
 ##################################################################################################################

 # make list of indices where modelTimes are between startTime and endTime
 wh = numpy.logical_and((numpy.array(modelTimes)>=startTime),(numpy.array(modelTimes)<=endTime)) 

 # make subset of modelTimes using full list of times and indices calculated above
 modelTimes = list(numpy.array(modelTimes)[wh])

 # make subset of modelData using full model data and indices calculated above 
 modelData = modelData[wh,:,:]

 ##################################################################################################################
 # Part 3: Temporal regridding
 #      i.e. model data may be monthly, and observation data may be daily.
 #           We need to compare like with like so the User Interface asks what time unit the user wants to work with
 #              e.g. the user may select that they would like to regrid everything to 'monthly' data
 #                   in which case, the daily observational data will be averaged onto monthly data
 #                   so that it can be compared directly with the monthly model data.
 ##################################################################################################################
 print 'Temporal Regridding Started'

 if(timeRegridOption):
        # Run both obs and model data through temporal regridding routine.
        #  NB. if regridding not required (e.g. monthly time units selected and model data is already monthly),
        #      then subroutine detects this and returns data untouched.
        obsData, newObsTimes = rcmes.process.calc_average_on_new_time_unit(obsData,obsTimes,unit=timeRegridOption)
 	modelData, newModelTimes = rcmes.process.calc_average_on_new_time_unit(modelData,modelTimes,unit=timeRegridOption)

 # Set a new 'times' list which describes the common times used for both model and obs after the regrid.
 if newObsTimes==newModelTimes:
        times = newObsTimes

 ##################################################################################################################
 # Catch situations where after temporal regridding the times in model and obs don't match.
 # If this occurs, take subset of data from times common to both model and obs only.
 #   e.g. imagine you are looking at monthly model data,
 #        the model times are set to the 15th of each month.
 #        + you are comparing against daily obs data.
 #        If you set the start date as Jan 1st, 1995 and the end date as Jan 1st, 1996
 #           -then system will load all model data in this range with the last date as Dec 15th, 1995
 #            loading the daily obs data from the database will have a last data item as Jan 1st, 1996.
 #        If you then do temporal regridding of the obs data from daily -> monthly (to match the model)
 #        Then there will be data for Jan 96 in the obs, but only up to Dec 95 for the model.
 #              This section of code deals with this situation by only looking at data
 #              from the common times between model and obs after temporal regridding.           
 ##################################################################################################################
 if newObsTimes!=newModelTimes:
        print 'Warning: after temporal regridding, times from observations and model do not match'
        print 'Check if this is unexpected.'
        print 'Proceeding with data from times common in both model and obs.'

        # Create empty lists ready to store data
        times = []
        newModelData = []
        newObsData = []

        # Loop through each time that is common in both model and obs
        for common_time in numpy.intersect1d(newObsTimes,newModelTimes):
                # build up lists of times, and model and obs data for each common time
                #  NB. use lists for data for convenience (then convert to masked arrays at the end)
                times.append(newObsTimes[numpy.where(numpy.array(newObsTimes)==common_time)[0][0]])
                newModelData.append(modelData[numpy.where(numpy.array(newModelTimes)==common_time)[0][0],:,:])
                newObsData.append(obsData[numpy.where(numpy.array(newObsTimes)==common_time)[0][0],:,:])

        # Convert data arrays from list back into full 3d arrays.
        modelData = ma.array(newModelData)
        obsData = ma.array(newObsData)

        # Reset all time lists so representative of the data actually used.
        newObsTimes = times
        newModelTimes = times
        obsTimes = times
        modelTimes = times

 ##################################################################################################################
 # Part 4: spatial regridding
 #         The model and obs are rarely on the same grid.
 #         To compare the two, you need them to be on the same grid.
 #         The User Interface asked the user if they'd like to regrid everything to the model grid or the obs grid.
 #         Alternatively, they could chose to regrid both model and obs onto a third regular lat/lon grid as defined
 #          by parameters that they enter.
 #      NB. from this point on in the code, the 'lats' and 'lons' arrays are common to both obsData and modelData.
 ##################################################################################################################

 ##################################################################################################################
 # either i) Regrid obs data to model grid.
 ##################################################################################################################
 if regridOption=='model':
        # User chose to regrid observations to the model grid
        modelData,obsData,lats,lons = rcmes.process.regrid_wrapper('0',obsData,obsLats,obsLons,modelData,modelLats,modelLons)

 ##################################################################################################################
 # or    ii) Regrid model data to obs grid.
 ##################################################################################################################
 if regridOption=='obs':
        # User chose to regrid model data to the observation grid

        modelData,obsData,lats,lons = rcmes.process.regrid_wrapper('1',obsData,obsLats,obsLons,modelData,modelLats,modelLons)

 ##################################################################################################################
 # or    iii) Regrid both model data and obs data to new regular lat/lon grid.
 ##################################################################################################################
 if regridOption=='regular':
        # User chose to regrid both model and obs data onto a newly defined regular lat/lon grid
        # Construct lats, lons from grid parameters

        # Create 1d lat and lon arrays
        lat = numpy.arange(nLats)*dLat+Lat0
        lon = numpy.arange(nLons)*dLon+Lon0

        # Combine 1d lat and lon arrays into 2d arrays of lats and lons
        lons,lats = numpy.meshgrid(lon,lat)

        ###########################################################################################################
        # Regrid model data for every time
        #  NB. store new data in a list and convert back to an array at the end.
        ###########################################################################################################
        rModelData = []

        nT = modelData.shape[0]
        for t in numpy.arange(nT):
           rModelData.append(rcmes.process.do_regrid(modelData[t,:,:],modelLats[:,:],modelLons[:,:],obsLats[:,:],obsLons[:,:]))

        # Convert list back into a masked array 
        modelData = ma.array(rModelData)

        ###########################################################################################################
        # Regrid obs data for every time
        #  NB. store new data in a list and convert back to an array at the end.
        ###########################################################################################################
        rObsData = []

        nT = obsData.shape[0]
        for t in numpy.arange(nT):
          rObsData.append(rcmes.process.do_regrid(obsData[t,:,:],obsLats[:,:],obsLons[:,:],modelLats[:,:],modelLons[:,:]))

        # Convert list back into a masked array 
        obsData = ma.array(rObsData)

 ##################################################################################################################
 # (Optional) Part 5: area-averaging
 #
 #      RCMET has the ability to either calculate metrics at every grid point, 
 #      or to calculate metrics for quantities area-averaged over a defined (masked) region.
 #
 #      If the user has selected to perform area-averaging, 
 #      then they have also selected how they want to define
 #      the area to average over.
 #      The options were:
 #              -define masked region using regular lat/lon bounding box parameters
 #              -read in masked region from file
 #
 #         either i) Load in the mask file (if required)
 #             or ii) Create the mask using latlonbox  
 #           then iii) Do the area-averaging
 #
 ##################################################################################################################
 if maskOption==1:  # i.e. define regular lat/lon box for area-averaging
    print 'Using Latitude/Longitude Mask for Area Averaging'

    ###############################################################################################################
    # Define mask using regular lat/lon box specified by users (i.e. ignore regions where mask = True)
    ###############################################################################################################
    mask = numpy.logical_or(numpy.logical_or(lats<=maskLatMin, lats>=maskLatMax),numpy.logical_or(lons<=maskLonMin, lons>=maskLonMax))

    ###############################################################################################################
    # Calculate area-weighted averages within this region and store in new lists
    ###############################################################################################################
    modelStore = []
    nT = modelData.shape[0]
    for t in numpy.arange(nT):
      modelStore.append(rcmes.process.calc_area_mean(modelData[t,:,:],lats,lons,mymask=mask))

    obsStore = []
    nT = obsData.shape[0]
    for t in numpy.arange(nT):
      obsStore.append(rcmes.process.calc_area_mean(obsData[t,:,:],lats,lons,mymask=mask))
  
    ###############################################################################################################
    # Now overwrite data arrays with the area-averaged values
    ###############################################################################################################
    modelData = ma.array(modelStore)
    obsData = ma.array(obsStore)

    ###############################################################################################################
    # Free-up some memory by overwriting big variables
    ###############################################################################################################
    obsStore = 0
    modelStore = 0

    ##############################################################################################################
    # NB. if area-averaging has been performed then the dimensions of the data arrays will have changed from 3D to 1D
    #           i.e. only one value per time.
    ##############################################################################################################

 ##################################################################################################################
 # (Optional) Part 6: seasonal cycle compositing
 #
 #      RCMET has the ability to calculate seasonal average values from a long time series of data.
 #
 #              e.g. for monthly data going from Jan 1980 - Dec 2010
 #                   If the user selects to do seasonal cycle compositing,
 #                   this section calculates the mean of all Januarys, mean of all Februarys, mean of all Marchs etc 
 #                      -result has 12 times.
 #
 #      NB. this works with incoming 3D data or 1D data (e.g. time series after avea-averaging).
 #
 #          If no area-averaging has been performed in Section 5, 
 #          then the incoming data is 3D, and the outgoing data will also be 3D, 
 #          but with the number of times reduced to 12
 #           i.e. you will get 12 map plots each one showing the average values for a month. (all Jans, all Febs etc)
 #
 #
 #          If area-averaging has been performed in Section 5, 
 #          then the incoming data is 1D, and the outgoing data will also be 1D, 
 #          but with the number of times reduced to 12
 #           i.e. you will get a time series of 12 data points 
 #                each one showing the average values for a month. (all Jans, all Febs etc).
 #
 ##################################################################################################################
 if seasonalCycleOption==1:

   print 'Compositing data to calculate seasonal cycle'

   modelData = rcmes.metrics.calc_annual_cycle_means(modelData,modelTimes)
   obsData = rcmes.metrics.calc_annual_cycle_means(obsData,modelTimes)

   modData= modelData
   obData = obsData 

 ##################################################################################################################
 # Part 7: metric calculation
 #              Calculate performance metrics comparing obsData and modelData.
 #              All output is stored in metricData regardless of what metric was calculated.
 #          
 #      NB. the dimensions of metricData will vary depending on the dimensions of the incoming data
 #          *and* on the type of metric being calculated.
 #
 #      e.g.    bias between incoming 1D model and 1D obs data (after area-averaging) will be a single number. 
 #              bias between incoming 3D model and 3D obs data will be 2D, i.e. a map of mean bias.
 #              correlation coefficient between incoming 3D model and 3D obs data will be 1D time series.
 # 
 ##################################################################################################################
 if metricOption=='bias':
   metricData = rcmes.metrics.calc_bias(modelData,obsData)
   metricTitle = 'Bias'

 if metricOption=='mae':
   metricData = rcmes.metrics.calc_mae(modelData,obsData)
   metricTitle = 'Mean Absolute Error'

 if metricOption=='rms':
   metricData = rcmes.metrics.calc_rms(modelData,obsData)
   metricTitle = 'RMS error'
 
 if metricOption=='difference':
   metricData = rcmes.metrics.calc_difference(modelData,obsData)
   metricTitle = 'Difference'

 if metricOption=='patcor':
   metricData = rcmes.metrics.calc_pat_cor(modelData,obsData)
   metricTitle = 'Pattern Correlation'

 if metricOption=='acc':
   metricData = rcmes.metrics.calc_anom_cor(modelData,obsData)
   metricTitle = 'Anomaly Correlation'

 if metricOption=='nacc':
   metricData = rcmes.metrics.calc_anom_corn(modelData,obsData)
   metricTitle = 'Anomaly Correlation'

 if metricOption=='pdf':
   metricData = rcmes.metrics.calc_pdf(modelData,obsData)
   metricTitle = 'Probability Distribution Function'

 if metricOption=='coe':
   metricData = rcmes.metrics.calc_nash_sutcliff(modelData,obsData)
   metricTitle = 'Coefficient of Efficiency'

 if metricOption=='stddev':
   metricData = rcmes.metrics.calc_stdev(modelData)
   data2 = rcmes.metrics.calc_stdev(obsData)
   metricTitle = 'Standard Deviation'
 ##################################################################################################################
 # Part 8: Plot production
 #
 #      Produce plots of metrics and obs,model data.
 #      Type of plot produced depends on dimensions of incoming data.
 #              e.g. 1D data is plotted as a time series.
 #                   2D data is plotted as a map.
 #                   3D data is plotted as a sequence of maps.
 #
 ##################################################################################################################

 ##################################################################################################################
 # 1 dimensional data, e.g. Time series plots
 ##################################################################################################################
 if metricData.ndim==1:
   print 'Producing time series plots ****'
   print metricData
   year_labels = True
#   mytitle = 'Area-average model v obs'

   ################################################################################################################
   # If producing seasonal cycle plots, don't want to put year labels on the time series plots.
   ################################################################################################################
   if seasonalCycleOption==1:
     year_labels = False
     mytitle = 'Annual cycle: area-average  model v obs'
     # Create a list of datetimes to represent the annual cycle, one per month.
     times = []
     for m in xrange(12):
       times.append(datetime.datetime(2000,m+1,1,0,0,0,0))

   ################################################################################################################
   # Special case for pattern correlation plots. TODO: think of a cleaner way of doing this.
   # Only produce these plots if the metric is NOT pattern correlation.
   ################################################################################################################

   # TODO - Clean up this if statement
   #KDW: change the if statement to if else to accommodate the 2D timeseries plots
   if (metricOption!='patcor')&(metricOption!='acc')&(metricOption!='nacc')&(metricOption!='coe')&(metricOption!='pdf'):
     # for anomaly and pattern correlation,
     # can't plot time series of model, obs as these are 3d fields
     # ^^ This is the reason modelData has been swapped for metricData in
     # the following function
     # TODO: think of a cleaner way of dealing with this.

     ##############################################################################################################
     # Produce the time series plots with two lines: obs and model
     ##############################################################################################################
     print 'two line timeseries'
#     mytitle = titleOption
     mytitle = 'Area-average model v obs'
     if titleOption=='default':
        mytitle = metricTitle+' model & obs'
     #status = rcmes.plots.draw_time_series_plot(modelData,times,plotFileNameOption+'both',workdir,data2=obsData,mytitle=mytitle,ytitle='Y',xtitle='time',year_labels=year_labels)
     status = rcmes.plots.draw_time_series_plot(metricData,times,plotFileNameOption+'both',workdir,data2,mytitle=mytitle,ytitle='Y',xtitle='time',year_labels=year_labels)

   else: 
   ################################################################################################################
   # Produce the metric time series plot (one line only)
   ################################################################################################################
     mytitle = titleOption
     if titleOption=='default':
        mytitle = metricTitle+' model v obs'
     print 'one line timeseries'
     status = rcmes.plots.draw_time_series_plot(metricData,times,plotFileNameOption,workdir,mytitle=mytitle,ytitle='Y',xtitle='time',year_labels=year_labels)

 ##################################################################################################################
 # 2 dimensional data, e.g. Maps
 ##################################################################################################################
 if metricData.ndim==2:

   ################################################################################################################
   # Calculate color bar ranges for data such that same range is used in obs and model plots
   # for like-with-like comparison.
   ################################################################################################################
   mymax = max(obsData.mean(axis=0).max(),modelData.mean(axis=0).max())
   mymin = min(obsData.mean(axis=0).min(),modelData.mean(axis=0).min())


   ################################################################################################################
   # Time title labels need their format adjusting depending on the temporal regridding used,
   #          e.g. if data are averaged to monthly,
   #               then want to write 'Jan 2002', 'Feb 2002', etc instead of 'Jan 1st, 2002', 'Feb 1st, 2002'
   #
   #  Also, if doing seasonal cycle compositing 
   #  then want to write 'Jan','Feb','Mar' instead of 'Jan 2002','Feb 2002','Mar 2002' etc 
   #  as data are representative of all Jans, all Febs etc. 
   ################################################################################################################
   if(timeRegridOption=='daily'):
       timeFormat = "%b %d, %Y"
   if(timeRegridOption=='monthly'):
       timeFormat = "%b %Y"
   if(timeRegridOption=='annual'):
       timeFormat = "%Y"
   if(timeRegridOption=='full'):
       timeFormat = "%b %d, %Y"

   #################################################################################################################
   # Special case: when plotting bias data, we also like to plot the mean obs and mean model data.
   #               In this case, we need to calculate new time mean values for both obs and model.
   #               When doing this time averaging, we also need to deal with missing data appropriately.
   #
   # Classify missing data resulting from multiple times (using threshold data requirment)
   #   i.e. if the working time unit is monthly data, and we are dealing with multiple months of data
   #        then when we show mean of several months, we need to decide what threshold of missing data we tolerate
   #        before classifying a data point as missing data.
   #################################################################################################################

   ################################################################################################################
   # Calculate time means of model and obs data
   ################################################################################################################
   modelDataMean = modelData.mean(axis=0)
   obsDataMean = obsData.mean(axis=0)

   ################################################################################################################
   # Calculate missing data masks using tolerance threshold of missing data going into calculations
   ################################################################################################################
   obsDataMask = rcmes.process.create_mask_using_threshold(obsData,threshold=0.75)
   modelDataMask = rcmes.process.create_mask_using_threshold(modelData,threshold=0.75)

   ################################################################################################################
   # Combine data and masks into masked arrays suitable for plotting.
   ################################################################################################################
   modelDataMean = ma.masked_array(modelDataMean, modelDataMask)
   obsDataMean = ma.masked_array(obsDataMean, obsDataMask)

   ################################################################################################################
   # Plot model data
   ################################################################################################################
   mytitle = 'Model data: mean between '+modelTimes[0].strftime(timeFormat)+' and '+modelTimes[-1].strftime(timeFormat)
   status = rcmes.plots.draw_map_color_filled(modelDataMean,lats,lons,plotFileNameOption+'model',workdir,mytitle=mytitle,rangeMax=mymax, rangeMin=mymin,colorTable=colorbar, niceValues=True)

   ################################################################################################################
   # Plot obs data
   ################################################################################################################
   mytitle = 'Obs data: mean between '+obsTimes[0].strftime(timeFormat)+' and '+obsTimes[-1].strftime(timeFormat)
   status = rcmes.plots.draw_map_color_filled(obsDataMean,lats,lons,plotFileNameOption+'obs',workdir,mytitle=mytitle,rangeMax=mymax, rangeMin=mymin,colorTable=colorbar, niceValues=True)

   ################################################################################################################
   # Plot metric
   ################################################################################################################
   mymax = metricData.max()
   mymin = metricData.min()

   mytitle = titleOption

   if titleOption=='default':
     mytitle = metricTitle+' model v obs '+obsTimes[0].strftime(timeFormat)+' to '+obsTimes[-1].strftime(timeFormat)

   status = rcmes.plots.draw_map_color_filled(metricData,lats,lons,plotFileNameOption,workdir,mytitle=mytitle,rangeMax=mymax, rangeMin=mymin,diff=True,niceValues=True,nsteps=24)

 ##################################################################################################################
 # 3 dimensional data, e.g. sequence of maps
 ##################################################################################################################
 if metricData.ndim==3:
   print 'Generating series of map plots, each for a different time.'
   for t in numpy.arange(obsData.shape[0]):

     ##############################################################################################################
     # Calculate color bar ranges for data such that same range is used in obs and model plots
     # for like-with-like comparison.
     ##############################################################################################################
     mymax = max(obsData[t,:,:].max(),modelData[t,:,:].max())
     mymin = min(obsData[t,:,:].min(),modelData[t,:,:].min())

     ##############################################################################################################
     # Time title labels need their format adjusting depending on the temporal regridding used,
     #          e.g. if data are averaged to monthly,
     #               then want to write 'Jan 2002', 'Feb 2002', etc instead of 'Jan 1st, 2002', 'Feb 1st, 2002'
     #
     #  Also, if doing seasonal cycle compositing 
     #  then want to write 'Jan','Feb','Mar' instead of 'Jan 2002','Feb 2002','Mar 2002' etc 
     #  as data are representative of all Jans, all Febs etc. 
     ##############################################################################################################
     if(timeRegridOption=='daily'):
       timeTitle = times[t].strftime("%b %d, %Y")
       if seasonalCycleOption==1:
          timeTitle = times[t].strftime("%b %d (all years)")

     if(timeRegridOption=='monthly'):
       timeTitle = times[t].strftime("%b %Y")
       if seasonalCycleOption==1:
          timeTitle = times[t].strftime("%b (all years)")

     if(timeRegridOption=='annual'):
       timeTitle = times[t].strftime("%Y")

     if(timeRegridOption=='full'):
       time1 = min(min(obsTimes),min(modelTimes))
       time2 = max(max(obsTimes),max(modelTimes))
       timeTitle = time1.strftime("%b %d, %Y")+' to '+time2.strftime("%b %d, %Y")

     ##############################################################################################################
     # Plot model data
     ##############################################################################################################
     mytitle = 'Model data: mean '+timeTitle
     status = rcmes.plots.draw_map_color_filled(modelData[t,:,:],lats,lons,plotFileNameOption+'model'+str(t),workdir,mytitle=mytitle,rangeMax=mymax, rangeMin=mymin,colorTable=colorbar, niceValues=True)

     ##############################################################################################################
     # Plot obs data
     ##############################################################################################################
     mytitle = 'Obs data: mean '+timeTitle
     status = rcmes.plots.draw_map_color_filled(obsData[t,:,:],lats,lons,plotFileNameOption+'obs'+str(t),workdir,mytitle=mytitle,rangeMax=mymax, rangeMin=mymin,colorTable=colorbar, niceValues=True)

     ##############################################################################################################
     # Plot metric
     ##############################################################################################################
     mytitle = titleOption

     if titleOption=='default':
        mytitle = metricTitle +' model v obs : '+timeTitle

     mymax = metricData.max()
     mymin = metricData.min()

     status = rcmes.plots.draw_map_color_filled(metricData[t,:,:],lats,lons,plotFileNameOption+str(t),workdir,mytitle=mytitle,rangeMax=mymax, rangeMin=mymin,diff=True, niceValues=True, nsteps=24)

 ##################################################################################################################
 # Processing complete
 ##################################################################################################################

 print 'RCMES processing completed.'

