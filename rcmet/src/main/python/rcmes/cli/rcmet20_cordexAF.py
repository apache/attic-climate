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

# 0. Keep both Peter's original and modified libraries

# Python Standard Lib Imports
import argparse
import ConfigParser
import datetime
import glob
import os
import sys
import json

# 3rd Party Modules
import numpy as np
import numpy.ma as ma

# RCMES Imports
# Appending rcmes via relative path
#sys.path.append(os.path.abspath('../.'))
import storage.files_v12
import storage.rcmed as db
import toolkit.do_data_prep
import toolkit.do_metrics_20
import toolkit.process as process
from classes import Settings, Model, BoundingBox, SubRegion, GridBox

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

def rcmet_cordexAF():
    """
     Command Line User interface for RCMET.
     Collects user options then runs RCMET to perform processing.
     Duplicates job of GUI.
     Peter Lean   March 2011
     
     Jul 2, 2011
     Modified to process multiple models
     Follow the logical variable "GUI" for interactive operations
     
     July 6, 2012: Jinwon Kim
     * This version works with do_rcmes_processing_sub_v12cmip5multi.py *
     Re-gridded data output options include both binary and netCDF.
      Interpolation of both model and obs data onto a user-define grid system has been completed.
      Allow generic treatment of both multiple model and observation data
       * longitudes/latitudes are defined for individual datasets
       * the metadata for observations will utilized Cameron's updates
      Still works for the global observation coverage scheme (may involve missing/bad values)
     * this version requires that all obs data are to be defined at the same temporal grid (monthly, daily)
     * this version requires that all mdl data are to be defined at the same temporal grid (monthly, daily)
    """
    print 'Start RCMET'


    """  COMMENTED OUT UN-USED CODE
    # Specify GUI or nonGUI version [True/False]
    GUI = False
    user_input = int(raw_input('Enter interactive/specified run: [0/1]: \n> '))
    if user_input == 0:
        GUI = True

    # 1.   Prescribe the directories and variable names for processing
    #dir_rcmet = '/nas/share3-wf/jinwonki/rcmet'   # The path to the python script to process the cordex-AF data
    if GUI: 
        workdir = os.path.abspath(raw_input('Please enter workdir:\n> '))
        cachedir = os.path.abspath(raw_input('Please enter cachedir:\n> '))
        mdlDataDir = os.path.abspath(raw_input('Enter the model data directory (e.g., ~/data/cordex-af):\n> '))
        modelVarName = raw_input('Enter the model variable name from above:\n> ')     # Input model variable name
        modelLatVarName = raw_input('Enter the Latitude variable name:\n> ')     # Input model variable name
        modelLonVarName = raw_input('Enter the Longitude variable name:\n> ')     # Input model variable name
        modelTimeVarName = raw_input('Enter the Time variable name:\n> ')     # Input model variable name
        mdlTimeStep = raw_input('Enter the model Time step (e.g., daily, monthly):\n> ')     # Input model variable name
    else:
        modelVarName = 'pr'
        #modelVarName='tas'
        #modelVarName='tasmax'
        #modelVarName='tasmin'
        #modelVarName='clt'
        mdlTimeStep = 'monthly'
        modelLatVarName = 'lat'
        modelLonVarName = 'lon'
        modelTimeVarName = 'time' # mdl var names for lat, long, & time coords
        workdir = '../cases/cordex-af/wrk2'
        cachedir = '../cases/cordex-af/cache'
        mdlDataDir = '/nas/share4-cf/jinwonki/data/cordex-af'
    if modelVarName == 'pr':
        precipFlag = True
    else:
        precipFlag = False
    """
    # 2.   Metadata for the RCMED database
    
    # TODO:  WORK OUT THE RCMED PARAMETERS API USAGE - Prolly need to move this into a PARAMETERS Object
    """  COMMENTED OUT HARDCODED VALUES
    try:
        parameters = db.getParams()
    except Exception:
        sys.exit()
    
    datasets = [parameter['longname'] for parameter in parameters]
    
    #   NOTE: the list must be updated whenever a new dataset is added to RCMED (current as of 11/22/2011)
    db_datasets = ['TRMM', 'ERA-Interim', 'AIRS', 'MODIS', 'URD', 'CRU3.0', 'CRU3.1']
    db_dataset_ids = [3, 1, 2, 5, 4, 6, 10]
    db_dataset_startTimes = [datetime.datetime(1998, 1, 1, 0, 0, 0, 0), datetime.datetime(1989, 01, 01, 0, 0, 0, 0), datetime.datetime(2002, 8, 31, 0, 0, 0, 0), \
                             datetime.datetime(2000, 2, 24, 0, 0, 0, 0), datetime.datetime(1948, 1, 1, 0, 0, 0, 0), datetime.datetime(1901, 1, 1, 0, 0, 0, 0), \
                             datetime.datetime(1901, 1, 1, 0, 0, 0, 0)]
    db_dataset_endTimes = [datetime.datetime(2010, 1, 1, 0, 0, 0, 0), datetime.datetime(2009, 12, 31, 0, 0, 0, 0), datetime.datetime(2010, 1, 1, 0, 0, 0, 0), \
                           datetime.datetime(2010, 5, 30, 0, 0, 0, 0), datetime.datetime(2010, 1, 1, 0, 0, 0, 0), datetime.datetime(2006, 12, 1, 0, 0, 0, 0), \
                           datetime.datetime(2009, 12, 31, 0, 0, 0, 0)] #adjusted the last end_time to 31-DEC-2009 instead of 01-DEC-2009
    db_parameters = [['pr_day', 'pr_mon'], ['T2m', 'Tdew2m'], ['T2m'], ['cldFrac'], ['pr_day'], ['T2m', 'T2max', 'T2min', 'pr'], ['pr', 'T2m', 'T2max', 'T2min', 'cldFrac']]
    db_parameter_ids = [[14, 36], [12, 13], [15], [31], [30], [33, 34, 35, 32], [37, 38, 39, 41, 42]]
    
     # Assign the obs dataset & and its attributes from the RCNMED dataset/parameter list above
    idObsDat = []
    idObsDatPara = []
    obsTimeStep = []
    
    if GUI:
        for n in np.arange(len(db_datasets)):
            print n, db_datasets[n]

        numOBSs = int(raw_input('Enter the number of observed datasets to be utilized:\n> '))
        # assign the obs dataset id and the parameter id defined within the dataset into the lists "idObsDat" & "idObsDatPara".
        for m in np.arange(numOBSs):
            idObsDat.append(input=int(raw_input('Enter the observed dataset number from above:\n> ')))
            for l in np.arange(len(db_parameters[input])):
                print l, db_parameters[idObsDat][l]
        
            idObsDatPara.append(int(raw_input('Enter the observed data parameter from above:\n> ')))
    else:
        numOBSs = 2
        idObsDat = [0, 6]
        idObsDatPara = [1, 0]
        obsTimeStep = ['monthly', 'monthly']
        #numOBSs=1; idObsDat=[6]; idObsDatPara=[0]; obsTimeStep=['monthly']
        #numOBSs=1; idObsDat=[5]; idObsDatPara=[3]; obsTimeStep=['monthly']
        #numOBSs=1; idObsDat=[0]; idObsDatPara=[1]; obsTimeStep=['monthly']
        ##### Data table to be replace with the use of metadata #################################
        #idObsDat=0; idObsDatPara=0; obsTimeStep='monthly'                 # TRMM daily
        #idObsDat=0; idObsDatPara=1; obsTimeStep='monthly'                 # TRMM monthly
        #idObsDat=3; idObsDatPara=0; obsTimeStep='monthly'                 # MODIS cloud fraction
        #idObsDat=5; idObsDatPara=0; obsTimeStep='monthly'                 # CRU3.0 - t2bar
        #idObsDat=5; idObsDatPara=1; obsTimeStep='monthly'                 # CRU3.0 - t2max
        #idObsDat=5; idObsDatPara=2; obsTimeStep='monthly'                 # CRU3.0 - t2min
        #idObsDat=5; idObsDatPara=3; obsTimeStep='monthly'                 # CRU3.0 - pr
        #idObsDat=6; idObsDatPara=0; obsTimeStep='monthly'                 # CRU3.1 - pr
        #idObsDat=6; idObsDatPara=1; obsTimeStep='monthly'                 # CRU3.1 - t2bar
        #idObsDat=6; idObsDatPara=2; obsTimeStep='monthly'                 # CRU3.1 - t2max
        #idObsDat=6; idObsDatPara=3; obsTimeStep='monthly'                 # CRU3.1 - t2min
        #idObsDat=6; idObsDatPara=4; obsTimeStep='monthly'                 # CRU3.1 - cloud fraction
        ##### Data table to be replace with the use of metadata #################################
    # assign observed data info: all variables are 'list'
    obsDataset = []
    data_type = []
    obsDatasetId = []
    obsParameterId = []
    obsStartTime = []
    obsEndTime = []
    obsList = []

    for m in np.arange(numOBSs):
        obsDataset.append(db_datasets[idObsDat[m]])# obsDataset=db_datasets[idObsDat[m]]
        data_type.append(db_parameters[idObsDat[m]][idObsDatPara[m]])# data_type = db_parameters[idObsDat[m]][idObsDatPara[m]]
        obsDatasetId.append(db_dataset_ids[idObsDat[m]])# obsDatasetId = db_dataset_ids[idObsDat[m]]
        obsParameterId.append(db_parameter_ids[idObsDat[m]][idObsDatPara[m]])# obsParameterId = db_parameter_ids[idObsDat[m]][idObsDatPara[m]]
        obsStartTime.append(db_dataset_startTimes[idObsDat[m]])# obsStartTime = db_dataset_startTimes[idObsDat[m]]
        obsEndTime.append(db_dataset_endTimes[idObsDat[m]])# obsEndTime = db_dataset_endTimes[idObsDat[m]]
        obsList.append(db_datasets[idObsDat[m]] + '_' + db_parameters[idObsDat[m]][idObsDatPara[m]])
                        TRMM_pr_mon
                        CRU3.1_pr
        
    print'obsDatasetId,obsParameterId,obsList,obsStartTime,obsEndTime= ', obsDatasetId, obsParameterId, obsStartTime, obsEndTime# return -1
    obsStartTmax = max(obsStartTime)
    obsEndTmin = min(obsEndTime)
    
    ###################################################################
    # 3.   Load model data and assign model-related processing info
    ###################################################################
    # 3a:  construct the list of model data files
    if GUI:
        FileList_instructions = raw_input('Enter model file (specify multiple files using wildcard: e.g., *pr.nc):\n> ')
    else:
        FileList_instructions = '*' + modelVarName + '.nc'
        #FileList_instructions = '*' + 'ARPEGE51' + '*' + modelVarName + '.nc'
    FileList_instructions = mdlDataDir + '/' + FileList_instructions
    FileList = glob.glob(FileList_instructions)
    n_infiles = len(FileList)
    #print FileList_instructions,n_infiles,FileList

    # 3b: (1) Attempt to auto-detect latitude and longitude variable names (removed in rcmes.files_v12.find_latlon_var_from_file)
    #     (2) Find lat,lon limits from first file in FileList              (active)
    file_type = 'nc'
    laName = modelLatVarName
    loName = modelLonVarName
    latMin = ma.zeros(n_infiles)
    latMax = ma.zeros(n_infiles)
    lonMin = ma.zeros(n_infiles)
    lonMax = ma.zeros(n_infiles)
    
    for n in np.arange(n_infiles):
        ifile = FileList[n]
        status, latMin[n], latMax[n], lonMin[n], lonMax[n] = storage.files_v12.find_latlon_var_from_file(ifile, file_type, laName, loName)
        print 'Min/Max Lon & Lat: ', n, lonMin[n], lonMax[n], latMin[n], latMax[n]
    if GUI:
        instruction = raw_input('Do the long/lat ranges all model files match? (y/n)\n> ')

    else:
        instruction = 'y'
    print instruction
    if instruction != 'y':
        print 'Long & lat ranges of model data files do not match: EXIT'; return -1
    latMin = latMin[0]
    latMax = latMax[0]
    lonMin = lonMin[0]
    lonMax = lonMax[0]
    print 'Min/Max Lon & Lat:', lonMin, lonMax, latMin, latMax
    print ''



    # TODO:  Work out how to handle when model files have different ranges for Latitude, Longitude or Time

    # 3c: Decode model times into a python datetime object (removed in rcmes.process_v12.decode_model_times; var name is hardwired in 1.)
    #     Check the length of model data period. Retain only the files that contain the entire 20yr records
    #     Also specify the model data time step. Not used for now, but will be used to control the selection of the obs data (4) & temporal regridding (7).
    # Note July 25, 2011: model selection for analysis is moved and is combined with the determination of the evaluation period
    timeName = modelTimeVarName
    mdldataTimeStep = 'monthly'
    file_type = 'nc'
    n_mos = ma.zeros(n_infiles)
    newFileList = []
    mdlStartT = []
    mdlEndT = []
    mdlName = []
    k = 0

    for n in np.arange(n_infiles):
        # extract model names for identification
        # Provided that model results are named as 
        # mdlDataDir/projectName_mdlName_(some other information)_variableName.nc
        ifile = FileList[n]
        name = ifile[len(mdlDataDir)+1:len(mdlDataDir)+20]  # +1 excludes '/'
        name_wo_project = name[name.find('_')+1:]   # file name without its project name
        
        mdlName.append(name_wo_project[0:name_wo_project.find('_')]) # print'model name= ',name[0:name.find('_')]
        # extract the temporal coverage of each model data file and the related time parameters
        
        modelTimes = process.getModelTimes(ifile, timeName)
        
        # NOW WE HAVE MODEL TIMES...WHAT ARE THEY USED FOR???
        
        # THIS APPEARS TO BE A MONTHLY SPECIFIC IMPLEMENTATAION DETAIL
        n_mos[n] = len(modelTimes)
        
        # PARSE OUT THE Min(YEAR and MONTH) and Max(YEAR and MONTH)
        # Could this merely be a MinTime and MaxTime so essentially a TimeRange?
        
        
        y0 = min(modelTimes).strftime("%Y")
        m0 = min(modelTimes).strftime("%m")
        y1 = max(modelTimes).strftime("%Y")
        m1 = max(modelTimes).strftime("%m")
        
        
        
        if mdlTimeStep == 'monthly':
            d0 = 1
            d1 = 1
        else:
            d0 = min(modelTimes).strftime("%d")
            d1 = max(modelTimes).strftime("%d")
            
        minMdlT = datetime.datetime(int(y0), int(m0), int(d0), 0, 0, 0, 0)
        maxMdlT = datetime.datetime(int(y1), int(m1), int(d1), 0, 0, 0, 0)
        
        # AFTER all the Datetime to string to int and back to datetime, we are left with the ModelTimeStart and ModelTimeEnd
        mdlStartT.append(minMdlT)
        mdlEndT.append(maxMdlT)

    print 'Mdl Times decoded: n= ', n, ' Name: ', mdlName[n], ' length= ', len(modelTimes), \
          ' 1st mdl time: ', mdlStartT[n].strftime("%Y/%m"), ' Lst mdl time: ', mdlEndT[n].strftime("%Y/%m")

    #print 'mdlStartT'; print mdlStartT; print 'mdlEndT'; print mdlEndT
    #print max(mdlStartT),min(mdlEndT)
    
    # get the list of models to be evaluated and the period of evaluation
    # July 25, 2011: the selection of model and evaluation period are modified:
    #   1. Default: If otherwise specified, select the longest overlapping period and exclude the model outputs that do not cover the default period
    #   2. MaxMdl : Select the max number of models for evaluation. The evaluation period may be reduced
    #   3. PrdSpc : The evaluation period is specified and the only data files that cover the specified period are included for evaluation.
    #   4. Note that the analysis period is limited to the full annual cycle, i.e., starts in Jan and ends in Dec.
    # 5:   Select the period for evaluation/analysis (defaults to overlapping times between model and obs)
    # 5a: First calculate the overlapping period
    startTime = []
    endTime = []
    
    for n in np.arange(n_infiles):
        startTime.append(max(mdlStartT[n], obsStartTmax))
        endTime.append(min(mdlEndT[n], obsEndTmin))
        
        #print n,mdlStartT[n],mdlEndT[n],startTime[n],endTime[n]
        yy = int(startTime[n].strftime("%Y"))
        mm = int(startTime[n].strftime("%m"))
        
        if mm != 1:
            yy = yy + 1
            mm = 1

        startTime[n] = datetime.datetime(int(yy), int(mm), 1, 0, 0, 0, 0)
        yy = int(endTime[n].strftime("%Y"))
        mm = int(endTime[n].strftime("%m"))
        
        if mm != 12:
            yy = yy - 1
            mm = 12
        
        endTime[n] = datetime.datetime(int(yy), int(mm), 1, 0, 0, 0, 0)
        print mdlName[n], ' common start/end time: ', startTime[n], endTime[n]

    maxAnlT0 = min(startTime)
    maxAnlT1 = max(endTime)
    minAnlT0 = max(startTime)
    minAnlT1 = min(endTime)
    #print startTime; print endTime
    print 'max common period: ', maxAnlT0, '-', maxAnlT1; print 'min common period: ', minAnlT0, '-', minAnlT1
    
    # 5b: Determine the evaluation period and the models to be evaluated
    if GUI:
        print 'Select evaluation period. Depending on the selected period, the number of models may vary. See above common start/end times'
        print 'Enter: 1 for max common period, 2 for min common period, 3 for your own choice: Note that all period starts from Jan and end at Dec'
        choice = int(raw_input('Enter your choice from above [1,2,3] \n> '))
    else:
        choice = 3
    if choice == 1:
        startTime = maxAnlT0
        endTime = maxAnlT1
        print 'Maximum(model,obs) period is selected. Some models will be dropped from evaluation'
        
    if choice == 2:
        startTime = minAnlT0
        endTime = minAnlT1
        print 'Minimum(model,obs) period is selected. All models will be evaluated except there are problems'
      
    if choice == 3:
        startYear = int(raw_input('Enter start year YYYY \n'))
        endYear = int(raw_input('Enter end year YYYY \n'))
        
        if startYear < int(maxAnlT0.strftime("%Y")):
            print 'Your start year is earlier than the available data period: EXIT; return -1'
            
        if endYear > int(maxAnlT1.strftime("%Y")):
            print 'Your end year is later than the available data period: EXIT; return -1'
            
        # CGOODALE - Updating the Static endTime to be 31-DEC
        startTime = datetime.datetime(startYear, 1, 1, 0, 0)
        endTime = datetime.datetime(endYear, 12, 31, 0, 0)
        print 'Evaluation will be performed for a user-selected period'
        
    print 'Final: startTime/endTime: ', startTime, '/', endTime


    # select model data for analysis and analysis period
    k = 0
    newFileList = []
    name = []
    print 'n_infiles= ', n_infiles
    for n in np.arange(n_infiles): 
        ifile = FileList[n]
        nMos = n_mos[n]
        print mdlName[n], n_mos[n], mdlStartT[n], startTime, mdlEndT[n], endTime
        
        # LOOP OVER THE MODEL START TIMES AND DETERMINE WHICH TO KEEP based on user entered Start/End Years
        
        if mdlStartT[n] <= startTime and mdlEndT[n] >= endTime:
            newFileList.append(ifile)
            name.append(mdlName[n])
            k += 1
    FileList = newFileList
    newFileList = 0
    FileList.sort()
    print 'the number of select files = ', len(FileList)
    mdlName = name
    numMDLs = len(FileList)
    
    for n in np.arange(numMDLs):
        print n, mdlName[n], FileList[n]
    
    # 6:   Select spatial regridding options
    # PULLED DOWN INTO THE MAIN Loop
    regridOption = 2      # for multi-model cases, this option can be selected only when all model data are on the same grid system.
    naLons = 1
    naLats = 1
    dLon = 0.5
    dLat = 0.5  # these are dummies for regridOption = 1 & 2
    
    if GUI:
        print 'Spatial regridding options: '
        print '[0] Use Observational grid'
        print '[1] Use Model grid'
        print '[2] Define new regular lat/lon grid to use'
        regridOption = int(raw_input('Please make a selection from above:\n> '))
        
    if np.logical_or(regridOption > 2, regridOption < 0):
        print 'Error: Non-existing spatial regridding option. EXIT'; return -1, -1, -1, -1
    # specify the regridding option
    if regridOption == 0: 
        regridOption = 'obs'
    if regridOption == 1:
        regridOption = 'model'
    # If requested, get new grid parameters: min/max long & lat values and their uniform increments; the # of longs and lats
    
    if regridOption == 2:
        regridOption = 'regular'
        dLon = 0.44
        dLat = 0.44
        lonMin = -24.64
        lonMax = 60.28
        latMin = -45.76
        latMax = 42.24
        naLons = int((lonMax - lonMin + 1.e-5 * dLon) / dLon) + 1
        naLats = int((latMax - latMin + 1.e-5 * dLat) / dLat) + 1

    if GUI:
        if regridOption == 2:
            regridOption = 'regular'
            lonMin = float(raw_input('Please enter the longitude at the left edge of the domain:\n> '))
            lonMax = float(raw_input('Please enter the longitude at the right edge of the domain:\n> '))
            latMin = float(raw_input('Please enter the latitude at the lower edge of the domain:\n> '))
            latMax = float(raw_input('Please enter the latitude at the upper edge of the domain:\n> '))
            dLon = float(raw_input('Please enter the longitude spacing (in degrees) e.g. 0.5:\n> '))
            dLat = float(raw_input('Please enter the latitude spacing (in degrees) e.g. 0.5:\n> '))
            nLons = int((lonMax - lonMin + 1.e-5 * dLon) / dLon) + 1
            nLats = int((latMax - latMin + 1.e-5 * dLat) / dLat) + 1
            
    print 'Spatial re-grid data on the ', regridOption, ' grid'


    # 7:   Temporal regridding: Bring the model and obs data to the same temporal grid for comparison
    #      (e.g., daily vs. daily; monthly vs. monthly)
    timeRegridOption = 2
    if GUI == True:
        print 'Temporal regridding options: i.e. averaging from daily data -> monthly data'
        print 'The time averaging will be performed on both model and observational data.'
        print '[0] Calculate time mean for full period.'
        print '[1] Calculate annual means'
        print '[2] Calculate monthly means'
        print '[3] Calculate daily means (from sub-daily data)'
        timeRegridOption = int(raw_input('Please make a selection from above:\n> '))
    # non-existing option is selected
    if np.logical_or(timeRegridOption > 3, timeRegridOption < 0):
        print 'Error: ', timeRegridOption, ' is a non-existing temporal regridding option. EXIT'; return -1, -1, -1, -1
    # specify the temporal regridding option
    if timeRegridOption == 0: 
        timeRegridOption = 'mean over all times: i.e., annual-mean climatology'
        
    if timeRegridOption == 1: 
        timeRegridOption = 'annual'
        
    if timeRegridOption == 2: 
        timeRegridOption = 'monthly'
        
    if timeRegridOption == 3: 
        timeRegridOption = 'daily'
        
    print 'timeRegridOption= ', timeRegridOption
    

    #******************************************************************************************************************
    # 8:   Select whether to perform Area-Averaging over masked region
    #      If choice != 'y', the analysis/evaluation will be performed at every grid points within the analysis domain
    #******************************************************************************************************************
    numSubRgn = 21
    subRgnLon0 = ma.zeros(numSubRgn)
    subRgnLon1 = ma.zeros(numSubRgn)
    subRgnLat0 = ma.zeros(numSubRgn)
    subRgnLat1 = ma.zeros(numSubRgn)
    # 21 rgns: SMHI11 + W+C+E. Mediterrenean (JK) + 3 in UCT (Western Sahara, Somalia, Madagascar) + 4 in Mideast
    subRgnLon0 = [-10.0, 0.0, 10.0, 20.0, -19.3, 15.0, -10.0, -10.0, 33.9, 44.2, 10.0, 10.0, 30.0, 13.6, 13.6, 20.0, 43.2, 33.0, 45.0, 43.0, 50.0]   # HYB 21 rgns
    subRgnLon1 = [  0.0, 10.0, 20.0, 33.0, -10.2, 30.0, 10.0, 10.0, 40.0, 51.8, 25.0, 25.0, 40.0, 20.0, 20.0, 35.7, 50.3, 40.0, 50.0, 50.0, 58.0]   # HYB 21 rgns
    subRgnLat0 = [ 29.0, 29.0, 25.0, 25.0, 12.0, 15.0, 7.3, 5.0, 6.9, 2.2, 0.0, -10.0, -15.0, -27.9, -35.0, -35.0, -25.8, 25.0, 28.0, 13.0, 20.0]   # HYB 21 rgns
    subRgnLat1 = [ 36.5, 37.5, 32.5, 32.5, 20.0, 25.0, 15.0, 7.3, 15.0, 11.8, 10.0, 0.0, 0.0, -21.4, -27.9, -21.4, -11.7, 35.0, 35.0, 20.0, 27.5]   # HYB 21 rgns
    subRgnName = ['R01', 'R02', 'R03', 'R04', 'R05', 'R06', 'R07', 'R08', 'R09', 'R10', 'R11', 'R12', 'R13', 'R14', 'R15', 'R16', 'R17', 'R18', 'R19', 'R20', 'R21']   # HYB 21 rgns
    print subRgnName

    maskOption = 0
    maskLonMin = 0
    maskLonMax = 0
    maskLatMin = 0
    maskLatMax = 0
    rgnSelect = 0
    
    choice = 'y'

    if GUI:
        choice = raw_input('Do you want to calculate area averages over a masked region of interest? [y/n]\n> ').lower()
        if choice == 'y':
            maskOption = 1
            #print '[0] Load spatial mask from file.'
            #print '[1] Enter regular lat/lon box to use as mask.'
            #print '[2] Use pre-determined mask ranges'
            #try:
            #  maskInputChoice = int(raw_input('Please make a selection from above:\n> '))
            #if maskInputChoice==0:    # Read mask from file
            #  maskFile = raw_input('Please enter the file containing the mask data (including full path):\n> ') 
            #  maskFileVar = raw_input('Please enter variable name of the mask data in the file:\n> ')
            #if maskInputChoice==1:
            #  maskLonMin = float(raw_input('Please enter the longitude at the left edge of the mask region:\n> '))
            #  maskLonMax = float(raw_input('Please enter the longitude at the right edge of the mask region:\n> '))
            #  maskLatMin = float(raw_input('Please enter the latitude at the lower edge of the mask region:\n> '))
            #  maskLatMax = float(raw_input('Please enter the latitude at the upper edge of the mask region:\n> '))
    ## maskInputChoice = 0/1: Load spatial mask from file/specifify with long,lat range'

    
    if choice == 'y':
        maskOption = 1
        maskInputChoice = 1
        if maskInputChoice == 1:
            for n in np.arange(numSubRgn):
                print 'Subregion [', n, '] ', subRgnName[n], subRgnLon0[n], 'E - ', subRgnLon1[n], ' E: ', subRgnLat0[n], 'N - ', subRgnLat1[n], 'N'
            rgnSelect = 3
            if GUI:
                rgnSelect = raw_input('Select the region for which regional-mean timeseries are to be analyzed\n')

        #if maskInputChoice==0:    # Read mask from file
        #   maskFile = 'maskFileNameTBD'
        #   maskFileVar = 'maskFileVarTBD'
    
    # 9.   Select properties to evaluate/analyze
    # old Section 8: Select: calculate seasonal cycle composites
    
    seasonalCycleOption = 'y'
    if GUI:
        seasonalCycleOption = raw_input('Composite the data to show seasonal cycles? [y/n]\n> ').lower()
    if seasonalCycleOption == 'y':
        seasonalCycleOption = 1
    else:
        seasonalCycleOption = 0

      
    # Section 9: Select Peformance Metric
    choice = 0
    if GUI:
        print 'Metric options'
        print '[0] Bias: mean bias across full time range'
        print '[1] Mean Absolute Error: across full time range'
        print '[2] Difference: calculated at each time unit'
        print '[3] Anomaly Correlation> '
        print '[4] Pattern Correlation> '
        print '[5] TODO: Probability Distribution Function similarity score'
        print '[6] RMS error'
        choice = int(raw_input('Please make a selection from the options above\n> '))
    # assign the metrics to be calculated
    if choice == 0: 
        metricOption = 'bias'
        
    if choice == 1: 
        metricOption = 'mae'
        
    if choice == 2:
        metricOption = 'difference'
    
    if choice == 3:
        metricOption = 'acc'
    
    if choice == 4:
        metricOption = 'patcor'
    
    if choice == 5:
        metricOption = 'pdf'
    
    if choice == 6:
        metricOption = 'rms'


    #  Select output option
    FoutOption = 0
    if GUI:
        choice = raw_input('Option for output files of obs/model data: Enter no/bn/nc\n> ').lower()
        if choice == 'no':
            FoutOption = 0
        if choice == 'bn':
            FoutOption = 1
        if choice == 'nc':
            FoutOption = 2

    ###################################################################################################
    # Section 11: Select Plot Options
    ###################################################################################################


    modifyPlotOptions = 'no'
    plotTitle = modelVarName + '_'
    plotFilenameStub = modelVarName + '_'
    
    if GUI:
        modifyPlotOptions = raw_input('Do you want to modify the default plot options? [y/n]\n> ').lower()
        
    if modifyPlotOptions == 'y':
        plotTitle = raw_input('Enter the plot title:\n> ')
        plotFilenameStub = raw_input('Enter the filename stub to use, without suffix e.g. files will be named <YOUR CHOICE>.png\n> ')



    print'------------------------------'
    print'End of preprocessor: Run RCMET'
    print'------------------------------'

    """


    # Section 13: Run RCMET, passing in all of the user options

    # TODO: **Cameron** Add an option to write a file that includes all options selected before this step to help repeating the same analysis.
    # read-in and regrid both obs and model data onto a common grid system (temporally & spatially).
    # the data are passed to compute metrics and plotting
    # numOBSs & numMDLs will be increased by +1 for multiple obs & mdls, respectively, to accomodate obs and model ensembles
    # nT: the number of time steps in the data
    
    
