"""Prepare Datasets both model and observations for analysis using metrics"""


import numpy as np
import numpy.ma as ma
import sys

import Nio

from storage import db, files
import process

# TODO:  swap gridBox for Domain
def prep_data(settings, obsDatasetList, gridBox, modelList, subRegions):
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
    startTime = settings.startDate
    endTime = settings.endDate

    # Use list comprehensions to deconstruct obsDatasetList
    #  ['TRMM_pr_mon', 'CRU3.1_pr']    Basically a list of Dataset NAME +'_' + parameter name - THE 'CRU*' one triggers unit conversion issues later
    # the plan here is to use the obsDatasetList which contains a longName key we can use.
    obsList = [str(x['longName']) for x in obsDatasetList]
    # Also using the obsDatasetList with a key of ['dataset_id']
    obsDatasetId = [str(x['dataset_id']) for x in obsDatasetList]
    # obsDatasetList ['paramter_id'] list
    obsParameterId = [str(x['parameter_id']) for x in obsDatasetList]
    mdlList = [model.filename for model in modelList]
    
    # TODO - SubRegions seems to be missing in the latest code
#    if subRegions:
#        numSubRgn = len(subRegions)
#        subRgnLon0 = [ x.lonMin for x in subRegions ]
#        subRgnLon1 = [ x.lonMax for x in subRegions ]
#        subRgnLat0 = [ x.latMin for x in subRegions ]
#        subRgnLat1 = [ x.latMax for x in subRegions ]
    
    # Since all of the model objects in the modelList have the same Varnames and Precip Flag, I am going to merely 
    # pull this from modelList[0] for now
    modelVarName = modelList[0].varName
    precipFlag = modelList[0].precipFlag
    modelTimeVarName = modelList[0].timeVariable
    modelLatVarName = modelList[0].latVariable
    modelLonVarName = modelList[0].lonVariable
    regridOption = settings.spatialGrid
    timeRegridOption = settings.temporalGrid
    
    #TODO: Un hardcode this later
    # TODO: These 2 variables are no longer used in the latest version.  Might be able to remove
