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
"""Prepare Datasets both model and observations for analysis using metrics"""


import numpy as np
import numpy.ma as ma
import sys, os

from storage import db, files
import process
from utils import misc

# TODO:  swap gridBox for Domain
def prep_data(settings, obsDatasetList, gridBox, modelList):
    """
    
    returns numOBSs,numMDLs,nT,ngrdY,ngrdX,Times,lons,lats,obsData,modelData,obsList
    
        numOBSs - number of Observational Datasets.  Really need to look at using len(obsDatasetList) instead
        numMDLs - number of Models used.  Again should use the len(modelList) instead
        nT - Time value count after temporal regridding. Should use length of the time axis for a given dataset
        ngrdY - size of the Y-Axis grid after spatial regridding
        ngrdX - size of the X-Axis grid after spatial regridding
        Times - list of python datetime objects the represent the list of time to be used in further calculations
        lons - 
        lats - 
        obsData - 
        modelData - 
        obsList - 
        
    
    """
    
    # TODO:  Stop the object Deserialization and work on refactoring the core code here
    cachedir = settings.cacheDir
    workdir = settings.workDir

    # Use list comprehensions to deconstruct obsDatasetList
    #  ['TRMM_pr_mon', 'CRU3.1_pr']    Basically a list of Dataset NAME +'_' + parameter name - THE 'CRU*' one triggers unit conversion issues later
    # the plan here is to use the obsDatasetList which contains a longName key we can use.
    obsList = [str(x['longname']) for x in obsDatasetList]
    # Also using the obsDatasetList with a key of ['dataset_id']
    obsDatasetId = [str(x['dataset_id']) for x in obsDatasetList]
    # obsDatasetList ['paramter_id'] list
    obsParameterId = [str(x['parameter_id']) for x in obsDatasetList]
    obsTimestep = [str(x['timestep']) for x in obsDatasetList]
    mdlList = [model.filename for model in modelList]

    # Since all of the model objects in the modelList have the same Varnames and Precip Flag, I am going to merely 
    # pull this from modelList[0] for now
    modelVarName = modelList[0].varName
    precipFlag = modelList[0].precipFlag
    modelTimeVarName = modelList[0].timeVariable
    modelLatVarName = modelList[0].latVariable
    modelLonVarName = modelList[0].lonVariable
    regridOption = settings.spatialGrid
    timeRegridOption = settings.temporalGrid
    
    """
     Routine to read-in and re-grid both obs and mdl datasets.
     Processes both single and multiple files of obs and mdl or combinations in a general way.
           i)    retrieve observations from the database
           ii)   load in model data
           iii)  spatial regridding
           iv)   temporal regridding
           v)    area-averaging
           Input:
                   cachedir 	- string describing directory path
                   workdir 	- string describing directory path
                   obsList        - string describing the observation data files
                   obsDatasetId 	- int, db dataset id
                   obsParameterId	- int, db parameter id 
                   latMin, latMax, lonMin, lonMax, dLat, dLon, naLats, naLons: define the evaluation/analysis domain/grid system
    	         latMin		- float
                   latMax		- float
                   lonMin		- float
                   lonMax		- float
                   dLat  		- float
                   dLon  		- float
                   naLats		- integer
                   naLons		- integer
                   mdlList	- string describing model file name + path
                   modelVarName	- string describing name of variable to evaluate (as written in model file)
    	         precipFlag	- bool  (is this precipitation data? True/False)
                   modelTimeVarName - string describing name of time variable in model file 	
                   modelLatVarName  - string describing name of latitude variable in model file 
                   modelLonVarName  - string describing name of longitude variable in model file 
                   regridOption 	 - string: 'obs'|'model'|'user'
                   timeRegridOption -string: 'full'|'annual'|'monthly'|'daily'
                   maskOption - Boolean
                   
                   # TODO:  This isn't true in the current codebase.
                   Instead the SubRegion's are being used.  You can see that these values are not
                   being used in the code, at least they are not being passed in from the function
                   
                   maskLatMin - float (only used if maskOption=1)
                   maskLatMax - float (only used if maskOption=1)
    	         maskLonMin - float (only used if maskOption=1)
                   maskLonMax - float (only used if maskOption=1)
           Output: image files of plots + possibly data
           Jinwon Kim, 7/11/2012
    """


    # check the number of obs & model data files
    numOBSs = len(obsList)
    numMDLs = len(mdlList)
    
    # assign parameters that must be preserved throughout the process
    
    print 'start & end time = ', settings.startDate, settings.endDate
    yymm0 = settings.startDate.strftime("%Y%m")
    yymm1 = settings.endDate.strftime("%Y%m")
    print 'start & end eval period = ', yymm0, yymm1



    #TODO: Wrap in try except blocks instead
    if numMDLs < 1: 
        print 'No input model data file. EXIT'
        sys.exit()
    if numOBSs < 1: 
        print 'No input observation data file. EXIT'
        sys.exit()

    ## Part 0: Setup the regrid variables based on the regridOption given

    # preparation for spatial re-gridding: define the size of horizontal array of the target interpolation grid system (ngrdX and ngrdY)
    print 'regridOption in prep_data= ', regridOption
    if regridOption == 'model':
        ifile = mdlList[0]
        typeF = 'nc'
        lats, lons, mTimes = files.read_data_from_one_file(ifile, modelVarName, 
                                                           modelLatVarName, 
                                                           modelLonVarName, 
                                                           modelTimeVarName, 
                                                           typeF)[:3]
        modelObject = modelList[0]
        latMin = modelObject.latMin
        latMax = modelObject.latMax
        lonMin = modelObject.lonMin
        lonMax = modelObject.lonMax
    elif regridOption == 'user':
        # Use the GridBox Object
        latMin = gridBox.latMin
        latMax = gridBox.latMax
        lonMin = gridBox.lonMin
        lonMax = gridBox.lonMax
        naLats = gridBox.latCount
        naLons = gridBox.lonCount
        dLat = gridBox.latStep
        dLon = gridBox.lonStep
        lat = np.arange(naLats) * dLat + latMin
        lon = np.arange(naLons) * dLon + lonMin
        lons, lats = np.meshgrid(lon, lat)
        lon = 0.
        lat = 0.
    else:
        print "INVALID REGRID OPTION USED"
        sys.exit()
        
    ngrdY = lats.shape[0]
    ngrdX = lats.shape[1]

    regObsData = []
    
    
    
    ## Part 1: retrieve observation data from the database and regrid them
    ##       NB. automatically uses local cache if already retrieved.
    
    for n in np.arange(numOBSs):
        # spatial regridding
        oLats, oLons, _, oTimes, oData = db.extractData(obsDatasetId[n],
                                                        obsParameterId[n],
                                                        latMin, latMax,
                                                        lonMin, lonMax,
                                                        settings.startDate, settings.endDate,
                                                        cachedir, obsTimestep[n])
        
        # TODO: modify this if block with new metadata usage.
        if precipFlag == True and obsList[n][0:3] == 'CRU':
            oData = 86400.0 * oData

        nstOBSs = oData.shape[0]         # note that the length of obs data can vary for different obs intervals (e.g., daily vs. monthly)
        print 'Regrid OBS dataset onto the ', regridOption, ' grid system: ngrdY, ngrdX, nstOBSs= ', ngrdY, ngrdX, nstOBSs
        print 'For dataset: %s' % obsList[n]
        
        tmpOBS = ma.zeros((nstOBSs, ngrdY, ngrdX))
        
        print 'tmpOBS shape = ', tmpOBS.shape
        
        # OBS SPATIAL REGRIDING 
        for t in np.arange(nstOBSs):
            tmpOBS[t, :, :] = process.do_regrid(oData[t, :, :], oLats, oLons, lats, lons)
            
        # TODO:  Not sure this is needed with Python Garbage Collector
        # The used memory should be freed when the objects are no longer referenced.  If this continues to be an issue we may need to look
        # at using generators where possible.
        oLats = 0.0
        oLons = 0.0       # release the memory occupied by the temporary variables oLats and oLons.
        
        # OBS TEMPORAL REGRIDING
        oData, newObsTimes = process.calc_average_on_new_time_unit_K(tmpOBS, oTimes, unit=timeRegridOption)

        tmpOBS = 0.0
        
        # check the consistency of temporally regridded obs data
        if n == 0:
            oldObsTimes = newObsTimes
        else:
            if oldObsTimes != newObsTimes:
                print 'temporally regridded obs data time levels do not match at ', n - 1, n
                print '%s Time through Loop' % (n + 1)
                print 'oldObsTimes Count: %s' % len(oldObsTimes)
                print 'newObsTimes Count: %s' % len(newObsTimes)
                # TODO:  We need to handle these cases using Try Except Blocks or insert a sys.exit if appropriate
                sys.exit()
            else:
                oldObsTimes = newObsTimes
        # if everything's fine, append the spatially and temporally regridded data in the obs data array (obsData)
        regObsData.append(oData)


    """ all obs datasets have been read-in and regridded. convert the regridded obs data from 'list' to 'array'
    also finalize 'obsTimes', the time coordinate values of the regridded obs data.
    NOTE: using 'list_to_array' assigns values to the missing points; this has become a problem in handling the CRU data.
          this problem disappears by using 'ma.array'."""

    obsData = ma.array(regObsData)
    obsTimes = newObsTimes

    # compute the simple multi-obs ensemble if multiple obs are used
    if numOBSs > 1:
        ensemble = np.mean(regObsData, axis=0)
        regObsData.append(ensemble)
        numOBSs = len(regObsData)
        obsList.append('ENS-OBS')
        obsData = ma.array(regObsData) # Cast to a masked array


    ## Part 2: load in and regrid model data from file(s)
    ## NOTE: the two parameters, numMDLs and numMOmx are defined to represent the number of models (w/ all 240 mos) &
    ##       the total number of months, respectively, in later multi-model calculations.

    typeF = 'nc'
    regridMdlData = []
    # extract the model names and store them in the list 'mdlList'
    mdlName = []
    mdlListReversed=[]
    if len(mdlList) >1:
       for element in mdlList:
           mdlListReversed.append(element[::-1])
       prefix=os.path.commonprefix(mdlList)
       postfix=os.path.commonprefix(mdlListReversed)[::-1]
       for element in mdlList:
           mdlName.append(element.replace(prefix,'').replace(postfix,''))
    else:
        mdlName.append('model') 

    
    for n in np.arange(numMDLs):
        # read model grid info, then model data
        ifile = mdlList[n]
        print 'ifile= ', ifile
        modelLats, modelLons, mTimes, mdlDat, mvUnit = files.read_data_from_one_file(ifile, 
                                                                                     modelVarName,
                                                                                     modelLatVarName,
                                                                                     modelLonVarName,
                                                                                     modelTimeVarName, 
                                                                                     typeF)
        mdlT = []
        mStep = len(mTimes)

        for i in np.arange(mStep):
            mdlT.append(mTimes[i].strftime("%Y%m"))

        wh = (np.array(mdlT) >= yymm0) & (np.array(mdlT) <= yymm1)
        modelTimes = list(np.array(mTimes)[wh])
        mData = mdlDat[wh, :, :]
   
        # determine the dimension size from the model time and latitude data.
        nT = len(modelTimes)

        print '  The shape of model data to be processed= ', mData.shape, ' for the period ', min(modelTimes), max(modelTimes)
        # spatial regridding of the modl data
        tmpMDL = ma.zeros((nT, ngrdY, ngrdX))

        if regridOption != 'model':
            for t in np.arange(nT):
                tmpMDL[t, :, :] = process.do_regrid(mData[t, :, :], modelLats, modelLons, lats, lons)
        else:
            tmpMDL = mData

        # temporally regrid the model data
        mData, newMdlTimes = process.regrid_in_time(tmpMDL, modelTimes, unit=timeRegridOption)
        tmpMDL = 0.0
        
        # check data consistency for all models 
        if n == 0:
            oldMdlTimes = newMdlTimes
        else:
            if oldMdlTimes != newMdlTimes:
                print 'temporally regridded mdl data time levels do not match at ', n - 1, n
                print len(oldMdlTimes), len(newMdlTimes)
                sys.exit()
            else:
                oldMdlTimes = newMdlTimes

        # if everything's fine, append the spatially and temporally regridded data in the obs data array (obsData)
        regridMdlData.append(mData)

    modelData  = ma.array(regridMdlData)
    modelTimes = newMdlTimes

    if (precipFlag == True) & (mvUnit == 'KG M-2 S-1'):
        print 'convert model variable unit from mm/s to mm/day'
        modelData = 86400.*modelData
    
    # check consistency between the time levels of the model and obs data
    #   this is the final update of time levels: 'Times' and 'nT'
    if obsTimes != modelTimes:
        print 'time levels of the obs and model data are not consistent. EXIT'
        print 'obsTimes'
        print obsTimes
        print 'modelTimes'
        print modelTimes
        sys.exit()
    #  'Times = modelTimes = obsTimes' has been established and modelTimes and obsTimes will not be used hereafter. (de-allocated)
    Times = modelTimes
    nT = len(modelTimes)
    modelTimes = 0
    obsTimes = 0

    print 'Reading and regridding model data are completed'
    print 'numMDLs, modelData.shape= ', numMDLs, modelData.shape

    # TODO:  Commented out until I can talk with Jinwon about this
    # compute the simple multi-model ensemble if multiple models are evaluated
    if numMDLs > 1:
        model_ensemble = np.mean(regridMdlData, axis=0)
        regridMdlData.append(model_ensemble)
        numMDLs = len(regridMdlData)
        modelData = ma.array(regridMdlData)
        mdlName.append('ENS-MODEL')
        print 'Eval mdl-mean timeseries for the obs periods: modelData.shape= ',modelData.shape
    # GOODALE:  This ensemble code should be refactored into process.py module since it's purpose is data processing

    # Processing complete
    print 'data_prep is completed: both obs and mdl data are re-gridded to a common analysis grid'
    return numOBSs, numMDLs, nT, ngrdY, ngrdX, Times, lons, lats, obsData, modelData, obsList, mdlName
