

import sys
import os

import subprocess
import numpy as np
import numpy.ma as ma
import Nio
import storage.db as db
import storage.files_20 as files
import process_v12 as process

# TODO:  swap gridBox for Domain
def prep_data(settings, obsDatasetList, gridBox, modelList, subRegions=None):
    
    
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
    # Ising the GridBox Object
    latMin = gridBox.latMin
    latMax = gridBox.latMax
    lonMin = gridBox.lonMin
    lonMax = gridBox.lonMax
    naLats = gridBox.latCount
    naLons = gridBox.lonCount
    dLat = gridBox.latStep
    dLon = gridBox.lonStep
    mdlList = [model.filename for model in modelList]
    
    numSubRgn = len(subRegions)
    subRgnLon0 = [ x.lonMin for x in subRegions ]
    subRgnLon1 = [ x.lonMax for x in subRegions ]
    subRgnLat0 = [ x.latMin for x in subRegions ]
    subRgnLat1 = [ x.latMax for x in subRegions ]
    
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
    maskOption = True
    FoutOption = settings.writeOutFile



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
    yymm0 = startTime.strftime("%Y%m")
    yymm1 = endTime.strftime("%Y%m")
    print 'start & end eval period = ', yymm0, yymm1
    # check the number of obs & model data files
    numOBSs = len(obsList)
    numMDLs = len(mdlList)
    if numMDLs < 1: 
        print 'No input model data file. EXIT'; return -1         # no input mdl data file
    if numOBSs < 1: 
        print 'No input observation data file. EXIT'; return -1   # no input obs data file

    ## Part 1: retrieve observation data from the database and regrid them
    ##       NB. automatically uses local cache if already retrieved.

    print 'the number of observation datasets: ', numOBSs
    print obsList, obsDatasetId, obsParameterId, latMin, latMax, lonMin, lonMax, startTime, endTime, cachedir
    
    # preparation for spatial re-gridding: define the size of horizontal array of the target interpolation grid system (ngrdX and ngrdY)
    if regridOption == 'model':
        ifile = mdlList[0]
        typeF = 'nc'
        lats, lons, mTimes = files.read_lolaT_from_file(ifile, modelLatVarName, modelLonVarName, modelTimeVarName, typeF)
        
    elif regridOption == 'user':
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
        oLats, oLons, oLevs, oTimes, oData = db.extractData(obsDatasetId[n],
                                                                               obsParameterId[n],
                                                                               latMin, latMax,
                                                                               lonMin, lonMax,
                                                                               startTime, endTime,
                                                                               cachedir)
        
        # TODO: modify this if block with new metadata usage.
        if precipFlag == True and obsList[n][0:3] == 'CRU':
            oData = 86400.0 * oData
        #print 'Raw data ',oData[10,100,51:150]# return -1,-1,-1,-1  # missing data are read-in ok.
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
        
        print n,' time through loop, newObsTImes length is: ',len(newObsTimes)
        
        tmpOBS = 0.
        
        # check the consistency of temporally regridded obs data
        if n == 0:
            oldObsTimes = newObsTimes
        else:
            if oldObsTimes != newObsTimes:
                print 'temporally regridded obs data time levels do not match at ', n - 1, n
                print '%s Time through Loop' % (n+1)
                print 'oldObsTimes Count: %s' % len(oldObsTimes)
                print 'newObsTimes Count: %s' % len(newObsTimes)
                # TODO:  We need to handle these cases using Try Except Blocks or insert a sys.exit if appropriate
                return -1, -1, -1, -1
            else:
                oldObsTimes = newObsTimes
        # if everything's fine, append the spatially and temporally regridded data in the obs data array (obsData)
        regObsData.append(oData)

    # all obs datasets have been read-in and regridded. convert the regridded obs data from 'list' to 'array'
