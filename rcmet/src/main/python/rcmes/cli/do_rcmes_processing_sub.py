#
#  Licensed to the Apache Software Foundation (ASF) under one or more
#  contributor license agreements.  See the NOTICE file distributed with
#  this work for additional information regarding copyright ownership.
#  The ASF licenses this file to You under the Apache License, Version 2.0
#  (the "License"); you may not use this file except in compliance with
#  the License.  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#
#!/usr/local/bin/python
""" 
    PENDING DEPRICATION - YOU SHOULD INSTEAD USE THE rcmet.py within the bin dir
    
    Module that is used to lauch the rcmes processing from the rcmet_ui.py
    script.
"""

import os, sys
import datetime
import numpy
import numpy.ma as ma 
import toolkit.plots as plots
import mpl_toolkits.basemap.cm as cm
import matplotlib.pyplot as plt
import storage.db as db
import storage.files as files
import toolkit.process as process
import toolkit.metrics as metrics

def do_rcmes(settings, params, model, mask, options):
    '''
    Routine to perform full end-to-end RCMET processing.

    i)    retrieve observations from the database
    ii)   load in model data
    iii)  temporal regridding
    iv)   spatial regridding
    v)    area-averaging
    vi)   seasonal cycle compositing
    vii)  metric calculation
    viii) plot production

    Input:
        5 dictionaries which contain a huge argument list with all of the user options 
        (which can be collected from the GUI)

    settings - dictionary of rcmes run settings::
    
        settings = {"cacheDir": string describing directory path,
                    "workDir": string describing directory path,
                    "fileList": string describing model file name + path }

    params - dictionary of rcmes run parameters::
    
        params = {"obsDatasetId": int( db dataset id ),
                  "obsParamId": int( db parameter id ),
                  "startTime": datetime object (needs to change to string + decode),
                  "endTime": datetime object (needs to change to string + decode),
                  "latMin": float,
                  "latMax": float,
                  "lonMin": float,
                  "lonMax": float }

    model - dictionary of model parameters::
        
        model = {"varName": string describing name of variable to evaluate (as written in model file),
                 "timeVariable": string describing name of time variable (as written in model file), 	
                 "latVariable": string describing name of latitude variable (as written in model file), 
                 "lonVariable": string describing name of longitude variable (as written in model file) } 
        
    mask - dictionary of mask specific options (only used if options['mask']=True)::
        
        mask = {"latMin": float,
                "latMax": float,
                "lonMin": float,
                "lonMax": float}
        
    options - dictionary full of different user supplied options::
        
        options = {"regrid": str( 'obs' | 'model' | 'regular' ),
                   "timeRegrid": str( 'full' | 'annual' | 'monthly' | 'daily' ),
                   "seasonalCycle": Boolean,
                   "metric": str('bias'|'mae'|'acc'|'pdf'|'patcor'|'rms'|'diff'),
                   "plotTitle": string describing title to use in plot graphic,
                   "plotFilename": basename of file to use for plot graphic i.e. {plotFilename}.png,
                   "mask": Boolean,
                   "precip": Boolean }

    Output: image files of plots + possibly data
    '''

    # check the number of model data files
    if len(settings['fileList']) < 1:         # no input data file
        print 'No input model data file. EXIT'
        sys.exit()
    # assign parameters that must be preserved throughout the process
    if options['mask'] == True: 
        options['seasonalCycle'] = True
    
    ###########################################################################
    # Part 1: retrieve observation data from the database
    #         NB. automatically uses local cache if already retrieved.
    ###########################################################################
    rcmedData = getDataFromRCMED( params, settings, options )

    ###########################################################################
    # Part 2: load in model data from file(s)
    ###########################################################################
    modelData = getDataFromModel( model, settings )

    ###########################################################################
    # Deal with some precipitation specific options
    #      i.e. adjust units of model data and set plot color bars suitable for precip
    ###########################################################################
    # AG 06/12/1013: Need to revise how we select colormaps in the future
    colorbar = None
    if options['precip'] == True:
        modelData['data'] = modelData['data']*86400.  # convert from kgm-2s-1 into mm/day
        colorbar = cm.s3pcpn

    # set color bar suitable for MODIS cloud data
    if params['obsParamId'] == 31:
        colorbar = plt.cm.gist_gray
    
    diffcolorbar = cm.GMT_polar

    ##################################################################################################################
    # Extract sub-selection of model data for required time range.
    #   e.g. a single model file may contain data for 20 years,
    #        but the user may have selected to only analyse data between 2003 and 2004.  
    ##################################################################################################################

    # Make list of indices where modelData['times'] are between params['startTime'] and params['endTime']
    modelTimeOverlap = numpy.logical_and((numpy.array(modelData['times'])>=params['startTime']), 
                                           (numpy.array(modelData['times'])<=params['endTime'])) 

    # Make subset of modelData['times'] using full list of times and indices calculated above
    modelData['times'] = list(numpy.array(modelData['times'])[modelTimeOverlap])

    # Make subset of modelData['data'] using full model data and indices calculated above 
    modelData['data'] = modelData['data'][modelTimeOverlap, :, :]

    ##################################################################################################################
    # Part 3: Temporal regridding
    #      i.e. model data may be monthly, and observation data may be daily.
    #           We need to compare like with like so the User Interface asks what time unit the user wants to work with
    #              e.g. the user may select that they would like to regrid everything to 'monthly' data
    #                   in which case, the daily observational data will be averaged onto monthly data
    #                   so that it can be compared directly with the monthly model data.
    ##################################################################################################################
    print 'Temporal Regridding Started'

    if(options['timeRegrid']):
        # Run both obs and model data through temporal regridding routine.
        #  NB. if regridding not required (e.g. monthly time units selected and model data is already monthly),
        #      then subroutine detects this and returns data untouched.
        rcmedData['data'], newObsTimes = process.calc_average_on_new_time_unit(rcmedData['data'], 
                                                                                        rcmedData['times'],
                                                                                        unit=options['timeRegrid'])
        
        modelData['data'], newModelTimes = process.calc_average_on_new_time_unit(modelData['data'],
                                                                                          modelData['times'],
                                                                                          unit=options['timeRegrid'])

    # Set a new 'times' list which describes the common times used for both model and obs after the regrid.
    if newObsTimes == newModelTimes:
        times = newObsTimes

    ###########################################################################
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
    ###########################################################################
    if newObsTimes != newModelTimes:
        print 'Warning: after temporal regridding, times from observations and model do not match'
        print 'Check if this is unexpected.'
        print 'Proceeding with data from times common in both model and obs.'

        # Create empty lists ready to store data
        times = []
        tempModelData = []
        tempObsData = []

        # Loop through each time that is common in both model and obs
        for commonTime in numpy.intersect1d(newObsTimes, newModelTimes):
            # build up lists of times, and model and obs data for each common time
            #  NB. use lists for data for convenience (then convert to masked arrays at the end)
            times.append(newObsTimes[numpy.where(numpy.array(newObsTimes) == commonTime)[0][0]])
            tempModelData.append(modelData['data'][numpy.where(numpy.array(newModelTimes) == commonTime)[0][0], :, :])
            tempObsData.append(rcmedData['data'][numpy.where(numpy.array(newObsTimes) == commonTime)[0][0], :, :])

        # Convert data arrays from list back into full 3d arrays.
        modelData['data'] = ma.array(tempModelData)
        rcmedData['data'] = ma.array(tempObsData)

        # Reset all time lists so representative of the data actually used.
        newObsTimes = times
        newModelTimes = times
        rcmedData['times'] = times
        modelData['times'] = times

    ##################################################################################################################
    # Part 4: spatial regridding
    #         The model and obs are rarely on the same grid.
    #         To compare the two, you need them to be on the same grid.
    #         The User Interface asked the user if they'd like to regrid everything to the model grid or the obs grid.
    #         Alternatively, they could chose to regrid both model and obs onto a third regular lat/lon grid as defined
    #          by parameters that they enter.
    #
    #         NB. from this point on in the code, the 'lats' and 'lons' arrays are common to 
    #             both rcmedData['data'] and modelData['data'].
    ##################################################################################################################

    ##################################################################################################################
    # either i) Regrid obs data to model grid.
    ##################################################################################################################
    if options['regrid'] == 'model':
        # User chose to regrid observations to the model grid
        modelData['data'], rcmedData['data'], lats, lons = process.regrid_wrapper('0', rcmedData['data'], 
                                                                                  rcmedData['lats'],
                                                                                  rcmedData['lons'], 
                                                                                  modelData['data'],
                                                                                  modelData['lats'],
                                                                                  modelData['lons'])

    ##################################################################################################################
    # or    ii) Regrid model data to obs grid.
    ##################################################################################################################
    if options['regrid'] == 'obs':
        # User chose to regrid model data to the observation grid

        modelData['data'], rcmedData['data'], lats, lons = process.regrid_wrapper('1', rcmedData['data'], 
                                                                                  rcmedData['lats'], 
                                                                                  rcmedData['lons'], 
                                                                                  modelData['data'],
                                                                                  modelData['lats'], 
                                                                                  modelData['lons'])

    ##################################################################################################################
    # or    iii) Regrid both model data and obs data to new regular lat/lon grid.
    ##################################################################################################################
    if options['regrid'] == 'regular':
        # User chose to regrid both model and obs data onto a newly defined regular lat/lon grid
        # Construct lats, lons from grid parameters

        # Create 1d lat and lon arrays
        # AG 06/21/2013: These variables are undefined, where are they generated from?
        lat = numpy.arange(nLats)*dLat+Lat0
        lon = numpy.arange(nLons)*dLon+Lon0

        # Combine 1d lat and lon arrays into 2d arrays of lats and lons
        lons, lats = numpy.meshgrid(lon, lat)

        ###########################################################################################################
        # Regrid model data for every time
        #  NB. store new data in a list and convert back to an array at the end.
        ###########################################################################################################
        tmpModelData = []

        timeCount = modelData['data'].shape[0]
        for t in numpy.arange(timeCount):
            tmpModelData.append(process.do_regrid(modelData['data'][t, :, :],
                                                          modelData['lats'][:, :],
                                                          modelData['lons'][:, :],
                                                          rcmedData['lats'][:, :],
                                                          rcmedData['lons'][:, :]))

        # Convert list back into a masked array 
        modelData['data'] = ma.array(tmpModelData)

        ###########################################################################################################
        # Regrid obs data for every time
        #  NB. store new data in a list and convert back to an array at the end.
        ###########################################################################################################
        tempObsData = []
        timeCount = rcmedData['data'].shape[0]
        for t in numpy.arange(timeCount):
            tempObsData.append(process.do_regrid(rcmedData['data'][t, :, :], 
                                                         rcmedData['lats'][:, :], 
                                                         rcmedData['lons'][:, :], 
                                                         modelData['lats'][:, :], modelData['lons'][:, :]))

        # Convert list back into a masked array 
        rcmedData['data'] = ma.array(tempObsData)

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
    ###############################################################################################################
    if options['mask'] == True:  # i.e. define regular lat/lon box for area-averaging
        print 'Using Latitude/Longitude Mask for Area Averaging'

        ###############################################################################################################
        # Define mask using regular lat/lon box specified by users (i.e. ignore regions where mask = True)
        ###############################################################################################################
        mask = numpy.logical_or(numpy.logical_or(lats<=mask['latMin'], lats>=mask['latMax']), 
                            numpy.logical_or(lons<=mask['lonMin'], lons>=mask['lonMax']))

        ######################m########################################################################################
        # Calculate area-weighted averages within this region and store in new lists
        ###############################################################################################################
        modelStore = []
        timeCount = modelData['data'].shape[0]
        for t in numpy.arange(timeCount):
            modelStore.append(process.calc_area_mean(modelData['data'][t, :, :], lats, lons, mymask=mask))

        obsStore = []
        timeCount = rcmedData['data'].shape[0]
        for t in numpy.arange(timeCount):
            obsStore.append(process.calc_area_mean(rcmedData['data'][t, :, :], lats, lons, mymask=mask))
  
        ###############################################################################################################
        # Now overwrite data arrays with the area-averaged values
        ###############################################################################################################
        modelData['data'] = ma.array(modelStore)
        rcmedData['data'] = ma.array(obsStore)

        ###############################################################################################################
        # Free-up some memory by overwriting big variables
        ###############################################################################################################
        obsStore = 0
        modelStore = 0

        ##############################################################################################################
        # NB. if area-averaging has been performed then the dimensions of the data arrays will have changed from 3D to 1D
        #           i.e. only one value per time.
        ##############################################################################################################

    ##############################################################################################################
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
    if options['seasonalCycle'] == True:
        print 'Compositing data to calculate seasonal cycle'

        modelData['data'] = metrics.calcAnnualCycleMeans(modelData['data'])
        rcmedData['data'] = metrics.calcAnnualCycleMeans(rcmedData['data'])

    ##################################################################################################################
    # Part 7: metric calculation
    #              Calculate performance metrics comparing rcmedData['data'] and modelData['data'].
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

    if options['metric'] == 'bias':
        metricData = metrics.calcBias(modelData['data'], rcmedData['data'])
        metricTitle = 'Bias'

    if options['metric'] == 'mae':
        metricData = metrics.calcBiasAveragedOverTime(modelData['data'], rcmedData['data'], 'abs')
        metricTitle = 'Mean Absolute Error'

    if options['metric'] == 'rms':
        metricData = metrics.calcRootMeanSquaredDifferenceAveragedOverTime(modelData['data'], rcmedData['data'])
        metricTitle = 'RMS error'
 
    #if options['metric'] == 'patcor':
        #metricData = metrics.calc_pat_cor2D(modelData['data'], rcmedData['data'])
        #metricTitle = 'Pattern Correlation'


    if options['metric'] == 'pdf':
        metricData = metrics.calcPdf(modelData['data'], rcmedData['data'])
        metricTitle = 'Probability Distribution Function'

    if options['metric'] == 'coe':
        metricData = metrics.calcNashSutcliff(modelData['data'], rcmedData['data'])
        metricTitle = 'Coefficient of Efficiency'

    if options['metric'] == 'stddev':
        metricData = metrics.calcTemporalStdev(modelData['data'])
        data2 = metrics.calcTemporalStdev(rcmedData['data'])
        metricTitle = 'Standard Deviation'

    ##################################################################################################################
    # Part 8: Plot production
    #
    #      Produce plots of metrics and obs, model data.
    #      Type of plot produced depends on dimensions of incoming data.
    #              e.g. 1D data is plotted as a time series.
    #                   2D data is plotted as a map.
    #                   3D data is plotted as a sequence of maps.
    #
    ##################################################################################################################

    ##################################################################################################################
    # 1 dimensional data, e.g. Time series plots
    ##################################################################################################################
    if metricData.ndim == 1:
        print 'Producing time series plots ****'
        print metricData
        yearLabels = True
        #   mytitle = 'Area-average model v obs'

        ################################################################################################################
        # If producing seasonal cycle plots, don't want to put year labels on the time series plots.
        ################################################################################################################
        if options['seasonalCycle'] == True:
            yearLabels = False
            mytitle = 'Annual cycle: area-average  model v obs'
            # Create a list of datetimes to represent the annual cycle, one per month.
            times = []
            for m in xrange(12):
                times.append(datetime.datetime(2000, m+1, 1, 0, 0, 0, 0))
    
        ###############################################################################################
        # Special case for pattern correlation plots. TODO: think of a cleaner way of doing this.
        # Only produce these plots if the metric is NOT pattern correlation.
        ###############################################################################################
    
        # TODO - Clean up this if statement.  We can use a list of values then ask if not in LIST...
        #KDW: change the if statement to if else to accommodate the 2D timeseries plots
        if (options['metric'] != 'patcor')&(options['metric'] != 'acc')&(options['metric'] != 'nacc')&(options['metric'] != 'coe')&(options['metric'] != 'pdf'):
            # for anomaly and pattern correlation,
            # can't plot time series of model, obs as these are 3d fields
            # ^^ This is the reason modelData['data'] has been swapped for metricData in
            # the following function
            # TODO: think of a cleaner way of dealing with this.
    
            ###########################################################################################
            # Produce the time series plots with two lines: obs and model
            ###########################################################################################
            print 'two line timeseries'
            #     mytitle = options['plotTitle']
            mytitle = 'Area-average model v obs'
            if options['plotTitle'] == 'default':
                mytitle = metricTitle+' model & obs'
            #plots.draw_time_series_plot(modelData['data'],times,options['plotFilename']+'both',
            #                                           settings['workDir'],data2=rcmedData['data'],mytitle=mytitle,
            #                                           ytitle='Y',xtitle='time',
            #                                           year_labels=yearLabels)
            plots.draw_time_series_plot(metricData, times, options['plotFilename']+'both',
                                                       settings['workDir'], data2, mytitle=mytitle, 
                                                       ytitle='Y', xtitle='time',
                                                       year_labels=yearLabels)
    
        else: 
            ###############################################################################################
            # Produce the metric time series plot (one line only)
            ###############################################################################################
            mytitle = options['plotTitle']
            if options['plotTitle'] == 'default':
                mytitle = metricTitle+' model v obs'
            print 'one line timeseries'
            plots.draw_time_series_plot(metricData, times, options['plotFilename'], 
                                                       settings['workDir'], mytitle=mytitle, ytitle='Y', xtitle='time',
                                                       year_labels=yearLabels)

    ###############################################################################################
    # 2 dimensional data, e.g. Maps
    ###############################################################################################
    if metricData.ndim == 2:

        ###########################################################################################
        # Calculate color bar ranges for data such that same range is used in obs and model plots
        # for like-with-like comparison.
        ###########################################################################################
        mymax = max(rcmedData['data'].mean(axis=0).max(), modelData['data'].mean(axis=0).max())
        mymin = min(rcmedData['data'].mean(axis=0).min(), modelData['data'].mean(axis=0).min())

        ###########################################################################################
        # Time title labels need their format adjusting depending on the temporal regridding used,
        #          e.g. if data are averaged to monthly,
        #               then want to write 'Jan 2002', 'Feb 2002', etc instead of 'Jan 1st, 2002', 'Feb 1st, 2002'
        #
        #  Also, if doing seasonal cycle compositing 
        #  then want to write 'Jan','Feb','Mar' instead of 'Jan 2002','Feb 2002','Mar 2002' etc 
        #  as data are representative of all Jans, all Febs etc. 
        ###########################################################################################
        if(options['timeRegrid'] == 'daily'):
            timeFormat = "%b %d, %Y"
        if(options['timeRegrid'] == 'monthly'):
            timeFormat = "%b %Y"
        if(options['timeRegrid'] == 'annual'):
            timeFormat = "%Y"
        if(options['timeRegrid'] == 'full'):
            timeFormat = "%b %d, %Y"

        ###########################################################################################
        # Special case: when plotting bias data, we also like to plot the mean obs and mean model data.
        #               In this case, we need to calculate new time mean values for both obs and model.
        #               When doing this time averaging, we also need to deal with missing data appropriately.
        #
        # Classify missing data resulting from multiple times (using threshold data requirment)
        #   i.e. if the working time unit is monthly data, and we are dealing with multiple months of data
        #        then when we show mean of several months, we need to decide what threshold of missing data we tolerate
        #        before classifying a data point as missing data.
        ###########################################################################################

        ###########################################################################################
        # Calculate time means of model and obs data
        ###########################################################################################
        modelDataMean = modelData['data'].mean(axis=0)
        obsDataMean = rcmedData['data'].mean(axis=0)

        ###########################################################################################
        # Calculate missing data masks using tolerance threshold of missing data going into calculations
        ###########################################################################################
        obsDataMask = process.create_mask_using_threshold(rcmedData['data'], threshold=0.75)
        modelDataMask = process.create_mask_using_threshold(modelData['data'], threshold=0.75)

        ###########################################################################################
        # Combine data and masks into masked arrays suitable for plotting.
        ###########################################################################################
        modelDataMean = ma.masked_array(modelDataMean, modelDataMask)
        obsDataMean = ma.masked_array(obsDataMean, obsDataMask)

        ###########################################################################################
        # Plot model data
        ###########################################################################################
        mytitle = 'Model data: mean between %s and %s' % ( modelData['times'][0].strftime(timeFormat), 
                                                           modelData['times'][-1].strftime(timeFormat) )
        myfname = os.path.join(options['workDir'], options['plotFilename']+'model')

        plots.draw_cntr_map_single(modelDataMean, lats, lons, mymin, mymax, mytitle, myfname, cMap = colorbar)

        ###########################################################################################
        # Plot obs data
        ###########################################################################################
        mytitle = 'Obs data: mean between %s and %s' % ( rcmedData['times'][0].strftime(timeFormat), 
                                                        rcmedData['times'][-1].strftime(timeFormat) )
        myfname = os.path.join(options['workDir'], options['plotFilename']+'obs')
        plots.draw_cntr_map_single(obsDataMean, lats, lons, mymin, mymax, mytitle, myfname, cMap = colorbar)


        ###########################################################################################
        # Plot metric
        ###########################################################################################
        mymax = metricData.max()
        mymin = metricData.min()

        mytitle = options['plotTitle']

        if options['plotTitle'] == 'default':
            mytitle = metricTitle+' model v obs %s to %s' % ( rcmedData['times'][0].strftime(timeFormat),
                                                                rcmedData['times'][-1].strftime(timeFormat) )
        myfname = os.path.join(options['workDir'], options['plotFilename'])
        plots.draw_cntr_map_single(metricData, lats, lons, mymin, mymax, mytitle, myfname, cMap = diffcolorbar)

    ###############################################################################################
    # 3 dimensional data, e.g. sequence of maps
    ###############################################################################################
    if metricData.ndim == 3:
        print 'Generating series of map plots, each for a different time.'
        for t in numpy.arange(rcmedData['data'].shape[0]):

            #######################################################################################
            # Calculate color bar ranges for data such that same range is used in obs and model plots
            # for like-with-like comparison.
            #######################################################################################
            colorRangeMax = max(rcmedData['data'][t, :, :].max(), modelData['data'][t, :, :].max())
            colorRangeMin = min(rcmedData['data'][t, :, :].min(), modelData['data'][t, :, :].min())

            # Setup the timeTitle
            timeSlice = times[t]
            timeTitle = createTimeTitle( options, timeSlice, rcmedData, modelData )

            #######################################################################################
            # Plot model data
            #######################################################################################
            mytitle = 'Model data: mean '+timeTitle
            myfname = os.path.join(settings['workDir'], options['plotFilename']+'model'+str(t))
            plots.draw_cntr_map_single(modelData['data'][t, :, :], lats, lons, colorRangeMin, colorRangeMax, 
                                       mytitle, myfname, cMap = colorbar)

            #######################################################################################
            # Plot obs data
            #######################################################################################
            mytitle = 'Obs data: mean '+timeTitle
            myfname = os.path.join(settings['workDir'], options['plotFilename']+'obs'+str(t))
            plots.draw_cntr_map_single(rcmedData['data'][t, :, :], lats, lons, colorRangeMin, colorRangeMax, 
                                       mytitle, myfname, cMap = colorbar)

            #######################################################################################
            # Plot metric
            #######################################################################################
            mytitle = options['plotTitle']
            myfname = os.path.join(settings['workDir'], options['plotFilename']+str(t))

            if options['plotTitle'] == 'default':
                mytitle = metricTitle +' model v obs : '+timeTitle

            colorRangeMax = metricData.max()
            colorRangeMin = metricData.min()
            plots.draw_cntr_map_single(metricData[t, :, :], lats, lons, colorRangeMin, colorRangeMax, 
                                       mytitle, myfname, cMap = diffcolorbar)


