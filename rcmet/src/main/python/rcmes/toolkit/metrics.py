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
from toolkit import plots, process
from utils import misc
from storage import files 

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
    Calculate monthly means at every grid points and the annual time series of single model.
    '''
    #-------------------------------------------------------------------------------------
    # JK20: This routine is modified from 'calc_clim_month'  with additional arguments and
    #       output, the annual time series of single model output (mData)
    # Calculate monthly means at every grid point including single point case (ndim=1)
    #-------------------------------------------------------------------------------------
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
            mm = months[t]
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
     Calculate domain mean difference between two fields over time
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
    d1 = ((oD - mo)*(oD - mo)).sum()
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
    mt1 = t1[:, :, :].mean(axis = 0)
    mt2 = t2[:, :, :].mean(axis = 0)
    nt = t1.shape[0]
    sigma_t1 = t1.std(axis = 0, ddof = 1)
    sigma_t2 = t2.std(axis = 0, ddof = 1)
    # TODO - What is ddof=1?  Will a user want to change this value?
    patcor = ((((t1[:, :, :] - mt1) * 
                (t2[:, :, :] - mt2)).sum(axis = 0)) / 
              (nt)) / (sigma_t1 * sigma_t2)
    
    return patcor


def calc_spatial_pat_cor(t1, t2, nY, nX):
    '''
    Calcualte pattern correlation between 2-D arrays.

    Input:
        t1 - 2-D array of model data
        t2 - 2-D array of observation data
        nY
        nX

    Output:
        Pattern correlation between two input arrays.
    '''
    # TODO - Update docstring. What are nY and nX?
    mt1 = t1.mean()
    mt2 = t2.mean()
    st1 = t1.std()
    st2 = t2.std()
    patcor = ((t1 - mt1) * (t2 - mt2)).sum() / (float(nX * nY) * st1 * st2)
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
    print patcor.shape
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
    '''

    # TODO:  Add in try block to ensure the shapes match
    nt = dataset_1.shape[0]
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
        patcor.append((((((dataset_1[t, :, :] - mt1) * 
                          (dataset_2[t, :, :] - mt2)).sum()) / 
                        (dataset_1.shape[1] * dataset_1.shape[2])) / (sigma_t1 * sigma_t2)))
        print t, mt1.shape, mt2.shape, sigma_t1.shape, sigma_t2.shape, patcor[t]
        
        # TODO: deal with missing data appropriately, i.e. mask out grid points
        # with missing data above tolerance level

    # convert from list into numpy array
    patcor = np.array(patcor)
    
    print patcor.shape
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


def metrics_plots(varName, numOBS, numMDL, nT, ngrdY, ngrdX, Times, lons, 
                  lats, obsData, mdlData, obsList, mdlList, workdir, subRegions):
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
    #        subRegions        - list of SubRegion Objects or False
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
    """
    If subRegions is true then process them
    """