# also finalize 'obsTimes', the time cooridnate values of the regridded obs data.
    # NOTE: using 'list_to_array' assigns values to the missing points; this has become a problem in handling the CRU data.
    #       this problem disappears by using 'ma.array'.
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
    mdlName = []
    regridMdlData = []
    
    # extract the model names and store them in the list 'mdlName'
    for n in np.arange(numMDLs):
        name = mdlList[n][46:60]
        ii = 3  #TODO:  What does this 3 mean?
        i = 0
        print 'Input model name= ', name
        
        for i in np.arange(ii):
            if(name[i] == '-'): 
                ii = i

        name = name[0:ii]
        mdlName.append(name)
        
        # read model grid info, then model data
        ifile = mdlList[n]
        print 'ifile= ', ifile
        modelLats, modelLons, mTimes = files.read_lolaT_from_file(ifile, modelLatVarName, modelLonVarName, modelTimeVarName, typeF)
        mTime, mdlDat = files.read_data_from_one_file(ifile, modelVarName, modelTimeVarName, modelLats, typeF)
        mdlT = []
        mStep = len(mTimes)
        
        for i in np.arange(mStep):
            mdlT.append(mTimes[i].strftime("%Y%m"))
        
        # TODO: Is this an intersection operation in numpy?
        wh = (np.array(mdlT) >= yymm0) & (np.array(mdlT) <= yymm1)
        modelTimes = list(np.array(mTimes)[wh])
        mData = mdlDat[wh, :, :]
        
        # determine the dimension size from the model time and latitude data.
        nT = len(modelTimes)
        nmdlY = modelLats.shape[0]
        nmdlX = modelLats.shape[1]
        print 'nT, ngrdY, ngrdX = ', nT, ngrdY, ngrdX, min(modelTimes), max(modelTimes)
        # spatial regridding of the modl data
        tmpMDL = ma.zeros((nT, ngrdY, ngrdX))
        for t in np.arange(nT):
            tmpMDL[t, :, :] = process.do_regrid(mData[t, :, :], modelLats, modelLons, lats, lons)
        
        # temporally regrid the model data
        mData, newMdlTimes = process.calc_average_on_new_time_unit_K(tmpMDL, modelTimes, unit=timeRegridOption)
        tmpMDL = 0.
        
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
    
    # check consistency between the time levels of the model and obs data
    #   this is the final update of time levels: 'Times' and 'nT'
    if obsTimes != modelTimes:
        print 'time levels of the obs and model data are not consistent. EXIT'
        print 'obsTimes: %s' % obsTimes
        print 'modelTimes: %s' % modelTimes
        sys.exit()
    
    #  'Times = modelTimes = obsTimes' has been established and modelTimes and obsTimes will not be used hereafter. (de-allocated)
    Times = modelTimes; nT = len(modelTimes); modelTimes = 0; obsTimes = 0
    
    print 'Reading and regridding model data are completed'; print 'numMDLs, modelData.shape= ', numMDLs, modelData.shape
    # compute the simple multi-model ensemble if multiple modles are evaluated
    if numMDLs > 1:
        modelData=np.vstack([modelData,ma.average(modelData, axis=0).reshape(1,nT,ngrdY,ngrdX)])
        numMDLs = numMDLs + 1 
        mdlName.append('ENS')
        print 'Eval mdl-mean timeseries for the obs periods: modelData.shape= ', modelData.shape
    
    # convert model precip unit from mm/s to mm/d: Note that only applies to CORDEX for now
    #* Looks like cru3.1 is in mm/sec & TRMM is mm/day. Need to check and must be fixed as a part of the metadata plan.
    # TODO: get rid of this if block with new metadata usage

    if precipFlag == True:
        modelData = modelData * 86400.  # convert from kg/m^2/s into mm/day

    # (Optional) Part 5: area-averaging
    #      RCMET calculate metrics either at grid point or for area-means over a defined (masked) region.
    #      If area-averaging is selected, then a user have also selected how to define the area to average over.
    #      The options were:
    #              -define masked region using regular lat/lon bounding box parameters
    #              -read in masked region from file
    #         either i) Load in the mask file (if required)
    #             or ii) Create the mask using latlonbox  
    #           then iii) Do the area-averaging
    
    obsRgnAvg = ma.zeros((numOBSs, numSubRgn, nT))
    mdlRgnAvg = ma.zeros((numMDLs, numSubRgn, nT))
    
    if maskOption:  # i.e. define regular lat/lon box for area-averaging
        print 'Enter area-averaging: modelData.shape, obsData.shape ', modelData.shape, obsData.shape
        print 'Using Latitude/Longitude Mask for Area Averaging'
        for n in np.arange(numSubRgn):
            # Define mask using regular lat/lon box specified by users (i.e. ignore regions where mask = True)
            maskLonMin = subRgnLon0[n]
            maskLonMax = subRgnLon1[n]
            maskLatMin = subRgnLat0[n]
            maskLatMax = subRgnLat1[n]
            
            print "N: %s S: %s E: %s, W: %s" % (maskLatMax, maskLatMin, maskLonMax, maskLonMin)

            mask = np.logical_or(np.logical_or(lats <= maskLatMin, lats >= maskLatMax), 
                                 np.logical_or(lons <= maskLonMin, lons >= maskLonMax))

            # TODO:  The next two for loops can be refactored into a function that operates on model and obs data
            # Calculate area-weighted averages within this region and store in new lists: first average obs data (single time series)
            for k in np.arange(numOBSs):
                obsStore = []
                
                for t in np.arange(nT):
                    obsStore.append(process.calc_area_mean(obsData[k, t, :, :], lats, lons, mymask=mask))
                    
                obsRgnAvg[k, n, :] = ma.array(obsStore[:])
                
            for k in np.arange(numMDLs):
                mdlStore = []
                
                for t in np.arange(nT):
                    mdlStore.append(process.calc_area_mean(modelData[k, t, :, :], lats, lons, mymask=mask))
                    
                mdlRgnAvg[k, n, :] = ma.array(mdlStore)

        # TODO:  When the previous blocks get refactored these will be obsolete
        obsStore = []
        mdlStore = []

    else:       # no sub-regions. return 'null' variables for the regional mean timeseries
        obsRgnAvg = 0.0 
        mdlRgnAvg = 0.0
    
    # Output according to the output method options
    # Create a binary file of raw obs & model data and exit. If maskOption == True, also write area-averaged time series
    #   in the same data file.

    if FoutOption == 'binary':
        # write 1-d long and lat values
        fileName = workdir + '/lonlat' + '.bn'
        # clean up old file
        if(os.path.exists(fileName) == False):
            files.writeBN_lola(fileName, lons, lats)

        # write obs/model data values
        fileName = workdir + '/Tseries_' + modelVarName + '.bn'

        print 'Created monthly data file ', fileName, ' for user"s own processing'
        print 'The file includes monthly time series of ', numOBSs, ' obs and ', numMDLs, ' models ', nT, ' steps ', ngrdX, 'x', ngrdY, ' grids'
        
        if(os.path.exists(fileName) == True):
            cmnd = 'rm -f ' + fileName
            subprocess.call(cmnd, shell=True)

        files.writeBNdata(fileName, maskOption, numOBSs, numMDLs, nT, ngrdX, ngrdY, numSubRgn, obsData, modelData, obsRgnAvg, mdlRgnAvg)

    if FoutOption == 'netcdf':                    # print a netCDF file
        foName = workdir + '/Tseries'
        tempName = foName + '.' + 'nc'

        # if the file already exists, delete it before writing. otherwise, the process below will add values to the existing file.
        if(os.path.exists(tempName) == True):
            print "removing %s from the local filesystem, so it can be replaced..." % (tempName,)
            #TODO:  Look into an os function to rm this without using subprocess shell=True
            cmnd = 'rm -f ' + tempName; subprocess.call(cmnd, shell=True)

        files.writeNCfile(foName, lons, lats, obsData, modelData, obsRgnAvg, mdlRgnAvg)
    
    # Processing complete
    print 'data_prep is completed: both obs and mdl data are re-gridded to a common analysis grid'

    # return regridded variables
    return numOBSs, numMDLs, nT, ngrdY, ngrdX, Times, obsData, mdlData, obsRgnAvg, mdlRgnAvg, obsList, mdlName