def getDataFromRCMED( params, settings, options ):
    """
    This function takes in the params, settings, and options dictionaries and will return an rcmedData dictionary.
    
    return:
        rcmedData = {"lats": 1-d numpy array of latitudes,
                      "lons": 1-d numpy array of longitudes,
                      "levels": 1-d numpy array of height/pressure levels (surface based data will have length == 1),
                      "times": list of python datetime objects,
                      "data": masked numpy arrays of data values}
    """
    rcmedData = {}
    obsLats, obsLons, obsLevs, obsTimes, obsData =  db.extractData(params['obsDatasetId'],
                                                                                 params['obsParamId'],
                                                                                 params['latMin'],
                                                                                 params['latMax'],
                                                                                 params['lonMin'],
                                                                                 params['lonMax'],
                                                                                 params['startTime'],
                                                                                 params['endTime'],
                                                                                 settings['cacheDir'],
										 options['timeRegrid'])
    rcmedData['lats'] = obsLats
    rcmedData['lons'] = obsLons
    rcmedData['levels'] = obsLevs
    rcmedData['times'] = obsTimes
    rcmedData['data'] = obsData
    
    return rcmedData

def getDataFromModel( model, settings ):
    """
    This function takes in the model and settings dictionaries and will return a model data dictionary.
    
    return:
        model = {"lats": 1-d numpy array of latitudes,
                 "lons": 1-d numpy array of longitudes,
                 "times": list of python datetime objects,
                 "data": numpy array containing data from all files}
    """
    model = files.read_data_from_file_list(settings['fileList'],
                                                 model['varName'],
                                                 model['timeVariable'],
                                                 model['latVariable'],
                                                 model['lonVariable'])
    return model

