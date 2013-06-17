#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
import calendar
import os
from datetime import datetime as datetime
import urllib

import storage.files as files
import toolkit.process as process
import utils.misc

class BoundingBox(object):
    
    def __init__(self, latMin, lonMin, latMax, lonMax):
        self.latMin = latMin
        self.lonMin = lonMin
        self.latMax = latMax
        self.lonMax = lonMax
        
        
class SubRegion(BoundingBox):
    
    def __init__(self, name, latMin, lonMin, latMax, lonMax):
        BoundingBox.__init__(self, latMin, lonMin, latMax, lonMax)
        self.name = name
        
class GridBox(BoundingBox):
    
    def __init__(self, latMin, lonMin, latMax, lonMax, lonStep, latStep):
        BoundingBox.__init__(self, latMin, lonMin, latMax, lonMax)
        self.lonStep = lonStep
        self.latStep = latStep
        self.lonCount = int((self.lonMax - self.lonMin) / self.lonStep) + 1
        self.latCount = int((self.latMax - self.latMin) / self.latStep) + 1

class JobProperties(object):
    
    def __init__(self, workDir, cacheDir, spatialGrid, temporalGrid, gridLonStep=None, gridLatStep=None, outputFile='false', 
                 latMin=None, latMax=None, lonMin=None, lonMax=None, startDate=None, endDate=None):
        self.workDir = os.path.abspath(workDir)
        self.cacheDir = os.path.abspath(cacheDir)
        self.spatialGrid = spatialGrid
        self.temporalGrid = temporalGrid
        
        if gridLonStep and gridLatStep:
            self.gridLonStep = float(gridLonStep)
            self.gridLatStep = float(gridLatStep)
        else:
            self.gridLonStep = None
            self.gridLatStep = None
        
        # Support for both User provided Dates, and Interactive Date Collection
        if startDate and endDate:
            self.startDate = datetime.strptime(startDate, '%Y%m%d')
            self.endDate = datetime.strptime(endDate, '%Y%m%d')
        else:
            self.startDate = None
            self.endDate = None

        if outputFile.lower() == 'false':
            self.writeOutFile = 'no'
        elif outputFile.lower() == 'netcdf':
            self.writeOutFile = 'nc'
        else:
            self.writeOutFile = False

        if self.spatialGrid.lower() == 'user':
            self.latMin = float(latMin)
            self.latMax = float(latMax)
            self.lonMin = float(lonMin)
            self.lonMax = float(lonMax)

    def obsDatasetCount(self):
        self.parameterList = self.obsParamId.split(',')
        count = len(self.paramterList)
        return count
    
class Model(object):
    
    def __init__(self, *args, **kwargs):
        """
        This Class can be instantiated with either a single filename or a dictionary of parameters.
        If a single filename is used, then the class will use internal methods to parse the file 
        and set the needed attributes.
        
        Input (single file)::
            filename - Full path to a local model file
        
        Input (keyword dictionary)::
            filename - Full path to a local model file
            latVariable - the name of the latitude variable within the file
            lonVariable - the name of the longitude variable within the file
            timeVariable - the name of the time variable within the file
            timeStep - description of the time between readings ['hourly','daily','monthly','annual']
            varName - name of the variable to analyze within the model
            precipFlag - boolean telling if this is precipitation data
        
        Output::
            Model object
        """
        if len(args) == 1:
            self.filename = args[0]
            self.name = os.path.basename(self.filename)
            self.processModelFile()
            self.precipFlag = False
        if len(kwargs) == 7:
            self.filename = kwargs['filename']
            self.name = os.path.basename(self.filename)
            self.latVariable = kwargs['latVariable']
            self.lonVariable = kwargs['lonVariable']
            self.timeVariable = kwargs['timeVariable']
            self.timeStep = kwargs['timeStep']
            self.varName = kwargs['varName']
            self.times, _ = process.getModelTimes(self.filename, self.timeVariable)
            self.minTime = min(self.times)
            self.maxTime = max(self.times)
            self.setLatitudeRange()
            self.setLongitudeRange()
    
            if kwargs['precipFlag'] == 'True':
                self.precipFlag = True
            else:
                self.precipFlag = False
        
    
    def setLatitudeRange(self):
        self.latMin, self.latMax = files.getVariableRange(self.filename, self.latVariable)
    
    def setLongitudeRange(self):
        self.lonMin, self.lonMax = files.getVariableRange(self.filename, self.lonVariable)
    
    def processModelFile(self):
        """ This series of steps should be consolidated to merely pass around a PyNIO object
            Until then we will be opening the same file repeatedly.  And clearly wasting I/O
        """
        self.latVariable, self.lonVariable, self.latMin, self.latMax, self.lonMin, self.lonMax = files.findLatLonVarFromFile(self.filename)
        self.timeVariable, modelVariables = files.findTimeVariable(self.filename)
        self.times, self.timeStep = process.getModelTimes(self.filename, self.timeVariable)
        self.varName = utils.misc.askUserForVariableName(modelVariables, "analysis")
        self.minTime = min(self.times)
        self.maxTime = max(self.times)
        
