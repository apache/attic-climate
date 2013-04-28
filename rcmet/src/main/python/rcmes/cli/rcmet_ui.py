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
sys.path.append(os.path.abspath('../.'))

# RCMES Imports
import storage.files as files
import storage.rcmed as db
import toolkit.process as process
import cli.do_rcmes_processing_sub as doProcess


# Empty dictionaries to collect all of the user's inputs 
OPTIONS = {}
MASK = {}
MODEL = {}
PARAMS = {}
SETTINGS = {}

def rcmetUI():
    """"
    Command Line User interface for RCMET.
    Collects user OPTIONS then runs RCMET to perform processing.
    
    Duplicates job of GUI.
    
    Peter Lean   March 2011
    
    """
    print 'Regional Climate Model Evaluation System BETA'
    print "Querying RCMED for available parameters..."

    try:
        parameters = db.getParams()
    except Exception:
        sys.exit()

    # Section 0: Collect directories to store RCMET working files.
    SETTINGS['workDir'] = raw_input('Please enter workdir:\n> ')   # This is where the images are created/stored
    SETTINGS['cacheDir'] = raw_input('Please enter cachedir:\n> ') # This is where the database cache files are stored
    
    # Section 1a: Enter model file/s
    inputFileList = raw_input('Please enter model file (or specify multiple files using wildcard):\n> ')
    SETTINGS['fileList'] = glob.glob(inputFileList)
    
    # Section 1b (i): 
    #     Attempt to auto-detect latitude and longitude variable names
    #     and lat, lon limits from first file in SETTINGS['fileList'] 
    autoDetectLatLon, MODEL['latVariable'], MODEL['lonVariable'], PARAMS['latMin'], PARAMS['latMax'], PARAMS['lonMin'], PARAMS['lonMax'], variableNameList = files.find_latlon_var_from_file(SETTINGS['fileList'])
    
    # Section 1b (ii)
    #     If unable to auto-detect latitude and longitude variables from file,
    #     then ask user to select from which variable corresponds to latitude and
    #     which corresponds to longitude (from a list of available variables in the file).  
    if autoDetectLatLon == 0:
        print 'Could not find latitude and longitude data in the file. \n'
        
        printVariableList(variableNameList)
        userVarChoice = raw_input('Please help, by selecting which of the above variables in the file is the latitude variable:\n (or if the latitudes and longitudes are stored in a separate file enter "z")\n> ').lower()

        if userVarChoice == 'z':
            latLonFilename = raw_input('Please enter the full path of the file containing the latitudes and longitudes:\n> ')
            latLonFileList = glob.glob(latLonFilename)
            autoDetectLatLon, MODEL['latVariable'], MODEL['lonVariable'], PARAMS['latMin'], PARAMS['latMax'], PARAMS['lonMin'], PARAMS['lonMax'], variableNameList = files.find_latlon_var_from_file(latLonFileList)

        # Section 1b (iii)
        if userVarChoice != 'z':
            try:
                MODEL['latVariable'] = variableNameList[int(userVarChoice)]
            except (IndexError, TypeError):
                MODEL['latVariable'] = variableNameList[int(raw_input('Are you sure? The previous selection did not work, please try again:\n> '))]

            try:
                MODEL['lonVariable'] = variableNameList[int(raw_input('..and which of the above variables is the longitude variable?\n> '))]
            except (IndexError, TypeError):
                MODEL['lonVariable'] = variableNameList[int(raw_input('Are you sure? The previous selection did not work, please try again:\n> '))]

        # Find lat/lon ranges by loading the data using the user supplied variable names
        PARAMS['latMin'], PARAMS['latMax'], PARAMS['lonMin'], PARAMS['lonMax'] = files.find_latlon_ranges(SETTINGS['fileList'], 
                                                                                                          MODEL['latVariable'], 
                                                                                                          MODEL['lonVariable']) 


    print 'Found latitude and longitude variables in model data files: '
    print 'Lat/Lon variable names : ', MODEL['latVariable'], MODEL['lonVariable']
    print 'Minimum Latitude: ', PARAMS['latMin']
    print 'Maximum Latitude: ', PARAMS['latMax']
    print 'Minimum Longitude: ', PARAMS['lonMin']
    print 'Maximum Longitude: ', PARAMS['lonMax']
    
    # Section 1c (i) Attempt to auto-detect the time variable in the file.
    #     NB. name of time variable needs to passed into RCMET.
    autoDetectTime, MODEL['timeVariable'], variableNameList = files.find_time_var_name_from_file(SETTINGS['fileList'])

    print 'Found time variable name :', MODEL['timeVariable']
    if autoDetectTime == 0:
        print 'Could not find time data in the file.'
        printVariableList(variableNameList)

        try:
            MODEL['timeVariable'] = variableNameList[int(raw_input('Please help, by selecting which of the above variables in the file is the time variable:\n> '))]
        except (IndexError, TypeError):
            MODEL['timeVariable'] = variableNameList[int(raw_input('There was a problem with your selection, please try again:\n> '))]

    # Section 1c (ii): Attempt to decode model times into a python datetime object.
    try:
        modelTimes = process.decode_model_times(SETTINGS['fileList'], MODEL['timeVariable'])
        modelStartTime = min(modelTimes)
        modelEndTime = max(modelTimes)

        print 'Model times decoded:'
        print 'First model time : ', modelStartTime.strftime("%Y/%m/%d %H:%M")
        print 'Last model time : ',  modelEndTime.strftime("%Y/%m/%d %H:%M")
    except:
        print 'Error: there was a problem decoding the model times.'

  
    # Section 2a: Select which model variable to use for evaluation (from list of variables in file)
    printVariableList(variableNameList)

    userVarChoice = raw_input('Which variable would you like to evaluate?\n> ')
    try:
        MODEL['varName'] = variableNameList[int(userVarChoice)]
    except:
        userVarChoice = raw_input('There was a problem with that selection, please try again:\n> ')    
        MODEL['varName'] = variableNameList[int(userVarChoice)]

  
    # Ask user if the above variable is precipitation data 
    # (as this needs some special treatment by RCMET, e.g. color tables, unit conversion etc)

    OPTIONS['precip'] = False
    precipChoice = raw_input('Is this precipitation data? [y/n]\n> ').lower()
    if precipChoice == 'y':
        OPTIONS['precip'] = True

  
    # Section 3a: Select observation dataset from database
  
    # dbDatasets = ['TRMM','ERA-Interim','AIRS','MODIS','URD','CRU']
    # replace with list comprehension
    # dbDatasets = [parameter['longname'] for parameter in parameters]
  
  
    # datasetIds = [3,1,2,5,4,6]
    # dbDatasetStartTimes = [datetime.datetime(1998,1,1,0,0,0,0),datetime.datetime(1989,01,01,0,0,0,0),datetime.datetime(2002,8,31,0,0,0,0),datetime.datetime(2000,2,24,0,0,0,0),datetime.datetime(1948,1,1,0,0,0,0),datetime.datetime(1901,1,1,0,0,0,0)]
    # dbDatasetEndTimes = [datetime.datetime(2010,1,1,0,0,0,0),datetime.datetime(2009,12,31,0,0,0,0),datetime.datetime(2010,1,1,0,0,0,0),datetime.datetime(2010,5,30,0,0,0,0),datetime.datetime(2010,1,1,0,0,0,0),datetime.datetime(2006,12,1,0,0,0,0)]

    dbParameters = [['daily precip', 'monthly precip'], ['2m temp', '2m dew point'], ['2m temp'], ['cloud fraction'], ['precip'], ['tavg', 'tmax', 'tmin', 'precip']]

    # dbParameterIds = [[14,36],[12,13],[15],[31],[30],[33,34,35,32]]
    # dbParameterIds = [parameter['parameterId'] for parameter in parameters]

    # Not sure this is needed anymore since we have a parameters list object to work with
    # datasetIds = [parameter['datasetId'] for parameter in parameters]
  
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

    for parameter in parameters:
        """( 38 ) - CRU3.1 Daily-Mean Temperature : monthly"""
        print "({:^2}) - {:<35} :: {:<10}".format(parameter['parameter_id'], parameter['longname'], parameter['timestep'])

    try:
        datasetChoice = int(raw_input('Please select which observational dataset you wish to compare against:\n> ')) 
        selection = next((p for p in parameters if p['parameter_id'] == datasetChoice), None)
        PARAMS['obsDatasetId'] = selection['dataset_id']
        obsStartTime = datetime.datetime.strptime(selection['start_date'], "%Y-%m-%d")
        obsEndTime = datetime.datetime.strptime(selection['end_date'], "%Y-%m-%d")
        PARAMS['obsParamId'] = selection['parameter_id']
    
    except:
        datasetChoice = raw_input('There was a problem with your selection, please try again:\n> ') 
        selection = next((p for p in parameters if p['parameter_id'] == datasetChoice), None)
        PARAMS['obsDatasetId'] = selection['dataset_id']
        obsStartTime = datetime.datetime.strptime(selection['start_date'], "%Y-%m-%d")
        obsEndTime = datetime.datetime.strptime(selection['end_date'], "%Y-%m-%d")
        PARAMS['obsParamId'] = selection['parameter_id']

    # Section 4: Select time range to evaluate (defaults to overlapping times between model and obs)
    
    # Calculate overlap
    PARAMS['startTime'] = max(modelStartTime, obsStartTime)
    PARAMS['endTime'] = min(modelEndTime, obsEndTime)
    
    print 'Model time range: ', modelStartTime.strftime("%Y/%m/%d %H:%M"), modelEndTime.strftime("%Y/%m/%d %H:%M")
    print 'Obs time range: ', obsStartTime.strftime("%Y/%m/%d %H:%M"), obsEndTime.strftime("%Y/%m/%d %H:%M")
    print 'Overlapping time range: ', PARAMS['startTime'].strftime("%Y/%m/%d %H:%M"), PARAMS['endTime'].strftime("%Y/%m/%d %H:%M")
    
    # If want sub-selection then enter start and end times manually
    choice = raw_input('Do you want to only evaluate data from a sub-selection of this time range? [y/n]\n> ').lower()
    if choice == 'y':
        startTimeString = raw_input('Please enter the start time in the format YYYYMMDDHHmm:\n> ')
        try:
            PARAMS['startTime'] = datetime.datetime(*time.strptime(startTimeString, "%Y%m%d%H%M")[:6])
        except:
            print 'There was a problem with your entry'

    endTimeString = raw_input('Please enter the end time in the format YYYYMMDDHHmm:\n> ')
    try:
        PARAMS['endTime'] = datetime.datetime(*time.strptime(endTimeString, "%Y%m%d%H%M")[:6])
    except:
        print 'There was a problem with your entry'
    
    print 'Selected time range: ', PARAMS['startTime'].strftime("%Y/%m/%d %H:%M"), PARAMS['endTime'].strftime("%Y/%m/%d %H:%M")
  
  
  # Section 5: Select Spatial Regridding OPTIONS
  
    print 'Spatial regridding OPTIONS: '
    print '[0] Use Observational grid'
    print '[1] Use Model grid'
    print '[2] Define new regular lat/lon grid to use'
    try:
        OPTIONS['regrid'] = int(raw_input('Please make a selection from above:\n> '))
    except:
        OPTIONS['regrid'] = int(raw_input('There was a problem with your selection, please try again:\n> '))
    
    if OPTIONS['regrid'] > 2:
        try:
            OPTIONS['regrid'] = int(raw_input('That was not an option, please make a selection from the list above:\n> '))
        except:
            OPTIONS['regrid'] = int(raw_input('There was a problem with your selection, please try again:\n> '))
    
    if OPTIONS['regrid'] == 0:
        OPTIONS['regrid'] = 'obs'
    
    if OPTIONS['regrid'] == 1:
        OPTIONS['regrid'] = 'model'
    
    # If requested, get new grid parameters
    if OPTIONS['regrid'] == 2:
        OPTIONS['regrid'] = 'regular'
        PARAMS['lonMin'] = float(raw_input('Please enter the longitude at the left edge of the domain:\n> '))
        PARAMS['lonMax'] = float(raw_input('Please enter the longitude at the right edge of the domain:\n> '))
        PARAMS['latMin'] = float(raw_input('Please enter the latitude at the lower edge of the domain:\n> '))
        PARAMS['latMax'] = float(raw_input('Please enter the latitude at the upper edge of the domain:\n> '))
        dLon = float(raw_input('Please enter the longitude spacing (in degrees) e.g. 0.5:\n> '))
        dLat = float(raw_input('Please enter the latitude spacing (in degrees) e.g. 0.5:\n> '))

  
    # Section 6: Select Temporal Regridding OPTIONS, e.g. average daily data to monthly.

    print 'Temporal regridding OPTIONS: i.e. averaging from daily data -> monthly data'
    print 'The time averaging will be performed on both model and observational data.'
    print '[0] Calculate time mean for full period.'
    print '[1] Calculate annual means'
    print '[2] Calculate monthly means'
    print '[3] Calculate daily means (from sub-daily data)'

    try:
        OPTIONS['timeRegrid'] = int(raw_input('Please make a selection from above:\n> '))
    except:
        OPTIONS['timeRegrid'] = int(raw_input('There was a problem with your selection, please try again:\n> '))
    
    if OPTIONS['timeRegrid'] > 3:
        try:
            OPTIONS['timeRegrid'] = int(raw_input('That was not an option, please make a selection from above:\n> '))
        except:
            OPTIONS['timeRegrid'] = int(raw_input('There was a problem with your selection, please try again:\n> '))
    
    if OPTIONS['timeRegrid'] == 0:
        OPTIONS['timeRegrid'] = 'full'
    
    if OPTIONS['timeRegrid'] == 1:
        OPTIONS['timeRegrid'] = 'annual'
    
    if OPTIONS['timeRegrid'] == 2:
        OPTIONS['timeRegrid'] = 'monthly'
    
    if OPTIONS['timeRegrid'] == 3:
        OPTIONS['timeRegrid'] = 'daily'

    # Section 7: Select whether to perform Area-Averaging over masked region

    OPTIONS['mask'] = False
    MASK['lonMin'] = 0
    MASK['lonMax'] = 0
    MASK['latMin'] = 0
    MASK['latMax'] = 0

    choice = raw_input('Do you want to calculate area averages over a masked region of interest? [y/n]\n> ').lower()
    if choice == 'y':
        OPTIONS['mask'] = True
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
            MASK['lonMin'] = float(raw_input('Please enter the longitude at the left edge of the mask region:\n> '))
            MASK['lonMax'] = float(raw_input('Please enter the longitude at the right edge of the mask region:\n> '))
            MASK['latMin'] = float(raw_input('Please enter the latitude at the lower edge of the mask region:\n> '))
            MASK['latMax'] = float(raw_input('Please enter the latitude at the upper edge of the mask region:\n> '))

    # Section 8: Select whether to calculate seasonal cycle composites

    OPTIONS['seasonalCycle'] = raw_input('Seasonal Cycle: do you want to composite the data to show seasonal cycles? [y/n]\n> ').lower()
    if OPTIONS['seasonalCycle'] == 'y':
        OPTIONS['seasonalCycle'] = True
    else:
        OPTIONS['seasonalCycle'] = False
  

    # Section 9: Select Performance Metric
    OPTIONS['metric'] = getMetricFromUserInput()

    # Section 11: Select Plot OPTIONS

    modifyPlotOPTIONS = raw_input('Do you want to modify the default plot OPTIONS? [y/n]\n> ').lower()
    
    OPTIONS['plotTitle'] = 'default'
    OPTIONS['plotFilename'] = 'default'
    
    if modifyPlotOPTIONS == 'y':
        OPTIONS['plotTitle'] = raw_input('Please enter the plot title:\n> ')
        OPTIONS['plotFilename'] = raw_input('Please enter the filename stub to use, without suffix e.g. files will be named <YOUR CHOICE>.png\n> ')
    
    # Section 13: Run RCMET, passing in all of the user OPTIONS

    print 'Running RCMET....'
    
    doProcess.do_rcmes( SETTINGS, PARAMS, MODEL, MASK, OPTIONS )

