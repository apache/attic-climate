#!/usr/local/bin/python
""" 
    Step by Step Wizard that demonstrates how the underlying RCMES code can
    be used to generate climate dataset intercomparisons
"""
# Imports
# Native Python Module Imports
import glob
import datetime
import time
import sys
import os

# Appending rcmes via relative path
sys.path.append(os.path.abspath('../../.'))

# RCMES Imports
import rcmes.storage.files as files
import rcmes.storage.rcmed as db
import rcmes.toolkit.process as process
import rcmes.cli.do_rcmes_processing_sub as doProcess


# Empty dictionaries to collect all of the user's inputs 
options = {}
mask = {}
model = {}
params = {}
settings = {}

def rcmetUI():
    """"
    Command Line User interface for RCMET.
    Collects user options then runs RCMET to perform processing.
    
    Duplicates job of GUI.
    
    Peter Lean   March 2011
    
    """
    print 'Regional Climate Model Evaluation System BETA'
    
    
    print "Querying RCMED for available parameters..."
    try:
        parameters = db.getParams()
    except:
        sys.exit()


    ###################################################################################################
    # Section 0: Collect directories to store RCMET working files.
    ###################################################################################################
    settings['workDir'] = raw_input('Please enter workdir:\n> ')   # This is where the images are created/stored
    settings['cacheDir'] = raw_input('Please enter cachedir:\n> ') # This is where the database cache files are stored
    
    ###################################################################################################
    # Section 1a: Enter model file/s
    ###################################################################################################
    inputFileList = raw_input('Please enter model file (or specify multiple files using wildcard):\n> ')
    settings['fileList'] = glob.glob(inputFileList)
    
    ###################################################################################################
    # Section 1b (i): 
    #     Attempt to auto-detect latitude and longitude variable names
    #     and lat, lon limits from first file in settings['fileList'] 
    ###################################################################################################
    status, model['latVariable'], model['lonVariable'], params['latMin'], params['latMax'], params['lonMin'], params['lonMax'], variableNameList = files.find_latlon_var_from_file(settings['fileList'])
    
    ###################################################################################################
    # Section 1b (ii)
    #     If unable to auto-detect latitude and longitude variables from file,
    #     then ask user to select from which variable corresponds to latitude and
    #     which corresponds to longitude (from a list of available variables in the file).  
    ###################################################################################################
    if status == 0:
        print 'Could not find latitude and longitude data in the file.'
        counter = 0
        for myvar in variableNameList:
            print '[', counter, ']', myvar
            counter += 1

        userVarChoice = raw_input('Please help, by selecting which of the above variables in the file is the latitude variable:\n (or if the latitudes and longitudes are stored in a separate file enter "z")\n> ').lower()

        if userVarChoice == 'z':
            latLonFilename = raw_input('Please enter the full path of the file containing the latitudes and longitudes:\n> ')
            latLonFileList = glob.glob(latLonFilename)
            status, model['latVariable'], model['lonVariable'], params['latMin'], params['latMax'], params['lonMin'], params['lonMax'], new_variableNameList = files.find_latlon_var_from_file(latLonFileList)

        ##################################################
        # Section 1b (iii)
        ##################################################
        if userVarChoice != 'z':
            try:
                model['latVariable'] = variableNameList[int(userVarChoice)]
            except:
                model['latVariable'] = variableNameList[int(raw_input('Are you sure? The previous selection did not work, please try again:\n> '))]

            try:
                model['lonVariable'] = variableNameList[int(raw_input('..and which of the above variables is the longitude variable?\n> '))]
            except:
                model['lonVariable'] = variableNameList[int(raw_input('Are you sure? The previous selection did not work, please try again:\n> '))]

        # Find lat/lon ranges by loading the data using the user supplied variable names
        params['latMin'], params['latMax'], params['lonMin'], params['lonMax'] = files.find_latlon_ranges(settings['fileList'], latVarName, lonVarName) 


    print 'Found latitude and longitude variables in model data files: '
    print 'Lat/Lon variable names : ', model['latVariable'], model['lonVariable']
    print 'Minimum Latitude: ', params['latMin']
    print 'Maximum Latitude: ', params['latMax']
    print 'Minimum Longitude: ', params['lonMin']
    print 'Maximum Longitude: ', params['lonMax']
    
    ###################################################################################################
    # Section 1c (i) Attempt to auto-detect the time variable in the file.
    #     NB. name of time variable needs to passed into RCMET.
    ###################################################################################################
    status, model['timeVariable'], variableNameList = files.find_time_var_name_from_file(settings['fileList'])

    print 'Found time variable name :', model['timeVariable']
    if status == 0:
        print 'Could not find time data in the file.'
        counter = 0
        for myvar in variableNameList:
            print '[', counter, ']', myvar
            counter += 1

        try:
            model['timeVariable'] = variableNameList[int(raw_input('Please help, by selecting which of the above variables in the file is the time variable:\n> '))]
        except:
            model['timeVariable'] = variableNameList[int(raw_input('There was a problem with your selection, please try again:\n> '))]

    ###################################################################################################
    # Section 1c (ii): Attempt to decode model times into a python datetime object.
    ###################################################################################################
    try:
        modelTimes = process.decode_model_times(settings['fileList'], model['timeVariable'])
        modelStartTime = min(modelTimes)
        modelEndTime = max(modelTimes)

        print 'Model times decoded:'
        print 'First model time : ', modelStartTime.strftime("%Y/%m/%d %H:%M")
        print 'Last model time : ',  modelEndTime.strftime("%Y/%m/%d %H:%M")
    except:
        print 'Error: there was a problem decoding the model times.'

  
    # Section 2a: Select which model variable to use for evaluation (from list of variables in file)
  
    counter = 0
    for myvar in variableNameList:
        print '[', counter, ']', myvar
        counter += 1

    userVarChoice = raw_input('Which variable would you like to evaluate?\n> ')
    try:
        model['var_name'] = variableNameList[int(userVarChoice)]
    except:
        userVarChoice = raw_input('There was a problem with that selection, please try again:\n> ')    
        model['var_name'] = variableNameList[int(userVarChoice)]

  
    # Ask user if the above variable is precipitation data 
    # (as this needs some special treatment by RCMET, e.g. color tables, unit conversion etc)

    options['precip'] = False
    precipChoice = raw_input('Is this precipitation data? [y/n]\n> ').lower()
    if precipChoice == 'y':
        options['precip'] = True

  
    # Section 3a: Select observation dataset from database
  
    # dbDatasets = ['TRMM','ERA-Interim','AIRS','MODIS','URD','CRU']
    # replace with list comprehension
    dbDatasets = [parameter['longName'] for parameter in parameters]
  
  
    # datasetIds = [3,1,2,5,4,6]
    # dbDatasetStartTimes = [datetime.datetime(1998,1,1,0,0,0,0),datetime.datetime(1989,01,01,0,0,0,0),datetime.datetime(2002,8,31,0,0,0,0),datetime.datetime(2000,2,24,0,0,0,0),datetime.datetime(1948,1,1,0,0,0,0),datetime.datetime(1901,1,1,0,0,0,0)]
    # dbDatasetEndTimes = [datetime.datetime(2010,1,1,0,0,0,0),datetime.datetime(2009,12,31,0,0,0,0),datetime.datetime(2010,1,1,0,0,0,0),datetime.datetime(2010,5,30,0,0,0,0),datetime.datetime(2010,1,1,0,0,0,0),datetime.datetime(2006,12,1,0,0,0,0)]

    dbParameters = [['daily precip', 'monthly precip'], ['2m temp', '2m dew point'], ['2m temp'], ['cloud fraction'], ['precip'], ['tavg', 'tmax', 'tmin', 'precip']]

    # dbParameterIds = [[14,36],[12,13],[15],[31],[30],[33,34,35,32]]
    dbParameterIds = [parameter['parameter_id'] for parameter in parameters]

    # Not sure this is needed anymore since we have a parameters list object to work with
    datasetIds = [parameter['dataset_id'] for parameter in parameters]
  
    try:
        dbDatasetStartTimes = [datetime.datetime.strptime(parameter['start_date'], '%Y-%m-%d') for parameter in parameters]
    except:
        print "Error parsing the start dates from RCMED. Expected Format 'YYYY-MM-DD'"
    
    try:
        dbDatasetEndTimes = [datetime.datetime.strptime(parameter['end_date'], '%Y-%m-%d') for parameter in parameters]
    except:
        print "Error parsing the end dates from RCMED. Expected Format 'YYYY-MM-DD'" 
    
    dbParameters = [parameter['dataset_id'] for parameter in parameters]

  
    # Section 3b: Select Dataset from list

    """
    counter = 0
    for dataset in dbDatasets:
       print '[', counter, '] ', dataset
       counter += 1
    REPLACED WITH THIS"""
    for parameter in parameters:
        """( 38 ) - CRU3.1 Daily-Mean Temperature : monthly"""
        print "({:^2}) - {:<35} :: {:<10}".format(parameter['parameter_id'], parameter['longName'], parameter['timestep'])

    try:
        datasetChoice = int(raw_input('Please select which observational dataset you wish to compare against:\n> ')) 
        selection = next((p for p in parameters if p['parameter_id'] == datasetChoice), None)
        params['obs_dataset_id'] = selection['dataset_id']
        obsStartTime = datetime.datetime.strptime(selection['start_date'], "%Y-%m-%d")
        obsEndTime = datetime.datetime.strptime(selection['end_date'], "%Y-%m-%d")
        params['obsParamId'] = selection['parameter_id']
        #params['obs_dataset_id'] = datasetIds[int(datasetChoice)]
        #obsStartTime = dbDatasetStartTimes[int(datasetChoice)]
        #obsEndTime = dbDatasetEndTimes[int(datasetChoice)]
    
    except:
        datasetChoice = raw_input('There was a problem with your selection, please try again:\n> ') 
        selection = next((p for p in parameters if p['parameter_id'] == datasetChoice), None)
        params['obs_dataset_id'] = selection['dataset_id']
        obsStartTime = datetime.datetime.strptime(selection['start_date'], "%Y-%m-%d")
        obsEndTime = datetime.datetime.strptime(selection['end_date'], "%Y-%m-%d")
        params['obsParamId'] = selection['parameter_id']
        #params['obs_dataset_id'] = datasetIds[int(datasetChoice)]
        #obsStartTime = dbDatasetStartTimes[int(datasetChoice)]
        #obsEndTime = dbDatasetEndTimes[int(datasetChoice)]


    """ This Section has been removed.  In the previous step the DataSet
    AND Parameter are Selected at the sametime.  These variables have been
    declared in that section
    ###################################################################################################
    # Section 3c: Select Parameter from list of available parameters in dataset (selected above)
    ###################################################################################################
    
     
    
     
    counter = 0
    for parameter in dbParameters[int(datasetChoice)]:
       print '[', counter, '] ', parameter
       counter += 1
    
    try:
      params['obsParamId'] = dbParameterIds[int(datasetChoice)][int(raw_input('Please select a parameter:\n> '))]
    except:
      params['obsParamId'] = dbParameterIds[int(datasetChoice)][int(raw_input('There was a problem with your selection, please try again:\n> '))]
    """

    # Section 4: Select time range to evaluate (defaults to overlapping times between model and obs)
    
    # Calculate overlap
    params['startTime'] = max(modelStartTime, obsStartTime)
    params['endTime'] = min(modelEndTime, obsEndTime)
    
    print 'Model time range: ', modelStartTime.strftime("%Y/%m/%d %H:%M"), modelEndTime.strftime("%Y/%m/%d %H:%M")
    print 'Obs time range: ', obsStartTime.strftime("%Y/%m/%d %H:%M"), obsEndTime.strftime("%Y/%m/%d %H:%M")
    print 'Overlapping time range: ', params['startTime'].strftime("%Y/%m/%d %H:%M"), params['endTime'].strftime("%Y/%m/%d %H:%M")
    
    # If want sub-selection then enter start and end times manually
    choice = raw_input('Do you want to only evaluate data from a sub-selection of this time range? [y/n]\n> ').lower()
    if choice == 'y':
        startTimeString = raw_input('Please enter the start time in the format YYYYMMDDHHmm:\n> ')
        try:
            params['startTime'] = datetime.datetime(*time.strptime(startTimeString, "%Y%m%d%H%M")[:6])
        except:
            print 'There was a problem with your entry'

    endTimeString = raw_input('Please enter the end time in the format YYYYMMDDHHmm:\n> ')
    try:
        params['endTime'] = datetime.datetime(*time.strptime(endTimeString, "%Y%m%d%H%M")[:6])
    except:
        print 'There was a problem with your entry'
    
    print 'Selected time range: ', params['startTime'].strftime("%Y/%m/%d %H:%M"), params['endTime'].strftime("%Y/%m/%d %H:%M")
  
  
  # Section 5: Select Spatial Regridding options
  
    print 'Spatial regridding options: '
    print '[0] Use Observational grid'
    print '[1] Use Model grid'
    print '[2] Define new regular lat/lon grid to use'
    try:
        options['regrid'] = int(raw_input('Please make a selection from above:\n> '))
    except:
        options['regrid'] = int(raw_input('There was a problem with your selection, please try again:\n> '))
    
    if options['regrid'] > 2:
        try:
            options['regrid'] = int(raw_input('That was not an option, please make a selection from the list above:\n> '))
        except:
            options['regrid'] = int(raw_input('There was a problem with your selection, please try again:\n> '))
    
    if options['regrid'] == 0:
        options['regrid'] = 'obs'
    
    if options['regrid'] == 1:
        options['regrid'] = 'model'
    
    # If requested, get new grid parameters
    if options['regrid'] == 2:
        options['regrid'] = 'regular'
        params['lonMin'] = float(raw_input('Please enter the longitude at the left edge of the domain:\n> '))
        params['lonMax'] = float(raw_input('Please enter the longitude at the right edge of the domain:\n> '))
        params['latMin'] = float(raw_input('Please enter the latitude at the lower edge of the domain:\n> '))
        params['latMax'] = float(raw_input('Please enter the latitude at the upper edge of the domain:\n> '))
        dLon = float(raw_input('Please enter the longitude spacing (in degrees) e.g. 0.5:\n> '))
        dLat = float(raw_input('Please enter the latitude spacing (in degrees) e.g. 0.5:\n> '))

  
    # Section 6: Select Temporal Regridding Options, e.g. average daily data to monthly.

    print 'Temporal regridding options: i.e. averaging from daily data -> monthly data'
    print 'The time averaging will be performed on both model and observational data.'
    print '[0] Calculate time mean for full period.'
    print '[1] Calculate annual means'
    print '[2] Calculate monthly means'
    print '[3] Calculate daily means (from sub-daily data)'

    try:
        options['timeRegrid'] = int(raw_input('Please make a selection from above:\n> '))
    except:
        options['timeRegrid'] = int(raw_input('There was a problem with your selection, please try again:\n> '))
    
    if options['timeRegrid'] > 3:
        try:
            options['timeRegrid'] = int(raw_input('That was not an option, please make a selection from above:\n> '))
        except:
            options['timeRegrid'] = int(raw_input('There was a problem with your selection, please try again:\n> '))
    
    if options['timeRegrid'] == 0:
        options['timeRegrid'] = 'full'
    
    if options['timeRegrid'] == 1:
        options['timeRegrid'] = 'annual'
    
    if options['timeRegrid'] == 2:
        options['timeRegrid'] = 'monthly'
    
    if options['timeRegrid'] == 3:
        options['timeRegrid'] = 'daily'

    # Section 7: Select whether to perform Area-Averaging over masked region

    options['mask'] = False
    mask['lonMin'] = 0
    mask['lonMax'] = 0
    mask['latMin'] = 0
    mask['latMax'] = 0

    choice = raw_input('Do you want to calculate area averages over a masked region of interest? [y/n]\n> ').lower()
    if choice == 'y':
        options['mask'] = True
        print '[0] Load spatial mask from file.'
        print '[1] Enter regular lat/lon box to use as mask.'
    
        try:
            maskInputChoice = int(raw_input('Please make a selection from above:\n> '))
        except:
            maskInputChoice = int(raw_input('There was a problem with your selection, please try again:\n> '))
    
        if maskInputChoice > 1:
            try:
                maskInputChoice = int(raw_input('That was not an option, please make a selection from above:\n> '))
            except:
                maskInputChoice = int(raw_input('There was a problem with your selection, please try again:\n> '))
    
        # Section 7a
        # Read mask from file
        if maskInputChoice == 0:
            maskFile = raw_input('Please enter the file containing the mask data (including full path):\n> ')
            maskFileVar = raw_input('Please enter variable name of the mask data in the file:\n> ')


        # Section 7b
        # User enters mask region manually
        if maskInputChoice == 1:
            mask['lonMin'] = float(raw_input('Please enter the longitude at the left edge of the mask region:\n> '))
            mask['lonMax'] = float(raw_input('Please enter the longitude at the right edge of the mask region:\n> '))
            mask['latMin'] = float(raw_input('Please enter the latitude at the lower edge of the mask region:\n> '))
            mask['latMax'] = float(raw_input('Please enter the latitude at the upper edge of the mask region:\n> '))

    # Section 8: Select whether to calculate seasonal cycle composites

    options['seasonalCycle'] = raw_input('Seasonal Cycle: do you want to composite the data to show seasonal cycles? [y/n]\n> ').lower()
    if options['seasonalCycle'] == 'y':
        options['seasonalCycle'] = True
    else:
        options['seasonalCycle'] = False
  

    # Section 9: Select Peformance Metric

    print 'Metric options'
    print '[0] Bias: mean bias across full time range'
    print '[1] Mean Absolute Error: across full time range'
    print '[2] Difference: calculated at each time unit'
    print '[3] Anomaly Correlation Timeseries> '
    print '[4] Pattern Correlation Timeseries> '
    print '[5] Probability Distribution Function similarity score'
    print '[6] RMS error'
    print '[7] Coefficient of Efficiency'
    print '[8] Standard deviation'  
    print '[9] new Anomaly Correlation'  
    choice = int(raw_input('Please make a selection from the options above\n> '))
    if choice == 0:
        options['metric'] = 'bias'
    if choice == 1:
        options['metric'] = 'mae'
    if choice == 2:
        options['metric'] = 'difference'
    if choice == 3:
        options['metric'] = 'acc'
    if choice == 4:
        options['metric'] = 'patcor'
    if choice == 5:
        options['metric'] = 'pdf'
    if choice == 6:
        options['metric'] = 'rms'
    if choice == 7:
        options['metric'] = 'coe'
    if choice == 8:
        options['metric'] = 'stddev'
    if choice == 9:
        options['metric'] = 'nacc'

    # Section 11: Select Plot Options

    modifyPlotOptions = raw_input('Do you want to modify the default plot options? [y/n]\n> ').lower()
    
    options['plotTitle'] = 'default'
    options['plotFilename'] = 'default'
    
    if modifyPlotOptions == 'y':
        options['plotTitle'] = raw_input('Please enter the plot title:\n> ')
        options['plotFilename'] = raw_input('Please enter the filename stub to use, without suffix e.g. files will be named <YOUR CHOICE>.png\n> ')
    
    # Section 13: Run RCMET, passing in all of the user options

    print 'Running RCMET....'
    
    doProcess.do_rcmes( settings, params, model, mask, options )



# Actually call the UI function.
if __name__ == "__main__":
    rcmetUI()

