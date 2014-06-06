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

import datetime
import subprocess
import sys
import os
import numpy as np
import numpy.ma as ma
from math import floor, log
from toolkit import process
from utils import misc
from storage import files 
from pylab import *
import scipy.stats.mstats as mstats
import matplotlib as mpl
import matplotlib.dates
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import ImageGrid
from matplotlib.font_manager import FontProperties
from mpl_toolkits.basemap import Basemap
from utils.Taylor import TaylorDiagram
# 6/10/2012 JK: any Ngl dependence will be removed in later versions
#import Ngl

def calc_ann_mean(t2, time):
    '''
    Calculate annual cycle in terms of monthly means at every grid point.
    '''
    # Calculate annual cycle in terms of monthly means at every grid point including single point case (ndim=1)
    # note: this routine is identical to 'calc_annual_cycle_means': must be converted to calculate the annual mean
    # Extract months from time variable
    months = np.empty(len(time))
    for t in np.arange(len(time)):
        months[t] = time[t].month
    if t2.ndim == 3:
        means = ma.empty((12, t2.shape[1], t2.shape[2])) # empty array to store means
        # Calculate means month by month
        for i in np.arange(12)+1:
            means[i - 1, :, :] = t2[months == i, :, :].mean(0)
    if t2.ndim == 1:
        means = np.empty((12)) # empty array to store means
        # Calculate means month by month
        for i in np.arange(12)+1:
            means[i - 1] = t2[months == i].mean(0)
    return means


def calc_clim_month(t2, time):
    '''
    Calculate monthly means at every grid point.
    '''
    # Calculate monthly means at every grid point including single point case (ndim=1)
    # Extract months from time variable
    months = np.empty(len(time))
    for t in np.arange(len(time)):
        months[t] = time[t].month
    if t2.ndim == 3:
        means = ma.empty((12, t2.shape[1], t2.shape[2])) # empty array to store means
        # Calculate means month by month
        for i in np.arange(12) + 1:
            means[i - 1, :, :] = t2[months == i, :, :].mean(0)
    if t2.ndim == 1:
        means = np.empty((12)) # empty array to store means
        # Calculate means month by month
        for i in np.arange(12) + 1:
            means[i - 1] = t2[months == i].mean(0)
    return means


def calc_clim_year(nYR, nT, ngrdY, ngrdX, t2, time):
    '''
    Calculate annual mean timeseries and climatology for both 2-D and point time series.
    '''
    # Extract months from time variable
    yy = np.empty(nT)
    mm = np.empty(nT)
    for t in np.arange(nT):
        yy[t] = time[t].year
        mm[t] = time[t].month
    if t2.ndim == 3:
        tSeries = ma.zeros((nYR, ngrdY, ngrdX))
        i = 0
        for myunit in np.unique(yy):
            wh = (yy == myunit)
            data = t2[wh, :, :]
            tSeries[i, :, :] = ma.average(data, axis = 0)
            #print 'data.shape= ',data.shape,'  i= ',i,'  yy= ',yy
            i += 1
        means = ma.zeros((ngrdY, ngrdX))
        means = ma.average(tSeries, axis = 0)
    elif t2.ndim == 1:
        tSeries = ma.zeros((nYR))
        i = 0
        for myunit in np.unique(yy):
            wh = (yy == myunit)
            data = t2[wh]
            tSeries[i] = ma.average(data, axis = 0)
            #print 'data.shape= ',data.shape,'  i= ',i,'  yy= ',yy
            i += 1
        means = ma.zeros((ngrdY, ngrdX))
        means = ma.average(tSeries, axis = 0)
    return tSeries, means


def calc_clim_season(nYR, nT, mB, mE, ngrdY, ngrdX, t2, time):
    '''
    Calculate seasonal mean timeseries and climatology for both 2-D and point time series.
    '''
    #-------------------------------------------------------------------------------------
    # Calculate seasonal mean timeseries and climatology for both 2-d and point time series
    # The season to be calculated is defined by moB and moE; moE>=moB always
    #-------------------------------------------------------------------------------------
    # Extract months from time variable
    yy = np.empty(nT)
    mm = np.empty(nT)
    for t in np.arange(nT):
        yy[t] = time[t].year
        mm[t] = time[t].month
    if t2.ndim == 3:
        tSeries = ma.zeros((nYR, ngrdY, ngrdX))
        i = 0
        for myunit in np.unique(yy):
            wh = (yy == myunit) & (mm >= mB) & (mm <= mE)
            data = t2[wh, :, :]
            tSeries[i, :, :] = ma.average(data, axis = 0)
            #print 'data.shape= ',data.shape,'  i= ',i,'  yy= ',yy
            i += 1
        means = ma.zeros((ngrdY, ngrdX))
        means = ma.average(tSeries, axis = 0)
    elif t2.ndim == 1:
        tSeries = ma.zeros((nYR))
        i = 0
        for myunit in np.unique(yy):
            wh = (yy == myunit) & (mm >= mB) & (mm <= mE)
            data = t2[wh]
            tSeries[i] = ma.average(data, axis = 0)
            #print 'data.shape= ',data.shape,'  i= ',i,'  yy= ',yy
            i += 1
        means = ma.zeros((ngrdY, ngrdX))
        means = ma.average(tSeries, axis = 0)
    return tSeries, means


def calc_clim_mo(nYR, nT, ngrdY, ngrdX, t2, time):
    '''
    Calculate monthly means at every grid points and the annual time series of single model including single point case (ndim=1).
    JK20: This is modified from 'calc_clim_month'  with additional arguments & output, the annual time series of single model output (mData)
    6/8/2013: bug fix: mm = months[t] --> mm = months[t] - 1, otherwise array overflow occurs
    '''
    # Extract months and monthly time series from the time and raw variable, respectively
    months = np.empty(nT)
    for t in np.arange(nT):
        months[t] = time[t].month
        if t == 0:
            yy0 = time[t].year
        # for a 2-D time series data
    if t2.ndim == 3:
        mData = ma.empty((nYR, 12, ngrdY, ngrdX))
        for t in np.arange(nT):
            yy = time[t].year
            mm = months[t] - 1
            yr = yy - yy0
            mData[yr, mm, :, :] = t2[t, :, :]
        # Calculate means month by month. means is an empty array to store means
        means = ma.empty((12, ngrdY, ngrdX))
        for i in np.arange(12) + 1:
            means[i - 1, :, :] = t2[months == i, :, :].mean(0)
        # for a point time series data
    if t2.ndim == 1:
        mData = ma.empty((nYR, 12))
        for t in np.arange(nT):
            yy = time[t].year
            mm = months[t]
            yr = yy - yy0
            mData[yr, mm] = t2[t]
        means = np.empty((12))
        # Calculate means month by month. means is an empty array to store means
        for i in np.arange(12) + 1:
            means[i - 1] = t2[months == i].mean(0)
    return mData, means


def calc_clim_One_month(moID, nYR, nT, t2, time):
    '''
    Calculate the montly mean at every grid point for a specified month.
    '''
    #-------------------------------------------------------------------------------------
    # Calculate monthly means at every grid point for a specified month
    #-------------------------------------------------------------------------------------
    # Extract months and the corresponding time series from time variable
    months = np.empty(nT)
    for t in np.arange(nT):
        months[t] = time[t].month
    if t2.ndim == 3:
        mData = ma.empty((nYR, t2.shape[1], t2.shape[2])) # empty array to store time series
        n = 0
        if months[t] == moID:
            mData[n, :, :] = t2[t, :, :]
            n += 1
        means = ma.empty((t2.shape[1], t2.shape[2])) # empty array to store means
        # Calculate means for the month specified by moID
        means[:, :] = t2[months == moID, :, :].mean(0)
    return mData, means


def calc_annual_cycle_means(data, time):
    '''
     Calculate monthly means for every grid point
     
     Inputs:: 
     	data - masked 3d array of the model data (time, lon, lat)
     	time - an array of python datetime objects
    '''
    # Extract months from time variable
    months = np.empty(len(time))
    
    for t in np.arange(len(time)):
        months[t] = time[t].month
    
    #if there is data varying in t and space
    if data.ndim == 3:
        # empty array to store means
        means = ma.empty((12, data.shape[1], data.shape[2]))
        
        # Calculate means month by month
        for i in np.arange(12) + 1:
            means[i - 1, :, :] = data[months == i, :, :].mean(0)
        
    #if the data is a timeseries over area-averaged values
    if data.ndim == 1:
        # TODO - Investigate using ma per KDW
        means = np.empty((12)) # empty array to store means??WHY NOT ma?
        
        # Calculate means month by month
        for i in np.arange(12) + 1:
            means[i - 1] = data[months == i].mean(0)
    
    return means


def calc_annual_cycle_std(data, time):
    '''
     Calculate monthly standard deviations for every grid point
    '''
    # Extract months from time variable
    months = np.empty(len(time))
    
    for t in np.arange(len(time)):
        months[t] = time[t].month
    
    # empty array to store means
    stds = np.empty((12, data.shape[1], data.shape[2]))
    
    # Calculate means month by month
    for i in np.arange(12) + 1:
        stds[i - 1, :, :] = data[months == i, :, :].std(axis = 0, ddof = 1)
    
    return stds


def calc_annual_cycle_domain_means(data, time):
    '''
     Calculate domain means for each month of the year
    '''
    # Extract months from time variable
    months = np.empty(len(time))
    
    for t in np.arange(len(time)):
        months[t] = time[t].month
       	
    means = np.empty(12) # empty array to store means
    
    # Calculate means month by month
    for i in np.arange(12) + 1:
        means[i - 1] = data[months == i, :, :].mean()
    
    return means


def calc_annual_cycle_domain_std(data, time):
    '''
     Calculate domain standard deviations for each month of the year
    '''
    # Extract months from time variable
    months = np.empty(len(time))
    
    for t in np.arange(len(time)):
        months[t] = time[t].month
    
    stds = np.empty(12) # empty array to store means
    
    # Calculate means month by month
    for i in np.arange(12) + 1:
        stds[i - 1] = data[months == i, :, :].std(ddof = 1)
    
    return stds


def calc_bias_annual(t1, t2, optn):        # Mean Bias
    '''
    Calculate the mean difference between two fields over time for each grid point.
    '''
    # Calculate mean difference between two fields over time for each grid point
    # Precrocessing of both obs and model data ensures the absence of missing values
    diff = t1-t2
    if(open == 'abs'): 
        diff = abs(diff)
    bias = diff.mean(axis = 0)
    return bias


def calc_bias(t1, t2):
    '''
    Calculate mean difference between two fields over time for each grid point
    
    Classify missing data resulting from multiple times (using threshold 
    data requirement)
    
    i.e. if the working time unit is monthly data, and we are dealing with 
    multiple months of data then when we show mean of several months, we need
    to decide what threshold of missing data we tolerate before classifying a
    data point as missing data.
    '''
    t1Mask = process.create_mask_using_threshold(t1, threshold = 0.75)
    t2Mask = process.create_mask_using_threshold(t2, threshold = 0.75)
    
    diff = t1 - t2
    bias = diff.mean(axis = 0)
    
    # Set mask for bias metric using missing data in obs or model data series
    #   i.e. if obs contains more than threshold (e.g.50%) missing data 
    #        then classify time average bias as missing data for that location. 
    bias = ma.masked_array(bias.data, np.logical_or(t1Mask, t2Mask))
    return bias


def calc_bias_dom(t1, t2):
    '''
     Calculate domain mean difference between two fields over time
    '''
    diff = t1 - t2
    bias = diff.mean()
    return bias


def calc_difference(t1, t2):
    '''
     Calculate mean difference between two fields over time for each grid point
    '''
    print 'Calculating difference'
    diff = t1 - t2
    return diff


def calc_mae(t1, t2):
    '''
    Calculate mean difference between two fields over time for each grid point
    
    Classify missing data resulting from multiple times (using threshold 
    data requirement) 
    
    i.e. if the working time unit is monthly data, and we are dealing with
    multiple months of data then when we show mean of several months, we need
    to decide what threshold of missing data we tolerate before classifying
    a data point as missing data.
    '''
    t1Mask = process.create_mask_using_threshold(t1, threshold = 0.75)
    t2Mask = process.create_mask_using_threshold(t2, threshold = 0.75)
    
    diff = t1 - t2
    adiff = abs(diff)
    
    mae = adiff.mean(axis = 0)
    
    # Set mask for mae metric using missing data in obs or model data series
    #   i.e. if obs contains more than threshold (e.g.50%) missing data 
    #        then classify time average mae as missing data for that location. 
    mae = ma.masked_array(mae.data, np.logical_or(t1Mask, t2Mask))
    return mae


def calc_mae_dom(t1, t2):
    '''
     Calculate domain mean difference between two fields over time
    '''
    diff = t1 - t2
    adiff = abs(diff)
    mae = adiff.mean()
    return mae


