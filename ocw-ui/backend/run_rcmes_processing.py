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
"""Module used to launch the RESTful API"""
import sys
import ast
sys.path.append('../../.')
from bottle import route, request

from classes import GridBox, JobProperties, Model
from storage import db
from storage.rcmed import getParams
from utils.misc import msg, readSubRegionsFile
from toolkit.do_data_prep import prep_data
from toolkit import process
from toolkit.metrics_kyo import calculate_metrics_and_make_plots

import ConfigParser
import json
import cli.do_rcmes_processing_sub as awesome
import time
import datetime
import os
import numpy as np
import numpy.ma as ma
time_format_new = '%Y-%m-%d %H:%M:%S'

#Static Default params
cachedir = '/tmp/rcmet/cache/'
workdir = '/tmp/rcmet/'
precipFlag =False
seasonalCycleOption=0
maskOption=False
maskLatMin=0         # float (only used if maskOption=1)
maskLatMax=0         # float (only used if maskOption=1)
maskLonMin=0         # float (only used if maskOption=1)
maskLonMax=0         # float (only used if maskOption=1)

# Hard-coded configuration/settings values that 
# are not yet mapped to UI settings
precipFlag=False   # 
maskOption=True    # To match rcmet.py line 221
spatialGrid='user' # Eventually, use options['regrid']
gridLonStep=0.5
gridLatStep=0.5

###########################################################
##OPEN FOR DISCUSSION
titleOption = 'default'   #this means that ' model vs obs :' will be used
plotFileNameOption = 'default'  #another good option we can use.
###########################################################

