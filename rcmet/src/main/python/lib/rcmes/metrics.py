'''
##########################################################################
#
# Module storing functions to calculate statistical metrics from numpy arrays
#
#	Peter Lean 	March 2010
#   Kim Whitehall June 2012
#    
###########################################################################
'''

import numpy as np
import numpy.ma as ma
import rcmes.process

def calc_annual_cycle_means(data, time):
    '''
    # Calculate monthly means for every grid point
    #inputs: 2 arrays modelData and modelTimes
    #         modelData is masked array of the model data list
    #         modelData is 3D - time,lon,lat
    #         modelTimes is an array of python datetime objects
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


###########################################################################
def calc_annual_cycle_std(data, time):
    '''
    # Calculate monthly standard deviations for every grid point
    '''
    
    # Extract months from time variable
    months = np.empty(len(time))
    
    for t in np.arange(len(time)):
        months[t] = time[t].month
    
    # empty array to store means
    stds = np.empty((12, data.shape[1], data.shape[2]))
    
    # Calculate means month by month
    for i in np.arange(12) + 1:
        stds[i - 1, :, :] = data[months == i, :, :].std(axis=0, ddof=1)
    
    return stds



###########################################################################
def calc_annual_cycle_domain_means(data, time):
    '''
    # Calculate domain means for each month of the year
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

###########################################################################
def calc_annual_cycle_domain_std(data, time):
    '''
    # Calculate domain standard deviations for each month of the year
    '''
    
    # Extract months from time variable
    months = np.empty(len(time))
    
    for t in np.arange(len(time)):
        months[t] = time[t].month
    
    stds = np.empty(12) # empty array to store means
    
    # Calculate means month by month
    for i in np.arange(12) + 1:
        stds[i - 1] = data[months == i, :, :].std(ddof=1)
    
    return stds

###########################################################################
# Bias / Mean Error

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
    
    print 'Calculating bias'
    
    # 
    
    t1Mask = rcmes.process.create_mask_using_threshold(t1, threshold=0.75)
    t2Mask = rcmes.process.create_mask_using_threshold(t2, threshold=0.75)
    
    diff = t1 - t2
    
    bias = diff.mean(axis=0)
    
    # Set mask for bias metric using missing data in obs or model data series
    #   i.e. if obs contains more than threshold (e.g.50%) missing data 
    #        then classify time average bias as missing data for that location. 
    bias = ma.masked_array(bias.data, np.logical_or(t1Mask, t2Mask))
    
    return bias


def calc_bias_dom(t1, t2):
    '''
    # Calculate domain mean difference between two fields over time
    '''
    diff = t1 - t2
    bias = diff.mean()
    return bias

###########################################################################
# Difference

def calc_difference(t1, t2):
    '''
    # Calculate mean difference between two fields over time for each grid point
    '''
    print 'Calculating difference'
    diff = t1 - t2
    return diff

