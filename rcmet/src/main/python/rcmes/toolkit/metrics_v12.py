"""
 Module storing functions to calculate statistical metrics from numpy arrays
"""

import sys
import os
# Appending rcmes via relative path
sys.path.append(os.path.abspath('../.'))
import numpy as np
import numpy.ma as ma
import toolkit.process as process

def calc_clim_month(t2, time):
    """
    Calculate monthly means at every grid point including single point case where ndim=1
    """
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

def calc_annual_cycle_means(t2, time):
    """
    Calculate monthly means for every grid point
    """

    # Extract months from time variable
    months = np.empty(len(time))
    for timeStep in xrange(len(time)):
        months[timeStep] = time[timeStep].month

    if t2.ndim == 3:
        means = ma.empty((12, t2.shape[1], t2.shape[2])) # empty array to store means
        # Calculate means month by month
        for i in xrange(12):
            calendarMonth = i + 1
            means[i, :, :] = t2[months == calendarMonth, :, :].mean(0)
    elif t2.ndim == 1:
        means = np.empty((12)) # empty array to store means
        # Calculate means month by month
        for i in np.arange(12) + 1:
            means[i - 1] = t2[months == i].mean(0)
    else:
        print 'Only 1 or 3 dimensional data can be processed.  Your data shape is %s' % t2.shape
        sys.exit()

    return means

def calc_annual_cycle_std(t2, time):
    """
    Calculate monthly standard deviations for every grid point
    """
    # Extract months from time variable
    months = np.empty(len(time))
    
    for t in np.arange(len(time)):
        months[t] = time[t].month
    
    stds = np.empty((12, t2.shape[1], t2.shape[2])) # empty array to store means
    
    # Calculate means month by month
    for i in np.arange(12) + 1:
        stds[i - 1, :, :] = t2[months == i, :, :].std(0)
    return stds

def calc_annual_cycle_domain_means(t2, time):
    """Calculate domain means for each month of the year"""
    # Extract months from time variable
    months = np.empty(len(time))
    for t in np.arange(len(time)):
        months[t] = time[t].month
    means = np.empty(12) # empty array to store means
    # Calculate means month by month
    for i in np.arange(12) + 1:
        means[i - 1] = t2[months == i, :, :].mean()
    return means

def calc_annual_cycle_domain_std(t2, time):
    """Calculate domain standard deviations for each month of the year"""
    
    # Extract months from time variable
    months = np.empty(len(time))
    for t in np.arange(len(time)):
        months[t] = time[t].month
    stds = np.empty(12) # empty array to store means
    # Calculate means month by month
    for i in np.arange(12) + 1:
        stds[i - 1] = t2[months == i, :, :].std()
    return stds

def calc_bias_annual(t1, t2, optn):
    """
    Calculate mean difference between two fields over time for each grid point
    Precrocessing of both obs and model data ensures the absence of missing values
    
    TODO:  Previously this imported numpy and numpy.ma but they aren't used.
    I think open should be optn, and diff.mean(axis=0) seems like a numpy method.
    """
    diff = t1 - t2
    if open == 'abs': 
        diff = abs(diff)
    bias = diff.mean(axis=0)
    return bias

def calc_bias(t1, t2):
    """
    Bias / Mean Error:
    Calculate mean difference between two fields over time for each grid point
    
    Classify missing data resulting from multiple times (using threshold data requirement)
    * i.e. if the working time unit is monthly data, and we are dealing with multiple months of data
    then when we show mean of several months, we need to decide what threshold of missing data we tolerate
    before classifying a data point as missing data.
    """
    print 'Calculating bias'

    t1Mask = process.create_mask_using_threshold(t1, threshold=0.75)
    t2Mask = process.create_mask_using_threshold(t2, threshold=0.75)
    # TODO:  This pattern of diff and bias computation is repeated.  Could be refactored out into a function.
    diff = t1 - t2
    bias = diff.mean(axis=0)  # Again this seems like a numpy function
    # Set mask for bias metric using missing data in obs or model data series
    #   i.e. if obs contains more than threshold (e.g.50%) missing data 
    #        then classify time average bias as missing data for that location. 
    bias = ma.masked_array(bias.data, np.logical_or(t1Mask, t2Mask))
    return bias

def calc_bias_dom(t1, t2):
    """
    Calculate domain mean difference between two fields over time
    """
    diff = t1 - t2
    bias = diff.mean()
    return bias

def calc_difference(t1, t2):
    """
    Calculate mean difference between two fields over time for each grid point
    """
    print 'Calculating difference'
    diff = t1 - t2
    return diff

def calc_mae(t1, t2):
    """
    Calculate mean difference between two fields over time for each grid point
    
    Classify missing data resulting from multiple times (using threshold data requirement)
    
    * i.e. if the working time unit is monthly data, and we are dealing with multiple months of data
    then when we show mean of several months, we need to decide what threshold of missing data we tolerate
    before classifying a data point as missing data.
    """
    t1Mask = process.create_mask_using_threshold(t1, threshold=0.75)
    t2Mask = process.create_mask_using_threshold(t2, threshold=0.75)
    diff = t1 - t2
    adiff = abs(diff)
    mae = adiff.mean(axis=0)
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

