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

'''
# running the program
'''

import networkx as nx
import mccSearch
import subprocess


def main():
    CEGraph = nx.DiGraph()
    prunedGraph = nx.DiGraph()
    MCCList = []
    MCSList = []
    MCSMCCNodesList = []
    allMCSsList = []
    allCETRMMList = []

    # for GrADs
    subprocess.call('export DISPLAY=:0.0', shell=True)

    mainDirStr = "/directory/to/where/to/store/outputs"
    TRMMdirName = "/directory/to/the/TRMM/netCDF/files"
    CEoriDirName = "/directory/to/the/MERG/netCDF/files"

    # for first time working with the raw MERG zipped files
    # mccSearch.preprocessingMERG("/directory/to/where/the/raw/MERG/files/are")
    # ---------------------------------------------------------------------------------

    # create main directory and file structure for storing intel
    mccSearch.createMainDirectory(mainDirStr)
    TRMMCEdirName = mainDirStr + '/TRMMnetcdfCEs'
    CEdirName = mainDirStr + '/MERGnetcdfCEs'

    # for doing some postprocessing with the clipped datasets instead of running the full program, e.g.
    # mccSearch.postProcessingNetCDF(3,CEoriDirName)
    # mccSearch.postProcessingNetCDF(2)
    # -------------------------------------------------------------------------------------------------

    # let's go!
    print "\n -------------- Read MERG Data ----------"
    mergImgs, timeList = mccSearch.readMergData(CEoriDirName)
    print ("-" * 80)

    print 'in main', len(mergImgs)
    # print 'timeList', timeList
    print 'TRMMdirName ', TRMMdirName
    print "\n -------------- TESTING findCloudElements ----------"
    CEGraph = mccSearch.findCloudElements(mergImgs, timeList, TRMMdirName)
    # if the TRMMdirName wasnt entered for whatever reason, you can still get the TRMM data this way
    # CEGraph = mccSearch.findCloudElements(mergImgs,timeList)
    # allCETRMMList=mccSearch.findPrecipRate(TRMMdirName,timeList)
    # ----------------------------------------------------------------------------------------------
    print ("-" * 80)
    print "number of nodes in CEGraph is: ", CEGraph.number_of_nodes()
    print ("-" * 80)
    print "\n -------------- TESTING findCloudClusters ----------"
    prunedGraph = mccSearch.findCloudClusters(CEGraph)
    print ("-" * 80)
    print "number of nodes in prunedGraph is: ", prunedGraph.number_of_nodes()
    print ("-" * 80)
    print "\n -------------- TESTING findMCCs ----------"
    MCCList, MCSList = mccSearch.findMCC(prunedGraph)
    print ("-" * 80)
    print "MCC List has been acquired ", len(MCCList)
    print "MCS List has been acquired ", len(MCSList)
    print ("-" * 80)
    # now ready to perform various calculations/metrics
    print "\n -------------- TESTING METRICS ----------"

    # some calculations/metrics that work that work
    # print "creating the MCC userfile ", mccSearch.createTextFile(MCCList,1)
    # print "creating the MCS userfile ", mccSearch.createTextFile(MCSList,2)
    # MCCTimes, tdelta = mccSearch.temporalAndAreaInfoMetric(MCCList)
    # print "number of MCCs is: ", mccSearch.numberOfFeatures(MCCList)
    # print "longest duration is: ", mccSearch.longestDuration(MCCTimes), "hrs"
    # print "shortest duration is: ", mccSearch.shortestDuration(MCCTimes), "hrs"
    # #print "Average duration is: ", mccSearch.convert_timedelta(mccSearch.averageMCCLength(MCCTimes))
    # print "Average duration is: ", mccSearch.averageDuration(MCCTimes), "hrs"
    # print "Average size is: ", mccSearch.averageFeatureSize(MCCList), "km^2"

    # some plots that work
    # mccSearch.plotAccTRMM(MCCList)
    mccSearch.displayPrecip(MCCList)
    # mccSearch.plotAccuInTimeRange('2009-09-01_00:00:00', '2009-09-01_09:00:00')
    # mccSearch.displaySize(MCCList)
    # mccSearch.displayPrecip(MCCList)
    # mccSearch.plotHistogram(MCCList)
    #
    print ("-" * 80)

main()
