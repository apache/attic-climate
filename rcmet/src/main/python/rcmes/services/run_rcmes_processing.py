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
sys.path.append('../../.')
from bottle import route, request
import json
import cli.do_rcmes_processing_sub as awesome
import time
import datetime
import os
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

###########################################################
##OPEN FOR DISCUSSION
titleOption = 'default'   #this means that ' model vs obs :' will be used
plotFileNameOption = 'default'  #another good option we can use.
###########################################################

@route('/rcmes/run/', method='POST')
def rcmes_go():
    print "**********\nBEGIN RCMES2.0_RUN\n**********"
    print 'cachedir', cachedir
    print 'workdir', workdir
    
    try:
        if not os.path.exists(cachedir):
            os.makedirs(cachedir)
    except Error as e:
        print "I/O error({0}: {1}".format(e.errno, e.strerror)
        sys.exit(1)

    obsDatasetId = int(request.POST.get('obsDatasetId', '').strip())
    print 'obsDatasetId', obsDatasetId
    obsParameterId = int(request.POST.get('obsParameterId', '').strip())
    print 'obsParameterId', obsParameterId

    #reformat DateTime after pulling it out of the POST
    POSTstartTime = str(request.POST.get('startTime', '').strip())
    startTime = datetime.datetime.fromtimestamp(time.mktime(time.strptime(POSTstartTime, time_format_new)))
    print 'startTime', startTime
    #reformat DateTime after pulling it out of the POST
    POSTendTime = str(request.POST.get('endTime', '').strip())
    endTime = datetime.datetime.fromtimestamp(time.mktime(time.strptime(POSTendTime, time_format_new)))
    print 'endTime', endTime

    latMin = float(request.POST.get('latMin', '').strip())
    print 'latMin', latMin
    latMax = float(request.POST.get('latMax', '').strip())
    print 'latMax', latMax 
    lonMin = float(request.POST.get('lonMin', '').strip())
    print 'lonMin', lonMin
    lonMax = float(request.POST.get('lonMax', '').strip())
    print 'lonMax', lonMax

    filelist = [request.POST.get('filelist', '').strip()]
    print 'filelist', filelist[0]

    modelVarName = str(request.POST.get('modelVarName', '').strip())
    print 'modelVarName', modelVarName
    precipFlag = request.POST.get('precipFlag', '').strip()
    print 'precipFlag', precipFlag
    modelTimeVarName = str(request.POST.get('modelTimeVarName', '').strip())
    print 'modelTimeVarName', modelTimeVarName
    modelLatVarName = str(request.POST.get('modelLatVarName', '').strip())
    print 'modelLatVarName', modelLatVarName
    modelLonVarName = str(request.POST.get('modelLonVarName', '').strip())
    print 'modelLonVarName', modelLonVarName

    regridOption = str(request.POST.get('regridOption', '').strip())
    print 'regridOption', regridOption
    timeRegridOption = str(request.POST.get('timeRegridOption', '').strip())
    print 'timeRegridOption', timeRegridOption
    seasonalCycleOption = request.POST.get('seasonalCycleOption', '').strip()
    print 'seasonalCycleOption', seasonalCycleOption
    metricOption = str(request.POST.get('metricOption', '').strip())
    print 'metricOption', metricOption    
    
    settings = {"cacheDir": cachedir, "workDir": workdir, "fileList": filelist}
    params = {"obsDatasetId": obsDatasetId, "obsParamId": obsParameterId, 
              "startTime": startTime, "endTime": endTime, "latMin": latMin, 
              "latMax": latMax, "lonMin": lonMin, "lonMax": lonMax}
    model = {"varName": modelVarName, "timeVariable": modelTimeVarName, 
             "latVariable": modelLatVarName, "lonVariable": modelLonVarName}
    mask = {"latMin": latMin, "latMax": latMax, "lonMin": lonMin, "lonMax": lonMax}
    options = {"regrid": regridOption, "timeRegrid": timeRegridOption, 
               "seasonalCycle": seasonalCycleOption, "metric": metricOption, 
               "plotTitle": titleOption, "plotFilename": plotFileNameOption, 
               "mask": maskOption, "precip": precipFlag}
    
    awesome.do_rcmes(settings, params, model, mask, options)
    
    model_path = os.path.join(workdir, plotFileNameOption + "model.png")
    obs_path = os.path.join(workdir, plotFileNameOption + "obs.png")
    comp_path = os.path.join(workdir, plotFileNameOption + ".png")

    product_dict = {'modelPath':model_path,
                    'obsPath': obs_path,
                    'comparisonPath':comp_path}
    
    #Extra Code in case bottle has an issue with my Dictionary
    #json_output = json.dumps(product_dict, sort_keys=True, indent=4)
    
    return product_dict