def calc_rms_annual(t1, t2):
    """
    Root Mean Square Error (What makes this ANNUAL?)
    TODO: Annual Question
    """
    diff = t1 - t2
    sqdiff = diff ** 2
    msd = sqdiff.mean(axis=0)
    rms = np.sqrt(msd)
    return rms

def calc_rms(t1, t2):
    """
    Calculate mean difference between two fields over time for each grid point
    """
    # TODO:  How does this differ from the previous function 'calc_rms_annual'?
    diff = t1 - t2
    sqdiff = diff ** 2
    msd = sqdiff.mean(axis=0)
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

def calc_temporal_pat_cor(t1, t2):
    '''
    Calculate the Temporal Pattern Correlation
    
      Input:
        t1 - 3d array of model data
        t2 - 3d array of obs data
    
      Output:
        patcor - a 2d array of time series pattern correlation coefficients at each grid point.
    '''
    mt1 = t1[:, :, :].mean(axis=0)
    mt2 = t2[:, :, :].mean(axis=0)
    nt = t1.shape[0]
    sigma_t1 = t1.std(axis=0)
    sigma_t2 = t2.std(axis=0)
    patcor = ((((t1[:, :, :] - mt1) * (t2[:, :, :] - mt2)).sum(axis=0)) / (nt)) / (sigma_t1 * sigma_t2)
    
    return patcor

def calc_pat_cor2D(t1, t2, nT):
    """
    Calculate the Pattern Correlation
      Input:
        t1 - 3d array of model data
        t2 - 3d array of obs data
      Output:
        patcor - a 1d array (time series) of pattern correlation coefficients.
    """
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
        patcor.append((((((t1[t, :, :] - mt1) * (t2[t, :, :] - mt2)).sum()) / (t1.shape[1] * t1.shape[2])) / (sigma_t1 * sigma_t2)))
        print t, mt1.shape, mt2.shape, sigma_t1.shape, sigma_t2.shape, patcor[t]

    # TODO: deal with missing data appropriately, i.e. mask out grid points with missing data above tolerence level
    # convert from list into numpy array
    patcor = np.array(patcor)
    print patcor.shape
    return patcor

def calc_pat_cor(t1, t2, nT):
    """
    Calculate the Pattern Correlation
      Input:
        t1 - 3d array of model data
        t2 - 3d array of obs data
      Output:
        patcor - a 1d array (time series) of pattern correlation coefficients.
    """
    nt = t1.shape[0]
    if(nt != nT):
        print 'input time levels do not match: Exit'
        return -1
    
    # store results in list for convenience (then convert to numpy array at the end)
    patcor = []
    for t in xrange(nt):
        mt1 = t1[t, :, :].mean()
        mt2 = t2[t, :, :].mean()
        sigma_t1 = t1[t, :, :].std()
        sigma_t2 = t2[t, :, :].std()
        # TODO: make means and standard deviations weighted by grid box area.
        patcor.append((((((t1[t, :, :] - mt1) * (t2[t, :, :] - mt2)).sum()) / (t1.shape[1] * t1.shape[2])) / (sigma_t1 * sigma_t2)))
        print t, mt1.shape, mt2.shape, sigma_t1.shape, sigma_t2.shape, patcor[t]
        # TODO: deal with missing data appropriately, i.e. mask out grid points with missing data above tolerence level
        
    # convert from list into numpy array
    patcor = np.array(patcor)
    print patcor.shape
    return patcor


def calc_anom_cor(t1, t2):
    '''
    Calculate the Anomaly Correlation
    '''
    nt = t1.shape[0]
    # store results in list for convenience (then convert to numpy array at the end)
    anomcor = []
    for t in xrange(nt):
        mt2 = t2[t, :, :].mean()
        sigma_t1 = t1[t, :, :].std()
        sigma_t2 = t2[t, :, :].std()
        # TODO: make means and standard deviations weighted by grid box area.
        anomcor.append(((((t1[t, :, :] - mt2) * (t2[t, :, :] - mt2)).sum()) / (t1.shape[1] * t1.shape[2])) / (sigma_t1 * sigma_t2))
        print t, mt2.shape, sigma_t1.shape, sigma_t2.shape, anomcor[t]
        # TODO: deal with missing data appropriately, i.e. mask out grid points with missing data above tolerence level
    
    # convert from list into numpy array
    anomcor = np.array(anomcor)
    return anomcor


# TODO: Coefficient of Efficiency


# Probability Distribution Function
def calc_pdf(data):
    '''
    Routine to calculate a normalised PDF with bins set according to data range.
     Input:
         data  - numpy data array
     Output:
         edges        - numpy array describing the edges of the bins
         distribution - numpy array of values for each bin
    '''
    # Define bin ranges
    nbins = 10
    #TODO:  in this function t2 is not defined.  Should it have been passed in?
    mybins = np.linspace(t2.min(), t2.max(), nbins)    
    # Calculate the number of occurrences in each bin
    distribution, edges = np.histogram(t2, bins=mybins, normed=True, new=True)
    return edges, distribution


