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
from ocw import plotter
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
    data = dataset1.reshape([nregion, nT/12, 12])
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
    nregion, nT = dataset1.shape
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
        
    
    temporalCorrelation = 0.
    sigLev = 0.
    t1=evaluationData[:]
    t2=referenceData[:]
    if t1.min()!=t1.max() and t2.min()!=t2.max():
        temporalCorrelation, sigLev=stats.pearsonr(t1,t2)
        sigLev=1.-sigLev  # p-value => confidence level
                    
        return temporalCorrelation

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


def calcPdf(evaluationData, referenceData):
    '''
    Routine to calculate a normalized Probability Distribution Function with 
    bins set according to data range.
    Equation from Perkins et al. 2007

        PS=sum(min(Z_O_i, Z_M_i)) where Z is the distribution (histogram of the data for either set)
        called in do_rcmes_processing_sub.py
         
    Inputs::
        2 arrays of data
        t1 is the modelData and t2 is 3D obsdata - time,lat, lon NB, time here 
        is the number of time values eg for time period 199001010000 - 199201010000 
        
        if annual means-opt 1, was chosen, then t2.shape = (2,lat,lon)
        
        if monthly means - opt 2, was choosen, then t2.shape = (24,lat,lon)
        
    User inputs: number of bins to use and edges (min and max)
    Output:

        one float which represents the PDF for the year

    TODO:  Clean up this docstring so we have a single purpose statement
     
    Routine to calculate a normalised PDF with bins set according to data range.

    Input::
        2 data  arrays, modelData and obsData

    Output::
        PDF for the year

    '''
    # float to store the final PDF similarity score
    similarityScore = 0.0

    print 'min modelData', evaluationData[:, :, :].min()
    print 'max modelData', evaluationData[:, :, :].max()
    print 'min obsData', referenceData[:, :, :].min()
    print 'max obsData', referenceData[:, :, :].max()
    # find a distribution for the entire dataset
    #prompt the user to enter the min, max and number of bin values. 
    # The max, min info above is to help guide the user with these choises
    print '****PDF input values from user required **** \n'
    nbins = int (raw_input('Please enter the number of bins to use. \n'))
    minEdge = float(raw_input('Please enter the minimum value to use for the edge. \n'))
    maxEdge = float(raw_input('Please enter the maximum value to use for the edge. \n'))
    
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
    


