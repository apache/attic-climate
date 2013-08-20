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
Module storing functions to calculate statistical metrics from numpy arrays
'''

import subprocess
import os, sys
import datetime
import numpy as np
import numpy.ma as ma
import scipy.stats as stats
import matplotlib.pyplot as plt
from toolkit import plots, process
from utils import misc
from storage import files 

def calcAnnualCycleMeans(dataset1):
    '''
    Purpose:: 
        Calculate annual cycle in terms of monthly means at every grid point.

    Input::
        dataset1 - 3d numpy array of data in (t,lat,lon) or 1d numpy array timeseries

    Output:: 
        means - if 3d numpy was entered, 3d (# of months,lat,lon), if 1d data entered
        it is a timeseries of the data of length # of months

     '''
    data = misc.reshapeMonthlyData(dataset1)
    means = data.mean(axis = 0)
    return data, means

def calcAnnualCycleMeansSubRegion(dataset1):
    '''
    Purpose:: 
        Calculate annual cycle in terms of monthly means at every sub-region.

    Input::
        dataset1 - 2d numpy array of data in (region, t)
        
    Output:: 
        means - (region, # of months)

     '''
    nregion, nT = dataset1.shape
    data = dataset1.reshape[nregion, nT/12, 12]
    means = data.mean(axis = 1)
    return data, means


def calcClimYear(dataset1):
    '''
    Purpose:: 
       Calculate annual mean timeseries and climatology for both 2-D and point time series.

    Input::
        dataset1 - 3d numpy array of data in (t,lat,lon) or 1d numpy array timeseries

    Output:: 
        tSeries - if 3d numpy was entered, 3d (nYr,lat,lon), if 1d data entered
        it is a timeseries of the data of length nYr
        means - if 3d numpy was entered, 2d (lat,lon), if 1d data entered
        it is a floating point number representing the overall mean
    '''
    data = misc.reshapeMonthlyData(dataset1)
    tSeries = data.mean(axis = 1)
    means = tSeries.mean(axis = 0)
    return tSeries, means

def calcClimSeason(monthBegin, monthEnd, dataset1):
    '''
    Purpose :: 
       Calculate seasonal mean montheries and climatology for both 3-D and point time series.
       For example, to calculate DJF mean time series, monthBegin = 12, monthEnd =2 
       This can handle monthBegin=monthEnd i.e. for climatology of a specific month

    Input::
        monthBegin - an integer for the beginning month (Jan =1)
        monthEnd - an integer for the ending month (Jan = 1)
        dataset1 - 3d numpy array of data in (t,lat,lon) or 1d numpy array montheries

    Output:: 
        tSeries - if 3d numpy was entered, 3d (number of years/number of years -1 if monthBegin > monthEnd,lat,lon),
        if 1d data entered it is a montheries of the data of length number of years
        means - if 3d numpy was entered, 2d (lat,lon), if 1d data entered
        it is a floating point number representing the overall mean
    '''
    if monthBegin > monthEnd:
        # Offset the original array so that the the first month
        # becomes monthBegin, note that this cuts off the first year of data
        offset = slice(monthBegin - 1, monthBegin - 13)
        data = misc.reshapeMonthlyData(dataset1[offset])
        monthIndex = slice(0, 13 - monthBegin + monthEnd)
    else:
        # Since monthBegin <= monthEnd, just take a slice containing those months
        data = misc.reshapeMonthlyData(dataset1)
        monthIndex =  slice(monthBegin - 1, monthEnd)
        
    tSeries = data[:, monthIndex].mean(axis = 1)
    means = tSeries.mean(axis = 0)        
    return tSeries, means

def calcClimSeasonSubRegion(monthBegin, monthEnd, dataset1):
    '''
    Purpose :: 
       Calculate seasonal mean montheries and climatology for both 3-D and point time series.
       For example, to calculate DJF mean time series, monthBegin = 12, monthEnd =2 
       This can handle monthBegin=monthEnd i.e. for climatology of a specific month

    Input::
        monthBegin - an integer for the beginning month (Jan =1)
        monthEnd - an integer for the ending month (Jan = 1)
        dataset1 - 3d numpy array of data in (region, t) or 1d numpy array montheries

    Output:: 
        tSeries - (region, number of years/number of years -1 if monthBegin > monthEnd,lat,lon),
        means - (region)
    '''
    nregion, nT = dataset1.shape
    nYR = nT/12
    if monthBegin > monthEnd:
        # Offset the original array so that the the first month
        # becomes monthBegin, note that this cuts off the first year of data
        offset = slice(monthBegin - 1, monthBegin - 13)
        data = dataset1[:,offset].reshape([nregion,nYR-1, 12])
        monthIndex = slice(0, 13 - monthBegin + monthEnd)
    else:
        # Since monthBegin <= monthEnd, just take a slice containing those months
        data = dataset1.reshape([nregion,nYR,12])
        monthIndex =  slice(monthBegin - 1, monthEnd)
        
    tSeries = data[:, :, monthIndex].mean(axis = 2)
    means = tSeries.mean(axis = 1)        
    return tSeries, means

def calcAnnualCycleStdev(dataset1):
    '''
     Purpose:: 
        Calculate monthly standard deviations for every grid point
     
     Input::
        dataset1 - 3d numpy array of data in (12* number of years,lat,lon) 

     Output:: 
        stds - if 3d numpy was entered, 3d (12,lat,lon)
    '''
    data = misc.reshapeMonthlyData(dataset1)
    stds = data.std(axis = 0, ddof = 1)
    return stds

def calcAnnualCycleStdevSubRegion(dataset1):
    '''
     Purpose:: 
        Calculate monthly standard deviations for every sub-region
     
     Input::
        dataset1 - 2d numpy array of data in (nregion, 12* number of years) 

     Output:: 
        stds - (nregion, 12)
    '''
    nregion, nT = data1.shape
    data = dataset1.reshape([nregion, nT/12, 12])
    stds = data.std(axis = 1, ddof = 1)
    return stds

def calcAnnualCycleDomainMeans(dataset1):
    '''
     Purpose:: 
        Calculate spatially averaged monthly climatology and standard deviation

     Input::
        dataset1 - 3d numpy array of data in (12* number of years,lat,lon) 

     Output::  
        means - time series (12)
    '''
    data = misc.reshapeMonthlyData(dataset1)
    
    # Calculate the means, month by month
    means = np.zeros(12)
    for i in np.arange(12):
        means[i] = data[:, i, :, :].mean()
        
    return means

def calcSpatialStdevRatio(evaluationData, referenceData):
    '''
    Purpose ::
        Calculate the ratio of spatial standard deviation (model standard deviation)/(observed standard deviation)

    Input ::
        evaluationData - model data array (lat, lon)
        referenceData- observation data array (lat,lon)

    Output::
        ratio of standard deviation (a scholar) 
    
    '''
    stdevRatio = evaluationData[(evaluationData.mask==False) & (referenceData.mask==False)].std()/ \
                 referenceData[(evaluationData.mask==False) & (referenceData.mask==False)].std()  
    return stdevRatio

def calcTemporalStdev(dataset1):
    '''
     Purpose:: 
        Calculate sample standard deviations over the time

     Input::
        dataset1 - 3d numpy array of data in (time,lat,lon) 
        

     Output::  
        stds - time series (lat, lon)
    '''
    stds = dataset1.std(axis = 0, ddof = 1)
    return stds

def calcAnnualCycleDomainStdev(dataset1):
    '''
     Purpose:: 
        Calculate sample standard deviations representing the domain in each month

     Input::
        dataset1 - 3d numpy array of data in (12* number of years,lat,lon) 

     Output::  
        stds - time series (12)
    '''
    data = misc.reshapeMonthlyData(dataset1)
    
    # Calculate the standard deviation, month by months
    stds = np.zeros(12)
    for i in np.arange(12):
        stds[i] = data[:, i, :, :].std(ddof = 1)
        
    return stds

def calcBiasAveragedOverTime(evaluationData, referenceData, option):        # Mean Bias
    '''
    Purpose:: 
        Calculate the mean difference between two fields over time for each grid point.

     Input::
        referenceData - array of data 
        evaluationData - array of data with same dimension of referenceData 
        option - string indicating absolute values or not

     Output::  
        bias - difference between referenceData and evaluationData averaged over the first dimension
    
    '''
    # Calculate mean difference between two fields over time for each grid point
    # Precrocessing of both obs and model data ensures the absence of missing values
    diff = evaluationData - referenceData
    if(option == 'abs'): 
        diff = abs(diff)
    bias = diff.mean(axis = 0)
    return bias


def calcBiasAveragedOverTimeAndSigLev(evaluationData, referenceData):
    '''
    Purpose::
        Calculate mean difference between two fields over time for each grid point
    
    Classify missing data resulting from multiple times (using threshold 
    data requirement)
    
    i.e. if the working time unit is monthly data, and we are dealing with 
    multiple months of data then when we show mean of several months, we need
    to decide what threshold of missing data we tolerate before classifying a
    data point as missing data.
 
        
     Input::
        referenceData - array of data 
        evaluationData - array of data with same dimension of referenceData 

     Output::  
        bias - difference between referenceData and evaluationData averaged over the first dimension
        sigLev - significance of the difference (masked array)
        For example: sig[iy,ix] = 0.95 means that the observation and model is different at 95% confidence level 
        at X=ix and Y=iy
    '''
    # If either gridcell in each data set is missing, set that cell to
    # missing for the output significance level
    evaluationDataMask = process.create_mask_using_threshold(evaluationData, threshold = 0.75)
    referenceDataMask = process.create_mask_using_threshold(referenceData, threshold = 0.75)
    
    # The overall mask associated with missing data
    overallMask = np.logical_or(evaluationDataMask, referenceDataMask)
    
    diff = evaluationData - referenceData
    bias = diff.mean(axis = 0)
    sigLev = 1 - stats.ttest_rel(evaluationData, referenceData, axis = 0)[1]
    sigLev[overallMask] = -100.
    sigLev = ma.masked_equal(sigLev, -100.) 
    # Set mask for bias metric using missing data in obs or model data series
    # i.e. if obs contains more than threshold (e.g.50%) missing data 
    # then classify time average bias as missing data for that location. 
    bias = ma.masked_array(bias.data, overallMask)
    return bias, sigLev


def calcBiasAveragedOverTimeAndDomain(evaluationData, referenceData):
    '''
    Purpose:: 
        Calculate the mean difference between two fields over time and domain
     Input::
        referenceData - array of data 
        evaluationData - array of data with same dimension of referenceData 
        
     Output::  
        bias - difference between referenceData and evaluationData averaged over time and space
    
    '''

    diff = evaluationData - referenceData
    
    bias = diff.mean()
    return bias

def calcBias(evaluationData, referenceData):
    '''
    Purpose:: 
        Calculate the difference between two fields at each grid point

     Input::
        referenceData - array of data 
        evaluationData - array of data with same dimension of referenceData 
        
     Output::  
        diff - difference between referenceData and evaluationData
    
    '''

    diff = evaluationData - referenceData
    return diff

def calcRootMeanSquaredDifferenceAveragedOverTime(evaluationData, referenceData):
    '''
    Purpose:: 
        Calculate root mean squared difference (RMS errors) averaged over time between two fields for each grid point

     Input::
        referenceData - array of data 
        evaluationData - array of data with same dimension of referenceData 
        
     Output::  
        rms - root mean squared difference, if the input is 1-d data, the output becomes a single floating number.
    
    '''
    sqdiff = (evaluationData - referenceData)** 2
    rms = np.sqrt(sqdiff.mean(axis = 0))
    return rms


def calcRootMeanSquaredDifferenceAveragedOverTimeAndDomain(evaluationData, referenceData):
    '''
    Purpose:: 
        Calculate root mean squared difference (RMS errors) averaged over time and space between two fields

     Input::
        referenceData - array of data (should be 3-d array)
        evaluationData - array of data with same dimension of referenceData 
        
     Output::  
        rms - root mean squared difference averaged over time and space
    '''
    sqdiff = (evaluationData - referenceData)** 2
    rms = np.sqrt(sqdiff.mean())
    return rms

def calcTemporalCorrelation(evaluationData, referenceData):
    '''
    Purpose ::
        Calculate the temporal correlation.
    
    Assumption(s) ::
        The first dimension of two datasets is the time axis.
    
    Input ::
        evaluationData - model data array of any shape
        referenceData- observation data array of any shape
            
    Output::
        temporalCorelation - A 2-D array of temporal correlation coefficients at each subregion
        sigLev - A 2-D array of confidence levels related to temporalCorelation 
    
    REF: 277-281 in Stat methods in atmos sci by Wilks, 1995, Academic Press, 467pp.
    sigLev: the correlation between model and observation is significant at sigLev * 100 %
    '''
    evaluationDataMask = process.create_mask_using_threshold(evaluationData, threshold = 0.75)
    referenceDataMask = process.create_mask_using_threshold(referenceData, threshold = 0.75)
    
    nregion = evaluationData.shape[0]
    temporalCorrelation = ma.zeros([nregion])-100.
    sigLev = ma.zeros([nregion])-100.
    for iregion in np.arange(nregion):
        temporalCorrelation[iregion], sigLev[iregion] = stats.pearsonr(evaluationData[iregion,:], referenceData[iregion,:])
        sigLev[iregion] = 1 - sigLev[iregion]
                    
    temporalCorrelation=ma.masked_equal(temporalCorrelation.data, -100.)        
    sigLev=ma.masked_equal(sigLev.data, -100.)    
    
    return temporalCorrelation, sigLev

def calcTemporalCorrelationSubRegion(evaluationData, referenceData):
    '''
    Purpose ::
        Calculate the temporal correlation.
    
    Assumption(s) ::
        both evaluation and reference data are subregion averaged time series
    
    Input ::
        evaluationData - model data array [region,t]
        referenceData- observation data [region, t]
            
    Output::
        temporalCorelation - A 1-D array of temporal correlation coefficients at each grid point.
        sigLev - A 1-D array of confidence levels related to temporalCorelation 
    
    REF: 277-281 in Stat methods in atmos sci by Wilks, 1995, Academic Press, 467pp.
    sigLev: the correlation between model and observation is significant at sigLev * 100 %
    '''
    evaluationDataMask = process.create_mask_using_threshold(evaluationData, threshold = 0.75)
    referenceDataMask = process.create_mask_using_threshold(referenceData, threshold = 0.75)
    
    ngrdY = evaluationData.shape[1] 
    ngrdX = evaluationData.shape[2] 
    temporalCorrelation = ma.zeros([ngrdY,ngrdX])-100.
    sigLev = ma.zeros([ngrdY,ngrdX])-100.
    for iy in np.arange(ngrdY):
        for ix in np.arange(ngrdX):
            if not evaluationDataMask[iy,ix] and not referenceDataMask[iy,ix]:
                t1=evaluationData[:,iy,ix]
                t2=referenceData[:,iy,ix]
                if t1.min()!=t1.max() and t2.min()!=t2.max():
                    temporalCorrelation[iy,ix], sigLev[iy,ix]=stats.pearsonr(t1[(t1.mask==False) & (t2.mask==False)],
                                                  t2[(t1.mask==False) & (t2.mask==False)])
                    sigLev[iy,ix]=1-sigLev[iy,ix]  # p-value => confidence level
                    
    temporalCorrelation=ma.masked_equal(temporalCorrelation.data, -100.)        
    sigLev=ma.masked_equal(sigLev.data, -100.)    
    
    return temporalCorrelation, sigLev

def calcPatternCorrelation(evaluationData, referenceData):
    '''
    Purpose ::
        Calculate the spatial correlation.

    Input ::
        evaluationData - model data array (lat, lon)
        referenceData- observation data array (lat,lon)

    Output::
        patternCorrelation - a single floating point
        sigLev - a single floating point representing the confidence level 
    
    '''
   
    patternCorrelation, sigLev = stats.pearsonr(evaluationData[(evaluationData.mask==False) & (referenceData.mask==False)],
                          referenceData[(evaluationData.mask==False) & (referenceData.mask==False)])
    return patternCorrelation, sigLev


def calcPatternCorrelationEachTime(evaluationData, referenceData):
    '''
     Purpose ::
        Calculate the spatial correlation for each time

     Assumption(s) ::
        The first dimension of two datasets is the time axis.

     Input ::
        evaluationData - model data array (time,lat, lon)
        referenceData- observation data array (time,lat,lon)

     Output::
        patternCorrelation - a timeseries (time)
        sigLev - a time series (time)
    ''' 
    nT = evaluationData.shape[0]
    patternCorrelation = ma.zeros(nT)-100.
    sigLev = ma.zeros(nT)-100.
    for it in np.arange(nT):
        patternCorrelation[it], sigLev[it] = calcPatternCorrelation(evaluationData[it,:,:], referenceData[it,:,:])

    return patternCorrelation,sigLev

def calcNashSutcliff(evaluationData, referenceData):
    '''
    Assumption(s)::  
    	Both evaluationData and referenceData are the same shape.
        * lat, lon must match up
        * time steps must align (i.e. months vs. months)
    
    Input::
    	evaluationData - 3d (time, lat, lon) array of data
        referenceData - 3d (time, lat, lon) array of data
    
    Output:
        nashcor - 1d array aligned along the time dimension of the input
        datasets. Time Series of Nash-Sutcliff Coefficient of efficiency
     
    '''
    # Flatten the spatial dimensions
    data1 = evaluationData[:]
    data2 = referenceData[:]
    nT = data1.shape[0]
    data1.shape = nT, data1.size / nT
    data2.shape = nT, data2.size / nT 
    meanData2 = data2.mean(axis = 1)
    
    # meanData2 must be reshaped to 2D as to obey
    # numpy broadcasting rules
    meanData2.shape = nT, 1
    nashcor = 1 - ((((data2 - data1) ** 2).sum(axis = 1)) / 
               (((data2 - meanData2) ** 2).sum(axis = 1)))
    return nashcor

def getPdfInputValues():
    print '****PDF input values from user required **** \n'
    nbins = int (raw_input('Please enter the number of bins to use. \n'))
    minEdge = float(raw_input('Please enter the minimum value to use for the edge. \n'))
    maxEdge = float(raw_input('Please enter the maximum value to use for the edge. \n'))
    
    return nbins, minEdge, maxEdge


def calcPdf(evaluationData, referenceData, settings=None):
    '''
    Routine to calculate a normalized Probability Distribution Function with 
    bins set according to data range.
    Equation from Perkins et al. 2007

        PS=sum(min(Z_O_i, Z_M_i)) where Z is the distribution (histogram of the data for either set)
        called in do_rcmes_processing_sub.py
         
    Inputs::
        evaluationData (3D numpy array): array shape (time, lat, lon)
        referenceData (3D numpy array): array shape (time, lat, lon)
        settings (tuple): [optional] format (binCount, minEdge, maxEdge)
            binCount (int): number of bins to use
            minEdge (int|float): minimum edge
            maxEdge (int|float): maximum edge
        
        NB, time here is the number of time values eg for time period
         199001010000 - 199201010000 
        
    Assumptions::
        If annual means-opt 1, was chosen, then referenceData.shape = (YearsCount,lat,lon)
        
        If monthly means - opt 2, was choosen, then referenceData.shape = (MonthsCount,lat,lon)
        
    Output::

        one float which represents the PDF for the year

    TODO:  Clean up this docstring so we have a single purpose statement
     
    Routine to calculate a normalised PDF with bins set according to data range.

    Input::
        2 data  arrays, modelData and obsData

    Output::
        PDF for the year

    '''
    similarityScore = 0.0
    print 'min modelData', evaluationData[:, :, :].min()
    print 'max modelData', evaluationData[:, :, :].max()
    print 'min obsData', referenceData[:, :, :].min()
    print 'max obsData', referenceData[:, :, :].max()

    if settings == None:
        nbins, minEdge, maxEdge = getPdfInputValues()
    else:
        nbins, minEdge, maxEdge = settings

    
    mybins = np.linspace(minEdge, maxEdge, nbins)
    print 'nbins is', nbins, 'mybins are', mybins
    
    pdfMod, edges = np.histogram(evaluationData, bins = mybins, normed = True, density = True)  
    print 'evaluationData distribution and edges', pdfMod, edges
    pdfObs, edges = np.histogram(referenceData, bins = mybins, normed = True, density = True)           
    print 'referenceData distribution and edges', pdfObs, edges    
    
    #find minimum at each bin between lists 
    i = 0
    for model_value in pdfMod :
        print 'model_value is', model_value, 'pdfObs[', i, '] is', pdfObs[i]
        if model_value < pdfObs[i]:
            similarityScore += model_value
        else:
            similarityScore += pdfObs[i] 
        i += 1 
    print 'similarity_score is', similarityScore
    return similarityScore


def metrics_plots(varName, numOBS, numMDL, nT, ngrdY, ngrdX, Times, lons, 
                  lats, obsData, mdlData, obsList, mdlList, workdir,subRegions, FoutOption):
    '''
    Calculate evaluation metrics and generate plots.
    '''
    ##################################################################################################################
    # Routine to compute evaluation metrics and generate plots
    #    (1)  metric calculation
    #    (2) plot production
    #    Input: 
    #        numOBS           - the number of obs data. either 1 or >2 as obs ensemble is added for multi-obs cases
    #        numMDL           - the number of mdl data. either 1 or >2 as obs ensemble is added for multi-mdl cases
    #        nT               - the length of the data in the time dimension
    #        ngrdY            - the length of the data in Y dimension
    #        ngrdX            - the length of the data in the X dimension
    #        Times            - time stamps
    #        lons,lats        - longitude & latitude values of the data domain (same for model & obs)
    #        obsData          - obs data, either a single or multiple + obs_ensemble, interpolated onto the time- and
    #                           grid for analysis
    #        mdlData          - mdl data, either a single or multiple + obs_ensemble, interpolated onto the time- and
    #                           spatial grid for analysis
    #JK2.0:  obsRgn           - obs time series averaged for subregions: Local variable in v2.0
    #JK2.0:  mdlRgn           - obs time series averaged for subregions: Local variable in v2.0
    #        obsList          - string describing the observation data files
    #        mdlList          - string describing model file names
    #        workdir        - string describing the directory path for storing results and plots
    #JK2.0:  mdlSelect        - the mdl data to be evaluated: Locally determined in v.2.0
    #JK2.0:  obsSelect        - the obs data to be used as the reference for evaluation: Locally determined in v.2.0
    #JK2.0:  numSubRgn        - the number of subregions: Locally determined in v.2.0
    #JK2.0:  subRgnName       - the names of subregions: Locally determined in v.2.0
    #JK2.0:  rgnSelect        - the region for which the area-mean time series is to be 
    #                               evaluated/plotted: Locally determined in v.2.0
    #        obsParameterId   - int, db parameter id. ** this is non-essential once the correct 
    #                               metadata use is implemented
    #      precipFlag       - to be removed once the correct metadata use is implemented
    #        timeRegridOption - string: 'full'|'annual'|'monthly'|'daily'
    #        seasonalCycleOption - int (=1 if set) (probably should be bool longterm) 
    #      metricOption - string: 'bias'|'mae'|'acc'|'pdf'|'patcor'|'rms'|'diff'
    #        titleOption - string describing title to use in plot graphic
    #        plotFileNameOption - string describing filename stub to use for plot graphic i.e. {stub}.png
    #    Output: image files of plots + possibly data
    #******************************************************
    # JK2.0: Only the data interpolated temporally and spatially onto the analysis grid 
    #        are transferred into this routine. The rest of processing (e.g., area-averaging, etc.) 
    #        are to be performed in this routine. Do not overwrite obsData[numOBs,nt,ngrdY,ngrdX] & 
    #        mdlData[numMDL,nt,ngrdY,ngrdX]. These are the raw, re-gridded data to be used repeatedly 
    #        for multiple evaluation steps as desired by an evaluator
    ##################################################################################################################

    #####################################################################################################
    # JK2.0: Compute evaluation metrics and plots to visualize the results
    #####################################################################################################
    # (mp.001) Sub-regions for local timeseries analysis
    #--------------------------------
    # Enter the location of the subrgns via screen input of data; 
    # modify this to add an option to read-in from data file(s)
    #----------------------------------------------------------------------------------------------------
    if subRegions:
        numSubRgn = len(subRegions)
        subRgnName = [ x.name   for x in subRegions ]
        subRgnLon0 = [ x.lonMin for x in subRegions ]
        subRgnLon1 = [ x.lonMax for x in subRegions ]
        subRgnLat0 = [ x.latMin for x in subRegions ]
        subRgnLat1 = [ x.latMax for x in subRegions ]
    else:
        print ''
        ans = raw_input('Calculate area-mean timeseries for subregions? y/n: \n> ')
        print ''
        if ans == 'y':
            ans = raw_input('Input subregion info interactively? y/n: \n> ')
            if ans == 'y':
                numSubRgn, subRgnName, subRgnLon0, subRgnLon1, subRgnLat0, subRgnLat1 = misc.createSubRegionObjectInteractively()
            else:
                print 'Read subregion info from a pre-fabricated text file'
                ans = raw_input('Read from a defaule file (workdir + "/sub_regions.txt")? y/n: \n> ')
                if ans == 'y':
                    subRgnFileName = workdir + "/sub_regions.txt"
                else:
                    subRgnFileName = raw_input('Enter the subRgnFileName to read from \n')
                print 'subRgnFileName ', subRgnFileName
                numSubRgn, subRgnName, subRgnLon0, subRgnLon1, subRgnLat0, subRgnLat1 = misc.assign_subRgns_from_a_text_file(subRgnFileName)
            print subRgnName, subRgnLon0, subRgnLon1, subRgnLat0, subRgnLat1
        else:
            numSubRgn = 0

    # compute the area-mean timeseries for all subregions if subregion(s) are defined.
    #   the number of subregions is usually small and memory usage is usually not a concern
    obsRgn = ma.zeros((numOBS, numSubRgn, nT))
    mdlRgn = ma.zeros((numMDL, numSubRgn, nT))
    if numSubRgn > 0:
        print 'Enter area-averaging: mdlData.shape, obsData.shape ', mdlData.shape, obsData.shape
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
            for k in np.arange(numOBS):           # area-average obs data
                Store = []
                for t in np.arange(nT):
                    Store.append(process.calc_area_mean(obsData[k, t, :, :], lats, lons, mymask = mask))
                obsRgn[k, n, :] = ma.array(Store[:])
            for k in np.arange(numMDL):           # area-average mdl data
                Store = []
                for t in np.arange(nT):
                    Store.append(process.calc_area_mean(mdlData[k, t, :, :], lats, lons, mymask = mask))
                mdlRgn[k, n, :] = ma.array(Store[:])
            Store = []                               # release the memory allocated by temporary vars

    #-------------------------------------------------------------------------
    # (mp.002) FoutOption: The option to create a binary or netCDF file of processed 
    #                      (re-gridded and regionally-averaged) data for user-specific processing. 
    #                      This option is useful for advanced users who need more than
    #                      the metrics and vidualization provided in the basic package.
    #----------------------------------------------------------------------------------------------------
    print ''
    if not FoutOption:
        FoutOption = raw_input('Option for output files of obs/model data: Enter no/bn/nc \
                               for no, binary, netCDF file \n> ').lower()
    print ''
    # write a binary file for post-processing if desired
    if FoutOption == 'bn':
        fileName = workdir + '/lonlat_eval_domain' + '.bn'
        if(os.path.exists(fileName) == True):
            cmnd = 'rm -f ' + fileName
            subprocess.call(cmnd, shell=True)
        files.writeBN_lola(fileName, lons, lats)
        fileName = workdir + '/Tseries_' + varName + '.bn'
        print "Create regridded data file ", fileName, " for offline processingr"
        print 'The file includes time series of ', numOBS, ' obs and ', numMDL, \
            ' models ', nT, ' steps ', ngrdX, 'x', ngrdY, ' grids'
        if(os.path.exists(fileName) == True):
            cmnd = 'rm -f ' + fileName
            subprocess.call(cmnd, shell=True)
        files.writeBNdata(fileName, numOBS, numMDL, nT, ngrdX, ngrdY, numSubRgn, obsData, mdlData, obsRgn, mdlRgn)
    # write a netCDF file for post-processing if desired
    if FoutOption == 'nc':
        fileName = workdir + '/'+varName+'_Tseries.nc' 
        if(os.path.exists(fileName) == True):
            print "removing %s from the local filesystem, so it can be replaced..." % (fileName,)
        files.writeNCfile(fileName, numSubRgn, lons, lats, obsData, mdlData, obsRgn, mdlRgn, obsList, mdlList, subRegions)
    if FoutOption == 'bn':
        print 'The regridded obs and model data are written in the binary file ', fileName
    elif FoutOption == 'nc':
        print 'The regridded obs and model data are written in the netCDF file ', fileName

    #####################################################################################################
    ###################### Metrics calculation and plotting cycle starts from here ######################
    #####################################################################################################

    print ''
    print 'OBS and MDL data have been prepared for the evaluation step'
    print ''
    doMetricsOption = raw_input('Want to calculate metrics and plot them? [y/n]\n> ').lower()
    print ''

    ####################################################
    # Terminate job if no metrics are to be calculated #
    ####################################################

    neval = 0

    while doMetricsOption == 'y':
        neval += 1
        print ' '
        print 'neval= ', neval
        print ' '
        #--------------------------------
        # (mp.003) Preparation
        #----------------------------------------------------------------------------------------------------
        # Determine info on years (the years in the record [YR] and its number[numYR])
        yy = ma.zeros(nT, 'i')
        for n in np.arange(nT):
            yy[n] = Times[n].strftime("%Y")
        YR = np.unique(yy)
        yy = 0
        nYR = len(YR)
        print 'nYR, YR = ', nYR, YR

        # Select the eval domain: over the entire domain (spatial distrib) or regional time series
        anlDomain = 'n'
        anlRgn = 'n'
        print ' '
        analSelect = int(raw_input('Eval over domain (Enter 0) or time series of selected regions (Enter 1) \n> '))
        print ' '
        if analSelect == 0:
            anlDomain = 'y'
        elif analSelect == 1:
            anlRgn = 'y'
        else:
            print 'analSelect= ', analSelect, ' is Not a valid option: CRASH'
            sys.exit()

        #--------------------------------
        # (mp.004) Select the model and data to be used in the evaluation step
        #----------------------------------------------------------------------------------------------------
        mdlSelect = misc.select_data(numMDL, Times, mdlList, 'mdl')
        obsSelect = misc.select_data(numOBS, Times, obsList, 'obs')
        mdlName = mdlList[mdlSelect]
        obsName = obsList[obsSelect]
        print 'selected obs and model for evaluation= ', obsName, mdlName


        #--------------------------------
        # (mp.005) Spatial distribution analysis/Evaluation (anlDomain='y')
        #          All climatology variables are 2-d arrays (e.g., mClim = ma.zeros((ngrdY,ngrdX))
        #----------------------------------------------------------------------------------------------------
        if anlDomain == 'y':
            # first determine the temporal properties to be evaluated
            print ''
            timeOption = misc.select_timOpt()
            print 'timeOption=',timeOption
            if timeOption == 1:
                timeScale = 'Annual'
                # compute the annual-mean time series and climatology. 
                # mTser=ma.zeros((nYR,ngrdY,ngrdX)), mClim = ma.zeros((ngrdY,ngrdX))
                mTser, mClim = calcClimYear(mdlData[mdlSelect, :, :, :])
                oTser, oClim = calcClimYear(obsData[obsSelect, :, :, :])
            elif timeOption == 2:
                timeScale = 'Seasonal'
                # select the timeseries and climatology for a season specifiec by a user
                print ' '
                moBgn = int(raw_input('Enter the beginning month for your season. 1-12: \n> '))
                moEnd = int(raw_input('Enter the ending month for your season. 1-12: \n> '))
                print ' '
                mTser, mClim = calcClimSeason(moBgn, moEnd, mdlData[mdlSelect, :, :, :])
                oTser, oClim = calcClimSeason(moBgn, moEnd, obsData[obsSelect, :, :, :])
            elif timeOption == 3:
                timeScale = 'Monthly'
                # compute the monthly-mean time series and climatology
                # Note that the shapes of the output vars are: 
                #   mTser = ma.zeros((nYR,12,ngrdY,ngrdX)) & mClim = ma.zeros((12,ngrdY,ngrdX))
                # Also same for oTser = ma.zeros((nYR,12,ngrdY,ngrdX)) &,oClim = ma.zeros((12,ngrdY,ngrdX))
                mTser, mClim = calcAnnualCycleMeans(mdlData[mdlSelect, :, :, :])
                oTser, oClim = calcAnnualCycleMeans(obsData[obsSelect, :, :, :])
            else:
                # undefined process options. exit
                print 'The desired temporal scale is not available this time. END the job'
                sys.exit()

            #--------------------------------
            # (mp.006) Select metric to be calculated
            # bias, mae, acct, accs, pcct, pccs, rmst, rmss, pdfSkillScore
            #----------------------------------------------------------------------------------------------------
            print ' '
            metricOption = misc.select_metrics()
            print ' '

            # metrics below yields 2-d array, i.e., metricDat = ma.array((ngrdY,ngrdX))
            if metricOption == 'BIAS':
                metricDat, sigLev = calcBiasAveragedOverTimeAndSigLev(mTser, oTser)
                oStdv = calcTemporalStdev(oTser)
            elif metricOption == 'MAE':
                metricDat= calcBiasAveragedOverTime(mTser, oTser, 'abs')
            # metrics below yields 1-d time series
            elif metricOption == 'PCt':
                metricDat, sigLev = calcPatternCorrelationEachTime(mTser, oTser)
            # metrics below yields 2-d array, i.e., metricDat = ma.array((ngrdY,ngrdX))
            elif metricOption == 'TC':
                
                metricDat, sigLev = calcTemporalCorrelation(mTser, oTser)
            # metrics below yields a scalar values
            elif metricOption == 'PCC':
                metricDat, sigLev = calcPatternCorrelation(mClim, oClim)
            # metrics below yields 2-d array, i.e., metricDat = ma.array((ngrdY,ngrdX))
            elif metricOption == 'RMSt':
                metricDat = calcRootMeanSquaredDifferenceAveragedOverTime(mTser, oTser)

            #--------------------------------
            # (mp.007) Plot the metrics. First, enter plot info
            #----------------------------------------------------------------------------------------------------

            # 2-d contour plots
            if metricDat.ndim == 2:
                # assign plot file name and delete old (un-saved) plot files
                plotFileName = workdir + '/' + timeScale + '_' + varName + '_' + metricOption 
                if(os.path.exists(plotFileName) == True):
                    cmnd = 'rm -f ' + plotFileName
                    subprocess.call(cmnd, shell=True)
                # assign plot title
                plotTitle = metricOption + '_' + varName
                # Data-specific plot options: i.e. adjust model data units & set plot color bars
                #cMap = 'rainbow'
                cMap = plt.cm.RdBu_r
                #cMap = 'BlWhRe'
                #cMap = 'BlueRed'
                #cMap = 'GreyWhiteGrey'
                # Calculate color bar ranges for data such that same range is used 
                # in obs and model plots for like-with-like comparison.
                obsDataMask = np.zeros_like(oClim.data[:, :])
                metricDat = ma.masked_array(metricDat, obsDataMask)
                oClim = ma.masked_array(oClim, obsDataMask)
                oStdv = ma.masked_array(oClim, obsDataMask)
                plotDat = metricDat
                mymax = plotDat.max()
                mymin = plotDat.min()
                if metricOption == 'BIAS':
                    abs_mymin = abs(mymin)
                    if abs_mymin <= mymax:
                        mymin = -mymax
                    else:
                        mymax = abs_mymin
                print 'Plot bias over the model domain: data MIN/MAX= ', mymin, mymax
                ans = raw_input('Do you want to use different scale for plotting? [y/n]\n> ').lower()
                if ans == 'y':
                    mymin = float(raw_input('Enter the minimum plot scale \n> '))
                    mymax = float(raw_input('Enter the maximum plot scale \n> '))
                wksType = 'png'
                # TODO This shouldn't return anything. Handle a "status" the proper way
                _ = plots.draw_cntr_map_single(plotDat, lats, lons, mymin, mymax, 
                                                      plotTitle, plotFileName, cMap=cMap)
                # if bias, plot also normalzied values and means: first, normalized by mean
                if metricOption == 'BIAS':
                    print ''
                    makePlot = raw_input('Plot bias in terms of % of OBS mean? [y/n]\n> ').lower()
                    print ''
                    if makePlot == 'y':
                        plotDat = 100.*metricDat / oClim
                        mymax = plotDat.max()
                        mymin = plotDat.min()
                        mymn = -100.
                        mymx = 105.
                        print 'Plot mean-normalized bias: data MIN/MAX= ', mymin, mymax, \
                            ' Default MIN/MAX= ', mymn, mymx
                        ans = raw_input('Do you want to use different scale for plotting? [y/n]\n> ').lower()
                        if ans == 'y':
                            mymin = float(raw_input('Enter the minimum plot scale \n> '))
                            mymax = float(raw_input('Enter the maximum plot scale \n> '))
                        else:
                            mymin = mymn
                            mymax = mymx
                        plotFileName = workdir + '/' + timeScale + '_' + varName + '_' + metricOption + '_Mean'
                        if(os.path.exists(plotFileName) == True):
                            cmnd = 'rm -f ' + plotFileName
                            subprocess.call(cmnd, shell = True)
                        plotTitle = 'Bias (% MEAN)'
                        # TODO Again, this shouldn't return a status
                        _ = plots.draw_cntr_map_single(plotDat, lats, lons, mymin, mymax, 
                                                              plotTitle, plotFileName, wksType, cMap)
                # normalized by sigma
                makePlot = raw_input('Plot bias in terms of % of interann sigma? [y/n]\n> ').lower()
                if makePlot == 'y':
                    plotDat = 100.*metricDat / oStdv
                    mymax = plotDat.max()
                    mymin = plotDat.min()
                    mymn = -200.
                    mymx = 205.
                    print 'Plot STD-normalized bias: data MIN/MAX= ', mymin, mymax, ' Default MIN/MAX= ', mymn, mymx
                    ans = raw_input('Do you want to use different scale for plotting? [y/n]\n> ').lower()
                    if ans == 'y':
                        mymin = float(raw_input('Enter the minimum plot scale \n> '))
                        mymax = float(raw_input('Enter the maximum plot scale \n> '))
                    else:
                        mymin = mymn
                        mymax = mymx
                    plotFileName = workdir + '/' + timeScale + '_' + varName + '_' + metricOption + '_SigT'
                    if(os.path.exists(plotFileName) == True):
                        cmnd = 'rm -f ' + plotFileName
                        subprocess.call(cmnd, shell = True)
                    plotTitle = 'Bias (% SIGMA_time)'
                    # TODO Hay look! A todo re. status returns!
                    _ = plots.draw_cntr_map_single(plotDat, lats, lons, mymin, mymax, 
                                                          plotTitle, plotFileName, wksType, cMap)
                # obs climatology
                makePlot = raw_input('Plot observation? [y/n]\n> ').lower()
                if makePlot == 'y':
                    if varName == 'pr':
                        cMap = plt.cm.jet
                    else:
                        cMap = plt.cm.jet
                    plotDat = oClim
                    mymax = plotDat.max()
                    mymin = plotDat.min()
                    print 'Plot STD-normalized bias over the model domain: data MIN/MAX= ', mymin, mymax
                    ans = raw_input('Do you want to use different scale for plotting? [y/n]\n> ').lower()
                    if ans == 'y':
                        mymin = float(raw_input('Enter the minimum plot scale \n> '))
                        mymax = float(raw_input('Enter the maximum plot scale \n> '))
                    plotFileName = workdir + '/' + timeScale + '_' + varName + '_OBS'
                    if(os.path.exists(plotFileName) == True):
                        cmnd = 'rm -f ' + plotFileName
                        subprocess.call(cmnd, shell=True)
                    plotTitle = 'OBS (mm/day)'
                    # TODO Yep
                    _ = plots.draw_cntr_map_single(plotDat, lats, lons, mymin, mymax, 
                                                          plotTitle, plotFileName, wksType, cMap)

                # Repeat for another metric
                print ''
                print 'Evaluation completed'
                print ''
                doMetricsOption = raw_input('Do you want to perform another evaluation? [y/n]\n> ').lower()
                print ''

        # metrics and plots for regional time series
        elif anlRgn == 'y':
            # select the region(s) for evaluation. model and obs have been selected before entering this if block
            print 'There are ', numSubRgn, ' subregions. Select the subregion(s) for evaluation'
            rgnSelect = misc.selectSubRegion(subRegions)
            print 'selected region for evaluation= ', rgnSelect
            # Select the model & obs data to be evaluated
            oData = ma.zeros(nT)
            mData = ma.zeros(nT)
            oData = obsRgn[obsSelect, rgnSelect, :]
            mData = mdlRgn[mdlSelect, rgnSelect, :]

            # compute the monthly-mean climatology to construct the annual cycle
            obsTseries, obsAnnualCycle = calcAnnualCycleMeans(oData)
            mdlTseries, mdlAnnualCycle = calcAnnualCycleMeans(mData)
            print 'obsAnnCyc= ', obsAnnualCycle
            print 'mdlAnnCyc= ', mdlAnnualCycle

            #--------------------------------
            # (mp.008) Select performance metric
            #----------------------------------------------------------------------------------------------------
            #metricOption = misc.select_metrics()
            # Temporarily, compute the RMSE and pattern correlation for the simulated 
            # and observed annual cycle based on monthly means
            # TODO This aren't used. Missing something here???
            
            tempRMS = calcRootMeanSquaredDifferenceAveragedOverTime(mdlAnnualCycle, obsAnnualCycle)
            tempCOR, tempSIG = stats.pearsonr(mdlAnnualCycle, obsAnnualCycle)

            #--------------------------------
            # (mp.009) Plot results
            #----------------------------------------------------------------------------------------------------
            # Data-specific plot options: i.e. adjust model data units & set plot color bars
            colorbar = 'rainbow'
            if varName == 'pr':                      # set color bar for prcp
                colorbar = plt.cm.jet

            # 1-d data, e.g. Time series plots
            plotFileName = 'anncyc_' + varName + '_' + subRgnName[rgnSelect][0:3]
            if(os.path.exists(plotFileName) == True):
                cmnd = 'rm -f ' + plotFileName
                subprocess.call(cmnd, shell = True)
            year_labels = False         # for annual cycle plots
            mytitle = 'Annual Cycle of ' + varName + ' at Sub-Region ' + subRgnName[rgnSelect][0:3]
            # Create a list of datetimes to represent the annual cycle, one per month.
            times = []
            for m in xrange(12):
                times.append(datetime.datetime(2000, m + 1, 1, 0, 0, 0, 0))
            #for i in np.arange(12):
            #  times.append(i+1)
            _ = plots.draw_time_series_plot(mdlAnnualCycle, times, plotFileName, workdir, 
                                                   data2 = obsAnnualCycle, mytitle = mytitle, ytitle = 'Y', 
                                                   xtitle = 'MONTH', year_labels = year_labels)

            # Repeat for another metric
            doMetricsOption = raw_input('Do you want to perform another evaluation? [y/n]\n> ').lower()

    # Processing complete if a user enters 'n' for 'doMetricsOption'
    print 'RCMES processing completed.'