#    
#    
#    print ''
#    ans = raw_input('Calculate area-mean timeseries for subregions? y/n: \n> ')
#    print ''
#    if ans == 'y':
#        ans = raw_input('Input subregion info interactively? y/n: \n> ')
#        if ans == 'y':
#            numSubRgn, subRgnName, subRgnLon0, subRgnLon1, subRgnLat0, subRgnLat1 = misc.assign_subRgns_interactively()
#        else:
#            print 'Read subregion info from a pre-fabricated text file'
#            ans = raw_input('Read from a defaule file (workdir + "/sub_regions.txt")? y/n: \n> ')
#            if ans == 'y':
#                subRgnFileName = workdir + "/sub_regions.txt"
#            else:
#                subRgnFileName = raw_input('Enter the subRgnFileName to read from \n')
#            print 'subRgnFileName ', subRgnFileName
#            numSubRgn, subRgnName, subRgnLon0, subRgnLon1, subRgnLat0, subRgnLat1 = misc.assign_subRgns_from_a_text_file(subRgnFileName)
#        print subRgnName, subRgnLon0, subRgnLon1, subRgnLat0, subRgnLat1
#    else:
#        numSubRgn = 0
    # compute the area-mean timeseries for all subregions if subregion(s) are defined.
    #   the number of subregions is usually small and memory usage is usually not a concern
    
    obsRgn = ma.zeros((numOBS, len(subRegions), nT))
    mdlRgn = ma.zeros((numMDL, len(subRegions), nT))
            
    if subRegions:        
    #if numSubRgn > 0:
        print 'Enter area-averaging: mdlData.shape, obsData.shape ', mdlData.shape, obsData.shape
        print 'Using Latitude/Longitude Mask for Area Averaging'  
        for n in np.arange(len(subRegions)):
            # Define mask using regular lat/lon box specified by users ('mask=True' defines the area to be excluded)
            maskLonMin = subRegions[n].lonMin 
            maskLonMax = subRegions[n].lonMax
            maskLatMin = subRegions[n].latMin
            maskLatMax = subRegions[n].latMax
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
        files.writeBNdata(fileName, numOBS, numMDL, nT, ngrdX, ngrdY, len(subRegions), obsData, mdlData, obsRgn, mdlRgn)
    # write a netCDF file for post-processing if desired
    if FoutOption == 'nc':
        fileName = workdir + '/Tseries' 
        tempName = fileName + '.' + 'nc'
        if(os.path.exists(tempName) == True):
            print "removing %s from the local filesystem, so it can be replaced..." % (tempName,)
            cmnd = 'rm -f ' + tempName
            subprocess.call(cmnd, shell=True)
        files.writeNCfile(fileName, len(subRegions), lons, lats, obsData, mdlData, obsRgn, mdlRgn)
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
        analSelect = int(raw_input('Eval over domain (Enter 0) or time series of selected Sub Regions (Enter 1) \n> '))
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
            print ''
            if timeOption == 1:
                timeScale = 'Annual'
                # compute the annual-mean time series and climatology. 
                # mTser=ma.zeros((nYR,ngrdY,ngrdX)), mClim = ma.zeros((ngrdY,ngrdX))
                mTser, mClim = calc_clim_year(nYR, nT, ngrdY, ngrdX, mdlData[mdlSelect, :, :, :], Times)
                oTser, oClim = calc_clim_year(nYR, nT, ngrdY, ngrdX, obsData[obsSelect, :, :, :], Times)
            elif timeOption == 2:
                timeScale = 'Seasonal'
                # select the timeseries and climatology for a season specifiec by a user
                print ' '
                moBgn = int(raw_input('Enter the beginning month for your season. 1-12: \n> '))
                moEnd = int(raw_input('Enter the ending month for your season. 1-12: \n> '))
                print ' '
                if moEnd >= moBgn:
                    nMoPerSeason = moEnd - moBgn + 1
                    mTser, mClim = calc_clim_season(nYR, nT, moBgn, moEnd, ngrdY, ngrdX, 
                                                                mdlData[mdlSelect, :, :, :], Times)
                    oTser, oClim = calc_clim_season(nYR, nT, moBgn, moEnd, ngrdY, ngrdX, 
                                                                obsData[obsSelect, :, :, :], Times)
                elif moEnd == moBgn:
                    # Eval for a single month. mTser, oTser are the annual time series 
                    # for the specified month (moEnd), and  mClim, oClim are the corresponding climatology
                    mTser, mClim = calc_clim_One_month(moEnd, nYR, nT, mdlData[mdlSelect, :, :, :], Times)
                    oTser, oClim = calc_clim_One_month(moEnd, nYR, nT, obsData[obsSelect, :, :, :], Times)
                elif moEnd < moBgn:        # have to lose the ending year. redefine nYR=nYR-1, and drop the YR[nYR]
                    nMoS1 = 12 - moBgn + 1
                    nMoS2 = moEnd
                    nMoPerSeason = nMoS1 + nMoS2
                    # calculate the seasonal timeseries and climatology for the model data
                    mTser1, mClim1 = calc_clim_season(nYR, nT, moBgn, 12, ngrdY, ngrdX, 
                                                                mdlData[mdlSelect, :, :, :], Times)
                    mTser2, mClim2 = calc_clim_season(nYR, nT, 1, moEnd, ngrdY, ngrdX, 
                                                                mdlData[mdlSelect, :, :, :], Times)
                    mTser = ma.zeros((nYR - 1, ngrdY, ngrdX))
                    for i in np.arange(nYR - 1):
                        mTser[i, :, :] = (real(nMoS1) * mTser1[i, :, :] + 
                            real(nMoS2) * mTser2[i + 1, :, :]) / nMoPerSeason
                    mClim = ma.zeros((ngrdY, ngrdX))
                    mClim = ma.average(mTser, axis=0)
                    # repeat for the obs data
                    mTser1, mClim1 = calc_clim_season(nYR, nT, moBgn, 12, ngrdY, ngrdX, 
                                                                obsData[obsSelect, :, :, :], Times)
                    mTser2, mClim2 = calc_clim_season(nYR, nT, 1, moEnd, ngrdY, ngrdX, 
                                                                obsData[obsSelect, :, :, :], Times)
                    oTser = ma.zeros((nYR - 1, ngrdY, ngrdX))
                    for i in np.arange(nYR - 1):
                        oTser[i, :, :] = (real(nMoS1) * mTser1[i, :, :] + 
                            real(nMoS2) * mTser2[i + 1, :, :]) / nMoPerSeason
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
                timeScale = 'Monthly'
                # compute the monthly-mean time series and climatology
                # Note that the shapes of the output vars are: 
                #   mTser = ma.zeros((nYR,12,ngrdY,ngrdX)) & mClim = ma.zeros((12,ngrdY,ngrdX))
                # Also same for oTser = ma.zeros((nYR,12,ngrdY,ngrdX)) &,oClim = ma.zeros((12,ngrdY,ngrdX))
                mTser, mClim = calc_clim_mo(mdlData[mdlSelect, :, :, :], Times)
                oTser, oClim = calc_clim_mo(obsData[mdlSelect, :, :, :], Times)
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

            # metrics below yields 2-d array, i.e., metricDat = ma.zeros((ngrdY,ngrdX))
            if metricOption == 'BIAS':
                metricDat = calc_bias(mTser, oTser)
                oStdv = calc_temporal_stdv(oTser)
            elif metricOption == 'MAE':
                metricDat = calc_mae(mTser, oTser)
            elif metricOption == 'ACCt':
                metricDat = calc_temporal_anom_cor(mTser, oTser)
            elif metricOption == 'PCCt':
                metricDat = calc_temporal_pat_cor(mTser, oTser)
            elif metricOption == 'RMSt':
                metricDat = calc_rms(mTser, oTser)

            # metrics below yields a scalar values
            elif metricOption == 'ACCs':
                metricDat = spatial_anom_cor(mClim, oClim)
            elif metricOption == 'PCCs':
                metricDat = spatial_pat_cor(mClim, oClim, ngrdY, ngrdX)
            elif metricOption == 'RMSs':
                metricDat = rms_dom(mClim, oClim)

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
                cMap = 'BlRe'
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
                wksType = 'ps'
                # TODO This shouldn't return anything. Handle a "status" the proper way
                _ = plots.draw_cntr_map_single(plotDat, lons, lats, mymin, mymax, 
                                                      plotTitle, plotFileName, cMap, wksType)
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
                        _ = plots.draw_cntr_map_single(plotDat, lons, lats, mymin, mymax, 
                                                              plotTitle, plotFileName, cMap, wksType)
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
                    _ = plots.draw_cntr_map_single(plotDat, lons, lats, mymin, mymax, 
                                                          plotTitle, plotFileName, cMap, wksType)
                # obs climatology
                makePlot = raw_input('Plot observation? [y/n]\n> ').lower()
                if makePlot == 'y':
                    if varName == 'pr':
                        cMap = 'precip2_17lev'
                    else:
                        cMap = 'BlRe'
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
                    _ = plots.draw_cntr_map_single(plotDat, lons, lats, mymin, mymax, 
                                                          plotTitle, plotFileName, cMap, wksType)

                # Repeat for another metric
                print ''
                print 'Evaluation completed'
                print ''
                doMetricsOption = raw_input('Do you want to perform another evaluation? [y/n]\n> ').lower()
                print ''

        # metrics and plots for regional time series
        elif anlRgn == 'y' and subRegions == False:
            print 'No SubRegions have been defined.  Regional Time Series Plots cannot be created'

        elif anlRgn == 'y':
            # select the region(s) for evaluation. model and obs have been selected before entering this if block
            print 'There are %s subregions. Select the subregion(s) for evaluation' % len(subRegions)
            rgnSelect = misc.selectSubRegion(subRegions)
            print 'selected region for evaluation= ', rgnSelect
            # Select the model & obs data to be evaluated
            oData = ma.zeros(nT)
            mData = ma.zeros(nT)
            oData = obsRgn[obsSelect, rgnSelect, :]
            mData = mdlRgn[mdlSelect, rgnSelect, :]

            # compute the monthly-mean climatology to construct the annual cycle
            obsAnnCyc = calc_annual_cycle_means(oData, Times)
            mdlAnnCyc = calc_annual_cycle_means(mData, Times)
            print 'obsAnnCyc= ', obsAnnCyc
            print 'mdlAnnCyc= ', mdlAnnCyc

            #--------------------------------
            # (mp.008) Select performance metric
            #----------------------------------------------------------------------------------------------------
            #metricOption = misc.select_metrics()
            # Temporarily, compute the RMSE and pattern correlation for the simulated 
            # and observed annual cycle based on monthly means
            # TODO tempRMS and tempCOR are not used in the code and throwing errors.