#    numOBS, numMDL, nT, ngrdY, ngrdX, Times, obsData, mdlData, obsRgn, mdlRgn, obsList, mdlList = toolkit.do_data_prep.prep_data(\
#         cachedir, workdir, \
#         obsList, obsDatasetId, obsParameterId, \
#         startTime, endTime, \
#         latMin, latMax, lonMin, lonMax, dLat, dLon, naLats, naLons, \
#         FileList, \
#         numSubRgn, subRgnLon0, subRgnLon1, subRgnLat0, subRgnLat1, subRgnName, \
#         modelVarName, precipFlag, modelTimeVarName, modelLatVarName, modelLonVarName, \
#         regridOption, timeRegridOption, maskOption, FoutOption)

    """
    Parameter to Object Mapping
    cachedir = settings.cacheDir
    workdir = settings.cacheDir
    obsList = obsDatasetList.each['longname']
    """

    numOBS, numMDL, nT, ngrdY, ngrdX, Times, obsData, mdlData, obsRgn, mdlRgn, obsList, mdlList = toolkit.do_data_prep(\
          settings, obsDatasetList, gridBox, models, subRegionTuple)
    
    """
    print 'Input and regridding of both obs and model data are completed. now move to metrics calculations'
    # Input and regridding of both obs and model data are completed. now move to metrics calculations

    print '-----------------------------------------------'
    print 'mdlID  numMOs  mdlStartTime mdlEndTime fileName'
    print '-----------------------------------------------'
    
    """
    mdlSelect = numMDL - 1                      # numMDL-1 corresponds to the model ensemble

    """
    if GUI:
        n = 0
        while n < len(mdlList):
            print n, n_mos[n], mdlStartT[n], mdlEndT[n], FileList[n][35:]
            n += 1
        ask = 'Enter the model ID to be evaluated from above:  ', len(FileList), ' for the model-ensemble: \n'
        mdlSelect = int(raw_input(ask))

    print '----------------------------------------------------------------------------------------------------------'

    
    if maskOption == 1:
        seasonalCycleOption = 1
    
    # TODO:  This seems like we can just use numOBS to compute obsSelect (obsSelect = numbOBS -1)
    if numOBS == 1:
        obsSelect = 1
    else:
        #obsSelect = 1          #  1st obs (TRMM)
        #obsSelect = 2          # 2nd obs (CRU3.1)
        obsSelect = numOBS      # obs ensemble

    obsSelect = obsSelect - 1   # convert to fit the indexing that starts from 0

    toolkit.do_metrics_20.metrics_plots(numOBS, numMDL, nT, ngrdY, ngrdX, Times, obsData, mdlData, obsRgn, mdlRgn, obsList, mdlList, \
                              workdir, \
                              mdlSelect, obsSelect, \
                              numSubRgn, subRgnName, rgnSelect, \
                              obsParameterId, precipFlag, timeRegridOption, maskOption, seasonalCycleOption, metricOption, \
                                                                                           plotTitle, plotFilenameStub)
    """

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
        configData['filename'] = modelFile
        model = Model(**configData)
        models.append(model)
    
    return models