##################################################################################################################
# Processing complete
##################################################################################################################

def createTimeTitle( options, timeSlice, rcmedData, modelData ):
    """
    Function that takes in the options dictionary and a specific timeSlice.
    
    Return:  string timeTitle properly formatted based on the 'timeRegrid' and 'seasonalCycle' options value.
    
    Time title labels need their format adjusting depending on the temporal regridding used
    
    e.g. if data are averaged to monthly, then want to write 'Jan 2002', 
    'Feb 2002', etc instead of 'Jan 1st, 2002', 'Feb 1st, 2002'

    Also, if doing seasonal cycle compositing then want to write 'Jan','Feb',
    'Mar' instead of 'Jan 2002', 'Feb 2002','Mar 2002' etc as data are 
    representative of all Jans, all Febs etc. 
    """
    if(options['timeRegrid'] == 'daily'):
        timeTitle = timeSlice.strftime("%b %d, %Y")
        if options['seasonalCycle'] == True:
            timeTitle = timeSlice.strftime("%b %d (all years)")

    if(options['timeRegrid'] == 'monthly'):
        timeTitle = timeSlice.strftime("%b %Y")
        if options['seasonalCycle'] == True:
            timeTitle = timeSlice.strftime("%b (all years)")

    if(options['timeRegrid'] == 'annual'):
        timeTitle = timeSlice.strftime("%Y")
    
    if(options['timeRegrid'] == 'full'):
        minTime = min(min(rcmedData['times']), min(modelData['times']))
        maxTime = max(max(rcmedData['times']), max(modelData['times']))
        timeTitle = minTime.strftime("%b %d, %Y")+' to '+maxTime.strftime("%b %d, %Y")
    
    return timeTitle