@route('/rcmes/run/')
def rcmes_go():

    print "**********\nBEGIN RCMES2.0_RUN\n**********"
    evalWorkDir = datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    evalPath = os.path.join( workdir, evalWorkDir )
    os.makedirs(evalPath)
    print 'evalPath', evalPath
    
    # Attempt to create the cache dir if it does not exist`
    try:
        if not os.path.exists(cachedir):
            os.makedirs(cachedir)
    except Error as e:
        print "I/O error({0}: {1}".format(e.errno, e.strerror)
        sys.exit(1)
    
    # Print request variables as received
    msg('Request Variables', {k:request.query.get(k) for k in request.query.keys()})

    # Obtain the observational dataset and parameter ids from the request
    obsDatasetIds = ast.literal_eval(request.query.get('obsDatasetIds', '[]'))
    obsParameterIds = ast.literal_eval(request.query.get('obsParameterIds', '[]'))


    # Reformat start date/time after pulling it out of the request
    requestStartTime = str(request.query.get('startTime', '').strip())
    startTime = datetime.datetime.fromtimestamp(time.mktime(time.strptime(requestStartTime, time_format_new)))
    
    # Reformat end date/time after pulling it out of the request
    requestEndTime = str(request.query.get('endTime', '').strip())
    endTime = datetime.datetime.fromtimestamp(time.mktime(time.strptime(requestEndTime, time_format_new)))

    # Obtain the geographical boundaries from the request
    latMin = float(request.query.get('latMin', '').strip())
    latMax = float(request.query.get('latMax', '').strip())
    lonMin = float(request.query.get('lonMin', '').strip())
    lonMax = float(request.query.get('lonMax', '').strip())

    # Obtain the list of model files from the request
    filelist = ast.literal_eval(request.query.get('filelist', '[]'))
    
    # Obtain the evaluation variable name info for each model from the request
    modelVarNames = ast.literal_eval(request.query.get('modelVarName', '[]'))
    
    # Obtain the time variable name info for each model from the request
    modelTimeVarNames = ast.literal_eval(request.query.get('modelTimeVarName', '[]'))
    
    # Obtain the lat variable name info for each model from the request
    modelLatVarNames = ast.literal_eval(request.query.get('modelLatVarName', '[]'))    
    modelLonVarNames = ast.literal_eval(request.query.get('modelLonVarName', ''))
    
    # Obtain regrid configuration info from the request
    regridOption = str(request.query.get('regridOption', '').strip())
    timeRegridOption = str(request.query.get('timeRegridOption', '').strip())
   
    # Parse subregion information from the request
    subRegionFile = str(request.query.get('subregionFile','').strip())
   
    # Parse additional options from the request
    seasonalCycleOption = request.query.get('seasonalCycleOption', '').strip()
    metricOption = str(request.query.get('metricOption', '').strip())
    
    # Build dicts of extracted request information
    settings = {"cacheDir": cachedir, "workDir": workdir, "fileList": filelist}
    params   = {"obsDatasetIds": obsDatasetIds, "obsParamIds": obsParameterIds, 
                "startTime": startTime, "endTime": endTime, "latMin": latMin, 
                "latMax": latMax, "lonMin": lonMin, "lonMax": lonMax}
    models   = {"varNames": modelVarNames, "timeVariables": modelTimeVarNames, 
                "latVariables": modelLatVarNames, "lonVariables": modelLonVarNames}
    mask     = {"latMin": latMin, "latMax": latMax, "lonMin": lonMin, 
                "lonMax": lonMax}
    options  = {"regrid": regridOption, "timeRegrid": timeRegridOption, 
                "seasonalCycle": seasonalCycleOption, "metric": metricOption, 
                "plotTitle": titleOption, "plotFilename": plotFileNameOption, 
                "mask": maskOption, "precip": precipFlag}
    
    # Include optional information
    options['subRegionFile'] = subRegionFile if subRegionFile != '' else False
    
    
    # Summarize what was extracted from the request
    msg('Parsed Evaluation Criteria: ---------')
    msg('Settings',  settings, 2)
    msg('Parameters',params, 2)
    msg('Models',    models, 2)
    msg('Mask',      mask, 2)
    msg('Options',   options, 2)
    
    # Parse the provided subregion data
    if options['subRegionFile']:
        # Parse the Config file
        subRegions = readSubRegionsFile(options['subRegionFile'])
        msg("Parsed SubRegions", subRegions)
    
    # Create a JobProperties object with the information
    # extracted from the request
    jobProperties = JobProperties(
        settings['workDir'],
        settings['cacheDir'],
        spatialGrid,
        options['timeRegrid'],
        latMin=params['latMin'], # only used if spatial grid ='user'
        latMax=params['latMax'], # only used if spatial grid ='user'
        lonMin=params['lonMin'], # only used if spatial grid ='user'
        lonMax=params['lonMax'], # only used if spatial grid ='user'
        startDate=params['startTime'].strftime("%Y%m%d"),
        endDate=params['endTime'].strftime("%Y%m%d"))
        
        
    # Create a GridBox object with the spatial information
    # extracted from the request
    gridBox = GridBox(params['latMin'],
        params['lonMin'],
        params['latMax'],
        params['lonMax'],
        gridLonStep,
        gridLatStep)
        
    # Prepare requested model files
    eval_models = []
    for i in xrange(len(settings['fileList'])):
        # use getModelTimes(modelFile,timeVarName) to generate the 
        # modelTimeStep and time list
        _ , timestep = process.getModelTimes(
            settings['fileList'][i],
            models['timeVariables'][i])
            
        modelInfo = {
            'filename':     settings['fileList'][i],
            'latVariable':  models['latVariables'][i],
            'lonVariable':  models['lonVariables'][i],
            'timeVariable': models['timeVariables'][i],
            'varName':      models['varNames'][i],
            'timeStep':     timestep,
            'precipFlag':   options['precip']
        }
        
        msg("Built model info dict for {0}".format(settings['fileList'][i]),
            modelInfo)

        model = Model(**modelInfo)
        eval_models.append(model)
        
    msg("Prepared {0} models".format(len(eval_models)))
    
    # Prepare requested observational data
    # Obtain dataset metadata from RCMED Query Service
    obs_timesteps = []
    for i in xrange(len(params['obsDatasetIds'])):
        dId = params['obsDatasetIds'][i]
        pId = params['obsParamIds'][i]
        query_service_url= 'http://rcmes.jpl.nasa.gov/query-api/query.php?datasetId={0}&parameterId={1}'.format(dId,pId)
        msg("Obtaining dataset information from", query_service_url)
        obs_timesteps.append(db.get_param_info(query_service_url)[1])
    
    # Build dict of dataset metadata
    obsInfo = {
        'obsDatasetId': params['obsDatasetIds'],
        'obsParamId':   params['obsParamIds'],
        'obsTimeStep':  obs_timesteps
    }
    
    # Get parameter listing from the database
    params = getParams()
    
    # Build the list of observational datasets that exist in RCMED
    eval_datasets = []
    for param_id in obsInfo['obsParamId']:
        for param in params:
            if param['parameter_id'] == int(param_id):
                eval_datasets.append(param)
    
    
    msg("Observation Info", obsInfo)
    msg("Observation Dataset List", eval_datasets)


    # At this point, all of the input parameters from the UI have
    # been pre-processed and formatted. It now remains to invoke
    # some series of processing steps to generate the requested
    # output. 
    #
    # TODO: Break down the following processing into more modular
    # discrete processing steps whose composition could then be
    # determined by providing additional configuration options to
    # the user via the UI.
    
    msg('Evaluation Output: ------------------')
    numOBSs, numMDLs, nT, ngrdY, ngrdX, Times, lons, lats, obsData, modelData, obsList, mdlName = prep_data(jobProperties,eval_datasets,gridBox,eval_models)
    
    msg('numOBSs',numOBSs)
    msg('numMDLs',numMDLs)
    msg('nT',nT)
    msg('ngrdY',ngrdY)
    msg('ngrdX',ngrdX)
    msg('Times',Times)
    msg('lons',lons)
    msg('lats',lats)
    msg('obsData Length',len(obsData))
    msg('modelData Length',len(modelData))
    msg('obsList',obsList)
    msg('mdlName',mdlName)
    
    # Prepare SubRegion data structures
    if options['subRegionFile']:
        numSubRgn = len(subRegions)
        msg("Processing {0} sub regions...".format(numSubRgn))
        if numSubRgn > 0:
            subRgnName = [ x.name   for x in subRegions ]
            subRgnLon0 = [ x.lonMin for x in subRegions ]
            subRgnLon1 = [ x.lonMax for x in subRegions ]
            subRgnLat0 = [ x.latMin for x in subRegions ]
            subRgnLat1 = [ x.latMax for x in subRegions ]
            # compute the area-mean timeseries for all subregions.
            #   the number of subregions is usually small and memory usage 
            #   is usually not a concern
            obsRgn = ma.zeros((numOBSs, numSubRgn, nT))
            mdlRgn = ma.zeros((numMDLs, numSubRgn, nT))
            
            print 'Enter area-averaging: mdlData.shape, obsData.shape ', modelData.shape, obsData.shape
            print 'Use Latitude/Longitude Mask for Area Averaging'
            for n in np.arange(numSubRgn):
                # Define mask using regular lat/lon box specified by users ('mask=True' defines the area to be excluded)
                maskLonMin = subRgnLon0[n] 
                maskLonMax = subRgnLon1[n]
                maskLatMin = subRgnLat0[n]
                maskLatMax = subRgnLat1[n]
                mask = np.logical_or(np.logical_or(lats <= maskLatMin, lats >= maskLatMax), 
                                    np.logical_or(lons <= maskLonMin, lons >= maskLonMax))
                # Calculate area-weighted averages within this region and store in a new list
                for k in np.arange(numOBSs):           # area-average obs data
                    Store = []
                    for t in np.arange(nT):
                        Store.append(process.calc_area_mean(obsData[k, t, :, :], lats, lons, mymask = mask))
                    obsRgn[k, n, :] = ma.array(Store[:])
                for k in np.arange(numMDLs):           # area-average mdl data
                    Store = []
                    for t in np.arange(nT):
                        Store.append(process.calc_area_mean(modelData[k, t, :, :], lats, lons, mymask = mask))
                    mdlRgn[k, n, :] = ma.array(Store[:])
                Store = []                               # release the memory allocated by temporary vars
    
    # Call combined metrics/plotting function
    print options['subRegionFile']
    print options['subRegionFile'] == False
    calculate_metrics_and_make_plots(
        models['varNames'][0], # won't work if models have different var names among themselves
        evalPath,
        lons, 
        lats, 
        obsData, 
        modelData, 
        (obsRgn if options['subRegionFile'] != False else None),  # Depends on presence of subregion info
        (mdlRgn if options['subRegionFile'] != False else None),  # Depends on presence of subregion info
        obsList, 
        mdlName, 
        (True if options['subRegionFile'] != False else False),   # Depends on presence of subregion info
        (subRgnLon0 if options['subRegionFile'] != False else None), 
        (subRgnLon1 if options['subRegionFile'] != False else None), 
        (subRgnLat0 if options['subRegionFile'] != False else None), 
        (subRgnLat1 if options['subRegionFile'] != False else None))
        
    # At this point, all of the plots have been written to various files
    
    # Obsolete invocation
    #awesome.do_rcmes(settings, params, models, mask, options)
    
    # Prepare a response with the results of the evaluation

    # TODO: This may be obsolete, if so, it should be removed:
    msg('Evaluation Complete, Preparing Response...')
    model_path = os.path.join(workdir, plotFileNameOption + "model.png")
    obs_path = os.path.join(workdir,   plotFileNameOption + "obs.png")
    comp_path = os.path.join(workdir,  plotFileNameOption + ".png")


    product_dict = {'modelPath':model_path,
                    'obsPath': obs_path,
                    'comparisonPath':comp_path,
                    'evalWorkDir':evalWorkDir}
    
    #Extra Code in case bottle has an issue with my Dictionary
    #json_output = json.dumps(product_dict, sort_keys=True, indent=4)
    
    if (request.query.callback):
        return"%s(%s)" % (request.query.callback, product_dict)
    else:
        return product_dict