def calc_rms(t1, t2):
    '''
     Calculate mean difference between two fields over time for each grid point
    '''
    diff = t1 - t2
    sqdiff = diff ** 2
    msd = sqdiff.mean(axis = 0)
    rms = np.sqrt(msd)
    return rms


def calc_rms_dom(t1, t2):
    '''
     Calculate RMS differences between two fields
    '''
    diff = t1 - t2
    sqdiff = diff ** 2
    msd = sqdiff.mean()
    rms = np.sqrt(msd)
    return rms


def calc_temporal_stdv(t1):
    '''
    Calculate the temporal standard deviation.

    Input:
        t1 - data array of any shape

    Output:
        A 2-D array of temporal standard deviation
    '''
    # TODO Make sure the first dimension of t1 is teh time axis.
    stdv = t1.std(axis = 0)
    return stdv


def calc_temporal_anom_cor(mD, oD):
    '''
    Calculate the temporal anomaly correlation.

    Assumption(s);
        The first dimension of mD and oD is the time axis.

    Input:
        mD - model data array of any shape
        oD - observation data array of any shape

    Output:
        A 2-D array of time series pattern correlation coefficients at each grid point.

    REF: 277-281 in Stat methods in atmos sci by Wilks, 1995, Academic Press, 467pp.
    '''
    mo = oD.mean(axis = 0)
    nt = oD.shape[0]
    deno1 = ((mD - mo) * (mD - mo)).sum(axis = 0)
    deno2 = ((oD - mo) * (oD - mo)).sum(axis = 0)
    patcor = ((mD - mo) * (oD - mo)).sum(axis = 0) / sqrt(deno1 * deno2)
    return patcor


def calc_spatial_anom_cor(mD, oD):
    '''
    Calculate anomaly correlation between two 2-D arrays.

    Input:
        mD - 2-D array of model data
        oD - 2-D array of observation data

    Output:
        The anomaly correlation between the two input arrays.
    '''
    mo = oD.mean()
    d1 = ((mD - mo)*(mD - mo)).sum()
    d2 = ((oD - mo)*(oD - mo)).sum()
    patcor = ((mD - mo) * (oD - mo)).sum() / sqrt(d1 * d2)
    return patcor


def calc_temporal_pat_cor(t1, t2):
    '''
     Calculate the Temporal Pattern Correlation
    
      Input::
        t1 - 3d array of model data
        t2 - 3d array of obs data
         
      Output::
        2d array of time series pattern correlation coefficients at each grid point.
        **Note:** std_dev is standardized on 1 degree of freedom
    '''
    mt1 = t1.mean(axis = 0)
    mt2 = t2.mean(axis = 0)
    nt = t1.shape[0]
    sigma_t1 = t1.std(axis = 0, ddof = 1)
    sigma_t2 = t2.std(axis = 0, ddof = 1)
    patcor = ((((t1 - mt1) * (t2 - mt2)).sum(axis = 0)) / (nt)) / (sigma_t1 * sigma_t2)
    
    return patcor


def calc_spatial_pat_cor(t1, t2):
    '''
    Calcualte pattern correlation between 2-D arrays.
    6/10/2013: JK: Enforce both t1 & t2 have the identical mask before calculating std and corr

    Input:
        t1 - 2-D array of model data
        t2 - 2-D array of observation data

    Output:
        Pattern correlation between two input arrays.
    '''
    import numpy as np
    msk1 = ma.getmaskarray(t1)
    msk2 = ma.getmaskarray(t2)
    t1 = ma.masked_array(t1.data, np.logical_or(msk1, msk2))
    t2 = ma.masked_array(t2.data, np.logical_or(msk1, msk2))
    np = ma.count(t1)
    mt1 = t1.mean()
    mt2 = t2.mean()
    st1 = t1.std()
    st2 = t2.std()
    patcor = ((t1 - mt1) * (t2 - mt2)).sum() / (np * st1 * st2)
    return patcor


def calc_pat_cor2D(t1, t2, nT):
    '''
    Calculate the pattern correlation between 3-D input arrays.

    Input:
        t1 - 3-D array of model data
        t2 - 3-D array of observation data
        nT

    Output:
        1-D array (time series) of pattern correlation coefficients.
    '''
    # TODO - Update docstring. What is nT?
    nt = t1.shape[0]
    if(nt != nT):
        print 'input time levels do not match: Exit', nT, nt
        return -1
    # store results in list for convenience (then convert to numpy array at the end)
    patcor = []
    for t in xrange(nt):
        mt1 = t1[t, :, :].mean()
        mt2 = t2[t, :, :].mean()
        sigma_t1 = t1[t, :, :].std()
        sigma_t2 = t2[t, :, :].std()
        # TODO: make means and standard deviations weighted by grid box area.
        patcor.append((((((t1[t, :, :] - mt1) * (t2[t, :, :] - mt2)).sum()) / 
                     (t1.shape[1] * t1.shape[2]) ) / (sigma_t1 * sigma_t2)))
        print t, mt1.shape, mt2.shape, sigma_t1.shape, sigma_t2.shape, patcor[t]
    # TODO: deal with missing data appropriately, i.e. mask out grid points with missing data above tolerence level
    # convert from list into numpy array
    patcor = numpy.array(patcor)
    #print patcor.shape
    return patcor

def calc_pat_cor(dataset_1, dataset_2):
    '''
     Purpose: Calculate the Pattern Correlation Timeseries
     Assumption(s)::  
     	Both dataset_1 and dataset_2 are the same shape.
        * lat, lon must match up
        * time steps must align (i.e. months vs. months)
     Input::
        dataset_1 - 3d (time, lat, lon) array of data
        dataset_2 - 3d (time, lat, lon) array of data
     Output:
        patcor - a 1d array (time series) of pattern correlation coefficients.
     **Note:** Standard deviation is using 1 degree of freedom.  Debugging print 
     statements to show the difference the n-1 makes. http://docs.scipy.org/doc/numpy/reference/generated/numpy.std.html
     6/17/2013 JK: Add an option for a 1-d arrays
    '''

    # TODO:  Add in try block to ensure the shapes match

    nDim1 = dataset_1.ndim
    nDim2 = dataset_2.ndim
    if nDim1 != nDim2:
        print 'dimension mismatch in calc_pat_cor: exit', nDim1,nDim2
        sys.exit()

    if nDim1 == 1:
        mt1 = dataset_1.mean()
        mt2 = dataset_2.mean()
        nt = dataset_1.shape[0]
        sigma_t1 = dataset_1.std()
        sigma_t2 = dataset_2.std()
        patcor=((dataset_1 - mt1) * (dataset_2 - mt2)).sum() / (nt * sigma_t1 * sigma_t2)

    elif nDim1 == 2:
        # find mean and std_dev 
        mt1 = dataset_1.mean()
        mt2 = dataset_2.mean()
        ny = dataset_1.shape[0]
        nx = dataset_1.shape[1]
        sigma_t1 = dataset_1.std()
        sigma_t2 = dataset_2.std()
        patcor=((dataset_1 - mt1) * (dataset_2 - mt2)).sum() / ((ny * nx) * (sigma_t1 * sigma_t2))

    elif nDim1 == 3:
        nt = dataset_1.shape[0]
        ny = dataset_1.shape[1]
        nx = dataset_1.shape[2]
        # store results in list for convenience (then convert to numpy array)
        patcor = []
        for t in xrange(nt):
            # find mean and std_dev 
            mt1 = dataset_1[t, :, :].mean()
            mt2 = dataset_2[t, :, :].mean()
            sigma_t1 = dataset_1[t, :, :].std(ddof = 1)
            sigma_t2 = dataset_2[t, :, :].std(ddof=1)
            # TODO: make means and standard deviations weighted by grid box area.
            # Equation from Santer_et_al 1995 
            #     patcor = (1/(N*M_std*O_std))*sum((M_i-M_bar)*(O_i-O_bar))
            patcor.append((((((dataset_1[t, :, :] - mt1) * (dataset_2[t, :, :] - mt2)).sum()) / (ny * nx)) / (sigma_t1 * sigma_t2)))
            print t, mt1.shape, mt2.shape, sigma_t1.shape, sigma_t2.shape, patcor[t]
            # TODO: deal with missing data appropriately, i.e. mask out grid points
            # with missing data above tolerance level
        # convert from list into numpy array
        patcor = np.array(patcor)
    
    #print patcor.shape, patcor
    return patcor


def calc_anom_corn(dataset_1, dataset_2, climatology = None):
    '''
    Calculate the anomaly correlation.

    Input:
        dataset_1 - First input dataset
        dataset_2 - Second input dataset
        climatology - Optional climatology input array. Assumption is that it is for 
            the same time period by default.

    Output:
        The anomaly correlation.
    '''
    # TODO: Update docstring with actual useful information

    # store results in list for convenience (then convert to numpy array)
    anomcor = []    
    nt = dataset_1.shape[0]
    #prompt for the third file, i.e. climo file...  
    #include making sure the lat, lon and times are ok for comparision
    # find the climo in here and then using for eg, if 100 yrs 
    # is given for the climo file, but only looking at 10yrs
    # ask if want to input climo dataset for use....if no, call previous 
   
    if climatology != None:
        climoFileOption = raw_input('Would you like to use the full observation dataset as \
                                     the climatology in this calculation? [y/n] \n>')
        if climoFileOption == 'y':
            base_dataset = climatology
        else:
            base_dataset = dataset_2
    for t in xrange(nt):
        mean_base = base_dataset[t, :, :].mean()
        anomcor.append((((dataset_1[t, :, :] - mean_base) * (dataset_2[t, :, :] - mean_base)).sum()) / 
                       np.sqrt(((dataset_1[t, :, :] - mean_base) ** 2).sum() * 
                               ((dataset_2[t, :, :] - mean_base) ** 2).sum()))
        print t, mean_base.shape, anomcor[t]

    # TODO: deal with missing data appropriately, i.e. mask out grid points 
    # with missing data above tolerence level
    
    # convert from list into numpy array
    anomcor = np.array(anomcor)
    print anomcor.shape, anomcor.ndim, anomcor
    return anomcor


def calc_anom_cor(t1, t2):
    '''
     Calculate the Anomaly Correlation (Deprecated)
    '''
    
    nt = t1.shape[0]
    
    # store results in list for convenience (then convert to numpy 
    # array at the end)
    anomcor = []
    for t in xrange(nt):
        
        mt2 = t2[t, :, :].mean()
        
        sigma_t1 = t1[t, :, :].std(ddof = 1)
        sigma_t2 = t2[t, :, :].std(ddof = 1)
        
        # TODO: make means and standard deviations weighted by grid box area.
        
        anomcor.append(((((t1[t, :, :] - mt2) * (t2[t, :, :] - mt2)).sum()) / 
                        (t1.shape[1] * t1.shape[2])) / (sigma_t1 * sigma_t2))
        
        print t, mt2.shape, sigma_t1.shape, sigma_t2.shape, anomcor[t]
        
        # TODO: deal with missing data appropriately, i.e. mask out grid points with 
        #       missing data above tolerence level
        
    # convert from list into numpy array
    anomcor = np.array(anomcor)
    print anomcor.shape, anomcor.ndim, anomcor
    return anomcor


def calc_nash_sutcliff(dataset_1, dataset_2):
    '''
    Routine to calculate the Nash-Sutcliff coefficient of efficiency (E)
    
    Assumption(s)::  
    	Both dataset_1 and dataset_2 are the same shape.
        * lat, lon must match up
        * time steps must align (i.e. months vs. months)
    
    Input::
    	dataset_1 - 3d (time, lat, lon) array of data
        dataset_2 - 3d (time, lat, lon) array of data
    
    Output:
        nashcor - 1d array aligned along the time dimension of the input
        datasets. Time Series of Nash-Sutcliff Coefficient of efficiency
     
     '''

    nt = dataset_1.shape[0]
    nashcor = []
    for t in xrange(nt):
        mean_dataset_2 = dataset_2[t, :, :].mean()
        
        nashcor.append(1 - ((((dataset_2[t, :, :] - dataset_1[t, :, :]) ** 2).sum()) / 
                            ((dataset_2[t, :, :] - mean_dataset_2) ** 2).sum()))
        
        print t, mean_dataset_2.shape, nashcor[t]
        
    nashcor = np.array(nashcor)
    print nashcor.shape, nashcor.ndim, nashcor
    return nashcor


