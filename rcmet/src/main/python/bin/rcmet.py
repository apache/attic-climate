#!/usr/local/bin/python
""" DOCSTRING"""

# Python Standard Lib Imports
import argparse
import ConfigParser
import datetime
import glob
import os
import sys


# RCMES Imports
import storage.rcmed as db
from toolkit import do_data_prep, process, metrics
from utils import misc
from classes import JobProperties, Model, GridBox
from cli import rcmet_ui as ui

parser = argparse.ArgumentParser(description='Regional Climate Model Evaluation Toolkit.  Use -h for help and options')
parser.add_argument('-c', '--config', dest='CONFIG', help='Path to an evaluation configuration file')
args = parser.parse_args()

def checkConfigSettings(config):
    """ This function will check the SETTINGS block of the user supplied config file.
    This will only check if the working and cache dirs are writable from this program.
    Additional configuration parameters can be checked here later on.
    
    Input::
        config - ConfigParser configuration object
    
    Output::
        none - An exception will be raised if something goes wrong
    """
    settings = config.items('SETTINGS')
    for key_val in settings:
        # Check the user provided directories are valid
        if key_val[0] == 'workDir' or key_val[0] == 'cacheDir':
            _ =  misc.isDirGood(os.path.abspath(key_val[1]))

        else:
            pass    

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
            modelFileList.sort()

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
        JobProperties - JobProperties Object
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
            configData[entry[0]] = entry[1:]

    return configData

def tempGetYears():
    startYear = int(raw_input('Enter start year YYYY \n'))
    endYear = int(raw_input('Enter end year YYYY \n'))
    # CGOODALE - Updating the Static endTime to be 31-DEC
    startTime = datetime.datetime(startYear, 1, 1, 0, 0)
    endTime = datetime.datetime(endYear, 12, 31, 0, 0)
    return (startTime, endTime)


def runUsingConfig(argsConfig):
    """
    This function is called when a user provides a configuration file to specify an evaluation job.

    Input::
        argsConfig - Path to a ConfigParser compliant file

    Output::
        Plots that visualize the evaluation job. These will be output to SETTINGS.workDir from the config file
    """
    
    print 'Running using config file: %s' % argsConfig
    # Parse the Config file
    userConfig = ConfigParser.SafeConfigParser()
    userConfig.optionxform = str # This is so the case is preserved on the items in the config file
    userConfig.read(argsConfig)

    try:
        checkConfigSettings(userConfig)
    except:
        raise

    jobProperties = generateSettings(userConfig.items('SETTINGS'))
    workdir = jobProperties.workDir
    
    try:
        gridBox = GridBox(jobProperties.latMin, jobProperties.lonMin, jobProperties.latMax,
                          jobProperties.lonMax, jobProperties.gridLonStep, jobProperties.gridLatStep)
    except:
        gridBox = None

    models = generateModels(userConfig.items('MODEL'))
    
    datasetDict = makeDatasetsDictionary(userConfig.items('RCMED'))


    # Go get the parameter listing from the database
    try:
        params = db.getParams()
    except:
        raise

    obsDatasetList = []
    for param_id in datasetDict['obsParamId']:
        for param in params:
            if param['parameter_id'] == int(param_id):
                obsDatasetList.append(param)
            else:
                pass

    #TODO: Unhardcode this when we decided where this belongs in the Config File
    jobProperties.maskOption = True

    numOBS, numMDL, nT, ngrdY, ngrdX, Times, lons, lats, obsData, mdlData, obsList, mdlName = do_data_prep.prep_data(jobProperties, obsDatasetList, gridBox, models)

    print 'Input and regridding of both obs and model data are completed. now move to metrics calculations'
    
    try:
        subRegionConfig = misc.configToDict(userConfig.items('SUB_REGION'))
        subRegions = misc.parseSubRegions(subRegionConfig)
        # REORDER SUBREGION OBJECTS until we standardize on Python 2.7
        # TODO Remove once Python 2.7 support is finalized
        if subRegions:
            subRegions.sort(key=lambda x:x.name)
        
    except ConfigParser.NoSectionError:
        
        counts = {'observations': numOBS,
                  'models'      : numMDL,
                  'times'       : nT}
        subRegions = misc.getSubRegionsInteractively(counts, workdir)
        
        if len(subRegions) == 0:
            print 'Processing without SubRegion support'
        

    # TODO: New function Call
    fileOutputOption = jobProperties.writeOutFile
    modelVarName = models[0].varName
    metrics.metrics_plots(modelVarName, numOBS, numMDL, nT, ngrdY, ngrdX, Times, lons, lats, obsData, mdlData, obsList, mdlName, workdir, subRegions, fileOutputOption)


if __name__ == "__main__":
    
    if args.CONFIG:
        
        runUsingConfig(args.CONFIG)

    else:
        print 'Interactive mode has been enabled'
        ui.rcmetUI()

    #rcmet_cordexAF()