class Parameter(object):
    def __init__(self, param_id, shortName=None, description=None, endDate=None ):
        pass

class RCMED(object):
    def __init__(self):
        pass
    
    def retriveData(self, parameter, dataBounds, timeStep=None):
        # Returns the data
        pass
    
    @classmethod
    def isoDateString(self, pythonDate):
        isoDate = pythonDate.strftime("%Y%m%dT%H%MZ")
        return isoDate
    
    @classmethod
    def jplUrl(self, datasetID, paramID, latMin, latMax, lonMin, lonMax, startTime, endTime, cachedir, timestep):
        """ This will create a valid RCMED Query URL used to contact the JPL RCMED Instance"""
        JPL_RCMED_URL = 'http://rcmes.jpl.nasa.gov/query-api/query.php?'

        """This block will expand the Time Range based on the timestep to ensure complete temporal range coverage"""
        expanded = False
        if timestep.lower() == 'monthly':
            if startTime.day != 1:
                # Clean the startTime
                startTimeString = startTime.strftime('%Y%m%d')
                normalInputDatetimeString = startTimeString[:6] + '01'
                startTime = datetime.strptime(normalInputDatetimeString, '%Y%m%d')
                expanded = True
            
            lastDayOfMonth = calendar.monthrange(endTime.year, endTime.month)[1]
            if endTime.day != lastDayOfMonth:
                # Clean the endTime
                endTimeString = endTime.strftime('%Y%m%d')
                endTimeString = endTimeString[:6] + str(lastDayOfMonth)
                endTime = datetime.strptime(endTimeString, '%Y%m%d')
                expanded = True
    
        elif timestep.lower() == 'daily':
            if startTime.hour != 0 or startTime.minute != 0 or startTime.second != 0:
                datetimeString = startTime.strftime('%Y%m%d%H%M%S')
                normalDatetimeString = datetimeString[:8] + '000000'
                startTime = datetime.strptime(normalDatetimeString, '%Y%m%d%H%M%S')
                expanded = True
            
            endTimeString = endTime.strftime('%Y%m%d%H%M%S')
            endTimeString = endTimeString[:8] + '235959'
            endTime = datetime.strptime(endTimeString, '%Y%m%d%H%M%S')
        
        if expanded:
            print "Your date range selection has been expanded to ensure we return the largest number of available readings."
            print "The new date Range is:  %s  through  %s" % (startTime.strftime('%Y-%m-%d %H:%M:%S'), endTime.strftime('%Y-%m-%d %H:%M:%S'))
        
        
        timeStart = self.isoDateString(startTime)
        timeEnd = self.isoDateString(endTime)
        query = [('datasetId',datasetID), ('parameterId',paramID), ('latMin',latMin), ('latMax',latMax),
                 ('lonMin', lonMin), ('lonMax',lonMax), ('timeStart', timeStart), ('timeEnd', timeEnd)]
        queryURL = urllib.urlencode(query)
        urlRequest = JPL_RCMED_URL+queryURL
        
        return urlRequest

class RCMEDDataset(object):
    
    def __init__(self, obsDatasetId, obsParamId, obsTimeStep):
        self.datasetId = obsDatasetId
        self.parameterId = obsParamId
        self.timeStep = obsTimeStep