def calc_pdf(dataset_1, dataset_2):
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
    #list to store PDFs of modelData and obsData
    pdf_mod = []
    pdf_obs = []
    # float to store the final PDF similarity score
    similarity_score = 0.0
    d1_max = dataset_1.amax()
    d1_min = dataset_1.amin()

    print 'min modelData', dataset_1[:, :, :].min()
    print 'max modelData', dataset_1[:, :, :].max()
    print 'min obsData', dataset_2[:, :, :].min()
    print 'max obsData', dataset_2[:, :, :].max()
    # find a distribution for the entire dataset
    #prompt the user to enter the min, max and number of bin values. 
    # The max, min info above is to help guide the user with these choises
    print '****PDF input values from user required **** \n'
    nbins = int (raw_input('Please enter the number of bins to use. \n'))
    minEdge = float(raw_input('Please enter the minimum value to use for the edge. \n'))
    maxEdge = float(raw_input('Please enter the maximum value to use for the edge. \n'))
    
    mybins = np.linspace(minEdge, maxEdge, nbins)
    print 'nbins is', nbins, 'mybins are', mybins
    
    
    # TODO:  there is no 'new' kwargs for numpy.histogram 
    # per: http://docs.scipy.org/doc/numpy/reference/generated/numpy.histogram.html
    # PLAN: Replace new with density param.
    pdf_mod, edges = np.histogram(dataset_1, bins = mybins, normed = True, new = True)  
    print 'dataset_1 distribution and edges', pdf_mod, edges
    pdf_obs, edges = np.histogram(dataset_2, bins = mybins, normed = True, new = True)           
    print 'dataset_2 distribution and edges', pdf_obs, edges    
    
    # TODO: drop this
    """
    considering using pdf function from statistics package. It is not 
     installed. Have to test on Mac.  
     http://bonsai.hgc.jp/~mdehoon/software/python/Statistics/manual/index.xhtml#TOC31 
    pdf_mod, edges = stats.pdf(dataset_1, bins=mybins)
    print 'dataset_1 distribution and edges', pdf_mod, edges
    pdf_obs,edges=stats.pdf(dataset_2,bins=mybins)           
    print 'dataset_2 distribution and edges', pdf_obs, edges 
    """

    #find minimum at each bin between lists 
    i = 0
    for model_value in pdf_mod :
        print 'model_value is', model_value, 'pdf_obs[', i, '] is', pdf_obs[i]
        if model_value < pdf_obs[i]:
            similarity_score += model_value
        else:
            similarity_score += pdf_obs[i] 
        i += 1 
    print 'similarity_score is', similarity_score
    return similarity_score


def calc_stdev(t1):
    ''' 
    Calculate the standard deviation for a given dataset.

    Input:
        t1 - Dataset to calculate the standard deviation on.

    Output:
        Array of the standard deviations for each month in the provided dataset.
    '''
    nt = t1.shape[0]
    sigma_t1 = []
    for t in xrange(nt):
        sigma_t1.append(t1[t, :, :].std(ddof = 1))
    sigma_t1 = np.array(sigma_t1)
    print sigma_t1, sigma_t1.shape
    return sigma_t1

# 6/10/2013 JK: plotting routines are added below

def pow_round(x):
    '''
     Function to round x to the nearest power of 10
    '''
    return 10 ** (floor(log(x, 10) - log(0.5, 10)))

def calcNiceIntervals(data, nLevs):
    '''
    Purpose::
        Calculates nice intervals between each color level for colorbars
        and contour plots. The target minimum and maximum color levels are
        calculated by taking the minimum and maximum of the distribution
        after cutting off the tails to remove outliers.

    Input::
        data - an array of data to be plotted
        nLevs - an int giving the target number of intervals

    Output::
        cLevs - A list of floats for the resultant colorbar levels
    '''
    # Find the min and max levels by cutting off the tails of the distribution
    # This mitigates the influence of outliers
    data = data.ravel()
    mnLvl = mstats.scoreatpercentile(data, 5)
    mxLvl = mstats.scoreatpercentile(data, 95)
    locator = mpl.ticker.MaxNLocator(nLevs)
    cLevs = locator.tick_values(mnLvl, mxLvl)

    # Make sure the bounds of cLevs are reasonable since sometimes
    # MaxNLocator gives values outside the domain of the input data
    cLevs = cLevs[(cLevs >= mnLvl) & (cLevs <= mxLvl)]
    return cLevs
    
def calcBestGridShape(nPlots, oldShape):
    '''
    Purpose::
        Calculate a better grid shape in case the user enters more columns
        and rows than needed to fit a given number of subplots.
    
    Input::
        nPlots - an int giving the number of plots that will be made
        oldShape - a tuple denoting the desired grid shape (nRows, nCols) for arranging
                    the subplots originally requested by the user.
   
    Output::
        newShape - the smallest possible subplot grid shape needed to fit nPlots
    '''
    nRows, nCols = oldShape
    size = nRows * nCols
    diff = size - nPlots
    if diff < 0:
        raise ValueError('gridShape=(%d, %d): Cannot fit enough subplots for data' %(nRows, nCols))
    else:
        # If the user enters an excessively large number of
        # rows and columns for gridShape, automatically
        # correct it so that it fits only as many plots
        # as needed
        while diff >= nCols:
            nRows -= 1
            size = nRows * nCols
            diff = size - nPlots

        # Don't forget to remove unnecessary columns too
        if nRows == 1:
            nCols = nPlots

        newShape = nRows, nCols
        return newShape

def drawPortraitDiagramSingle(data, rowLabels, colLabels, cLevs, fName, fType = 'png',
                              xLabel = '', yLabel = '', cLabel = '', pTitle = '', cMap = None):
    '''
    Purpose::
        Makes a portrait diagram plot.
        
    Input::
        data - 2d array of the field to be plotted
        rowLabels - list of strings denoting labels for each row
        colLabels - list of strings denoting labels for each column
        cLevs - a list of integers or floats specifying the colorbar levels
        xLabel - a string specifying the x-axis title
        yLabel - a string specifying the y-axis title
        cLabel - a string specifying the colorbar title
        pTitle - a string specifying the plot title
        fName  - a string specifying the filename of the plot
        fType  - an optional string specifying the filetype, default is .png
        cMap - an optional matplotlib.LinearSegmentedColormap object denoting the colormap,
    '''
    # Set up the colormap if not specified
    if cMap is None:
        cMap = plt.cm.RdBu_r

    # Set up figure and axes
    fig = plt.figure()
    ax = fig.add_subplot(111)

    # Make the portrait diagram
    norm = mpl.colors.BoundaryNorm(cLevs, cMap.N)
    cs = ax.matshow(data, cmap = cMap, aspect = 'auto', origin = 'lower', norm = norm)

    # Add colorbar
    cbar = fig.colorbar(cs, norm = norm, boundaries = cLevs, drawedges = True,
                        pad = .05)
    cbar.set_label(cLabel)
    cbar.set_ticks(cLevs)
    cbar.ax.xaxis.set_ticks_position("none")
    cbar.ax.yaxis.set_ticks_position("none")

    # Add grid lines
    ax.xaxis.set_ticks(np.arange(data.shape[1] + 1))
    ax.yaxis.set_ticks(np.arange(data.shape[0] + 1))
    x = (ax.xaxis.get_majorticklocs() - .5)
    y = (ax.yaxis.get_majorticklocs() - .5)
    ax.vlines(x, y.min(), y.max())
    ax.hlines(y, x.min(), x.max())

    # Configure ticks
    ax.xaxis.tick_bottom()
    ax.xaxis.set_ticks_position('none')
    ax.yaxis.set_ticks_position('none')
    ax.set_xticklabels(rowLabels)
    ax.set_yticklabels(colLabels)

    # Add labels and title
    ax.set_xlabel(xLabel)
    ax.set_ylabel(yLabel)
    ax.set_title(pTitle)

    # Save the figure
    fig.savefig('%s.%s' %(fName, fType))

def drawPortraitDiagram(dataset, rowLabels, colLabels, fName, fType = 'png',
                              gridShape = (1, 1), xLabel = '', yLabel = '', cLabel = '',
                              pTitle = '', subTitles = None, cMap = None, cLevs = None,
                              nLevs = 10, extend = 'neither'):
    '''
    Purpose::
        Makes a portrait diagram plot.

    Input::
        dataset - 3d array of the field to be plotted (nT, nRows, nCols)
        rowLabels - a list of strings denoting labels for each row
        colLabels - a list of strings denoting labels for each column
        fName - a string specifying the filename of the plot
        fType - an optional string specifying the output filetype
        xLabel - an optional string specifying the x-axis title
        yLabel - an optional string specifying the y-axis title
        cLabel - an optional string specifying the colorbar title
        pTitle - a string specifying the plot title
        subTitles - an optional list of strings specifying the title for each subplot
        cMap - an optional matplotlib.LinearSegmentedColormap object denoting the colormap
        cLevs - an optional list of ints or floats specifying colorbar levels
        nLevs - an optional integer specifying the target number of contour levels if
                cLevs is None
        extend - an optional string to toggle whether to place arrows at the colorbar
             boundaries. Default is 'neither', but can also be 'min', 'max', or
             'both'. Will be automatically set to 'both' if cLevs is None.

    '''
    # Handle the single plot case.
    if dataset.ndim == 2 or (dataset.ndim == 3 and dataset.shape[0] == 1):
        dataset = dataset.reshape(1, *dataset.shape)

    nPlots = dataset.shape[0]

    # Make sure gridShape is compatible with input data
    gridShape = calcBestGridShape(nPlots, gridShape)

    # Row and Column labels must be consistent with the shape of
    # the input data too
    nRows, nCols = dataset.shape[1:]
    if len(rowLabels) != nRows or len(colLabels) != nCols:
        raise ValueError('rowLabels and colLabels must have %d and %d elements respectively' %(nRows, nCols))

    # Set up the colormap if not specified
    if cMap is None:
        cMap = plt.cm.coolwarm

    # Set up the figure
    fig = plt.figure()
    fig.set_size_inches((8.5, 11.))
    fig.dpi = 300

    # Make the subplot grid
    grid = ImageGrid(fig, 111,
                nrows_ncols = gridShape,
                axes_pad = 0.4,
                share_all = True,
                aspect = False,
                add_all = True,
                ngrids = nPlots,
                label_mode = "all",
                cbar_mode = 'single',
                cbar_location = 'bottom',
                cbar_pad = '3%',
                cbar_size = .15
                )
   
    # Calculate colorbar levels if not given
    if cLevs is None:
        # Cut off the tails of the distribution
        # for more representative colorbar levels
        cLevs = calcNiceIntervals(dataset, nLevs)
        extend = 'both'

    norm = mpl.colors.BoundaryNorm(cLevs, cMap.N)

    # Do the plotting
    for i, ax in enumerate(grid):
        data = dataset[i]
        cs = ax.matshow(data, cmap = cMap, aspect = 'auto', origin = 'lower', norm = norm)

        # Add grid lines
        ax.xaxis.set_ticks(np.arange(data.shape[1] + 1))
        ax.yaxis.set_ticks(np.arange(data.shape[0] + 1))
        x = (ax.xaxis.get_majorticklocs() - .5)
        y = (ax.yaxis.get_majorticklocs() - .5)
        ax.vlines(x, y.min(), y.max())
        ax.hlines(y, x.min(), x.max())

        # Configure ticks
        ax.xaxis.tick_bottom()
        ax.xaxis.set_ticks_position('none')
        ax.yaxis.set_ticks_position('none')
        ax.set_xticklabels(colLabels, fontsize = 'xx-small')
        ax.set_yticklabels(rowLabels, fontsize = 'xx-small')

        # Add axes title
        if subTitles is not None:
            ax.text(0.5, 1.04, subTitles[i], va = 'center', ha = 'center',
                    transform = ax.transAxes, fontsize = 'small')

    # Add colorbar
    cbar = fig.colorbar(cs, cax = ax.cax, norm = norm, boundaries = cLevs, drawedges = True,
                        extend = extend, orientation = 'horizontal')
    cbar.set_label(cLabel)
    cbar.set_ticks(cLevs)
    cbar.ax.xaxis.set_ticks_position("none")
    cbar.ax.yaxis.set_ticks_position("none")

    # This is an ugly hack to make the title show up at the correct height.
    # Basically save the figure once to achieve tight layout and calculate
    # the adjusted heights of the axes, then draw the title slightly above
    # that height and save the figure again
    fig.savefig('%s.%s' %(fName, fType), bbox_inches = 'tight', dpi = fig.dpi)
    ymax = 0
    for ax in grid:
        bbox = ax.get_position()
        ymax = max(ymax, bbox.ymax)

    # Add figure title and axes labels
    fig.text(.51, .14, yLabel, va = 'center', ha = 'center', rotation = 'horizontal')
    fig.text(.08, .53, xLabel, va = 'center', ha = 'center', rotation = 'vertical')
    fig.suptitle(pTitle, y = ymax + .04, fontsize = 16)
    fig.savefig('%s.%s' %(fName, fType), bbox_inches = 'tight', dpi = fig.dpi)
    fig.clf()