#            tempRMS = calc_rms(mdlAnnCyc, obsAnnCyc)
#            tempCOR = calc_temporal_pat_cor(mdlAnnCyc, obsAnnCyc)

            #--------------------------------
            # (mp.009) Plot results
            #----------------------------------------------------------------------------------------------------
            # Data-specific plot options: i.e. adjust model data units & set plot color bars
            colorbar = 'rainbow'
            if varName == 'pr':                      # set color bar for prcp
                colorbar = 'precip2_17lev'

            # 1-d data, e.g. Time series plots
            plotFileName = 'anncyc_' + varName + '_' + subRegions[rgnSelect].name
            if(os.path.exists(plotFileName) == True):
                cmnd = 'rm -f ' + plotFileName
                subprocess.call(cmnd, shell = True)
            year_labels = False         # for annual cycle plots
            mytitle = 'Annual Cycle of ' + varName + ' at Sub-Region ' + subRegions[rgnSelect].name
            # Create a list of datetimes to represent the annual cycle, one per month.
            times = []
            for m in xrange(12):
                times.append(datetime.datetime(2000, m + 1, 1, 0, 0, 0, 0))
            #for i in np.arange(12):
            #  times.append(i+1)
            _ = plots.draw_time_series_plot(mdlAnnCyc, times, plotFileName, workdir, 
                                                   data2 = obsAnnCyc, mytitle = mytitle, ytitle = 'Y', 
                                                   xtitle = 'MONTH', year_labels = year_labels)

            # Repeat for another metric
            doMetricsOption = raw_input('Do you want to perform another evaluation? [y/n]\n> ').lower()

    # Processing complete if a user enters 'n' for 'doMetricsOption'
    print 'RCMES processing completed.'


