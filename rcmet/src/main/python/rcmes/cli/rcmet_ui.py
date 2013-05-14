#!/usr/local/bin/python
""" 
    Step by Step Wizard that demonstrates how the underlying RCMES code can
    be used to generate climate dataset intercomparisons
"""
# Imports
# Native Python Module Imports
import datetime
import time
import sys

# RCMES Imports
import cli.do_rcmes_processing_sub as doProcess
#import storage.files as files
import storage.rcmed as rcmed
import toolkit.do_data_prep
from utils import misc
from classes import Model, JobProperties


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
    """
    print 'Regional Climate Model Evaluation System BETA'
    print "Querying RCMED for available parameters..."

    try:
        parameters = rcmed.getParams()
    except Exception:
        raise
        sys.exit()

    # Section 0: Collect directories to store RCMET working files.
    misc.getDirSettings(SETTINGS)
    # collect temporal step and spatial settings
    misc.getTemporalGrid(SETTINGS)
    SETTINGS['spatialGrid'] = misc.getSpatialGrid()
    # Section 1a: Enter model file/s
    modelFiles = misc.getModelFiles()

    # Create a list of model objects for use later
    models = [Model(modelFile) for modelFile in modelFiles]

    # Section 3b: Select 1 Parameter from list
    for parameter in parameters:
        """( 38 ) - CRU3.1 Daily-Mean Temperature : monthly"""
        print "({:^2}) - {:<54} :: {:<10}".format(parameter['parameter_id'], parameter['longname'], parameter['timestep'])

    obsDatasetList = []
    validParamIds = [int(p['parameter_id']) for p in parameters]
    while obsDatasetList == []:
        print("Please select the available observation you would like to use from the list above:")
        userChoice = int(raw_input(">>>"))
        if userChoice in validParamIds:
            for param in parameters:
                if param['parameter_id'] == userChoice:
                    obsDatasetList.append(param)
                else:
                    pass
        else:
            print("Your selection '%s' is invalid.  Please make another selection." % userChoice)


"""



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

"""

#def printVariableList(variableNames):
#    """Private function that will print a list of selections using a zero based
#    counter.  Typically used to gather user selections"""
#    i = 0
#    for variable in variableNames:
#        print '[', i, ']', variable
#        i += 1

#    """ BLOCK TAKEN FROM THE NON-GUI rcmet.py """
        # Go get the parameter listing from the database
#    try:
#        params = rcmed.getParams()
#    except:
#        raise

#    obsDatasetList = []
#    for param_id in datasetDict['obsParamId']:
#        for param in params:
#            if param['parameter_id'] == int(param_id):
#                obsDatasetList.append(param)
#            else:
#                pass

    #TODO: Unhardcode this when we decided where this belongs in the Config File
#    jobProperties.maskOption = True
#
#    numOBS, numMDL, nT, ngrdY, ngrdX, Times, lons, lats, obsData, mdlData, obsList, mdlName = toolkit.do_data_prep.prep_data(jobProperties, obsDatasetList, gridBox, models)
#
#    print 'Input and regridding of both obs and model data are completed. now move to metrics calculations'
#    
#    try:
#        subRegionConfig = misc.configToDict(userConfig.items('SUB_REGION'))
#        subRegions = misc.parseSubRegions(subRegionConfig)
#        # REORDER SUBREGION OBJECTS until we standardize on Python 2.7
#        # TODO Remove once Python 2.7 support is finalized
#        if subRegions:
#            subRegions.sort(key=lambda x:x.name)
#        
#    except ConfigParser.NoSectionError:
#        
#        counts = {'observations': numOBS,
#                  'models'      : numMDL,
#                  'times'       : nT}
#        subRegions = misc.getSubRegionsInteractively(counts, workdir)
#        
#        if len(subRegions) == 0:
#            print 'Processing without SubRegion support'
#        
#
#    # TODO: New function Call
#    fileOutputOption = jobProperties.writeOutFile
#    modelVarName = models[0].varName
#    metrics.metrics_plots(modelVarName, numOBS, numMDL, nT, ngrdY, ngrdX, Times, lons, lats, obsData, mdlData, obsList, mdlName, workdir, subRegions, fileOutputOption)
#
""" END OF BLOCK """





# Actually call the UI function.
if __name__ == "__main__":
    rcmetUI()

