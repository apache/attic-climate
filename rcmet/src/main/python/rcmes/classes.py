import os
from datetime import datetime as datetime

import storage.files as files
import toolkit.process as process

class BoundingBox(object):
    
    def __init__(self, latMin, lonMin, latMax, lonMax):
        self.latMin = latMin
        self.lonMin = lonMin
        self.latMax = latMax
        self.lonMin = lonMax
        
        
class SubRegion(object):
    
    def __init__(self, name, bbox):
        self.name = name
        self.bbox = bbox

class Settings(object):
    
    def __init__(self, workDir, cacheDir, startDate, endDate, spatialGrid, gridLonStep, gridLatStep):
        self.workDir = os.path.abspath(workDir)
        self.cacheDir = os.path.abspath(cacheDir)
        self.startDate = datetime.strptime(startDate, '%Y%m%d')
        self.endDate = datetime.strptime(endDate, '%Y%m%d')
        self.spatialGrid = spatialGrid
        self.gridLonStep = float(gridLonStep)
        self.gridLatStep = float(gridLatStep)
        """
        TODO:  These will be split apart into Object Attributes
        self.latMin=config['latmin']
        self.latMax=config['latmax']
        self.lonMin=config['lonmin']
        self.lonMax=config['lonmax']
        self.obsDatasetId=config['obsdatasetid']
        self.obsParamId=config['obsparamid']
        self.obsTimeStep=config['obstimestep']
        self.startTime=config['starttime']
        self.endTime=config['endtime']
        self.mask=config['mask']

        if self.mask == 'True':
            self.maskLonMin=config['masklonmin']
            self.maskLonMax=config['masklonmax']
            self.maskLatMin=config['masklatmin']
            self.maskLatMax=config['masklatmax']
        """

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