def calculate_metrics_and_make_plots(varName, workdir, lons, lats, obsData, mdlData, obsRgn, mdlRgn, obsList, mdlList, subRegions, \
                                     subRgnLon0, subRgnLon1, subRgnLat0, subRgnLat1):
    '''
    Purpose:: 
        Calculate all the metrics used in Kim et al. [2013] paper and plot them 

    Input::
        varName - evaluating variable
        workdir -
        lons -
        lats -
        obsData -
        mdlData -
        obsRgn -
        mdlRgn -
        obsList -
        mdlList -
        subRegions - 
        subRgnLon0, subRgnLat0 - southwest boundary of sub-regions [numSubRgn]
        subRgnLon1, subRgnLat1 - northeast boundary of sub-regions [numSubRgn]
    Output:: 
        png files
        
     '''
   
   
    nobs, nt, ny, nx = obsData.shape
    nmodel = mdlData.shape[0]
    ### TODO: unit conversion (K to C)
    if varName == 'temp':
        obsData[0, :, :, :] = obsData[0, :, :, :] - 273.15
        if subRegions:
            obsRgn[0, :, :] = obsRgn[0, :, :] - 273.15
    if varName == 'prec' and obsData.max() > mdlData.max()*1000.:
        mdlData[:, :, :, :] = mdlData[:, :, :, :]*86400.
        if subRegions:
            mdlRgn[:, :, :] = mdlRgn[:, :, :]*86400.
        
    oTser, oClim = calcClimYear( obsData[0, :, :, :])
    bias_of_overall_average = ma.zeros([nmodel, ny, nx])
    spatial_stdev_ratio = np.zeros([nmodel])
    spatial_corr = np.zeros([nmodel])
    mdlList.append('ENS')
    
    for imodel in np.arange(nmodel):
        mTser, mClim = calcClimYear( mdlData[imodel,:,:,:])
        bias_of_overall_average[imodel,:,:] = calcBias(mClim, oClim)
        spatial_corr[imodel], sigLev = calcPatternCorrelation(oClim, mClim)
        spatial_stdev_ratio[imodel] = calcSpatialStdevRatio(mClim, oClim)   
    fig_return = plotter.draw_contour_map(oClim, lats, lons, workdir+'/observed_climatology_'+varName, fmt='png', gridshape=(1, 1),
                   clabel='', ptitle='', subtitles=obsList, cmap=None, 
                   clevs=None, nlevs=10, parallels=None, meridians=None,
                   extend='neither')    
    # TODO:
    # Be sure to update "gridshape" argument to be the number of sub plots (rows,columns). This should be improved so that the 
    # gridshape is optimally determined for a given number of models. For example:
    # For 3 models, a gridshape of (2,2) would be sensible:
    # X X 
    # X
    #
    fig_return = plotter.draw_contour_map(bias_of_overall_average, lats, lons, workdir+'/bias_of_climatology_'+varName, fmt='png', gridshape=(6, 2),
                   clabel='', ptitle='', subtitles=mdlList, cmap=None, 
                   clevs=None, nlevs=10, parallels=None, meridians=None,
                   extend='neither')
    Taylor_data = np.array([spatial_stdev_ratio, spatial_corr]).transpose()
    
    fig_return = plotter.draw_taylor_diagram(Taylor_data, mdlList, refname='CRU', fname = workdir+'/Taylor_'+varName, fmt='png',frameon=False)

    if subRegions:
        nseason = 2      # (0: summer and 1: winter)
        nregion = len(subRgnLon0)
        season_name = ['summer','winter']
        rowlabels = ['PNw','PNe','CAn','CAs','SWw','SWe','COL','GPn','GPc','GC','GL','NE','SE','FL']
        collabels = ['M1','M2','M3','M4','M5','M6','ENS']
        collabels[nmodel-1] = 'ENS'
        
        for iseason in [0,1]:
            portrait_subregion = np.zeros([4, nregion, nmodel])
            portrait_titles = ['(a) Normalized Bias', '(b) Normalized STDV', '(c) Normalized RMSE', '(d) Correlation']
            if iseason == 0:
                monthBegin=6
                monthEnd=8
            if iseason == 1:
                monthBegin=12
                monthEnd=2
                      
            obsTser,obsClim = calcClimSeasonSubRegion(6,8,obsRgn[0,:,:])
            for imodel in np.arange(nmodel):
                mTser, mClim =  calcClimSeasonSubRegion(6,8,mdlRgn[imodel,:,:])
                for iregion in np.arange(nregion):
                      portrait_subregion[0,iregion,imodel] = calcBias(mClim[iregion],obsClim[iregion])/calcTemporalStdev(obsTser[iregion,:])   
                      portrait_subregion[1,iregion,imodel] = calcTemporalStdev(mTser[iregion,:])/ calcTemporalStdev(obsTser[iregion,:]) 
                      portrait_subregion[2,iregion,imodel] = calcRootMeanSquaredDifferenceAveragedOverTime(mTser[iregion,:], obsTser[iregion,:])/calcTemporalStdev(obsTser[iregion,:])
                      portrait_subregion[3,iregion, imodel] = calcTemporalCorrelationSubRegion(mTser[iregion,:],obsTser[iregion,:])
            portrait_return = plotter.draw_portrait_diagram(portrait_subregion, rowlabels, collabels[0:nmodel], workdir+'/portrait_diagram_'+season_name[iseason]+'_'+varName, fmt='png', 
                             gridshape=(2, 2), xlabel='', ylabel='', clabel='', 
                             ptitle='', subtitles=portrait_titles, cmap=None, clevs=None, 
                             nlevs=10, extend='neither')  
            # annual cycle
            nmonth = 12
            times = np.arange(nmonth)
            data_names = [obsList[0]] + list(mdlList)
            annual_cycle = np.zeros([nregion, nmonth, nmodel+1])
            obsTser, annual_cycle[:, :, 0] = calcAnnualCycleMeansSubRegion(obsRgn[0,:,:])
            obsStd = calcAnnualCycleStdevSubRegion(obsRgn[0,:,:])
            for imodel in np.arange(nmodel):
                mdlTser, annual_cycle[:, :, imodel+1] = calcAnnualCycleMeansSubRegion(mdlRgn[imodel, :, :])
            # Make annual_cycle shape compatible with draw_time_series
            annual_cycle = annual_cycle.swapaxes(1, 2)
            tseries_return = plotter.draw_time_series(annual_cycle, times, data_names, workdir+'/time_series_'+varName, gridshape=(7, 2), 
                  subtitles=rowlabels, label_month=True)
            
         
        