###########################################################################
# Mean Absolute Error

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
    
    print 'Calculating mean absolute error'

    
    t1Mask = rcmes.process.create_mask_using_threshold(t1, threshold=0.75)
    t2Mask = rcmes.process.create_mask_using_threshold(t2, threshold=0.75)
    
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
    # Calculate domain mean difference between two fields over time
    '''
    diff = t1 - t2
    adiff = abs(diff)
    mae = adiff.mean()
    return mae


###########################################################################
# RMS Error

def calc_rms(t1, t2):
    '''
    # Calculate mean difference between two fields over time for each grid point
    '''
    
    diff = t1 - t2
    sqdiff = diff ** 2
    msd = sqdiff.mean(axis=0)
    rms = np.sqrt(msd)
    return rms

def calc_rms_dom(t1, t2):
    '''
    # Calculate domain mean difference between two fields over time
    '''
    diff = t1 - t2
    sqdiff = diff ** 2
    msd = sqdiff.mean()
    rms = np.sqrt(msd)
    return rms

###########################################################################
def calc_temporal_pat_cor(t1, t2):
    '''
    # Calculate the Temporal Pattern Correlation
    #
    #  Input:
    #    t1 - 3d array of model data
    #    t2 - 3d array of obs data
    #     
    #  Output:
    #    patcor - a 2d array of time series pattern correlation coefficients at each grid point.
    #
    #    Peter Lean  March 2011
    # Editing: Kim Whitehall June 2012
    #         reason: std_dev to be standarized on (n-1) not n
    '''
    
    mt1 = t1[:, :, :].mean(axis=0)
    mt2 = t2[:, :, :].mean(axis=0)
    
    nt = t1.shape[0]
    
    sigma_t1 = t1.std(axis=0, ddof=1)
    sigma_t2 = t2.std(axis=0, ddof=1)
    # TODO - What is ddof=1?  Will a user want to change this value?
    
    patcor = ((((t1[:, :, :] - mt1) * 
                (t2[:, :, :] - mt2)).sum(axis=0)) / 
              (nt)) / (sigma_t1 * sigma_t2)
    
    return patcor

###########################################################################
def calc_pat_cor(dataset_1, dataset_2):
    '''
    # Purpose: Calculate the Pattern Correlation
    #
    #  Assumption(s):  Both dataset_1 and dataset_2 are the same shape.
                       lat, lon must match up
                       time steps must align (i.e. months vs. months)
    #
    #  Input:
    #    dataset_1 - 3d (time, lat, lon) array of data
    #    dataset_2 - 3d (time, lat, lon) array of data
    #     
    #  Output:
    #    patcor - a 1d array (time series) of pattern correlation coefficients.
    #
    #    Peter Lean  March 2011
    #    Editing: Kim Whitehall June 2012
    #        reason: std_dev not standardized on N-1
    #  
    # Output: time series of pattern correlation coefficients.
    
    TODO: ADD THIS TO THE DOC STRING
     # Calculate the Pattern Correlation Timeseries

   # called in do_rcmes_processing_sub.py 
   # Inputs:2 arrays of data
   #        t1 is the modelData and t2 is 3D obsdata - time,lat, lon NB, time here 
   #             is the number of time values eg for time period 199001010000 - 199201010000 
   #              if annual means-opt 1, was chosen, then t2.shape = (2,lat,lon)
   #          if monthly means - opt 2, was choosen, then t2.shape = (24,lat,lon)    
   #  Output:
   #    patcor - a 1d array (time series) of pattern correlation coefficients.
   #
   #    Peter Lean  March 2011
   #    Editing: Kim Whitehall June 2012
   #        reason: std_dev not standardized on N-1
           ##### Debugging print statements to show the difference the n-1 makes.
        #http://docs.scipy.org/doc/numpy/reference/generated/numpy.std.html
    '''
    # TODO:  Add in try block to ensure the shapes match
    
    
    
    nt = dataset_1.shape[0]
    
    # store results in list for convenience (then convert to numpy array)
    patcor = []
    
    for t in xrange(nt):
        # find mean and std_dev 
        mt1 = dataset_1[t, :, :].mean()
        mt2 = dataset_2[t, :, :].mean()
        
        sigma_t1 = dataset_1[t, :, :].std(ddof=1)
        sigma_t2 = dataset_2[t, :, :].std(ddof=1)
        
        # TODO: make means and standard deviations weighted by grid box area.

        
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

###########################################################################
# Anomaly Correlation

def calc_anom_corn(dataset_1, dataset_2, climatology=None):
    '''
    
        # Calculate the Anomaly Correlation
        # Kim Whitehall June 2012
        # Edited according to new metrics 
        # input three arrays, dataset_1, dataset_2 and climatology
        # Assumes climatology is for same time period 
        # TODO:  Rename function vars to declare what they are
    '''

    # store results in list for convenience (then convert to numpy array)
    anomcor = []    
    nt = dataset_1.shape[0]
    #prompt for the third file, i.e. climo file...  
    #include making sure the lat, lon and times are ok for comparision
    # find the climo in here and then using for eg, if 100 yrs 
    # is given for the climo file, but only looking at 10yrs
    # ask if want to input climo dataset for use....if no, call previous 
   
    if climatology != None:
        
        climoFileOption = raw_input('Would you like to use the full observation dataset as the climatology in this calculation? [y/n] \n>')
        if climoFileOption == 'y':
            base_dataset = climatology

        else:
            base_dataset = dataset_2
    
    #---------------------------------------------------------------------

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

###########################################################################
# Anomaly Correlation

def calc_anom_cor(t1, t2):
    '''
    # Calculate the Anomaly Correlation (Deprecated)
    '''
    
    nt = t1.shape[0]
    
    # store results in list for convenience (then convert to numpy 
    # array at the end)
    anomcor = []
    
    for t in xrange(nt):
        
        mt2 = t2[t, :, :].mean()
        
        sigma_t1 = t1[t, :, :].std(ddof=1)
        sigma_t2 = t2[t, :, :].std(ddof=1)
        
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

###########################################################################
# Coefficient of Efficiency
# Nash-sutcliff coefficient of efficiency (E)
def calc_nash_sutcliff(dataset_1, dataset_2):
    '''
    Routine to calculate the Nash-Sutcliff coefficient of efficiency (E)

      Assumption(s):  Both dataset_1 and dataset_2 are the same shape.
                      lat, lon must match up
                      time steps must align (i.e. months vs. months)
    
      Input:
        dataset_1 - 3d (time, lat, lon) array of data
        dataset_2 - 3d (time, lat, lon) array of data
    
     Output:
           nashcor - 1d array aligned along the time dimension of the input
           datasets. Time Series of Nash-Sutcliff Coefficient of efficiency
     Kim Whitehall June 2012 
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