def taylorDiagram(pltDat, pltTit, pltFileName, refName, legendPos, radMax):
    '''
    Draw a Taylor diagram
    '''
    stdref = 1.                     # Standard reference value 
    rect = 111                      # Subplot setting and location
    markerSize = 6
    fig = plt.figure()
    fig.suptitle(pltTit)            # PLot title
    dia = TaylorDiagram (stdref, fig = fig, radMax = radMax, rect = rect, label = refName)
    for i,(stddev,corrcoef,name) in enumerate(pltDat):
        dia.add_sample (stddev, corrcoef, marker = '$%d$' % (i+1), ms = markerSize, label=name)
    # Add ploylines to mark a range specified by input data - 2 be implemented
    #circular_line = dia.add_stddev_contours(0.959, 1, 0.965)
    #circular_line = dia.add_stddev_contours(1.1, 1, 0.973)
    #straight_line = dia.add_contours(0.959, 1, 1.1, 1)
    #straight_line = dia.add_contours(0.959, 0.965, 1.1, 0.973)
    #l=fig.legend (dia.samplePoints, [p.get_label() for p in dia.samplePoints ], handlelength=0., prop={'size':10}, numpoints=1, loc=legendPos)
    # loc: 1='upper right', 2='upper left' or specified in the calling program via "legendPos"
    l = fig.legend (dia.samplePoints, [p.get_label() for p in dia.samplePoints ], handlelength=0., prop={'size':10}, numpoints=1, loc=legendPos)
    l.draw_frame(False)
    plt.savefig(pltFileName)
    pltDat = 0.

def drawTimeSeriesSingle(dataset, times, labels, fName, fType = 'png', xLabel = '', yLabel ='', pTitle ='',
                   legendPos = 'upper center', legendFrameOn = False, yearLabels = True, yscale = 'linear'):
    '''
    Purpose::
        Function to draw a time series plot

    Input::
        dataset - a list of arrays for each dataset as a time series
        times - a list of python datetime objects
        labels - a list of strings with the names of each dataset
        fName - a string specifying the filename of the plot
        fType - an optional string specifying the output filetype
        xLabel - a string specifying the x-axis title
        yLabel - a string specifying the y-axis title
        pTitle - a string specifying the plot title
        legendPos - an optional string or tuple of float for determining
                    the position of the legend
        legendFrameOn - optional bool to toggle drawing the frame around
                        the legend
        yearLabels - optional bool to toggle drawing year labels on the x-xaxis
        yscale - optional string for setting the y-axis scale, 'linear' for linear
                 and 'log' for log base 10.
    '''
    fig = plt.figure()
    ax = fig.add_subplot(111)

    if not yearLabels:
        xfmt = mpl.dates.DateFormatter('%b')
        ax.xaxis.set_major_formatter(xfmt)

    ax.set_xlabel(xLabel)
    ax.set_ylabel(yLabel)
    ax.set_title(pTitle)

    # Set up list of lines for legend
    lines = []
    ymin, ymax = 0, 0

    # Plot each dataset
    for data in dataset:
        line = ax.plot_date(times, data, '', linewidth = 2)
        lines.extend(line)
        cmin, cmax = data.min(), data.max()
        if ymin > cmin:
            ymin = cmin
        if ymax < cmax:
            ymax = cmax

    # Add a bit of padding so lines don't touch bottom and top of the plot
    ymin = ymin - ((ymax - ymin) * 0.1)
    ymax = ymax + ((ymax - ymin) * 0.1)
    ax.set_ylim((ymin, ymax))

    # Set the y-axis scale
    ax.set_yscale(yscale)

    # Create the legend
    ax.legend((lines), labels, loc = legendPos, ncol = 10, fontsize='x-small',
                       frameon=legendFrameOn)
    fig.savefig('%s.%s' %(fName, fType), bbox_inches = 'tight')
    fig.clf()


def pltXY(x, y, lineLabel, lineTyp, pltTit, xLabel, yLabel, pltName, xmin, xmax, deltaX, ymin, ymax, deltaY, legendPos, xScale, yScale):
    """
    The default drawing order for axes is patches, lines, text.This order is determined by the zorder attribute. The following defaults are set:
    Artist                      Z-order
    Patch / PatchCollection      1
    Line2D / LineCollection      2
    Text                         3
    You can change the order for individual artists by setting the zorder.  Any individual plot() call can set a value
      for the zorder of that particular item.
    In the fist subplot below, the lines are drawn above the patch collection from the scatter, which is the default.
    In the subplot below, the order is reversed.
    The second figure shows how to control the zorder of individual lines.
    Arguments
      x (nX)   : np array: the number of points in the x axis
      y (nX,nY): np array: the number of y values to be plotted
      lineLabel: list(nY): labels for individual y data
      pltTit   : Text    : plot title
      xLabel   : Text    : x-axis label
      yLabel   : Text    : y-axis label
      pltName  : Text    : name of the plot file
    3/28/2013 Jinwon Kim: Modification of a routine in the matplotlib gallery
    """
    #lineColors = ['k', 'b', 'r', 'g', 'c', 'm', 'y', '0.5', '0.55', '0.6', '0.65', '0.7', '0.75', '0.8', '0.85', '0.9', '0.95', '1.0']
    lineColors = ['k','r','y','g','b','c','m','k','r','y','g','b','c','m','k','r','y','g','b','c','m','0.35','0.5','0.65','0.8','.95']
    nX = x.size
    nY = len(lineLabel)
    lineColors[nY - 1] = 'b'
    fig = plt.figure()
    ax = fig.add_subplot(1,1,1)
    for n in np.arange(nY):
        if n <= 6:
            opacity=1.
        elif n <= 13:
            opacity = .75
        elif n <= 20:
            opacity = .40
        plot(x,y[n, :], linewidth=1, alpha=opacity, color=lineColors[n], linestyle=lineTyp[n], label=lineLabel[n], zorder = 10)
    xlabel(xLabel,fontsize=10); ylabel(yLabel,fontsize=10)
    if xmax > xmin:
        plt.xlim(xmin,xmax)
        ticks = frange(xmin,xmax,npts=(xmax-xmin)/deltaX+1)
        ax.xaxis.set_ticks(ticks,minor=False)
    if ymax > ymin:
        plt.ylim(ymin,ymax)
        ticks = frange(ymin,ymax,npts=(ymax-ymin)/deltaY+1)
        ax.yaxis.set_ticks(ticks,minor=False)
    ax.set_title(pltTit)
    ax.xaxis.tick_bottom(); ax.yaxis.tick_left()    # put tick marks only on the left (for y) and bottom (for x) axis
    if xScale == 'log':
        ax.set_xscale('log')
    else:
        ax.set_xscale('linear')
    if yScale == 'log':
        ax.set_yscale('log')
    else:
        ax.set_yscale('linear')
    if(nY>1):
        l = legend(prop={'size':10},loc='best')
        l.set_zorder(20) # put the legend on top
    plt.savefig(pltName)
    # release work arrays
    x=0.; y=0.


def pltSca1F(x, y, pltName, xLabel, yLabel, pmin, pmax, delP, pTit, pFname, xScale, yScale):
    #*************************************#
    # Plot a single-frame scatter diagram #
    #*************************************#
    fig = plt.figure(); ax = fig.add_subplot(1,1,1)
    lTyp='o'
    plot(x,y,lTyp,c='r')
    if pmax > pmin:
        ticks = frange(pmin,pmax,npts=(pmax-pmin)/delP+1)
        plt.xlim(pmin,pmax); ax.xaxis.set_ticks(ticks,minor=False)
        plt.ylim(pmin,pmax); ax.yaxis.set_ticks(ticks,minor=False)
    ax.set_title(pTit)
    if xScale == 'log':
        ax.set_xscale('log')
    else:
        ax.set_xscale('linear')
    if yScale == 'log':
        ax.set_yscale('log')
    else:
        ax.set_yscale('linear')
    xlabel(xLabel,fontsize=10); ylabel(yLabel,fontsize=10)
    l = legend(prop={'size':8},loc='best')
    l.set_zorder(20)
    plt.savefig(pFname)
    x=0.; y=0.


def pltSca6F(x, dName, pmin, pmax, delP, pTitle, pFname, xScale, yScale):
    #****************************************************#
    # Plot up to 6 frames (6 rows X 2 columns) on a page #
    #****************************************************#
    nPlt = x.shape[0]
    if pmax > pmin:
        ticks = frange(pmin,pmax,npts=(pmax-pmin)/delP+1)
    if nPlt > 6:
        print 'frames exceed 12: return'
        return
    nrows = 3; ncols = 2; npmax = nrows*ncols; lTyp='o'; xlabcol='black'; ylabcol='green'
    fig = plt.figure()
    plt.subplots_adjust(hspace=0.3, wspace=0.2)
    for n in range(1,nPlt):
        pid = n % npmax
        if pid == 0:
            pid = npmax
        ax = fig.add_subplot(nrows,ncols,pid)
        #ax.set_title(pTitle[n-1],fontsize=6)
        if xScale == 'log':
            ax.set_xscale('log')
        else:
            ax.set_xscale('linear')
        if yScale == 'log':
            ax.set_yscale('log')
        else:
            ax.set_yscale('linear')
        plot(x[0,:],x[n,:],lTyp,label=pTitle[n-1],c='r')
        plot(x[0,:],x[n,:],lTyp,c='r')
        plot(frange(pmin,pmax),c='b')
        l = legend(prop={'size':8},loc='best')
        l.set_zorder(20)
        xlabel(dName[0],fontsize=10); ylabel(dName[n],fontsize=10)
        if pmax > pmin:
            plt.xlim(pmin,pmax); ax.xaxis.set_ticks(ticks,minor=False)
            plt.ylim(pmin,pmax); ax.yaxis.set_ticks(ticks,minor=False)
        for label in ax.xaxis.get_ticklabels():
            label.set_color(xlabcol)
            label.set_rotation(0)
            label.set_fontsize(8)
        for label in ax.yaxis.get_ticklabels():
            label.set_color(ylabcol)
            label.set_rotation(0)
            label.set_fontsize(8)
    plt.savefig(pFname)
    x=0.

def drawContourMapSingle(data, lats, lons, cLevs, fName, fType = 'png',
                         cLabel = '', pTitle = '', cMap = None, nParallels = 5, nMeridians = 5):
    '''
    Purpose::
        Plots a filled contour map.
    Input::
        data - 2d array of the field to be plotted with shape (nLon, nLat)
        lats - array of latitudes 
        lons - array of longitudes
        cLevs - A list of ints or floats specifying contour levels
        fName  - a string specifying the filename of the plot
        fType  - an optional string specifying the filetype, default is .png
        cLabel - an optional string specifying the colorbar title
        pTitle - an optional string specifying plot title
        cMap - an optional matplotlib.LinearSegmentedColormap object denoting the colormap
        nParallels - an optional int for the number of parallels to draw
        nMeridians - an optional int for the number of meridians to draw        
    '''
    # Set up the colormap if not specified
    if cMap is None:
        cMap = plt.cm.RdBu_r

    # Set up the figure
    fig = plt.figure()
    ax = fig.add_subplot(111)

    # Determine the map boundaries and construct a Basemap object
    lonMin = lons.min()
    lonMax = lons.max()
    latMin = lats.min()
    latMax = lats.max()
    m = Basemap(projection = 'cyl', llcrnrlat = latMin, urcrnrlat = latMax,
                llcrnrlon = lonMin, urcrnrlon = lonMax, resolution = 'l', ax = ax)

    # Draw the borders for coastlines and countries
    m.drawcoastlines(linewidth = 1)
    m.drawcountries(linewidth = .75)

    # Draw parallels / meridians.
    m.drawmeridians(np.linspace(lonMin, lonMax, nMeridians), labels = [0, 0, 0, 1])
    m.drawparallels(np.linspace(latMin, latMax, nMeridians), labels = [1, 0, 0, 1])

    # Convert lats and lons to projection coordinates
    if lats.ndim == 1 and lons.ndim == 1:
        lons, lats = np.meshgrid(lons, lats)
    x, y = m(lons, lats)

    # Plot data with filled contours
    cs = m.contourf(x, y, data, cmap = cMap, levels = cLevs)

    # Add colorbar
    cbar = m.colorbar(cs, drawedges = True, pad = '2%', size = '3%')
    cbar.set_label(cLabel)
    cbar.set_ticks(cLevs)
    cbar.ax.xaxis.set_ticks_position("none")
    cbar.ax.yaxis.set_ticks_position("none")

    # Add title and save the figure
    ax.set_title(pTitle)
    fig.savefig('%s.%s' %(fName, fType))