#    maskOption = True
#    FoutOption = settings.writeOutFile



    """
     Routine to read-in and re-grid both obs and mdl datasets.
     Processes both single and multiple files of obs and mdl or combinations in a general way.
           i)    retrieve observations from the database
           ii)   load in model data
           iii)  temporal regridding
           iv)   spatial regridding
           v)    area-averaging
           Input:
                   cachedir 	- string describing directory path
                   workdir 	- string describing directory path
                   obsList        - string describing the observation data files
                   obsDatasetId 	- int, db dataset id
                   obsParameterId	- int, db parameter id 
                   startTime	- datetime object, the starting time of evaluation
                   endTime	- datetime object, the ending time of evaluation
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

    # assign parameters that must be preserved throughout the process
    print 'start & end time = ', startTime, endTime
    yymm0 = startTime.strftime("%Y%m")
    yymm1 = endTime.strftime("%Y%m")
    print 'start & end eval period = ', yymm0, yymm1
    # check the number of obs & model data files
    numOBSs = len(obsList)
    numMDLs = len(mdlList)
    
    #TODO: Wrap in try except blocks instead
    if numMDLs < 1: 
        print 'No input model data file. EXIT'
        sys.exit()
    if numOBSs < 1: 
        print 'No input observation data file. EXIT'
        sys.exit()

    ## Part 1: retrieve observation data from the database and regrid them
    ##       NB. automatically uses local cache if already retrieved.

    # preparation for spatial re-gridding: define the size of horizontal array of the target interpolation grid system (ngrdX and ngrdY)
    print 'regridOption in prep_data= ', regridOption
    if regridOption == 'model':
        ifile = mdlList[0]
        typeF = 'nc'
        lats, lons, mTimes = files.read_lolaT_from_file(ifile, modelLatVarName, modelLonVarName, modelTimeVarName, typeF)
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
    
    for n in np.arange(numOBSs):
        # spatial regridding
        oLats, oLons, _, oTimes, oData = db.extractData(obsDatasetId[n],
                                                        obsParameterId[n],
                                                        latMin, latMax,
                                                        lonMin, lonMax,
                                                        startTime, endTime,
                                                        cachedir)
        
        # TODO: modify this if block with new metadata usage.
        if precipFlag == True and obsList[n][0:3] == 'CRU':
            oData = 86400.0 * oData

        nstOBSs = oData.shape[0]         # note that the length of obs data can vary for different obs intervals (e.g., daily vs. monthly)
        print 'Regrid OBS dataset onto the ', regridOption, ' grid system: ngrdY, ngrdX, nstOBSs= ', ngrdY, ngrdX, nstOBSs
        print 'For dataset: %s' % obsList[n]
        
        tmpOBS = ma.zeros((nstOBSs, ngrdY, ngrdX))
        
        print 'tmpOBS shape = ', tmpOBS.shape
        
        for t in np.arange(nstOBSs):
            tmpOBS[t, :, :] = process.do_regrid(oData[t, :, :], oLats, oLons, lats, lons)
            
        # TODO:  Not sure this is needed with Python Garbage Collector
        # The used memory should be freed when the objects are no longer referenced.  If this continues to be an issue we may need to look
        # at using generators where possible.
        oLats = 0.0
        oLons = 0.0       # release the memory occupied by the temporary variables oLats and oLons.
        
        # temporally regrid the spatially regridded obs data
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
    also finalize 'obsTimes', the time cooridnate values of the regridded obs data.
    NOTE: using 'list_to_array' assigns values to the missing points; this has become a problem in handling the CRU data.
          this problem disappears by using 'ma.array'."""

    obsData = ma.array(regObsData)
    obsTimes = newObsTimes
    regObsData = 0
    oldObsTimes = 0
    nT = len(obsTimes)

    # TODO:  Refactor this into a function within the toolkit module
    # compute the simple multi-obs ensemble if multiple obs are used
    if numOBSs > 1:
        print 'numOBSs = ', numOBSs
        oData = obsData
        print 'oData shape = ', oData.shape
        obsData = ma.zeros((numOBSs + 1, nT, ngrdY, ngrdX))
        print 'obsData shape = ', obsData.shape
        avg = ma.zeros((nT, ngrdY, ngrdX))
        
        for i in np.arange(numOBSs):
            obsData[i, :, :, :] = oData[i, :, :, :]
            avg[:, :, :] = avg[:, :, :] + oData[i, :, :, :]

        avg = avg / float(numOBSs)
        obsData[numOBSs, :, :, :] = avg[:, :, :]     # store the model-ensemble data
        numOBSs = numOBSs + 1                     # update the number of obs data to include the model ensemble
        obsList.append('ENS-OBS')
    print 'OBS regridded: ', obsData.shape


    ## Part 2: load in and regrid model data from file(s)
    ## NOTE: tthe wo parameters, numMDLs and numMOmx are defined to represent the number of models (w/ all 240 mos) &
    ##       the total number of months, respectively, in later multi-model calculations.

    typeF = 'nc'
    #mdlName = []
    regridMdlData = []
    
    # extract the model names and store them in the list 'mdlName'
    for n in np.arange(numMDLs):
        # read model grid info, then model data
        ifile = mdlList[n]
        print 'ifile= ', ifile
        modelLats, modelLons, mTimes = files.read_lolaT_from_file(ifile, modelLatVarName, modelLonVarName, modelTimeVarName, typeF)
        mTime, mdlDat, mvUnit = files.read_data_from_one_file(ifile, modelVarName, modelTimeVarName, modelLats, typeF)
        mdlT = []
        mStep = len(mTimes)

        for i in np.arange(mStep):
            mdlT.append(mTimes[i].strftime("%Y%m"))

        wh = (np.array(mdlT) >= yymm0) & (np.array(mdlT) <= yymm1)
        modelTimes = list(np.array(mTimes)[wh])
        mData = mdlDat[wh, :, :]
   
        # determine the dimension size from the model time and latitude data.
        nT = len(modelTimes)
        
        # UNUSED VARIABLES - WILL DELETE AFTER TESTING
        # nmdlY=modelLats.shape[0]
        # nmdlX=modelLats.shape[1]
        #print 'nT, ngrdY, ngrdX = ',nT,ngrdY, ngrdX,min(modelTimes),max(modelTimes)
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

    modelData = ma.array(regridMdlData)
    modelTimes = newMdlTimes
    regridMdlData = 0
    oldMdlTimes = 0
    newMdlTimes = 0
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
    
    # TODO: Do we need to make this a user supplied flag, or do we just create an ensemble ALWAYS
    # TODO: Add in Kyo's code here as well
    # TODO:  Commented out until I can talk with Jinwon about this
    # compute the simple multi-model ensemble if multiple models are evaluated
#    if numMDLs > 1:
#        mdlData=modelData
#        modelData=ma.zeros((numMDLs+1,nT,ngrdY,ngrdX))
#        avg=ma.zeros((nT,ngrdY,ngrdX))
#        for i in np.arange(numMDLs):
#            modelData[i,:,:,:]=mdlData[i,:,:,:]
#            avg[:,:,:]=avg[:,:,:]+mdlData[i,:,:,:]
#        avg=avg/float(numMDLs)
#        modelData[numMDLs,:,:,:]=avg[:,:,:]     # store the model-ensemble data
#        # THESE ARE NOT USED.  WILL DELETE AFTER TESTING
#        # i0mdl=0
#        # i1mdl=numMDLs
#        numMDLs=numMDLs+1 
#        mdlName.append('ENS')
#        print 'Eval mdl-mean timeseries for the obs periods: modelData.shape= ',modelData.shape
    # GOODALE:  This ensemble code should be refactored into process.py module since it's purpose is data processing

    # Processing complete
    print 'data_prep is completed: both obs and mdl data are re-gridded to a common analysis grid'
    return numOBSs, numMDLs, nT, ngrdY, ngrdX, Times, lons, lats, obsData, modelData, obsList, mdlList
