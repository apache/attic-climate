import os
from datetime import datetime as datetime

import storage.files as files
import toolkit.process as process

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
    
    def __init__(self, workDir, cacheDir, startDate, endDate, spatialGrid, temporalGrid, gridLonStep, gridLatStep, outputFile, latMin=None, latMax=None, lonMin=None, lonMax=None):
        self.workDir = os.path.abspath(workDir)
        self.cacheDir = os.path.abspath(cacheDir)
        self.startDate = datetime.strptime(startDate, '%Y%m%d')
        self.endDate = datetime.strptime(endDate, '%Y%m%d')
        self.spatialGrid = spatialGrid
        self.temporalGrid = temporalGrid
        self.gridLonStep = float(gridLonStep)
        self.gridLatStep = float(gridLatStep)

        if outputFile.lower() == 'false':
            self.writeOutFile = False
        elif outputFile.lower() == 'binary':
            self.writeOutFile = 'binary'
        elif outputFile.lower() == 'netcdf':
            self.writeOutFile = 'netcdf'
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
    
    def __init__(self, filename, latVariable, lonVariable, timeVariable, timeStep, varName, precipFlag):
        self.filename = filename
        self.latVariable = latVariable
        self.lonVariable = lonVariable
        self.timeVariable = timeVariable
        self.timeStep = timeStep
        self.varName = varName
        self.times = process.getModelTimes(self.filename, self.timeVariable)
        self.minTime = min(self.times)
        self.maxTime = max(self.times)
        self.setLatitudeRange()
        self.setLongitudeRange()
    
        if precipFlag == 'True':
            self.precipFlag = True
        else:
            self.precipFlag = False
        
    
    def setLatitudeRange(self):
        self.latMin, self.latMax = files.getVariableRange(self.filename, self.latVariable)
    
    def setLongitudeRange(self):
        self.lonMin, self.lonMax = files.getVariableRange(self.filename, self.lonVariable)
        
class Parameter(object):
    def __init__(self, param_id, shortName=None, description=None, endDate=None ):
        pass

class RCMED(object):
    def __init__(self):
        pass
    
    def retriveData(self, parameter, dataBounds, timeStep=None):
        # Returns the data

        pass

class RCMEDDataset(object):
    
    def __init__(self, obsDatasetId, obsParamId, obsTimeStep):
        self.datasetId = obsDatasetId
        self.parameterId = obsParamId
        self.timeStep = obsTimeStep