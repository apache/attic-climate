import os

import storage.files as files

class Settings(object):
    
    def __init__(self, config):
        
        self.workDir = os.path.abspath(config['workdir'])
        self.cacheDir = os.path.abspath(config['cachedir'])
        
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
    
    def __init__(self, config):
        self.filename = config['filename']
        self.latVariable = config['latvariable']
        self.lonVariable = config['lonvariable']
        self.timeVariable = config['timevariable']
        self.timeStep = config['timestep']
        self.varName = config['varname']
        
        self.setLatitudeRange()
        self.setLongitudeRange()
    
        if config['precipflag'] == 'True':
            self.precipFlag = True
        else:
            self.precipFlag = False
        
    
    def setLatitudeRange(self):
        self.latMin, self.latMax = files.getVariableRange(self.filename, self.latVariable)
    
    def setLongitudeRange(self):
        self.lonMin, self.lonMax = files.getVariableRange(self.filename, self.lonVariable)