def drawCntrMap(data,lon,lat,titles,ncols,pFname):
    '''
    This routine is based on PyNGL, i.e., NcarGraphics
    data - a masked numpy array of data to plot (nT,nY,nX)
    lon - longitude (nY,nX)
    lat - latitude  (nY,nX)
    titles - array of titles (nT)
    nrows - number of rows of the paneled plots
    ncols - number of columns of the paneled plots
    nT = nrows * ncols
    pFname - name of output postscript file
    '''
    wks_type = 'ps'
    if data.ndim == 2:
        nT = 1; nrows = 1; ncols = 1
    elif data.ndim == 3:
        nT=data.shape[0]
        if nT % ncols == 0:
            nrows = nT/ncols
        else:
            nrows = nT/ncols + 1
    # set workstation type (X11, ps, png)
    res = Ngl.Resources()
    wks = Ngl.open_wks(wks_type,pFname,res)
    # set plot resource paramters
    resources = Ngl.Resources()
    resources.mpLimitMode = "LatLon"    # Limit the map view.
    resources.mpMinLonF   = lon.min()
    resources.mpMaxLonF   = lon.max()
    resources.mpMinLatF   = lat.min()
    resources.mpMaxLatF   = lat.max()
    resources.cnFillOn      = True
    resources.cnLineLabelsOn        = False    # Turn off line labels.
    resources.cnInfoLabelOn         = False    # Turn off info label.
    resources.cnLinesOn             = False    # Turn off countour line (only filled colors)
    resources.sfXArray              = lon[:,:]
    resources.sfYArray              = lat[:,:]
    resources.pmTickMarkDisplayMode = "Never"  # Turn off map tickmarks.
    resources.mpOutlineBoundarySets = "GeophysicalAndUSStates"
    resources.mpGeophysicalLineColor = "red"
    resources.mpUSStateLineColor = "red"
    resources.mpGeophysicalLineThicknessF = 0.75
    resources.mpUSStateLineThicknessF = 0.75
    resources.mpPerimOn             = True     # Turn on/off map perimeter
    resources.mpGridAndLimbOn = True           # Turn off map grid.
    resources.nglFrame = False    # Don't advance the frame
    resources.nglDraw = False
    plot=[]
    for iT in np.arange(nT):
        resources.tiMainString = titles[iT]
        #resources.pmLabelBarDisplayMode = "Never" # Turn off individual label bars
        resources.pmLabelBarDisplayMode = "Always" # Turn on individual label bars
        if data.ndim == 3:
            plot.append(Ngl.contour_map(wks,data[iT,:,:],resources))
        elif data.ndim == 2:
            plot.append(Ngl.contour_map(wks,data[:,:],resources))
    panelres = Ngl.Resources()
    panelres.nglPanelTop=0.95
    panelres.nglPanelBottom=0.05
    panelres.nglPanelLabelBar                 = False   # Turn on panel labelbar
    panelres.nglPanelLabelBarLabelFontHeightF = 0.012  # Labelbar font height
    panelres.nglPanelLabelBarHeightF          = 0.03   # Height of labelbar
    panelres.nglPanelLabelBarWidthF           = 0.8    # Width of labelbar
    panelres.lbLabelFont                      = "helvetica-bold" # Labelbar font
    Ngl.panel(wks,plot[0:nT],[nrows,ncols],panelres)
    Ngl.destroy(wks)
    del plot
    del resources
    del wks
    return

def drawContourMap(dataset, lats, lons, fName, fType = 'png', gridShape = (1, 1),
                      cLabel = '', pTitle = '', subTitles = None, cMap = None,
                      cLevs = None, nLevs = 10, parallels = None, meridians = None,
                      extend = 'neither'):
    '''
    Purpose::
        Create a multiple panel contour map plot.
    Input::
        dataset -  3d array of the field to be plotted with shape (nT, nLon, nLat)
        lats - array of latitudes
        lons - array of longitudes
        fName  - a string specifying the filename of the plot
        fType  - an optional string specifying the filetype, default is .png
        gridShape - optional tuple denoting the desired grid shape (nRows, nCols) for arranging
                    the subplots.
        cLabel - an optional string specifying the colorbar title
        pTitle - an optional string specifying plot title
        subTitles - an optional list of strings specifying the title for each subplot
        cMap - an optional matplotlib.LinearSegmentedColormap object denoting the colormap
        cLevs - an optional list of ints or floats specifying contour levels
        nLevs - an optional integer specifying the target number of contour levels if
                cLevs is None
        parallels - an optional list of ints or floats for the parallels to be drawn
        meridians - an optional list of ints or floats for the meridians to be drawn
        extend - an optional string to toggle whether to place arrows at the colorbar
                 boundaries. Default is 'neither', but can also be 'min', 'max', or
                 'both'. Will be automatically set to 'both' if cLevs is None.
    '''
    # Handle the single plot case. Meridians and Parallels are not labeled for
    # multiple plots to save space.
    if dataset.ndim == 2 or (dataset.ndim == 3 and dataset.shape[0] == 1):
        if dataset.ndim == 2:
            dataset = dataset.reshape(1, *dataset.shape)
        nPlots = 1
        mLabels = [0, 0, 0, 1]
        pLabels = [1, 0, 0, 1]
    else:
        nPlots = dataset.shape[0]
        mLabels = [0, 0, 0, 0]
        pLabels = [0, 0, 0, 0]

    # Make sure gridShape is compatible with input data
    gridShape = calcBestGridShape(nPlots, gridShape)

    # Set up the colormap if not specified
    if cMap is None:
        cMap = plt.cm.coolwarm

    # Set up the figure
    fig = plt.figure()
    #fig.set_size_inches((8.5, 11.))
    #fig.dpi = 600

    # Make the subplot grid
    grid = ImageGrid(fig, 111,
                nrows_ncols = gridShape,
                axes_pad = 0.3,
                share_all = True,
                add_all = True,
                ngrids = nPlots,
                label_mode = "L",
                cbar_mode = 'single',
                cbar_location = 'bottom',
                cbar_pad = '0%'
                )

    # Determine the map boundaries and construct a Basemap object
    lonMin = lons.min()
    lonMax = lons.max()
    latMin = lats.min()
    latMax = lats.max()
    m = Basemap(projection = 'cyl', llcrnrlat = latMin, urcrnrlat = latMax,
                llcrnrlon = lonMin, urcrnrlon = lonMax, resolution = 'l')

    # Convert lats and lons to projection coordinates
    if lats.ndim == 1 and lons.ndim == 1:
        lons, lats = np.meshgrid(lons, lats)

    # Calculate contour levels if not given
    if cLevs is None:
        # Cut off the tails of the distribution
        # for more representative contour levels
        cLevs = calcNiceIntervals(dataset, nLevs)
    extend = 'both'

    # Create default meridians and parallels
    if meridians is None:
        meridians = np.arange(-180, 181, 15)
    if parallels is None:
        parallels = np.arange(-90, 91, 15)

    x, y = m(lons, lats)
    for i, ax in enumerate(grid):
        # Load the data to be plotted
        data = dataset[i]
        m.ax = ax

        # Draw the borders for coastlines and countries
        m.drawcoastlines(linewidth = 1)
        m.drawcountries(linewidth = .75)

        # Draw parallels / meridians
        m.drawmeridians(meridians, labels = mLabels, linewidth = .75)
        m.drawparallels(parallels, labels = pLabels, linewidth = .75)

        # Draw filled contours
        cs = m.contourf(x, y, data, cmap = cMap, levels = cLevs, extend = extend)

        # Add title
        if subTitles is not None:
            ax.set_title(subTitles[i], fontsize = 'small')


    # Add colorbar
    cbar = fig.colorbar(cs, cax = ax.cax, drawedges = True, orientation = 'horizontal',
                        extendfrac = 'auto')
    cbar.set_label(cLabel)
    cbar.set_ticks(cLevs)
    cbar.ax.xaxis.set_ticks_position("none")
    cbar.ax.yaxis.set_ticks_position("none")

    # This is an ugly hack to make the title show up at the correct height.
    # Basically save the figure once to achieve tight layout and calculate
    # the adjusted heights of the axes, then draw the title slightly above
    # that height and save the figure again
    fig.savefig('%s.%s' %(fName, fType), bbox_inches = 'tight', dpi = fig.dpi)
    ymax = 0
    for ax in grid:
        bbox = ax.get_position()
        ymax = max(ymax, bbox.ymax)

    # Add figure title
    fig.suptitle(pTitle, y = ymax + .04, fontsize = 16)
    fig.savefig('%s.%s' %(fName, fType), bbox_inches = 'tight', dpi = fig.dpi)
    fig.clf()

def drawSubRegions(subRegions, lats, lons, fName, fType = 'png', pTitle = '',
                    parallels = None, meridians = None, subRegionMasks = None):
    '''
    Purpose::
        Function to draw subregion domain(s) on a map
    
    Input::
            subRegions - a list of subRegion objects
        lats - array of latitudes
        lons - array of longitudes
        fName  - a string specifying the filename of the plot
        fType  - an optional string specifying the filetype, default is .png
        pTitle - an optional string specifying plot title
        parallels - an optional list of ints or floats for the parallels to be drawn
        meridians - an optional list of ints or floats for the meridians to be drawn
        subRegionMasks - optional dictionary of boolean arrays for each subRegion
                         for giving finer control of the domain to be drawn, by default
                         the entire domain is drawn.
    '''
    # Set up the figure
    fig = plt.figure()
    fig.set_size_inches((8.5, 11.))
    fig.dpi = 300
    ax = fig.add_subplot(111)
   
    # Determine the map boundaries and construct a Basemap object
    lonMin = lons.min()
    lonMax = lons.max()
    latMin = lats.min()
    latMax = lats.max()
    m = Basemap(projection = 'cyl', llcrnrlat = latMin, urcrnrlat = latMax,
                llcrnrlon = lonMin, urcrnrlon = lonMax, resolution = 'l', ax = ax)
   
    # Draw the borders for coastlines and countries
    m.drawcoastlines(linewidth = 1)
    m.drawcountries(linewidth = .75)
    m.drawstates()

    # Create default meridians and parallels
    if meridians is None:
        meridians = np.arange(-180, 181, 15)
    if parallels is None:
        parallels = np.arange(-90, 91, 15)

    # Draw parallels / meridians
    m.drawmeridians(meridians, labels = [0, 0, 0, 1], linewidth = .75)
    m.drawparallels(parallels, labels = [1, 0, 0, 1], linewidth = .75)

    # Set up the color scaling
    cMap = plt.cm.jet
    norm = mpl.colors.BoundaryNorm(np.arange(1, len(subRegions) + 3), cMap.N)

    # Process the subregions
    for i, reg in enumerate(subRegions):
        if subRegionMasks is not None and reg.name in subRegionMasks.keys():
            domain = (i + 1) * subRegionMasks[reg.name]
        else:
            domain = (i + 1) * np.ones((2, 2))

        nLats, nLons = domain.shape
        domain = ma.masked_equal(domain, 0)
        regLats = np.linspace(reg.latMin, reg.latMax, nLats)
        regLons = np.linspace(reg.lonMin, reg.lonMax, nLons)
        regLons, regLats = np.meshgrid(regLons, regLats)

        # Convert to to projection coordinates. Not really necessary
        # for cylindrical projections but keeping it here in case we need
        # support for other projections.
        x, y = m(regLons, regLats)

        # Draw the subregion domain
        m.pcolormesh(x, y, domain, cmap = cMap, norm = norm, alpha = .5)

        # Label the subregion
        xm, ym = x.mean(), y.mean()
        m.plot(xm, ym, marker = '$%s$' %(reg.name), markersize = 12, color = 'k')

    # Add the the title
    ax.set_title(pTitle)

    # Save the figure
    fig.savefig('%s.%s' %(fName, fType), bbox_inches = 'tight', dpi = fig.dpi)
    fig.clf()