###########################################################################
# Probability Distribution Function

def calc_pdf(dataset_1, dataset_2, 
             d1_max=dataset_1.amax(),
             d1_min=dataset_1.amin()):
    '''
   #################################################################################################
   # 
   #################################################################################################
   # Routine to calculate a normalised Probability Distribution Function with 
   # bins set according to data range.
   # Equation from Perkins et al. 2007
   #     PS=sum(min(Z_O_i, Z_M_i)) where Z is the distribution (histogram of the data for either 
   #                set)
   # called in do_rcmes_processing_sub.py 
   # Inputs:2 arrays of data
   #        t1 is the modelData and t2 is 3D obsdata - time,lat, lon NB, time here 
   #             is the number of time values eg for time period 199001010000 - 199201010000 
   #              if annual means-opt 1, was chosen, then t2.shape = (2,lat,lon)
   #          if monthly means - opt 2, was choosen, then t2.shape = (24,lat,lon)
   # User inputs: number of bins to use and edges (min and max)
   # Output:
   #     one float which represents the PDF for the year
   #
   #   Peter Lean July 2010 
   #   Edited: KDW July 2012
   #################################################################################################
    Routine to calculate a normalised PDF with bins set according to data range.
   # Input:
   #     2 data  arrays, modelData and obsData
   # Output:
   #     PDF for the year
   #
   #   Peter Lean July 2010 
   #   Edited: KDW July 2012
   #   Reason: according to new metrics given.Equation from Perkins et al. 2007
   #################################################################################################
   '''

    #import statistics as stats
    
    #list to store PDFs of modelData and obsData
    pdf_mod = []
    pdf_obs = []
    # float to store the final PDF similarity score
    similarity_score = 0.0

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
    pdf_mod, edges = np.histogram(dataset_1, bins=mybins, normed=True, new=True)  
    print 'dataset_1 distribution and edges', pdf_mod, edges
    pdf_obs, edges = np.histogram(dataset_2, bins=mybins, normed=True, new=True)           
    print 'dataset_2 distribution and edges', pdf_obs, edges    
    
    """
    *****************************************************
    #considering using pdf function from statistics package. It is not 
    # installed. Have to test on Mac.  
    # http://bonsai.hgc.jp/~mdehoon/software/python/Statistics/manual/index.xhtml#TOC31 
    #pdf_mod, edges = stats.pdf(dataset_1, bins=mybins)
    #print 'dataset_1 distribution and edges', pdf_mod, edges
    #pdf_obs,edges=stats.pdf(dataset_2,bins=mybins)           
    #print 'dataset_2 distribution and edges', pdf_obs, edges 
    *****************************************************
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

###########################################################################
# Standard deviation
# Kim Whitehall June 2012
# inputs: 1 parameter, the model dataset or obs dataset
def calc_stdev(t1):
    ''' 
    # Input: a dataset
    # Output: an array of the std_dev for each month in the dataset entered
    # use build in function from numpy
    # Calculate standard deviation in a given dataset
    
    '''

    nt = t1.shape[0]
    sigma_t1 = []
    for t in xrange(nt):
        sigma_t1.append(t1[t, :, :].std(ddof=1))
    sigma_t1 = np.array(sigma_t1)
    print sigma_t1, sigma_t1.shape
    return sigma_t1

###########################################################################