def generateSettings(settingsConfig):
    """
    Helper function to decouple the argument parsing from the Settings object creation
    
    Input::  
        settingsConfig - list of ('key', 'value') tuples.
            workdir - string i.e. '/nas/run/rcmet/work/'
            cachedir - string i.e. '/tmp/rcmet/cache/'
    Output::
        settings - Settings Object
    """
    # Setup the config Data Dictionary to make parsing easier later
    configData = {}
    for entry in settingsConfig:
        configData[entry[0]] = entry[1]
        
    return Settings(**configData)

def generateDatasets(rcmedConfig):
    """
    Helper function to decouple the argument parsing from the RCMEDDataset object creation

    Input::  
        rcmedConfig - list of ('key', 'value') tuples.
            obsDatasetId=3,10
            obsParamId=36,32
            obsTimeStep=monthly,monthly

    Output::
        datasets - list of RCMEDDataset Objects
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

if __name__ == "__main__":
    
    if args.CONFIG:
        print 'Running using config file: %s' % args.CONFIG
        # Parse the Config file
        userConfig = ConfigParser.SafeConfigParser()
        userConfig.optionxform = str # This is so the case is preserved on the items in the config file
        userConfig.read(args.CONFIG)
        settings = generateSettings(userConfig.items('SETTINGS'))
        models = generateModels(userConfig.items('MODEL'))
        datasets = generateDatasets(userConfig.items('RCMED'))
        
        # Go get the parameter listing from the database
        try:
            params = db.getParams()
        except Exception:
            sys.exit()
        
        obsDatasetList = []
        for param_id in datasets['obsParamId']:
            for param in params:
                if param['parameter_id'] == int(param_id):
                    obsDatasetList.append(param)
                else:
                    pass

        # TODO:  Find a home for the regrid parameters in the CONFIG file
        # Setup the Regridding Options
        regridOption = 'regular'
        # dLon = 0.44 - Provided in the SETTINGS config section
        # dLat = 0.44
        lonMin = -24.64
        lonMax = 60.28
        latMin = -45.76
        latMax = 42.24
        # Create a Grid Box Object that extends the bounding box Object
        gridBox = GridBox(latMin, lonMin, latMax, lonMax, settings.gridLonStep, settings.gridLatStep)
       
        """ These can now be accessed from the gridBox object using gridBox.latCount and gridBox.lonCount attributes
        naLons = int((gridBox.lonMax - gridBox.lonMin + 1.e-5 * settings.gridLonStep) / settings.gridLonStep) + 1
        print naLons
        print int((gridBox.lonMax - gridBox.lonMin) / gridBox.lonStep) + 1 
        naLats = int((gridBox.latMax - gridBox.latMin + 1.e-5 * settings.gridLatStep) / settings.gridLatStep) + 1
        """
        timeRegridOption = settings.temporalGrid
        
        # TODO:  How do we support n subregions as Jinwon has below?
        
        numSubRgn = 21
#        subRgnLon0 = ma.zeros(numSubRgn)
#        subRgnLon1 = ma.zeros(numSubRgn)
#        subRgnLat0 = ma.zeros(numSubRgn)
#        subRgnLat1 = ma.zeros(numSubRgn)
        # 21 rgns: SMHI11 + W+C+E. Mediterrenean (JK) + 3 in UCT (Western Sahara, Somalia, Madagascar) + 4 in Mideast
        subRgnLon0 = [-10.0, 0.0, 10.0, 20.0, -19.3, 15.0, -10.0, -10.0, 33.9, 44.2, 10.0, 10.0, 30.0, 13.6, 13.6, 20.0, 43.2, 33.0, 45.0, 43.0, 50.0]   # HYB 21 rgns
        subRgnLon1 = [  0.0, 10.0, 20.0, 33.0, -10.2, 30.0, 10.0, 10.0, 40.0, 51.8, 25.0, 25.0, 40.0, 20.0, 20.0, 35.7, 50.3, 40.0, 50.0, 50.0, 58.0]   # HYB 21 rgns
        subRgnLat0 = [ 29.0, 29.0, 25.0, 25.0, 12.0, 15.0, 7.3, 5.0, 6.9, 2.2, 0.0, -10.0, -15.0, -27.9, -35.0, -35.0, -25.8, 25.0, 28.0, 13.0, 20.0]   # HYB 21 rgns
        subRgnLat1 = [ 36.5, 37.5, 32.5, 32.5, 20.0, 25.0, 15.0, 7.3, 15.0, 11.8, 10.0, 0.0, 0.0, -21.4, -27.9, -21.4, -11.7, 35.0, 35.0, 20.0, 27.5]   # HYB 21 rgns
        subRgnName = ['R01', 'R02', 'R03', 'R04', 'R05', 'R06', 'R07', 'R08', 'R09', 'R10', 'R11', 'R12', 'R13', 'R14', 'R15', 'R16', 'R17', 'R18', 'R19', 'R20', 'R21']   # HYB 21 rgns
        print subRgnName
        
        subRegionTuple = (numSubRgn, subRgnLon0, subRgnLon1, subRgnLat0, subRgnLat1, subRgnName)
        
        
        rgnSelect = 3
        maskOption = settings.maskOption
        
        bbox = BoundingBox(subRgnLat0[rgnSelect], 
                           subRgnLon0[rgnSelect], 
                           subRgnLat1[rgnSelect], 
                           subRgnLon1[rgnSelect])
        
        regionMask = SubRegion(subRgnName[rgnSelect], bbox)
        
        # Using a 'mask' instance of the BoundingBox object
#        maskLonMin = 0
#        maskLonMax = 0
#        maskLatMin = 0
#        maskLatMax = 0
        
        choice = 'y'
        
        #  THIS JUST MEANS A USER DEFINED MASK IS BEING USED (basically from the hardcoded values listed above (line 819 ish)
        maskInputChoice = 1

        if maskInputChoice == 1:
            for n in np.arange(numSubRgn):
                print 'Subregion [', n, '] ', subRgnName[n], subRgnLon0[n], 'E - ', subRgnLon1[n], ' E: ', subRgnLat0[n], 'N - ', subRgnLat1[n], 'N'
            rgnSelect = 3
        
        # Section 9: Select Peformance Metric
        metricOption = 'bias'
        FoutOption = 0
        
        # Section 11: Select Plot Options
        # TODO: Using first model in models since Var name is the same across all
        modifyPlotOptions = 'no'
        plotTitle = models[0].varName + '_'
        plotFilenameStub = models[0].varName + '_'
        
        print'------------------------------'
        print'End of preprocessor: Run RCMET'
        print'------------------------------'
        
        numOBS, numMDL, nT, ngrdY, ngrdX, Times, obsData, mdlData, obsRgn, mdlRgn, obsList, mdlList = toolkit.do_data_prep.prep_data(settings, obsDatasetList, gridBox, models, subRegionTuple)
        
        
        print 'Input and regridding of both obs and model data are completed. now move to metrics calculations'
        
        """FROM THE UPPER SECTION OF CODE"""

        mdlSelect = numMDL - 1                      # numMDL-1 corresponds to the model ensemble
    
        """ Disregard GUI block for now
        if GUI:
            n = 0
            while n < len(mdlList):
                print n, n_mos[n], mdlStartT[n], mdlEndT[n], FileList[n][35:]
                n += 1
            ask = 'Enter the model ID to be evaluated from above:  ', len(FileList), ' for the model-ensemble: \n'
            mdlSelect = int(raw_input(ask))
    
        print '----------------------------------------------------------------------------------------------------------'
        """
        
        if maskOption:
            seasonalCycleOption = True
        
        # TODO:  This seems like we can just use numOBS to compute obsSelect (obsSelect = numbOBS -1)
        if numOBS == 1:
            obsSelect = 1
        else:
            #obsSelect = 1          #  1st obs (TRMM)
            #obsSelect = 2          # 2nd obs (CRU3.1)
            obsSelect = numOBS      # obs ensemble
    
        obsSelect = obsSelect - 1   # convert to fit the indexing that starts from 0
    
    
    
        # TODO:  Undo the following code when refactoring later
        obsParameterId = [str(x['parameter_id']) for x in obsDatasetList]
        precipFlag = models[0].precipFlag
    
        toolkit.do_metrics_20.metrics_plots(numOBS, numMDL, nT, ngrdY, ngrdX, Times, obsData, mdlData, obsRgn, mdlRgn, obsList, mdlList, \
                                  settings.workDir, \
                                  mdlSelect, obsSelect, \
                                  numSubRgn, subRgnName, rgnSelect, \
                                  obsParameterId, precipFlag, timeRegridOption, maskOption, seasonalCycleOption, metricOption, \
                                                                                               plotTitle, plotFilenameStub)
        

        
    else:
        print 'Interactive mode has been enabled'
        #getSettings(SETTINGS)
        print "But isn't implemented.  Try using the -c option instead"

    #rcmet_cordexAF()
