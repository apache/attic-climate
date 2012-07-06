#!/usr/local/bin/python

import sys
sys.path.append('../lib')
from bottle import route, request
#import Nio
import json
import do_rcmes_processing_sub as awesome
import time
import datetime
time_format_new = '%Y-%m-%d %H:%M:%S'

#Static Default params
cachedir = '/tmp/rcmet/cache/'
workdir = '/tmp/rcmet/'
precipFlag =False
seasonalCycleOption=0
maskOption=0         # int (=1 if set)
maskLatMin=0         # float (only used if maskOption=1)
maskLatMax=0         # float (only used if maskOption=1)
maskLonMin=0         # float (only used if maskOption=1)
maskLonMax=0         # float (only used if maskOption=1)

###########################################################
##OPEN FOR DISCUSSION
titleOption = 'default'   #this means that ' model vs obs :' will be used
plotFileNameOption = 'default'  #another good option we can use.
###########################################################

@route('/rcmes/run/', method='POST')
def rcmes_go():
    #cachedir = request.POST.get('cachedir', '').strip()
    print 'cachedir '+cachedir
    #workdir = request.POST.get('workdir', '').strip()
    print 'workdir '+workdir
    obsDatasetId = int(request.POST.get('obsDatasetId', '').strip())
    print 'obsDatasetId '+str(obsDatasetId)
    obsParameterId = int(request.POST.get('obsParameterId', '').strip())
    print 'obsParameterId '+str(obsParameterId)
    #reformat DateTime after pulling it out of the POST
    POSTstartTime = str(request.POST.get('startTime', '').strip())
    startTime = datetime.datetime.fromtimestamp(time.mktime(time.strptime(POSTstartTime, time_format_new)))
    print 'startTime '+str(startTime)
    #reformat DateTime after pulling it out of the POST
    POSTendTime = str(request.POST.get('endTime', '').strip())
    endTime = datetime.datetime.fromtimestamp(time.mktime(time.strptime(POSTendTime, time_format_new)))
    print 'endTime '+str(endTime)
    latMin = float(request.POST.get('latMin', '').strip())
    print 'latMin '+str(latMin)
    latMax = float(request.POST.get('latMax', '').strip())
    print 'latMax '+str(latMax) 
    lonMin = float(request.POST.get('lonMin', '').strip())
    print 'lonMin '+str(lonMin)
    lonMax = float(request.POST.get('lonMax', '').strip())
    print 'lonMax '+str(lonMax)
    filelist = [request.POST.get('filelist', '').strip()]
    print 'filelist '+filelist[0]
    modelVarName = str(request.POST.get('modelVarName', '').strip())
    print 'modelVarName'+modelVarName
    #precipFlag = request.POST.get('precipFlag', '').strip()
    print 'precipFlag '+str(precipFlag)
    modelTimeVarName = str(request.POST.get('modelTimeVarName', '').strip())
    print 'modelTimeVarName '+modelTimeVarName
    modelLatVarName = str(request.POST.get('modelLatVarName', '').strip())
    print 'modelLatVarName '+modelLatVarName
    modelLonVarName = str(request.POST.get('modelLonVarName', '').strip())
    print 'modelLonVarName '+modelLonVarName
    regridOption = str(request.POST.get('regridOption', '').strip())
    print 'regridOption '+regridOption
    timeRegridOption = str(request.POST.get('timeRegridOption', '').strip())
    print 'timeRegridOption '+timeRegridOption
    #seasonalCycleOption = request.POST.get('seasonalCycleOption', '').strip()
    print 'seasonalCycleOption '+str(seasonalCycleOption)
    metricOption = str(request.POST.get('metricOption', '').strip())
    print 'metricOption '+str(metricOption)
    #titleOption = str(request.POST.get('titleOption', '').strip())
    
    #plotFileNameOption = str(request.POST.get('plotFileNameOption', '').strip())
    
    #maskOption = request.POST.get('maskOption', '').strip()
    
    #maskLatMin = request.POST.get('maskLatMin', '').strip()
    
    #maskLatMax = request.POST.get('maskLatMax', '').strip()
    
    #maskLonMin = request.POST.get('maskLonMin', '').strip()
    
    #maskLonMax = request.POST.get('maskLonMax', '').strip()
    
    
    
    
    awesome.do_rcmes(cachedir, workdir, obsDatasetId, obsParameterId, startTime, endTime, latMin, latMax, lonMin, lonMax, filelist, modelVarName, precipFlag, modelTimeVarName, modelLatVarName, modelLonVarName, regridOption, timeRegridOption,seasonalCycleOption,metricOption,titleOption,plotFileNameOption,maskOption,maskLatMin,maskLatMax,maskLonMin,maskLonMax)
    
    model_path = workdir+plotFileNameOption+'model.000001'+'.png'
    obs_path = workdir+plotFileNameOption+'obs.000001'+'.png'
    comp_path = workdir+plotFileNameOption+'.000001.png'
    
    product_dict = {'modelPath':model_path,
                    'obsPath': obs_path,
                    'comparisonPath':comp_path}
    
    #Extra Code in case bottle has an issue with my Dictionary
    #json_output = json.dumps(product_dict, sort_keys=True, indent=4)
    
    return product_dict
