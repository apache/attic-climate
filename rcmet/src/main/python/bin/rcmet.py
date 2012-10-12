#!/usr/local/bin/python

# Python Standard Lib Imports
import argparse
import ConfigParser
import datetime
import glob
import os
import sys
import json

# RCMES Imports
import storage.rcmed as db
import toolkit.do_data_prep_20
import toolkit.do_metrics_20
import toolkit.process as process

from classes import JobProperties, Model, GridBox, SubRegion

parser = argparse.ArgumentParser(description='Regional Climate Model Evaluation Toolkit.  Use -h for help and options')
parser.add_argument('-c', '--config', dest='CONFIG', help='Path to an evaluation configuration file')
args = parser.parse_args()


def getSettings(settings):
    """
    This function will collect 2 parameters from the user about the RCMET run they have started.
    
    Input::
        settings - Empty Python Dictionary they will be used to store the user supplied inputs
        
    Output::
        None - The user inputs will be added to the supplied dictionary.
    """
    settings['workDir'] = os.path.abspath(raw_input('Please enter workDir:\n> '))
    if os.path.isdir(settings['workDir']):
        pass
    else:
        makeDirectory(settings['workDir'])
    
    settings['cacheDir'] = os.path.abspath(raw_input('Please enter cacheDir:\n> '))
    if os.path.isdir(settings['cacheDir']):
        pass
    else:
        makeDirectory(settings['cacheDir'])    

def setSettings(settings, config):
    """
    This function is used to set the values within the 'SETTINGS' dictionary when a user provides an external
    configuration file.
    
    Input::
        settings - Python Dictionary object that will collect the key : value pairs
        config - A configparse object that contains the external config values
    
    Output::
        None - The settings dictionary will be updated in place.
    """
    pass

def makeDirectory(directory):
    print "%s doesn't exist.  Trying to create it now." % directory
    try:
        os.mkdir(directory)
    except OSError:
        print "This program cannot create dir: %s due to permission issues." % directory
        sys.exit()

def generateModels(modelConfig):
    """
    This function will return a list of Model objects that can easily be used for 
    metric computation and other processing tasks.
    
    Input::  
        modelConfig - list of ('key', 'value') tuples.  Below is a list of valid keys
            filenamepattern - string i.e. '/nas/run/model/output/MOD*precip*.nc'
            latvariable - string i.e. 'latitude'
            lonvariable - string i.e. 'longitude'
            timevariable - string i.e. 't'
            timestep - string 'monthly' | 'daily' | 'annual'
            varname - string i.e. 'pr'

    Output::
        modelList - List of Model objects
    """
    # Setup the config Data Dictionary to make parsing easier later
    configData = {}
    for entry in modelConfig:
        configData[entry[0]] = entry[1]

    modelFileList = None
    for keyValTuple in modelConfig:
        if keyValTuple[0] == 'filenamePattern':
            modelFileList = glob.glob(keyValTuple[1])
    
    # Remove the filenamePattern from the dict since it is no longer used
    configData.pop('filenamePattern')
    
    models = []
    for modelFile in modelFileList:
        # use getModelTimes(modelFile,timeVarName) to generate the modelTimeStep and time list
        _ , configData['timeStep'] = process.getModelTimes(modelFile, configData['timeVariable'])
        configData['filename'] = modelFile
        model = Model(**configData)
        models.append(model)
    
    return models

def generateSettings(config):
    """
    Helper function to decouple the argument parsing from the Settings object creation
    
    Input::  
        config - list of ('key', 'value') tuples.
            workdir - string i.e. '/nas/run/rcmet/work/'
            cachedir - string i.e. '/tmp/rcmet/cache/'
    Output::
        settings - Settings Object
    """
    # Setup the config Data Dictionary to make parsing easier later
    configData = {}
    for entry in config:
        configData[entry[0]] = entry[1]
        
    return JobProperties(**configData)

def makeDatasetsDictionary(rcmedConfig):
    """
    Helper function to decouple the argument parsing from the RCMEDDataset object creation

    Input::  
        rcmedConfig - list of ('key', 'value') tuples.
            obsDatasetId=3,10
            obsParamId=36,32
            obsTimeStep=monthly,monthly

    Output::
        datasetDict - Dictionary with dataset metadata
    # Setup the config Data Dictionary to make parsing easier later
    """
    delimiter = ','
    configData = {}
    for entry in rcmedConfig:
        if delimiter in entry[1]:
            # print 'delim found - %s' % entry[1]
            valueList = entry[1].split(delimiter)
            configData[entry[0]] = valueList
        else:
            configData[entry[0]] = entry[1]

    return configData