def metrics_plots(varName, numOBS, numMDL, nT, ngrdY, ngrdX, Times, lons, lats, allData, dataList, workdir, subRegions, timeStep, fileOutputOption):
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
    #        allData          - the sum of the observed and model data (combines obsData & mdlData in the old code)
    #        dataList         - the list of data names (combines obsList and mdlList in the old code)
    #        workdir        - string describing the directory path for storing results and plots
    #        subRegions        - list of SubRegion Objects or False
    #        fileOutputOption - option to write regridded data in a netCDF file or not
    #    Output: image files of plots + possibly data
    #******************************************************
    # JK2.0: Only the data interpolated temporally and spatially onto the analysis grid 
    #        are transferred into this routine. The rest of processing (e.g., area-averaging, etc.) 
    #        are to be performed in this routine. Do not overwrite obsData[numOBs,nt,ngrdY,ngrdX] & 
    #        mdlData[numMDL,nt,ngrdY,ngrdX]. These are the raw, re-gridded data to be used repeatedly 
    #        for multiple evaluation steps as desired by an evaluator
    # JK2.1: The observed and model data are unified in a single variable for ease of processing
    ##################################################################################################################

    print ''
    print 'Start metrics.py'
    print ''
    # JK2.1: define the variable to represent the total number of combined (obs + model) datasets
    numDatasets = numOBS + numMDL

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
        ans = raw_input('Calculate area-mean timeseries for subregions? y/n: [n] \n')
        print ''
        if ans == 'y':
            ans = raw_input('Input subregion info interactively? y/n: \n> ')
            if ans == 'y':
                numSubRgn, subRgnName, subRgnLon0, subRgnLon1, subRgnLat0, subRgnLat1 = misc.assign_subRgns_interactively()
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
    dataRgn = np.zeros((numDatasets, numSubRgn, nT))
            
    if subRegions:        
        print 'Enter area-averaging: allData.shape ', allData.shape
        print 'Using Latitude/Longitude Mask for Area Averaging'  
        for n in np.arange(numSubRgn):
            # Define mask using regular lat/lon box specified by users ('mask=True' defines the area to be excluded)
            maskLonMin = subRegions[n].lonMin 
            if maskLonMin > 180.:
                maskLonMin = maskLonMin - 360.
            maskLonMax = subRegions[n].lonMax
            if maskLonMax > 180.:
                maskLonMax = maskLonMax - 360.
            maskLatMin = subRegions[n].latMin
            maskLatMax = subRegions[n].latMax
            mask = np.logical_or(np.logical_or(lats <= maskLatMin, lats >= maskLatMax), 
                                 np.logical_or(lons <= maskLonMin, lons >= maskLonMax))
            
            # Calculate area-weighted averages within this region and store in a new list
            for k in np.arange(numDatasets):           #JK2.1: area-average all data
                Store = []
                for t in np.arange(nT):
                    Store.append(process.calc_area_mean(allData[k, t, :, :], lats, lons, mymask = mask))
                dataRgn[k, n, :] = ma.array(Store[:])
            Store = []                               # release the memory allocated by temporary vars

    #-------------------------------------------------------------------------
    # (mp.002) fileOutputOption: The option to create a binary or netCDF file of processed 
    #                      (re-gridded and regionally-averaged) data for user-specific processing. 
    #                      This option is useful for advanced users who need more than
    #                      the metrics and vidualization provided in the basic package.
    #----------------------------------------------------------------------------------------------------
    print ''
    if not fileOutputOption:
        while fileOutputOption not in ['no', 'nc']:
            fileOutputOption = raw_input('Option for output files of obs/model data: Enter no/nc \
                                for no, netCDF file \n> ').lower()
    print ''

    # write a netCDF file for post-processing if desired. JK21: binary output option has been completely eliminated
    if fileOutputOption == 'nc':
        fileName = '%s/%s_Tseries.nc' % (workdir, varName)
        tempName = fileName 
        if(os.path.exists(tempName) == True):
            print "removing %s from the local filesystem, so it can be replaced..." % (tempName,)
            cmnd = 'rm -f ' + tempName
            subprocess.call(cmnd, shell=True)
        #files.writeNCfile1(fileName, numSubRgn, lons, lats, allData, dataRgn, dataList, subRegions)
        files.writeNCfile1(fileName, numDatasets, numOBS, numMDL, numSubRgn, lons, lats, allData, dataRgn, dataList, subRegions)
        print 'The regridded obs and model data are written in the netCDF file ', fileName

    #####################################################################################################
    ###################### Metrics calculation and plotting cycle starts from here ######################
    #####################################################################################################
    print ''
    print 'OBS and MDL data have been prepared for the evaluation step'
    print ''
    doMetricsOption = raw_input('Want to calculate metrics and plot them? [y/n]\n> ').lower()
    if doMetricsOption == 'y':
        # Assign the variable name and unit to be used in plots
        print 'The variable to be processed is ',timeStep,' ',varName
        pltVarName = raw_input('Enter the variable name to appear in the plot\n> ')
        pltVarUnit = raw_input('Enter the variable unit to appear in the plot\n> ')
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
        analSelect = int(raw_input('Eval over domain (Enter 0) or time series of selected Sub Regions (Enter 1) \n> '))
        print ' '
        if analSelect == 0:
            anlDomain = 'y'
        elif analSelect == 1:
            anlRgn = 'y'
        else:
            print 'analSelect= ', analSelect, ' is Not a valid option: CRASH'

        #--------------------------------------------------------------------------------------------------------------------
        # (mp.004) Select the model and data to be used in the evaluation step
        # 6/7/2013: JK4 - unified handling of the ref & mdl datasets allows several diff types of evaluation (RCMES v2.1)
        #                 such as ref vs. one model or ref; ref vs. all models; ref vs. all model + non-ref refs
        #          refID: the ID of the reference data against which all data are to be evaluated
        #          mdlID: the list of data ID's to be evaluated. if mdlSelect == -99, the list also includes non-ref obs data
        #--------------------------------------------------------------------------------------------------------------------
        refID = int(misc.select_data_combined(numDatasets, Times, dataList, 'ref'))
        mdlSelect = int(misc.select_data_combined(numDatasets, Times, dataList, 'mdl'))
        mdlID=[]
        # Assign the data id to be evaluated. Note that a non-reference obs dataset is treated like a model dataset (mdlSelect == -99)
        if mdlSelect >= 0:
            mdlID.append(mdlSelect)
        elif mdlSelect == -1:
            for n in np.arange(numMDL):
                mdlID.append(n+numOBS)
        elif mdlSelect == -2:
            for n in np.arange(refID):
                mdlID.append(n)
            for n in range(refID + 1, numDatasets):
                mdlID.append(n)
        elif mdlSelect == -3:
            if numOBS == 1:
                print 'There exist only one reference data: EXIT'
                sys.exit()
            for n in np.arange(refID):
                mdlID.append(n)
            for n in range(refID + 1, numOBS):
                mdlID.append(n)
        elif mdlSelect == -4:
            id4eval = 0         # any number != -9
            print 'Enter the data id to be evaluated: -9 to stop entering'
            while id4eval != -9:
                id4eval = int(raw_input('Enter the data id for evaluation. -9 to stop entry\n> '))
                if id4eval != -9:
                    mdlID.append(id4eval)
        refName = dataList[refID]
        mdlName = []
        numMdl = len(mdlID)
        for n in np.arange(numMdl):
            tname = dataList[mdlID[n]]
            m = min(len(tname), 8)
            for k in np.arange(m):
                if tname[k] == ' ':
                    break
                elif k == m-1:
                    k = m
            mdlName.append(tname[0:k])
        print 'selected reference and model data for evaluation= ', refName, mdlName

        #--------------------------------
        # (mp.005) Spatial distribution analysis/Evaluation (anlDomain='y')
        #          Obs/mdl climatology variables are 2-d/3d arrays (e.g., oClim = ma.zeros((ngrdY,ngrdX), mClim = ma.zeros((numMdl,ngrdY,ngrdX))
        #----------------------------------------------------------------------------------------------------
        if anlDomain == 'y':
            # first determine the temporal properties to be evaluated
            print ''
            timeOption = misc.select_timOpt()
            print ''
            if timeOption == 1:
                timeScale = 'annual'
                # compute the annual-mean time series and climatology. 
                oTser, oClim = calc_clim_year(nYR, nT, ngrdY, ngrdX, allData[refID, :, :, :], Times)
                mTser = ma.zeros((numMdl, nYR, ngrdY, ngrdX))
                mClim = ma.zeros((numMdl, ngrdY, ngrdX))
                for n in np.arange(numMdl):
                    id = mdlID[n]
                    mTser[n, :, :, :], mClim[n, :, :] = calc_clim_year(nYR, nT, ngrdY, ngrdX, allData[id, :, :, :], Times)
            elif timeOption == 2:
                timeScale = 'seasonal'
                # select the timeseries and climatology for a season specifiec by a user
                mTser = ma.zeros((numMdl, nYR, ngrdY, ngrdX))
                mClim = ma.zeros((numMdl, ngrdY, ngrdX))
                print ' '
                moBgn = int(raw_input('Enter the beginning month for your season. 1-12: \n> '))
                moEnd = int(raw_input('Enter the ending month for your season. 1-12: \n> '))
                print ' '
                if moEnd >= moBgn:
                    nMoPerSeason = moEnd - moBgn + 1
                    oTser, oClim = calc_clim_season(nYR, nT, moBgn, moEnd, ngrdY, ngrdX, allData[refID, :, :, :], Times)
                    for n in np.arange(numMdl):
                        id = mdlID[n]
                        mTser[n, :, :, :], mClim[n, :, :] = calc_clim_season(nYR, nT, moBgn, moEnd, ngrdY, ngrdX, allData[id, :, :, :], Times)
                elif moEnd == moBgn:
                    # Eval for a single month. mTser, oTser are the annual time series 
                    # for the specified month (moEnd), and  mClim, oClim are the corresponding climatology
                    oTser, oClim = calc_clim_One_month(moEnd, nYR, nT, allData[refID, :, :, :], Times)
                    for n in np.arange(numMdl):
                        id = mdlID[n]
                        mTser[n, :, :, :], mClim[n, :, :] = calc_clim_One_month(moEnd, nYR, nT, allData[id, :, :, :], Times)
                elif moEnd < moBgn:        # have to lose the ending year. redefine nYR=nYR-1, and drop the YR[nYR]
                    nMoS1 = 12 - moBgn + 1
                    nMoS2 = moEnd
                    nMoPerSeason = nMoS1 + nMoS2
                    mTser = ma.zeros((numMdl, nYR - 1, ngrdY, ngrdX))
                    # calculate the seasonal timeseries and climatology for the model data
                    for n in np.arange(numMdl):
                        id = mdlID[n]
                        mTser1, mClim1 = calc_clim_season(nYR, nT, moBgn, 12, ngrdY, ngrdX, allData[id, :, :, :], Times)
                        mTser2, mClim2 = calc_clim_season(nYR, nT, 1, moEnd, ngrdY, ngrdX, allData[id, :, :, :], Times)
                        for i in np.arange(nYR - 1):
                            mTser[n, i, :, :] = (real(nMoS1) * mTser1[i, :, :] + real(nMoS2) * mTser2[i + 1, :, :]) / nMoPerSeason
                    mClim = ma.average(mTser, axis=1)
                    # repeat for the obs data
                    mTser1, mClim1 = calc_clim_season(nYR, nT, moBgn, 12, ngrdY, ngrdX, allData[refID, :, :, :], Times)
                    mTser2, mClim2 = calc_clim_season(nYR, nT, 1, moEnd, ngrdY, ngrdX, allData[refID, :, :, :], Times)
                    oTser = ma.zeros((nYR - 1, ngrdY, ngrdX))
                    for i in np.arange(nYR - 1):
                        oTser[i, :, :] = (real(nMoS1) * mTser1[i, :, :] + real(nMoS2) * mTser2[i + 1, :, :]) / nMoPerSeason
                    oClim = ma.zeros((ngrdY, ngrdX))
                    oClim = ma.average(oTser, axis=0)
                    nYR = nYR - 1
                    yy = ma.empty(nYR)
                    for i in np.arange(nYR):
                        yy[i] = YR[i]
                    mTser1 = 0.
                    mTser2 = 0.
                    mClim1 = 0.
                    mClim2 = 0.
            elif timeOption == 3:
                timeScale = 'monthly'
                # compute the monthly-mean time series and climatology
                # Note that the shapes of the output vars are: 
                #   mTser = ma.zeros((nYR,12,ngrdY,ngrdX)) & mClim = ma.zeros((12,ngrdY,ngrdX))
                # Also same for oTser = ma.zeros((nYR,12,ngrdY,ngrdX)) &,oClim = ma.zeros((12,ngrdY,ngrdX))
                oTser, oClim = calc_clim_mo(nYR, nT, ngrdY, ngrdX, allData[refID, :, :, :], Times)
                mTser = ma.zeros((numMdl, nYR, 12, ngrdY, ngrdX))
                mClim = ma.zeros((numMdl, 12, ngrdY, ngrdX))
                for n in np.arange(numMdl):
                    id = mdlID[n]
                    mTser[n, :, :, :, :], mClim[n, :, :, :] = calc_clim_mo(nYR, nT, ngrdY, ngrdX, allData[id, :, :, :], Times)
            else:
                # undefined process options. exit
                print 'The desired temporal scale is not available this time. END the job'
                sys.exit()

            # compute the interannual variability
            if timeScale == 'monthly':
                oTsig = ma.zeros((12, ngrdY, ngrdX))
                mTsig = ma.zeros((numMdl, 12, ngrdY, ngrdX))
            else:
                oTsig = ma.zeros((ngrdY, ngrdX))
                mTsig = ma.zeros((numMdl, ngrdY, ngrdX))
            oTsig = oTser.std(axis = 0)
            mTsig = mTser.std(axis = 1)

            #--------------------------------
            # (mp.006) Select metric to be calculated
            # bias, mae, acct, accs, pcct, pccs, rmst, rmss, pdfSkillScore, taylor diagram
            #----------------------------------------------------------------------------------------------------
            print ' '
            metricOption = misc.select_metrics(mdlSelect)
            print ' '

            # metrics calculation: the shape of metricDat varies according to the metric type & timescale opetions

            if metricOption == 'BIAS':
                iselect = int (raw_input('Enter to evaluate: 0 for the mean climatology; 1 for the interannual variability. \n'))
            else:
                iselect = 0

            # metrics below yields a 2-d (annual or seasonal) or 3-d (monthly) array for each model
            if metricOption == 'BIAS':
                if timeScale == 'monthly':
                    oStdv = np.zeros(12)
                    metricDat = ma.zeros((numMdl, 12, ngrdY, ngrdX))
                    for n in np.arange(numMdl):
                        for m in np.arange(12):
                            if iselect == 0:
                                metricDat[n, m, :, :]  = calc_bias(mTser[n, :, m, :, :], oTser[m, :, :])
                            elif iselect == 1:
                                metricDat[n, m, :, :]  = mTsig[n, m, :, :] - oTsig[m, :, :]
                            if n == 0:
                                oStdv[m] = calc_temporal_stdv(oTser[m, :, :])
                else:
                    oStdv = calc_temporal_stdv(oTser)
                    metricDat = ma.zeros((numMdl, ngrdY, ngrdX))
                    for n in np.arange(numMdl):
                        if iselect == 0:
                            metricDat[n, :, :]  = calc_bias(mTser[n, :, :, :], oTser)
                        elif iselect == 1:
                            for n in np.arange(numMdl):
                                metricDat[n, :, :]  = mTsig[n, :, :] - oTsig[:, :]

            elif metricOption == 'MAE':
                if timeScale == 'monthly':
                    metricDat = ma.zeros((numMdl, 12, ngrdY, ngrdX))
                    for n in np.arange(numMdl):
                        for m in np.arange(12):
                            metricDat[n, m, :, :]  = calc_mae(mTser[n, :, m, :, :], oTser[m, :, :])
                else:
                    metricDat = ma.zeros((numMdl, ngrdY, ngrdX))
                    for n in np.arange(numMdl):
                        metricDat[n, :, :]  = calc_mae(mTser[n, :, :, :], oTser)

            elif metricOption == 'ACt':
                if timeScale == 'monthly':
                    metricDat = ma.zeros((numMdl, 12, ngrdY, ngrdX))
                    for n in np.arange(numMdl):
                        for m in np.arange(12):
                            metricDat[n, m, :, :]  = calc_temporal_anom_cor(mTser[n, :, m, :, :], oTser[m, :, :])
                else:
                    metricDat = ma.zeros((numMdl, ngrdY, ngrdX))
                    for n in np.arange(numMdl):
                        metricDat[n, :, :]  = calc_temporal_anom_cor(mTser[n, :, :, :], oTser)

            elif metricOption == 'PCt':
                if timeScale == 'monthly':
                    metricDat = ma.zeros((numMdl, 12, ngrdY, ngrdX))
                    for n in np.arange(numMdl):
                        for m in np.arange(12):
                            metricDat[n, m, :, :]  = calc_temporal_pat_cor(mTser[n, :, m, :, :], oTser[m, :, :])
                else:
                    metricDat = ma.zeros((numMdl, ngrdY, ngrdX))
                    for n in np.arange(numMdl):
                        metricDat[n, :, :]  = calc_temporal_pat_cor(mTser[n, :, :, :], oTser)

            elif metricOption == 'RMSt':
                if timeScale == 'monthly':
                    metricDat = ma.zeros((numMdl, 12, ngrdY, ngrdX))
                    for n in np.arange(numMdl):
                        for m in np.arange(12):
                            metricDat[n, m, :, :]  = calc_rms(mTser[n, :, m, :, :], oTser[m, :, :])
                else:
                    metricDat = ma.zeros((numMdl, ngrdY, ngrdX))
                    for n in np.arange(numMdl):
                        metricDat[n, :, :]  = calc_rms(mTser[n, :, :, :], oTser)

            # metrics below yields a scalar value for each model
            elif metricOption == 'ACs':
                if timeScale == 'monthly':
                    metricDat = ma.zeros((numMdl, 12))
                    for n in np.arange(numMdl):
                        for m in np.arange(12):
                            metricDat[n, m]  = calc_spatial_anom_cor(mClim[n, m, :, :], oClim[m, :, :])
                else:
                    metricDat = ma.zeros(numMdl)
                    for n in np.arange(numMdl):
                        metricDat[n]  = calc_spatial_anom_cor(mClim[n, :, :], oClim)
                    print 'spatial anomaly correlation vs the reference data:', refName
                    for n in np.arange(numMdl):
                        print dataList[n+1][0:8],metricDat[n]

            elif metricOption == 'PCs':
                if timeScale == 'monthly':
                    metricDat = ma.zeros((numMdl, 12))
                    for n in np.arange(numMdl):
                        for m in np.arange(12):
                            metricDat[n, m]  = calc_spatial_pat_cor(mClim[n, m, :, :], oClim[m, :, :])
                else:
                    metricDat = ma.zeros(numMdl)
                    for n in np.arange(numMdl):
                        metricDat[n]  = calc_spatial_pat_cor(mClim[n, :, :], oClim)
                    print 'spatial pattern correlation vs the reference data:', refName
                    for n in np.arange(numMdl):
                        print dataList[n+1][0:8],metricDat[n]

            elif metricOption == 'RMSs':
                if timeScale == 'monthly':
                    metricDat = ma.zeros((numMdl, 12))
                    for n in np.arange(numMdl):
                        for m in np.arange(12):
                            metricDat[n, m]  = calc_rms_dom(mClim[n, m, :, :], oClim[m, :, :])
                else:
                    metricDat = ma.zeros(numMdl)
                    for n in np.arange(numMdl):
                        metricDat[n]  = calc_rms_dom(mClim[n, :, :], oClim)
                    print 'RMSE over the entire domain'
                    for n in np.arange(numMdl):
                        print dataList[n+1][0:8],metricDat[n]

            # metrics to plot taylor diagram
            elif metricOption == 'Taylor_space':
                if timeScale == 'monthly':
                    oStdv = ma.zeros(12)
                    mStdv = ma.zeros((numMdl, 12))
                    mCorr = ma.zeros((numMdl, 12))
                    mTemp = ma.zeros((ngrdY, ngrdX))
                    for m in np.arange(12):
                        oStdv[m] = oClim[m, :, :].std() 
                    for n in np.arange(numMdl):
                        for m in np.arange(12):
                            mTemp = mClim[n, m, :, :]
                            mStdv[n, m] = mTemp.std()
                            mCorr[n, m] = calc_spatial_pat_cor(mTemp, oClim)
                else:
                    oStdv = oClim.std()
                    mStdv = ma.zeros(numMdl)
                    mCorr = ma.zeros(numMdl)
                    for n in np.arange(numMdl):
                        mStdv[n] = mClim[n, :, :].std()
                        mCorr[n] = calc_spatial_pat_cor(mClim[n, :, :], oClim)
                mStdv = mStdv / oStdv                          # standardized deviation

            #--------------------------------
            # (mp.008 & 009) Coeff of Variation or Signal-to-noise ratio: only application to the case of
            #                                     multiple datasets of the same kind (e.g., obs or model)
            #----------------------------------------------------------------------------------------------------
            elif metricOption == 'CV' or metricOption == 'S2N':
                if numMDL == 1:
                    print 'CV/S2N not available when only one dataset exists'
                    pass
                else:
                    if timeScale == 'monthly':
                        metricDat = ma.zeros((12, ngrdY, ngrdX))
                        Stdv = ma.zeros((12, ngrdY, ngrdX))
                        Stdv = mClim.std(axis = 0, ddof = 1); print Stdv.shape
                    else:
                        metricDat = ma.zeros((ngrdY, ngrdX))
                        Stdv = ma.zeros((ngrdY, ngrdX))
                        Stdv = mClim.std(axis = 0, ddof = 1); print Stdv.shape
                        metricDat = oClim / Stdv           # Signal-2-noise ratio
                    if metricOption == 'CV':
                        metricDat = Stdv / oClim

            #--------------------------------
            # (mp.007) Plot the metrics. First, enter plot info
            #----------------------------------------------------------------------------------------------------
            # Taylor diagram
            if metricOption == 'Taylor_space':
                taylorDat = []
                for n in np.arange(numMdl):
                    ttmp = []
                    ttmp.append(mStdv[n])
                    ttmp.append(mCorr[n])
                    entryLegend = mdlName[n]
                    ttmp.append(entryLegend)
                    taylorDat.append(ttmp)
                pltTit = 'Spatial variability evaluation'
                pltFileName = workdir + '/taylor_space_' + timeScale + '-' + varName
                legendPos = 'upper right'
                if max(mStdv) > 2.5:
                    radMax = 5.
                elif max(mStdv) > 2.:
                    radMax = 2.5
                else:
                    radMax = 2
                status = taylorDiagram(taylorDat, pltTit, pltFileName, refName, legendPos, radMax)

            # multiple 2-d contour plots
            elif metricDat.ndim == 3:
                print 'Plot',metricOption,'in',timeScale,varName
                # Plot metrics (2-d contour plots)
                if iselect == 0:
                    plotFileName = workdir + '/' + timeScale + '_' + varName + '_' + metricOption  + '_tAVG'
                elif iselect == 1:
                    plotFileName = workdir + '/' + timeScale + '_' + varName + '_' + metricOption  + '_INTRANN VAR'
                if(os.path.exists(plotFileName)==True):
                    cmnd='rm -f ' + plotFileName
                    subprocess.call(cmnd,shell=True)
                pltTit = []
                if metricDat.shape[0] > 1:
                    ncols = 3
                    for n in np.arange(numMdl):
                        pltTit.append(mdlName[n])
                elif metricDat.shape[0] == 1:
                    ncols = 1
                    pltTit.append(mdlName[0])
                if metricDat.shape[0] // ncols == 0:
                    nrows = max( int(metricDat.shape[0] / ncols), 1)
                else:
                    nrows = int(metricDat.shape[0]/ncols) + 1
                status = drawContourMap(metricDat, lats, lons, plotFileName, fType = 'png', gridShape = (nrows, ncols),
                                        cLabel = '', pTitle = '', subTitles = pltTit, cMap = None,
                                        cLevs = None, nLevs = 10, parallels = None, meridians = None, extend = 'neither')
                if metricOption == 'BIAS':
                    # obs climatology
                    plotDat = np.zeros((ngrdY, ngrdX))
                    print''
                    makePlot = raw_input('Plot observed climatology? [y/n]\n> ').lower()
                    if makePlot == 'y':
                        pltTit = []
                        if iselect == 0:
                            plotDat = oClim
                            plotFileName = workdir + '/' + timeScale + '_' + varName + '_OBS_tAVG'
                            pltTit.append('OBS (' + pltVarName + ': ' + pltVarUnit +'): MEAN CLIM')
                        elif iselect == 1:
                            plotDat = oTsig
                            plotFileName = workdir + '/' + timeScale + '_' + varName + '_OBS_tSIG'
                            pltTit.append('OBS (' + pltVarName + ': ' + pltVarUnit + '): INTRANN VAR')
                        if(os.path.exists(plotFileName)==True):
                            cmnd='rm -f ' + plotFileName
                            subprocess.call(cmnd,shell=True)
                        ncols = 1
                        nrows = 1
                        status = drawContourMap(plotDat, lats, lons, plotFileName, fType = 'png', gridShape = (ncols, nrows),
                                                cLabel = '', pTitle = '', subTitles = pltTit, cMap = None,
                                                cLevs = None, nLevs = 10, parallels = None, meridians = None, extend = 'neither')
                    # plot bias normalized by the mean climatology
                    if iselect == 0:
                        makePlot = raw_input('Plot bias in terms of % of OBS mean? [y/n]\n> ').lower()
                    else:
                        makePlot = 'n'
                    if makePlot != 'y':
                        pass
                    else:
                        plotDat = ma.empty((numMdl, ngrdY, ngrdX))
                        print plotDat.shape, metricDat.shape
                        for n in np.arange(numMdl):
                            plotDat[n,:,:] = 100.* metricDat[n,:,:] / oClim[:,:]
                        plotFileName = workdir + '/' + timeScale + '_' + varName + '_' + metricOption + '_MEAN'
                        if(os.path.exists(plotFileName)==True):
                            cmnd='rm -f ' + plotFileName
                            subprocess.call(cmnd,shell=True)
                        pltTit = []
                        if plotDat.shape[0] > 1:
                            ncols = 3
                            for n in np.arange(numMdl):
                                pltTit.append(mdlName[n])
                        elif plotDat.shape[0] == 1:
                            ncols = 1
                            pltTit.append(mdlName[0])
                        if plotDat.shape[0]/ncols == 0:
                            nrows = max(int(plotDat.shape[0] / ncols), 0)
                        else:
                            nrows = int(metricDat.shape[0]/ncols) + 1
                        status = drawContourMap(plotDat, lats, lons, plotFileName, fType = 'png', gridShape = (ncols, nrows),
                                                cLabel = '', pTitle = '', subTitles = pltTit, cMap = None,
                                                cLevs = None, nLevs = 10, parallels = None, meridians = None, extend = 'neither')
                        plotDat = 0.
                    # plot bias normalized by the interannual variability
                    if iselect == 0:
                        makePlot = raw_input('Plot bias in terms of % of interann sigma? [y/n]\n> ').lower()  # inactive for this version
                    else:
                        makePlot = 'n'
                    if makePlot == 'y':
                        print 'plot normalized by sigma'
                        plotDat = ma.empty((numMdl, ngrdY, ngrdX))
                        print plotDat.shape, metricDat.shape
                        for n in np.arange(numMdl):
                            plotDat[n,:,:] = 100.* metricDat[n,:,:] / oStdv[:,:]
                        plotFileName = workdir + '/' + timeScale + '_' + varName + '_' + metricOption + '_SIG'
                        if(os.path.exists(plotFileName)==True):
                            cmnd='rm -f ' + plotFileName
                            subprocess.call(cmnd,shell=True)
                        pltTit = []
                        if metricDat.shape[0] > 1:
                            ncols = 3
                            for n in np.arange(numMdl):
                                pltTit.append(mdlName[n])
                        elif metricDat.shape[0] == 1:
                            ncols = 1
                            pltTit.append(mdlName[0])
                        if metricDat.shape[0]/ncols == 0:
                            nrows = max(int(metricDat.shape[0] / ncols), 0)
                        else:
                            nrows = int(metricDat.shape[0]/ncols) + 1
                        status = drawContourMap(plotDat, lats, lons, plotFileName, fType = 'png', gridShape = (ncols, nrows),
                                                cLabel = '', pTitle = '', subTitles = pltTit, cMap = None,
                                                cLevs = None, nLevs = 10, parallels = None, meridians = None, extend = 'neither')
                        plotDat = 0.

            # a single 2-d array
            elif metricDat.ndim == 2:
                # obs climatology
                print''
                plotFileName = workdir + '/' + metricOption + '_' + varName + '_OBS'
                if(os.path.exists(plotFileName)==True):
                    cmnd='rm -f ' + plotFileName
                    subprocess.call(cmnd,shell=True)
                pltTit = []
                pltTit.append(metricOption)
                ncols = 1
                nrows = 1
                cLevs = [1., 5., 10., 25., 50.]
                status = drawContourMap(metricDat, lats, lons, plotFileName, fType = 'png', gridShape = (ncols, nrows),
                                        cLabel = '', pTitle = '', subTitles = pltTit, cMap = None,
                                        cLevs = cLevs, nLevs = 10, parallels = None, meridians = None, extend = 'neither')

            # Repeat for another metric. Also release memory used by temporary variables
            metricDat = 0.
            oTser = 0.
            oClim = 0.
            mTser = 0.
            mClim = 0.
            print ''
            print 'Evaluation completed'
            print ''
            doMetricsOption = raw_input('Do you want to perform another evaluation? [y/n]\n> ').lower()
            print ''

        # metrics and plots for regional time series
        elif anlRgn == 'y' and subRegions == False:
            print 'No SubRegions have been defined.  Regional Time Series Plots cannot be created'

        # metrics and plots for regional time series
        elif anlRgn == 'y':
            oData = ma.zeros((numSubRgn, nT))
            mData = ma.zeros((numMdl, numSubRgn, nT))
            oData[:, :] = dataRgn[refID, :, :]
            for n in np.arange(numMdl):
                mData[n, :, :] = dataRgn[mdlID[n], :, :]
            # select the region(s) for evaluation. model and obs have been selected before entering this if block
            print 'There are %s subregions. Select the subregion(s) for evaluation' % numSubRgn
            rgnSelect = misc.selectSubRegion(subRegions)
            print 'selected region for evaluation= ', rgnSelect

            # compute the annual cycle (in terms of monthly means) regardless of its use
            if rgnSelect >= 0:
                obsAnnCyc = calc_annual_cycle_means(oData[rgnSelect, :], Times)
                mdlAnnCyc = ma.empty((numMdl, 12))
                for n in np.arange(numMdl):
                    mdlAnnCyc[n, :] = calc_annual_cycle_means(mData[n, rgnSelect, :], Times)
                print 'Annual cycles for  a single subregion are calculated'
            elif rgnSelect == -9:
                obsAnnCyc = ma.empty((numSubRgn, 12))
                mdlAnnCyc = ma.empty((numMdl, numSubRgn, 12))
                for r in np.arange(numSubRgn):
                    obsAnnCyc[r, :] = calc_annual_cycle_means(oData[r, :], Times)
                    for n in np.arange(numMdl):
                        mdlAnnCyc[n, r, :] = calc_annual_cycle_means(mData[n, r, :], Times)
                print 'Annual cycles for all subregions are calculated'

            # (rgn01) evaluate the annual cycle
            ans = raw_input('Do you want evaluate the annual cycle? [y/n]\n> ').lower()
            if ans == 'y':                     # analysis for a single region
                if rgnSelect >= 0:
                    # plot obs and model within a single frame
                    pltYvar = ma.empty((numMdl+1, 12))
                    pltYvar[0, :] = obsAnnCyc[:]
                    for n in np.arange(numMdl):
                        pltYvar[n+1, :] = mdlAnnCyc[n, :]
                    # assign lineLabel: add data name, rmse and corr between the model and ref data for the model data
                    lineLabel = []
                    lineLabel.append(refName)
                    for n in np.arange(numMdl):
                        rms = calc_rms(obsAnnCyc, mdlAnnCyc[n, :])
                        cor = calc_pat_cor(obsAnnCyc, mdlAnnCyc[n, :])
                        lineLabel.append(mdlName[n])
                    lineTyp = []
                    for n in np.arange(numMdl + 1):
                        if (n == 0) or (n == numMdl):
                            lineTyp.append('-')
                        else:
                            lineTyp.append(':')
                    xLabel = 'Month'
                    yLabel = pltVarUnit
                    pltTit = 'Annual cycle of ' + pltVarName +' at Subregion ' + subRgnName[rgnSelect]
                    plotFileName = workdir + '/annCyc_' + varName + '_' + subRgnName[rgnSelect]
                    if(os.path.exists(plotFileName)==True):
                        cmnd='rm -f ' + plotFileName
                        subprocess.call(cmnd, shell=True)
                    pltXvar = frange(1, 12, npts=12)
                    xmin = 1
                    xmax = 12
                    deltaX = 1
                    mn1 = 1.e24
                    mx1 = -mn1
                    for n in np.arange(numMdl):
                        mn1 = min(min(mdlAnnCyc[n]), mn1)
                        mx1 = max(max(mdlAnnCyc[n]), mx1)
                    print 'Minimum y value= ', min(min(obsAnnCyc), mn1)
                    print 'Maximum y value= ', max(max(obsAnnCyc), mx1)
                    ymin = float(raw_input('Enter the minimum y to be plotted\n> '))
                    ymax = float(raw_input('Enter the maximum y to be plotted\n> '))
                    if(ymax>ymin):
                        deltaY = float(raw_input('Enter the delta_y (tick mark intervals)\n> '))
                    legendPos = 'best'
                    xScale = 'linear'
                    yScale = 'linear'
                    status = pltXY(pltXvar, pltYvar, lineLabel, lineTyp, pltTit, xLabel, yLabel, plotFileName, \
                                   xmin, xmax, deltaX, ymin, ymax, deltaY, legendPos, xScale, yScale)
                    pltXvar = 0
                    pltYvar = 0
                else:                           # analysis for all subregions - draw a multi-frame plot
                    # compute rmse and corr between the ref and model annual cycle
                    rms = np.zeros((numMdl, numSubRgn))
                    crr = np.zeros((numMdl, numSubRgn))
                    for n in np.arange(numMdl):
                        for r in np.arange(numSubRgn):
                            rms[n, r] = calc_rms(obsAnnCyc[r, :], mdlAnnCyc[n, r, :])
                            crr[n, r] = calc_pat_cor(obsAnnCyc[r, :], mdlAnnCyc[n, r, :])

                    # Make a portrait diagram here
                    rgnName = []
                    for i in np.arange(numSubRgn):
                        j = i+1
                        if j < 10:
                            rgnName.append('R0' + str(j))
                        else:
                            rgnName.append('R' + str(j))
                    # plot correlation coefficients
                    plotFileName = workdir + '/pd_annCyc_corr_' + varName + '.subRgns'
                    pTitle = 'Annual Cycle CORR COEF'
                    data = crr
                    cLevs = [0., .1, .2, .3, .4, .5, .6, .7, .8, .9, 1.]
                    status = drawPortraitDiagramSingle(data, rowLabels = rgnName, colLabels = mdlName, cLevs = cLevs,
                                                       fName = plotFileName, fType = 'png', xLabel = 'Region', yLabel = 'Model',
                                                       cLabel = '', pTitle = pTitle, cMap = None)
                    # plot correlation coefficients
                    plotFileName = workdir + '/pd_annCyc_rmse_' + varName + '.subRgns'
                    if varName == 'pr' or varName == 'prec':
                        pTitle = 'Ann Cyc RMSE: % Mean'
                        for n in np.arange(numMdl):
                            for r in np.arange(numSubRgn):
                                rgnSum = 0.
                                for i in np.arange(12):
                                    rgnSum = rgnSum + obsAnnCyc[r, i]
                                data[n, r] = rms[n, r] / (rgnSum / 12.)
                    cLevs = [0., 20., 50., 100., 150., 200., 250., 300., 400.]
                    data = data * 100.
                    status = drawPortraitDiagramSingle(data, rowLabels = rgnName, colLabels = mdlName, cLevs = cLevs,
                                                       fName = plotFileName, fType = 'png', xLabel = 'Region', yLabel = 'Model',
                                                       cLabel = '', pTitle = pTitle, cMap = None)
                    data = 0.
                    # Make x-y plots for all regions (replace with multi-plot page(s))
                    autoYscale = raw_input('Automatic scaling for the Y axis? y/n \n> ')
                    if autoYscale == 'y':
                        ymin = 0.
                        ymax = 0.
                        deltaY = 0.
                    pltXvar = frange(1,12,npts=12)
                    pltYvar = ma.empty((numMdl+1, 12))
                    xLabel = 'Month'
                    xmin = 1
                    xmax = 12
                    deltaX = 1
                    yLabel = pltVarUnit
                    xScale = 'linear'
                    yScale = 'linear'
                    legendPos = 'best'
                    lineLabel = []
                    lineLabel.append(refName)
                    for n in np.arange(numMdl):
                        lineLabel.append(mdlName[n])
                    lineTyp = []
                    for n in np.arange(numMdl + 1):
                        if (n==0) or (n==numMdl):
                            lineTyp.append('-')
                        else:
                            lineTyp.append(':')
                    for r in np.arange(numSubRgn):
                        plotFileName = workdir + '/annCyc_' + varName + '_' + subRgnName[r]
                        print 'Annual cycle plot for r= ', r, ' Rgn Name= ', subRgnName[r]
                        pltTit = ''
                        if autoYscale != 'y':
                            mn1 = mdlAnnCyc[:, r, :].min()
                            mx1 = mdlAnnCyc[:, r, :].max()
                            print 'Minimum y value= ', min(obsAnnCyc[r, :].min(), mn1)
                            print 'Maximum y value= ', max(obsAnnCyc[r, :].max(), mx1)
                            ymin = float(raw_input('Enter the minimum y to be plotted\n> '))
                            ymax = float(raw_input('Enter the maximum y to be plotted\n> '))
                            if(ymax>ymin):
                                deltaY = float(raw_input('Enter the delta_y (tick mark intervals)\n> '))
                            else:
                                deltaY = 0.
                        # assign plot values
                        pltYvar[0, :] = obsAnnCyc[r, :]
                        for n in np.arange(numMdl):
                            pltYvar[n+1, :] = mdlAnnCyc[n, r, :]
                        status = pltXY(pltXvar, pltYvar, lineLabel, lineTyp, pltTit, xLabel, yLabel, plotFileName, \
                                       xmin, xmax, deltaX, ymin, ymax, deltaY, legendPos, xScale, yScale)
                    pltXvar = 0
                    pltYvar = 0

            #--------------------------------
            # (mp.008) Other metrics options to be added here
            #----------------------------------------------------------------------------------------------------

            # Repeat for another metric
            doMetricsOption = raw_input('Do you want to perform another evaluation? [y/n]\n> ').lower()

    # Processing complete if a user enters 'n' for 'doMetricsOption'
    print 'RCMES processing completed.'


