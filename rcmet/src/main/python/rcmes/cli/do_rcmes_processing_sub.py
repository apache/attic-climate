#!/usr/local/bin/python
""" 
    Module that is used to lauch the rcmes processing from the rcmet_ui.py
    script.
"""

import sys
import datetime
import numpy
import numpy.ma as ma 
import rcmes.toolkit.plots

import rcmes.storage.db
import rcmes.storage.files
import rcmes.toolkit.process
import rcmes.toolkit.metrics

# NOT USED?
# global mmt1
# global sigma_tt1
# import rcmes.fortranfile

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

        Input: 5 dictionaries which contain a huge argument list with all of the user options 
        (which can be collected from the GUI)

            settings - dictionary of rcmes run settings
                settings = {"cache_dir": string describing directory path,
                            "work_dir": string describing directory path,
                            "file_list": string describing model file name + path }

            params - dictionary of rcmes run parameters
                params = {"obs_dataset_id": int( db dataset id ),
                          "obs_param_id": int( db parameter id ),
                          "start_time": datetime object (needs to change to string + decode),
                          "end_time": datetime object (needs to change to string + decode),
                          "lat_min": float,
                          "lat_max": float,
                          "lon_min": float,
                          "lon_max": float }

            model - dictionary of model parameters
                model = {"var_name": string describing name of variable to evaluate 
                                     (as written in model file),
                         "time_variable": string describing name of time variable 
                                     (as written in model file), 	
                         "lat_variable": string describing name of latitude variable 
                                     (as written in model file), 
                         "lon_variable": string describing name of longitude variable 
                                     (as written in model file) } 
            
            mask - dictionary of mask specific options (only used if options['mask']=True)
                mask = {"lat_min": float,
                        "lat_max": float,
                        "lon_min": float,
                        "lon_max": float}
            
            options - dictionary full of different user supplied options
                options = {"regrid": str( 'obs' | 'model' | 'regular' ),
                           "time_regrid": str( 'full' | 'annual' | 'monthly' | 'daily' ),
                           "seasonal_cycle": Boolean,
                           "metric": str('bias'|'mae'|'acc'|'pdf'|'patcor'|'rms'|'diff'),
                           "plot_title": string describing title to use in plot graphic,
                           "plot_filename": basename of file to use for plot graphic 
                                             i.e. {plot_filename}.png,
                           "mask": Boolean,
                           "precip": Boolean }


        Output: image files of plots + possibly data

        Peter Lean      February 2011
        Cameron Goodale August 2012

    '''



    print "%s is type of params['start_time']" % type(params['start_time'])


    # check the number of model data files
    if len(settings['file_list']) < 1:         # no input data file
        print 'No input model data file. EXIT'
        sys.exit()
    # assign parameters that must be preserved throughout the process
    if options['mask'] == True: 
        options['seasonal_cycle'] = True

    print 'start & end eval period = %s to %s' % ( params['start_time'].strftime("%Y%m"),
                                                   params['end_time'].strftime("%Y%m") )
    
    print(params['obs_dataset_id'], params['obs_param_id'], params['lat_min'],
          params['lat_max'], params['lon_min'], params['lon_max'], params['start_time'],
          params['end_time'], settings['cache_dir'])

    ###########################################################################
    # Part 1: retrieve observation data from the database
    #         NB. automatically uses local cache if already retrieved.
    ###########################################################################
    rcmed_data = get_data_from_rcmed( params, settings )


    #extract climo data

    ###########################################################################
    # Part 2: load in model data from file(s)
    ###########################################################################
    model_data = get_data_from_model( model, settings )

    ###########################################################################
    # Deal with some precipitation specific options
    #      i.e. adjust units of model data and set plot color bars suitable for precip
    ###########################################################################
    colorbar = 'rainbow'
    if options['precip'] == True:
        model_data['data'] = model_data['data']*86400.  # convert from kgm-2s-1 into mm/day
        colorbar = 'precip2_17lev'

    # set color bar suitable for MODIS cloud data
    if params['obs_param_id'] == 31:
        colorbar = 'gsdtol'

    ##################################################################################################################
    # Extract sub-selection of model data for required time range.
    #   e.g. a single model file may contain data for 20 years,
    #        but the user may have selected to only analyse data between 2003 and 2004.  
    ##################################################################################################################

    # make list of indices where model_data['times'] are between params['start_time'] and params['end_time']
    model_time_overlap = numpy.logical_and((numpy.array(model_data['times'])>=params['start_time']), 
                                           (numpy.array(model_data['times'])<=params['end_time'])) 

    # make subset of model_data['times'] using full list of times and indices calculated above
    model_data['times'] = list(numpy.array(model_data['times'])[model_time_overlap])

    # make subset of model_data['data'] using full model data and indices calculated above 
    model_data['data'] = model_data['data'][model_time_overlap, :, :]

    ##################################################################################################################
    # Part 3: Temporal regridding
    #      i.e. model data may be monthly, and observation data may be daily.
    #           We need to compare like with like so the User Interface asks what time unit the user wants to work with
    #              e.g. the user may select that they would like to regrid everything to 'monthly' data
    #                   in which case, the daily observational data will be averaged onto monthly data
    #                   so that it can be compared directly with the monthly model data.
    ##################################################################################################################
    print 'Temporal Regridding Started'

    if(options['time_regrid']):
        # Run both obs and model data through temporal regridding routine.
        #  NB. if regridding not required (e.g. monthly time units selected and model data is already monthly),
        #      then subroutine detects this and returns data untouched.
        rcmed_data['data'], new_obs_times = rcmes.process.calc_average_on_new_time_unit(rcmed_data['data'], 
                                                                                        rcmed_data['times'],
                                                                                        unit=options['time_regrid'])
        
        model_data['data'], new_model_times = rcmes.process.calc_average_on_new_time_unit(model_data['data'],
                                                                                          model_data['times'],
                                                                                          unit=options['time_regrid'])

    # Set a new 'times' list which describes the common times used for both model and obs after the regrid.
    if new_obs_times == new_model_times:
        times = new_obs_times

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
    if new_obs_times != new_model_times:
        print 'Warning: after temporal regridding, times from observations and model do not match'
        print 'Check if this is unexpected.'
        print 'Proceeding with data from times common in both model and obs.'

        # Create empty lists ready to store data
        times = []
        temp_model_data = []
        temp_obs_data = []

        # Loop through each time that is common in both model and obs
        for common_time in numpy.intersect1d(new_obs_times, new_model_times):
            # build up lists of times, and model and obs data for each common time
            #  NB. use lists for data for convenience (then convert to masked arrays at the end)
            times.append(new_obs_times[numpy.where(numpy.array(new_obs_times) == common_time)[0][0]])
            temp_model_data.append(model_data['data'][numpy.where(numpy.array(new_model_times) == common_time)[0][0], :, :])
            temp_obs_data.append(rcmed_data['data'][numpy.where(numpy.array(new_obs_times) == common_time)[0][0], :, :])

        # Convert data arrays from list back into full 3d arrays.
        model_data['data'] = ma.array(temp_model_data)
        rcmed_data['data'] = ma.array(temp_obs_data)

        # Reset all time lists so representative of the data actually used.
        new_obs_times = times
        new_model_times = times
        rcmed_data['times'] = times
        model_data['times'] = times

    ##################################################################################################################
    # Part 4: spatial regridding
    #         The model and obs are rarely on the same grid.
    #         To compare the two, you need them to be on the same grid.
    #         The User Interface asked the user if they'd like to regrid everything to the model grid or the obs grid.
    #         Alternatively, they could chose to regrid both model and obs onto a third regular lat/lon grid as defined
    #          by parameters that they enter.
    #
    #         NB. from this point on in the code, the 'lats' and 'lons' arrays are common to 
    #             both rcmed_data['data'] and model_data['data'].
    ##################################################################################################################

    ##################################################################################################################
    # either i) Regrid obs data to model grid.
    ##################################################################################################################
    if options['regrid'] == 'model':
        # User chose to regrid observations to the model grid
        model_data['data'], rcmed_data['data'], lats, lons = rcmes.process.regrid_wrapper('0', rcmed_data['data'], 
                                                                                  rcmed_data['lats'],
                                                                                  rcmed_data['lons'], 
                                                                                  model_data['data'],
                                                                                  model_data['lats'],
                                                                                  model_data['lons'])

    ##################################################################################################################
    # or    ii) Regrid model data to obs grid.
    ##################################################################################################################
    if options['regrid'] == 'obs':
        # User chose to regrid model data to the observation grid

        model_data['data'], rcmed_data['data'], lats, lons = rcmes.process.regrid_wrapper('1', rcmed_data['data'], 
                                                                                  rcmed_data['lats'], 
                                                                                  rcmed_data['lons'], 
                                                                                  model_data['data'],
                                                                                  model_data['lats'], 
                                                                                  model_data['lons'])

    ##################################################################################################################
    # or    iii) Regrid both model data and obs data to new regular lat/lon grid.
    ##################################################################################################################
    if options['regrid'] == 'regular':
        # User chose to regrid both model and obs data onto a newly defined regular lat/lon grid
        # Construct lats, lons from grid parameters

        # Create 1d lat and lon arrays
        lat = numpy.arange(nLats)*dLat+Lat0
        lon = numpy.arange(nLons)*dLon+Lon0

        # Combine 1d lat and lon arrays into 2d arrays of lats and lons
        lons, lats = numpy.meshgrid(lon, lat)

        ###########################################################################################################
        # Regrid model data for every time
        #  NB. store new data in a list and convert back to an array at the end.
        ###########################################################################################################
        tmp_model_data = []

        time_count = model_data['data'].shape[0]
        for t in numpy.arange(time_count):
            tmp_model_data.append(rcmes.process.do_regrid(model_data['data'][t, :, :],
                                                          model_data['lats'][:, :],
                                                          model_data['lons'][:, :],
                                                          rcmed_data['lats'][:, :],
                                                          rcmed_data['lons'][:, :]))

        # Convert list back into a masked array 
        model_data['data'] = ma.array(tmp_model_data)

        ###########################################################################################################
        # Regrid obs data for every time
        #  NB. store new data in a list and convert back to an array at the end.
        ###########################################################################################################
        temp_obs_data = []
        time_count = rcmed_data['data'].shape[0]
        for t in numpy.arange(time_count):
            temp_obs_data.append(rcmes.process.do_regrid(rcmed_data['data'][t, :, :], 
                                                         rcmed_data['lats'][:, :], 
                                                         rcmed_data['lons'][:, :], 
                                                         model_data['lats'][:, :], model_data['lons'][:, :]))

        # Convert list back into a masked array 
        rcmed_data['data'] = ma.array(temp_obs_data)

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
    mask = numpy.logical_or(numpy.logical_or(lats<=mask['lat_min'], lats>=mask['lat_max']), 
                            numpy.logical_or(lons<=mask['lon_min'], lons>=mask['lon_max']))

    ###############################################################################################################
    # Calculate area-weighted averages within this region and store in new lists
    ###############################################################################################################
    model_store = []
    time_count = model_data['data'].shape[0]
    for t in numpy.arange(time_count):
        model_store.append(rcmes.process.calc_area_mean(model_data['data'][t, :, :], lats, lons, mymask=mask))

    obs_store = []
    time_count = rcmed_data['data'].shape[0]
    for t in numpy.arange(time_count):
        obs_store.append(rcmes.process.calc_area_mean(rcmed_data['data'][t, :, :], lats, lons, mymask=mask))
  
    ###############################################################################################################
    # Now overwrite data arrays with the area-averaged values
    ###############################################################################################################
    model_data['data'] = ma.array(model_store)
    rcmed_data['data'] = ma.array(obs_store)

    ###############################################################################################################
    # Free-up some memory by overwriting big variables
    ###############################################################################################################
    obs_store = 0
    model_store = 0

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
    if options['seasonal_cycle'] == True:

        print 'Compositing data to calculate seasonal cycle'

        model_data['data'] = rcmes.metrics.calc_annual_cycle_means(model_data['data'], model_data['times'])
        rcmed_data['data'] = rcmes.metrics.calc_annual_cycle_means(rcmed_data['data'], model_data['times'])

    ##################################################################################################################
    # Part 7: metric calculation
    #              Calculate performance metrics comparing rcmed_data['data'] and model_data['data'].
    #              All output is stored in metric_data regardless of what metric was calculated.
    #          
    #      NB. the dimensions of metric_data will vary depending on the dimensions of the incoming data
    #          *and* on the type of metric being calculated.
    #
    #      e.g.    bias between incoming 1D model and 1D obs data (after area-averaging) will be a single number. 
    #              bias between incoming 3D model and 3D obs data will be 2D, i.e. a map of mean bias.
    #              correlation coefficient between incoming 3D model and 3D obs data will be 1D time series.
    # 
    ##################################################################################################################

    if options['metric'] == 'bias':
        metric_data = rcmes.metrics.calc_bias(model_data['data'], rcmed_data['data'])
        metric_title = 'Bias'

    if options['metric'] == 'mae':
        metric_data = rcmes.metrics.calc_mae(model_data['data'], rcmed_data['data'])
        metric_title = 'Mean Absolute Error'

    if options['metric'] == 'rms':
        metric_data = rcmes.metrics.calc_rms(model_data['data'], rcmed_data['data'])
        metric_title = 'RMS error'
 
    if options['metric'] == 'difference':
        metric_data = rcmes.metrics.calc_difference(model_data['data'], rcmed_data['data'])
        metric_title = 'Difference'

    if options['metric'] == 'patcor':
        metric_data = rcmes.metrics.calc_pat_cor(model_data['data'], rcmed_data['data'])
        metric_title = 'Pattern Correlation'

    if options['metric'] == 'acc':
        metric_data = rcmes.metrics.calc_anom_cor(model_data['data'], rcmed_data['data'])
        metric_title = 'Anomaly Correlation'

    if options['metric'] == 'nacc':
        metric_data = rcmes.metrics.calc_anom_corn(model_data['data'], rcmed_data['data'])
        metric_title = 'Anomaly Correlation'

    if options['metric'] == 'pdf':
        metric_data = rcmes.metrics.calc_pdf(model_data['data'], rcmed_data['data'])
        metric_title = 'Probability Distribution Function'

    if options['metric'] == 'coe':
        metric_data = rcmes.metrics.calc_nash_sutcliff(model_data['data'], rcmed_data['data'])
        metric_title = 'Coefficient of Efficiency'

    if options['metric'] == 'stddev':
        metric_data = rcmes.metrics.calc_stdev(model_data['data'])
        data2 = rcmes.metrics.calc_stdev(rcmed_data['data'])
        metric_title = 'Standard Deviation'
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
    if metric_data.ndim == 1:
        print 'Producing time series plots ****'
        print metric_data
        year_labels = True
        #   mytitle = 'Area-average model v obs'

    ################################################################################################################
    # If producing seasonal cycle plots, don't want to put year labels on the time series plots.
    ################################################################################################################
    if options['seasonal_cycle'] == True:
        year_labels = False
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
        # ^^ This is the reason model_data['data'] has been swapped for metric_data in
        # the following function
        # TODO: think of a cleaner way of dealing with this.

        ###########################################################################################
        # Produce the time series plots with two lines: obs and model
        ###########################################################################################
        print 'two line timeseries'
        #     mytitle = options['plot_title']
        mytitle = 'Area-average model v obs'
        if options['plot_title'] == 'default':
            mytitle = metric_title+' model & obs'
        #rcmes.plots.draw_time_series_plot(model_data['data'],times,options['plot_filename']+'both',
        #                                           settings['work_dir'],data2=rcmed_data['data'],mytitle=mytitle,
        #                                           ytitle='Y',xtitle='time',
        #                                           year_labels=year_labels)
        
        rcmes.plots.draw_time_series_plot(metric_data, times, options['plot_filename']+'both',
                                                   settings['work_dir'], data2, mytitle=mytitle, 
                                                   ytitle='Y', xtitle='time',
                                                   year_labels=year_labels)

    else: 
    ###############################################################################################
    # Produce the metric time series plot (one line only)
    ###############################################################################################
        mytitle = options['plot_title']
        if options['plot_title'] == 'default':
            mytitle = metric_title+' model v obs'
        print 'one line timeseries'
        rcmes.plots.draw_time_series_plot(metric_data, times, options['plot_filename'], 
                                                   settings['work_dir'], mytitle=mytitle, ytitle='Y', xtitle='time',
                                                   year_labels=year_labels)

    ###############################################################################################
    # 2 dimensional data, e.g. Maps
    ###############################################################################################
    if metric_data.ndim == 2:

        ###########################################################################################
        # Calculate color bar ranges for data such that same range is used in obs and model plots
        # for like-with-like comparison.
        ###########################################################################################
        mymax = max(rcmed_data['data'].mean(axis=0).max(), model_data['data'].mean(axis=0).max())
        mymin = min(rcmed_data['data'].mean(axis=0).min(), model_data['data'].mean(axis=0).min())

        ###########################################################################################
        # Time title labels need their format adjusting depending on the temporal regridding used,
        #          e.g. if data are averaged to monthly,
        #               then want to write 'Jan 2002', 'Feb 2002', etc instead of 'Jan 1st, 2002', 'Feb 1st, 2002'
        #
        #  Also, if doing seasonal cycle compositing 
        #  then want to write 'Jan','Feb','Mar' instead of 'Jan 2002','Feb 2002','Mar 2002' etc 
        #  as data are representative of all Jans, all Febs etc. 
        ###########################################################################################
        if(options['time_regrid'] == 'daily'):
            time_format = "%b %d, %Y"
        if(options['time_regrid'] == 'monthly'):
            time_format = "%b %Y"
        if(options['time_regrid'] == 'annual'):
            time_format = "%Y"
        if(options['time_regrid'] == 'full'):
            time_format = "%b %d, %Y"

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
        model_data_mean = model_data['data'].mean(axis=0)
        obs_data_mean = rcmed_data['data'].mean(axis=0)

        ###########################################################################################
        # Calculate missing data masks using tolerance threshold of missing data going into calculations
        ###########################################################################################
        obs_data_mask = rcmes.process.create_mask_using_threshold(rcmed_data['data'], threshold=0.75)
        model_data_mask = rcmes.process.create_mask_using_threshold(model_data['data'], threshold=0.75)

        ###########################################################################################
        # Combine data and masks into masked arrays suitable for plotting.
        ###########################################################################################
        model_data_mean = ma.masked_array(model_data_mean, model_data_mask)
        obs_data_mean = ma.masked_array(obs_data_mean, obs_data_mask)

        ###########################################################################################
        # Plot model data
        ###########################################################################################
        mytitle = 'Model data: mean between %s and %s' % ( model_data['times'][0].strftime(time_format), 
                                                           model_data['times'][-1].strftime(time_format) )
        rcmes.plots.draw_map_color_filled(model_data_mean, lats, lons, options['plot_filename']+'model',
                                                   settings['work_dir'], mytitle=mytitle, rangeMax=mymax,
                                                   rangeMin=mymin, colorTable=colorbar, niceValues=True)

        ###########################################################################################
        # Plot obs data
        ###########################################################################################
        mytitle = 'Obs data: mean between %s and %s' % ( rcmed_data['times'][0].strftime(time_format), 
                                                        rcmed_data['times'][-1].strftime(time_format) )
        rcmes.plots.draw_map_color_filled(obs_data_mean, lats, lons, options['plot_filename']+'obs',
                                                   settings['work_dir'], mytitle=mytitle, rangeMax=mymax, 
                                                   rangeMin=mymin, colorTable=colorbar, niceValues=True)

        ###########################################################################################
        # Plot metric
        ###########################################################################################
        mymax = metric_data.max()
        mymin = metric_data.min()

        mytitle = options['plot_title']

        if options['plot_title'] == 'default':
            mytitle = metric_title+' model v obs %s to %s' % ( rcmed_data['times'][0].strftime(time_format),
                                                                rcmed_data['times'][-1].strftime(time_format) )

        rcmes.plots.draw_map_color_filled(metric_data, lats, lons, options['plot_filename'],
                                                   settings['work_dir'], mytitle=mytitle, 
                                                   rangeMax=mymax, rangeMin=mymin, diff=True, 
                                                   niceValues=True, nsteps=24)

    ###############################################################################################
    # 3 dimensional data, e.g. sequence of maps
    ###############################################################################################
    if metric_data.ndim == 3:
        print 'Generating series of map plots, each for a different time.'
        for t in numpy.arange(rcmed_data['data'].shape[0]):

            #######################################################################################
            # Calculate color bar ranges for data such that same range is used in obs and model plots
            # for like-with-like comparison.
            #######################################################################################
            color_range_max = max(rcmed_data['data'][t, :, :].max(), model_data['data'][t, :, :].max())
            color_range_min = min(rcmed_data['data'][t, :, :].min(), model_data['data'][t, :, :].min())

            # Setup the time_title
            time_slice = times[t]
            time_title = create_time_title( options, time_slice, rcmed_data, model_data )

            #######################################################################################
            # Plot model data
            #######################################################################################
            mytitle = 'Model data: mean '+time_title
            rcmes.plots.draw_map_color_filled(model_data['data'][t, :, :], lats, lons, 
                                                       options['plot_filename']+'model'+str(t),
                                                       settings['work_dir'], mytitle=mytitle, 
                                                       rangeMax=color_range_max, rangeMin=color_range_min,
                                                       colorTable=colorbar, niceValues=True)

            #######################################################################################
            # Plot obs data
            #######################################################################################
            mytitle = 'Obs data: mean '+time_title
            rcmes.plots.draw_map_color_filled(rcmed_data['data'][t, :, :], lats, lons, 
                                                       options['plot_filename']+'obs'+str(t),
                                                       settings['work_dir'], mytitle=mytitle, 
                                                       rangeMax=color_range_max, rangeMin=color_range_min,
                                                       colorTable=colorbar, niceValues=True)

            #######################################################################################
            # Plot metric
            #######################################################################################
            mytitle = options['plot_title']

            if options['plot_title'] == 'default':
                mytitle = metric_title +' model v obs : '+time_title

            color_range_max = metric_data.max()
            color_range_min = metric_data.min()

            rcmes.plots.draw_map_color_filled(metric_data[t, :, :], lats, lons, 
                                                       options['plot_filename']+str(t), settings['work_dir'], 
                                                       mytitle=mytitle, rangeMax=color_range_max, rangeMin=color_range_min, diff=True,
                                                       niceValues=True, nsteps=24)


def get_data_from_rcmed( params, settings ):
    """
    This function takes in the params and settings dictionaries and will return an rcmed_data dictionary.
    
    return:
        rcmed_data = {"lats": 1-d numpy array of latitudes,
                      "lons": 1-d numpy array of longitudes,
                      "levels": 1-d numpy array of height/pressure levels (surface based data will have length == 1),
                      "times": list of python datetime objects,
                      "data": masked numpy arrays of data values}
    """
    rcmed_data = {}
    obs_lats, obs_lons, obs_levs, obs_times, obs_data =  rcmes.db.extract_data_from_db(params['obs_dataset_id'],
                                                                                       params['obs_param_id'],
                                                                                       params['lat_min'],
                                                                                       params['lat_max'],
                                                                                       params['lon_min'],
                                                                                       params['lon_max'],
                                                                                       params['start_time'],
                                                                                       params['end_time'],
                                                                                       settings['cache_dir'])
    rcmed_data['lats'] = obs_lats
    rcmed_data['lons'] = obs_lons
    rcmed_data['levels'] = obs_levs
    rcmed_data['times'] = obs_times
    rcmed_data['data'] = obs_data
    
    return rcmed_data

def get_data_from_model( model, settings ):
    """
    This function takes in the model and settings dictionaries and will return a model data dictionary.
    
    return:
        model = {"lats": 1-d numpy array of latitudes,
                 "lons": 1-d numpy array of longitudes,
                 "times": list of python datetime objects,
                 "data": numpy array containing data from all files}
    """
    model = rcmes.files.read_data_from_file_list(settings['file_list'],
                                                 model['var_name'],
                                                 model['time_variable'],
                                                 model['lat_variable'],
                                                 model['lon_variable'])
    return model

##################################################################################################################
# Processing complete
##################################################################################################################

def create_time_title( options, time_slice, rcmed_data, model_data ):
    """
    Function that takes in the options dictionary and a specific time_slice.
    
    Return:  string time_title properly formatted based on the 'time_regrid' and 'seasonal_cycle' options value.
    
    #######################
    
    Time title labels need their format adjusting depending on the temporal regridding used,
        e.g. if data are averaged to monthly,
                   then want to write 'Jan 2002', 'Feb 2002', etc instead of 'Jan 1st, 2002', 'Feb 1st, 2002'

    Also, if doing seasonal cycle compositing then want to write 'Jan','Feb','Mar' instead of 'Jan 2002',
     'Feb 2002','Mar 2002' etc as data are representative of all Jans, all Febs etc. 
    """
    if(options['time_regrid'] == 'daily'):
        time_title = time_slice.strftime("%b %d, %Y")
        if options['seasonal_cycle'] == True:
            time_title = time_slice.strftime("%b %d (all years)")

    if(options['time_regrid'] == 'monthly'):
        time_title = time_slice.strftime("%b %Y")
        if options['seasonal_cycle'] == True:
            time_title = time_slice.strftime("%b (all years)")

    if(options['time_regrid'] == 'annual'):
        time_title = time_slice.strftime("%Y")
    
    if(options['time_regrid'] == 'full'):
        min_time = min(min(rcmed_data['times']), min(model_data['times']))
        max_time = max(max(rcmed_data['times']), max(model_data['times']))
        time_title = min_time.strftime("%b %d, %Y")+' to '+max_time.strftime("%b %d, %Y")
    
    return time_title


print 'RCMES processing completed.'