def printVariableList(variableNames):
    """Private function that will print a list of selections using a zero based
    counter.  Typically used to gather user selections"""
    i = 0
    for variable in variableNames:
        print '[', i, ']', variable
        i += 1

def getMetricFromUserInput():
    """Collection of different Metrics that a user can run against datasets
    they have previously selected.  
    
    TODO: Refactor this into the metrics module so the list is not maintained
    here.
    """
    print 'Metric OPTIONS'
    print '[0] Bias: mean bias across full time range'
    print '[1] Mean Absolute Error: across full time range'
    print '[2] Difference: calculated at each time unit'
    print '[3] Pattern Correlation Timeseries> '
    print '[4] Probability Distribution Function similarity score'
    print '[5] RMS error'
    print '[6] Coefficient of Efficiency'
    print '[7] Standard deviation'  
    print '[8] new Anomaly Correlation'  
    choice = int(raw_input('Please make a selection from the OPTIONS above\n> '))
    if choice == 0:
         return 'bias'
    if choice == 1:
        return 'mae'
    if choice == 2:
        return 'difference'
    if choice == 3:
        return 'patcor'
    if choice == 4:
        return 'pdf'
    if choice == 5:
        return 'rms'
    if choice == 6:
        return 'coe'
    if choice == 7:
        return 'stddev'
    if choice == 8:
        return 'nacc'


# Actually call the UI function.
if __name__ == "__main__":
    rcmetUI()

