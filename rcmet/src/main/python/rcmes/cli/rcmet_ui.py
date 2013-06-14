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
""" 
    Step by Step Wizard that demonstrates how the underlying RCMES code can
    be used to generate climate dataset intercomparisons
"""
# Imports
# Native Python Module Imports
import sys

# RCMES Imports
from classes import Model, JobProperties, GridBox
import storage.rcmed as rcmed
import toolkit.metrics
import toolkit.do_data_prep
from utils import misc

def rcmetUI():
    """"
    Command Line User interface for RCMET.
    Collects user OPTIONS then runs RCMET to perform processing.
    
    Duplicates job of GUI.
    """
    print 'Regional Climate Model Evaluation System BETA'
    print "Querying RCMED for available parameters..."

    try:
        parameters = rcmed.getParams()
    except Exception:
        raise
        sys.exit()

    # Section 0: Collect directories to store RCMET working files.
    workDir, cacheDir = misc.getDirSettings()
    temporalGrid = misc.getTemporalGrid()
    spatialGrid = misc.getSpatialGrid()
    jobProperties = JobProperties(workDir, cacheDir, spatialGrid, temporalGrid)
    
    # Section 1a: Enter model file/s
    modelFiles = misc.getModelFiles()
    # Create a list of model objects for use later
    models = [Model(modelFile) for modelFile in modelFiles]

    # Section 3b: Select 1 Parameter from list
    for parameter in parameters:
        """( 38 ) - CRU3.1 Daily-Mean Temperature : monthly"""
        print "({:^2}) - {:<54} :: {:<10}".format(parameter['parameter_id'], parameter['longname'], parameter['timestep'])

    obsDatasetList = []
    validParamIds = [int(p['parameter_id']) for p in parameters]
    while obsDatasetList == []:
        print("Please select the available observation you would like to use from the list above:")
        userChoice = int(raw_input(">>>"))
        if userChoice in validParamIds:
            for param in parameters:
                if param['parameter_id'] == userChoice:
                    obsDatasetList.append(param)
                else:
                    pass
        else:
            print("Your selection '%s' is invalid.  Please make another selection." % userChoice)
    

    # User must provide startTime and endTime if not defined
    if jobProperties.startDate == None or jobProperties.endDate == None:
        jobProperties.startDate, jobProperties.endDate = misc.userDefinedStartEndTimes(obsDatasetList, models)

    try:
        gridBox = GridBox(jobProperties.latMin, jobProperties.lonMin, jobProperties.latMax,
                          jobProperties.lonMax, jobProperties.gridLonStep, jobProperties.gridLatStep)
    except:
        gridBox = None

    numOBS, numMDL, nT, ngrdY, ngrdX, Times, lons, lats, obsData, mdlData, obsList, mdlName = toolkit.do_data_prep.prep_data(jobProperties, obsDatasetList, gridBox, models)
  
    counts = {'observations': numOBS,
              'models'      : numMDL,
              'times'       : nT}
    subRegions = misc.getSubRegionsInteractively(counts, jobProperties.workDir)

    # TODO: New function Call
    fileOutputOption = jobProperties.writeOutFile
    modelVarName = models[0].varName
    toolkit.metrics.metrics_plots(modelVarName, numOBS, numMDL, nT, ngrdY, ngrdX, Times, lons, lats, obsData, mdlData, obsList, mdlName, workDir, subRegions, fileOutputOption)



# Actually call the UI function.
if __name__ == "__main__":
    rcmetUI()