def tempGetYears():
    startYear = int(raw_input('Enter start year YYYY \n'))
    endYear = int(raw_input('Enter end year YYYY \n'))
    # CGOODALE - Updating the Static endTime to be 31-DEC
    startTime = datetime.datetime(startYear, 1, 1, 0, 0)
    endTime = datetime.datetime(endYear, 12, 31, 0, 0)
    return (startTime, endTime)

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
    if os.path.exists(regionsFile):
        regionsConfig = ConfigParser.SafeConfigParser()
        regionsConfig.optionxform = str
        regionsConfig.read(regionsFile)
        regions = regionsConfig.items('REGIONS')
        return regions
        
    else:
        raise IOError

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
        subRegion = SubRegion(name, latMin, lonMin, latMax, lonMax)
        subRegions.append(subRegion)
    return subRegions

if __name__ == "__main__":
    
    if args.CONFIG:
        print 'Running using config file: %s' % args.CONFIG
        # Parse the Config file
        userConfig = ConfigParser.SafeConfigParser()
        userConfig.optionxform = str # This is so the case is preserved on the items in the config file
        userConfig.read(args.CONFIG)
        jobProperties = generateSettings(userConfig.items('SETTINGS'))
        models = generateModels(userConfig.items('MODEL'))
        datasetDict = makeDatasetsDictionary(userConfig.items('RCMED'))
        
        #TODO: Unhardcode this when we decided where this belongs in the Config File
        jobProperties.maskOption = True
        
        regions = {}
        try:
            subRegions = configToDict(userConfig.items('SUB_REGION'))
            
            if subRegions['subRegionFile'] == '':
                print 'SubRegion File path is empty.  Check your configuration file, or comment out the SUB_REGION Section'
            else:
                regions = readSubRegionsFile(subRegions['subRegionFile'])
                
        except ConfigParser.NoSectionError:
            print "No SUB_REGION configuration found in %s" % args.CONFIG
        
        except IOError:
            print "Unable to open %s.  Running without SubRegions" % (subRegions['subRegionFile'], )

        subRegions = generateSubRegions(regions)


        #sys.exit()


        # Go get the parameter listing from the database
        try:
            params = db.getParams()
        except Exception:
            sys.exit()
        
        obsDatasetList = []
        for param_id in datasetDict['obsParamId']:
            for param in params:
                if param['parameter_id'] == int(param_id):
                    obsDatasetList.append(param)
                else:
                    pass

        gridBox = GridBox(jobProperties.latMin, jobProperties.lonMin, jobProperties.latMax, jobProperties.lonMax, jobProperties.gridLonStep, jobProperties.gridLatStep)


        #subRegionTuple = (numSubRgn, subRgnLon0, subRgnLon1, subRgnLat0, subRgnLat1, subRgnName)
        #rgnSelect = 3
               
        #for n in subRegions:
        #    print 'Subregion: ', n.name, n.lonMin, 'E - ', n.lonMax, ' E: ', n.latMin, 'N - ', n.latMax, 'N'


        
        metricOption = 'bias'
        plotTitle = models[0].varName + '_'
        plotFilenameStub = models[0].varName + '_'

        numOBS, numMDL, nT, ngrdY, ngrdX, Times, obsData, mdlData, obsRgn, mdlRgn, obsList, mdlList = toolkit.do_data_prep_20.prep_data(jobProperties, obsDatasetList, gridBox, models, subRegions)

        print 'Input and regridding of both obs and model data are completed. now move to metrics calculations'

        if jobProperties.maskOption:
            seasonalCycleOption = True
        
        # TODO:  This seems like we can just use numOBS to compute obsSelect (obsSelect = numbOBS -1)
        if numOBS == 1:
            obsSelect = 1
        else:
            #obsSelect = 1          #  1st obs (TRMM)
            #obsSelect = 2          # 2nd obs (CRU3.1)
            obsSelect = numOBS      # obs ensemble
    
        obsSelect = numOBS - 1   # convert to fit the indexing that starts from 0
    
    
    
        # TODO:  Undo the following code when refactoring later
        obsParameterId = [str(x['parameter_id']) for x in obsDatasetList]
        precipFlag = models[0].precipFlag

        mdlSelect = numMDL - 1                      # numMDL-1 corresponds to the model ensemble


        # TODO:  Really need to sort out the SubRegion Code  
        numSubRgn = len(subRegions)
        rgnSelect = 0
        subRgnName = [str(region.name) for region in subRegions]
        toolkit.do_metrics_20.metrics_plots(numOBS, numMDL, nT, ngrdY, ngrdX, Times, obsData, mdlData, obsRgn, mdlRgn, obsList, mdlList, \
                                  jobProperties.workDir, \
                                  mdlSelect, obsSelect, \
                                  numSubRgn, subRgnName, rgnSelect, \
                                  obsParameterId, precipFlag, jobProperties.temporalGrid, jobProperties.maskOption, seasonalCycleOption, metricOption, \
                                                                                               plotTitle, plotFilenameStub)
        

        
    else:
        print 'Interactive mode has been enabled'
        #getSettings(SETTINGS)
        print "But isn't implemented.  Try using the -c option instead"

    #rcmet_cordexAF()
