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
TODO: Text needed here to describe the module
'''

import datetime
import numpy
import numpy.ma as ma
import math
import re
import string
import time
import Nio

from scipy.ndimage import map_coordinates

def extract_subregion_from_data_array(data, lats, lons, latmin, latmax, lonmin, lonmax):
    '''
    Extract a sub-region from a data array.
       e.g. the user may load a global model file, but only want to examine data over North America
            This function extracts a sub-domain from the original data.
            The defined sub-region must be a regular lat/lon bounding box,
            but the model data may be on a non-regular grid (e.g. rotated, or Guassian grid layout).
            Data are kept on the original model grid and a rectangular (in model-space) region 
            is extracted which contains the rectangular (in lat/lon space) user supplied region.
    
     INPUT:
       data - 3d masked data array
       lats - 2d array of latitudes corresponding to data array
       lons - 2d array of longitudes corresponding to data array
       latmin, latmax, lonmin, lonmax - bounding box of required region to extract
       
     OUTPUT:
       data2 - subset of original data array containing only data from required subregion
       lats2 - subset of original latitude data array
       lons2 - subset of original longitude data array
    '''

    # Mask model data array to find grid points inside the supplied bounding box
    whlat = (lats > latmin) & (lats < latmax)
    whlon = (lons > lonmin) & (lons < lonmax)
    wh = whlat & whlon

    # Find required matrix indices describing the limits of the regular lat/lon bounding box
    jmax = numpy.where(wh == True)[0].max()
    jmin = numpy.where(wh == True)[0].min()
    imax = numpy.where(wh == True)[1].max()
    imin = numpy.where(wh == True)[1].min()

    # Cut out the sub-region from the data array
    jmax=max(jmax,data.shape[1]-1)
    imax=max(imax,data.shape[2]-1)
    data2 = ma.zeros((data.shape[0], jmax-jmin+1, imax-imin+1))    
    data2 = data[:,jmin:jmax+1,imin:imax+1]                        

    # Cut out sub-region from lats,lons arrays
    lats2 = lats[jmin:jmax+1,imin:imax+1]                          
    lons2 = lons[jmin:jmax+1,imin:imax+1]                         
    return data2, lats2, lons2


def calc_area_mean(data, lats, lons, mymask='not set'):
    '''
    Calculate Area Average of data in a masked array
     INPUT:
         data:  a masked array of data (NB. only data from one time expected to be passed at once)
         lats:  2d array of regularly gridded latitudes
         lons:  2d array of regularly gridded longitudes
         mymask:  (optional) defines spatial region to do averaging over
     
     OUTPUT:
         area_mean: a value for the mean inside the area
    '''

    # If mask not passed in, then set maks to cover whole data domain
    if mymask == 'not set':
       mymask = numpy.empty(data.shape)
       mymask[:] = False # NB. mask means (don't show), so False everywhere means use everything.
   
    # Dimension check on lats, lons
    #  Sometimes these arrays are 3d, sometimes 2d, sometimes 1d
    #  This bit of code just converts to the required 2d array shape
    if len(lats.shape) == 3:
       lats = lats[0,:,:]

    if len(lons.shape) == 3:
       lons = lons[0,:,:]

    if numpy.logical_and(len(lats.shape) == 1, len(lons.shape) == 1):
       lons,lats = numpy.meshgrid(lons, lats)
 
    # Calculate grid length (assuming regular lat/lon grid)
    dlat = lats[1,0] - lats[0,0]
    dlon = lons[0,1] - lons[0,0]

    # Calculates weights for each grid box
    myweights = calc_area_in_grid_box(lats, dlon, dlat)

    # Create a new masked array covering just user selected area (defined in mymask)
    #   NB. this preserves missing data points in the observations data
    subdata = ma.masked_array(data, mask=mymask)
 
    if myweights.shape != subdata.shape:
       myweights.resize(subdata.shape)
       myweights[1:,:] = myweights[0,:]

    # Calculate weighted mean using ma.average (which takes weights)
    area_mean = ma.average(subdata, weights=myweights)
 
    return area_mean


def calc_area_in_grid_box(latitude, dlat, dlon):
    '''
    Calculate area of regular lat-lon grid box
     INPUT:
        latitude: latitude of grid box (degrees)
        dlat:     grid length in latitude direction (degrees)
        dlon:     grid length in longitude direction (degrees)
     OUTPUT:
        A:        area of the grid box
    '''

    R = 6371000  # radius of Earth in metres
    C = 2*math.pi*R

    latitude = numpy.radians(latitude)

    A = (dlon*(C/360.)) * (dlat*(C/360.)*numpy.cos(latitude))

    return A

def do_regrid(q, lat, lon, lat2, lon2, order=1, mdi=-999999999):
    '''
    Perform regridding from one set of lat,lon values onto a new set (lat2,lon2)
     Input: 
        q          - the variable to be regridded
        lat,lon    - original co-ordinates corresponding to q values
        lat2,lon2  - new set of latitudes and longitudes that you want to regrid q onto 
        order      - (optional) interpolation order 1=bi-linear, 3=cubic spline
        mdi  	    - (optional) fill value for missing data (used in creation of masked array)
     Output:
        q2  - q regridded onto the new set of lat2,lon2 
    '''
    nlat  = q.shape[0]
    nlon  = q.shape[1]
    nlat2 = lat2.shape[0]
    nlon2 = lon2.shape[1]
    # To make our lives easier down the road, let's turn these into arrays of x & y coords
    loni = lon2.ravel()
    lati = lat2.ravel()
    # NB. it won't run unless you do this
    loni = loni.copy()
    lati = lati.copy()
    # Now, we'll set points outside the boundaries to lie along an edge
    loni[loni > lon.max()] = lon.max()
    loni[loni < lon.min()] = lon.min()
    # To deal with the "hard" break, we'll have to treat y differently, so we're just setting the min here...
    lati[lati > lat.max()] = lat.max()
    lati[lati < lat.min()] = lat.min()
    # We need to convert these to (float) indicies (xi should range from 0 to (nx - 1), etc)
    loni = (nlon - 1) * (loni - lon.min()) / (lon.max() - lon.min())
    # Deal with the "hard" break in the y-direction
    lati = (nlat - 1) * (lati - lat.min()) / (lat.max() - lat.min())
    # Notes on dealing with MDI when regridding data.
    #  Method adopted here:
    #    Use bilinear interpolation of data by default (but user can specify other order using order=... in call)
    #    Perform bilinear interpolation of data, and of mask.
    #    To be conservative, new grid point which contained some missing data on the old grid is set to missing data.
    #            -this is achieved by looking for any non-zero interpolated mask values.
    #    To avoid issues with bilinear interpolation producing strong gradients leading into the MDI,
    #     set values at MDI points to mean data value so little gradient visible = not ideal, but acceptable for now.
    # Set values in MDI so that similar to surroundings so don't produce large gradients when interpolating
    # Preserve MDI mask, by only changing data part of masked array object.
    for shift in (-1,1):
        for axis in (0,1):        
            q_shifted = numpy.roll(q, shift=shift, axis=axis)
            idx=~q_shifted.mask * q.mask
            q.data[idx] = q_shifted[idx]
    # Now we actually interpolate
    # map_coordinates does cubic interpolation by default, 
    # use "order=1" to preform bilinear interpolation instead...
    q2 = map_coordinates(q, [lati, loni], order=order)
    q2 = q2.reshape([nlat2, nlon2])
    # Set values to missing data outside of original domain
    q2 = ma.masked_array(q2, mask=numpy.logical_or(numpy.logical_or(lat2>=lat.max(), lat2<=lat.min()), \
        numpy.logical_or(lon2<=lon.min(),lon2>=lon.max())))
    # Make second map using nearest neighbour interpolation -use this to determine locations with MDI and mask these
    qmdi = numpy.zeros_like(q)
    qmdi[q.mask==True] = 1.
    qmdi[q.mask==False] = 0.
    qmdi_r = map_coordinates(qmdi, [lati, loni], order=order)
    qmdi_r = qmdi_r.reshape([nlat2, nlon2])
    mdimask = (qmdi_r != 0.0)
    # Combine missing data mask, with outside domain mask define above.
    q2.mask = numpy.logical_or(mdimask,q2.mask)
    return q2

def create_mask_using_threshold(masked_array, threshold=0.5):
    '''
    Routine to create a mask, depending on the proportion of times with missing data.
    For each pixel, calculate proportion of times that are missing data, if the proportion is above a 
    specified threshold value, then mark the pixel as missing data.
   
    Input:
       masked_array - a numpy masked array of data (assumes time on axis 0, and space on axes 1 and 2.
       threshold    - (optional) threshold proportion above which a pixel is marked as 'missing data'.
                               NB. default threshold = 50%
    Output:
       mymask       - a numpy array describing the mask. NB. not a masked array, just the mask itself.
    '''

    # try, except used as some model files don't have a full mask, but a single bool
    #  the except catches this situation and deals with it appropriately.
    try:
        nT = masked_array.mask.shape[0]

        # For each pixel, count how many times are masked.
        nMasked = masked_array.mask[:,:,:].sum(axis=0)

        # Define new mask as when a pixel has over a defined threshold ratio of masked data
        #   e.g. if the threshold is 75%, and there are 10 times,
        #        then a pixel will be masked if more than 5 times are masked.
        mymask = nMasked > (nT*threshold)
    except:
        mymask = numpy.zeros_like(masked_array.data[0,:,:])

    return mymask


def calc_average_on_new_time_unit_K(data, dateList, unit):
    '''
    Routine to calculate averages on longer time units than the data exists on.
    e.g. if the data is 6-hourly, calculate daily, or monthly means.
     
    Input:
        data     - data values
        dateList - list of python datetime structures corresponding to data values
        unit     - string describing time unit to average onto 
                      e.g. 'monthly', 'daily', 'pentad','annual','decadal'
    Output:
        meanstorem - numpy masked array of data values meaned over required time period
        newTimesList - a list of python datetime objects representing the data in the new averagin period
                           NB. currently set to beginning of averaging period, 
                           i.e. mean Jan 1st - Jan 31st -> represented as Jan 1st, 00Z.
    '''

    # Check if the user-selected temporal grid is valid. If not, EXIT
    acceptable = (unit=='full')|(unit=='annual')|(unit=='monthly')|(unit=='daily')|(unit=='pentad')
    if not acceptable:
        print 'Error: unknown unit type selected for time averaging: EXIT'
        return -1,-1,-1,-1

    # Calculate arrays of: annual timeseries: year (2007,2007),
    #                      monthly time series: year-month (200701,200702),
    #                      daily timeseries:  year-month-day (20070101,20070102) 
    #  depending on user-selected averaging period.

    # Year list
    if unit=='annual':
        timeunits = []
        for i in numpy.arange(len(dateList)):
            timeunits.append(str(dateList[i].year))
        timeunits = numpy.array(timeunits, dtype=int)
         
    # YearMonth format list
    if unit=='monthly':
        timeunits = []
        for i in numpy.arange(len(dateList)):
            timeunits.append(str(dateList[i].year) + str("%02d" % dateList[i].month))
        timeunits = numpy.array(timeunits,dtype=int)

    # YearMonthDay format list
    if unit=='daily':
        timeunits = []
        for i in numpy.arange(len(dateList)):
            timeunits.append(str(dateList[i].year) + str("%02d" % dateList[i].month) + str("%02d" % dateList[i].day))
        timeunits = numpy.array(timeunits,dtype=int)

    # TODO: add pentad setting using Julian days?

    # Full list: a special case
    if unit == 'full':
        comment='Calculating means data over the entire time range: i.e., annual-mean climatology'
        timeunits = []
        for i in numpy.arange(len(dateList)):
            timeunits.append(999)  # i.e. we just want the same value for all times.
        timeunits = numpy.array(timeunits, dtype=int)

    # empty list to store new times
    newTimesList = []

    # Decide whether or not you need to do any time averaging.
    #   i.e. if data are already on required time unit then just pass data through and 
    #        calculate and return representative datetimes.
    processing_required = True
    if len(timeunits)==(len(numpy.unique(timeunits))):
        processing_required = False

    # 1D data arrays, i.e. time series
    if data.ndim==1:
        # Create array to store the resulting data
        meanstore = numpy.zeros(len(numpy.unique(timeunits)))
  
        # Calculate the means across each unique time unit
        i=0
        for myunit in numpy.unique(timeunits):
            if processing_required:
                datam=ma.masked_array(data,timeunits!=myunit)
                meanstore[i] = ma.average(datam)
            
            # construct new times list
            smyunit = str(myunit)
            if len(smyunit)==4:  # YYYY
                yyyy = int(myunit[0:4])
                mm = 1
                dd = 1
            if len(smyunit)==6:  # YYYYMM
                yyyy = int(smyunit[0:4])
                mm = int(smyunit[4:6])
                dd = 1
            if len(smyunit)==8:  # YYYYMMDD
                yyyy = int(smyunit[0:4])
                mm = int(smyunit[4:6])
                dd = int(smyunit[6:8])
            if len(smyunit)==3:  # Full time range
                # Need to set an appropriate time representing the mid-point of the entire time span
                dt = dateList[-1]-dateList[0]
                halfway = dateList[0]+(dt/2)
                yyyy = int(halfway.year)
                mm = int(halfway.month)
                dd = int(halfway.day)

            newTimesList.append(datetime.datetime(yyyy,mm,dd,0,0,0,0))
            i = i+1

    # 3D data arrays
    if data.ndim==3:
        # datamask = create_mask_using_threshold(data,threshold=0.75)
        # Create array to store the resulting data
        meanstore = numpy.zeros([len(numpy.unique(timeunits)),data.shape[1],data.shape[2]])
  
        # Calculate the means across each unique time unit
        i=0
        datamask_store = []
        for myunit in numpy.unique(timeunits):
            if processing_required:
                mask = numpy.zeros_like(data)
                mask[timeunits!=myunit,:,:] = 1.0
                # Calculate missing data mask within each time unit...
                datamask_at_this_timeunit = numpy.zeros_like(data)
                datamask_at_this_timeunit[:]= create_mask_using_threshold(data[timeunits==myunit,:,:],threshold=0.75)
                # Store results for masking later
                datamask_store.append(datamask_at_this_timeunit[0])
                # Calculate means for each pixel in this time unit, ignoring missing data (using masked array).
                datam = ma.masked_array(data,numpy.logical_or(mask,datamask_at_this_timeunit))
                meanstore[i,:,:] = ma.average(datam,axis=0)
            # construct new times list
            smyunit = str(myunit)
            if len(smyunit)==4:  # YYYY
                yyyy = int(smyunit[0:4])
                mm = 1
                dd = 1
            if len(smyunit)==6:  # YYYYMM
                yyyy = int(smyunit[0:4])
                mm = int(smyunit[4:6])
                dd = 1
            if len(smyunit)==8:  # YYYYMMDD
                yyyy = int(smyunit[0:4])
                mm = int(smyunit[4:6])
                dd = int(smyunit[6:8])
            if len(smyunit)==3:  # Full time range
                # Need to set an appropriate time representing the mid-point of the entire time span
                dt = dateList[-1]-dateList[0]
                halfway = dateList[0]+(dt/2)
                yyyy = int(halfway.year)
                mm = int(halfway.month)
                dd = int(halfway.day)
            newTimesList.append(datetime.datetime(yyyy,mm,dd,0,0,0,0))
            i += 1

        if not processing_required:
            meanstorem = data

        if processing_required:
            # Create masked array (using missing data mask defined above)
            datamask_store = numpy.array(datamask_store)
            meanstorem = ma.masked_array(meanstore, datamask_store)

    return meanstorem,newTimesList

def calc_average_on_new_time_unit(data, dateList, unit='monthly'):
    '''
    Routine to calculate averages on longer time units than the data exists on.
    e.g. if the data is 6-hourly, calculate daily, or monthly means.
   
    Input:
            data     - data values
            dateList - list of python datetime structures corresponding to data values
            unit     - string describing time unit to average onto 
                          e.g. 'monthly', 'daily', 'pentad','annual','decadal'
      
    Output:
            meanstorem - numpy masked array of data values meaned over required time period
            newTimesList - a list of python datetime objects representing the data in the new averagin period
                               NB. currently set to beginning of averaging period, 
                               i.e. mean Jan 1st - Jan 31st -> represented as Jan 1st, 00Z.
    '''

    # First catch unknown values of time unit passed in by user
    acceptable = (unit=='full')|(unit=='annual')|(unit=='monthly')|(unit=='daily')|(unit=='pentad')

    if not acceptable:
        print 'Error: unknown unit type selected for time averaging'
        print '       Please check your code.'
        return

    # Calculate arrays of years (2007,2007),
    #                     yearsmonths (200701,200702),
    #                     or yearmonthdays (20070101,20070102) 
    #  -depending on user selected averaging period.

    # Year list
    if unit=='annual':
        print 'Calculating annual mean data'
        timeunits = []

        for i in numpy.arange(len(dateList)):
            timeunits.append(str(dateList[i].year))

        timeunits = numpy.array(timeunits, dtype=int)
         
    # YearMonth format list
    if unit=='monthly':
        print 'Calculating monthly mean data'
        timeunits = []

        for i in numpy.arange(len(dateList)):
            timeunits.append(str(dateList[i].year) + str("%02d" % dateList[i].month))

        timeunits = numpy.array(timeunits,dtype=int)

    # YearMonthDay format list
    if unit=='daily':
        print 'Calculating daily mean data'
        timeunits = []
        for i in numpy.arange(len(dateList)):
            timeunits.append(str(dateList[i].year) + str("%02d" % dateList[i].month) + str("%02d" % dateList[i].day))
        timeunits = numpy.array(timeunits,dtype=int)

    # TODO: add pentad setting using Julian days?

    # Full list: a special case
    if unit=='full':
        print 'Calculating means data over the entire time range: i.e., annual-mean climatology'
        timeunits = []

        for i in numpy.arange(len(dateList)):
            timeunits.append(999)  # i.e. we just want the same value for all times.

        timeunits = numpy.array(timeunits, dtype=int)

    # empty list to store new times
    newTimesList = []

    # Decide whether or not you need to do any time averaging.
    #   i.e. if data are already on required time unit then just pass data through and 
    #        calculate and return representative datetimes.
    processing_required = True
    if len(timeunits)==(len(numpy.unique(timeunits))):
        processing_required = False

    # 1D data arrays, i.e. time series
    if data.ndim==1:
        # Create array to store the resulting data
        meanstore = numpy.zeros(len(numpy.unique(timeunits)))
  
        # Calculate the means across each unique time unit
        i=0
        for myunit in numpy.unique(timeunits):
            if processing_required:
                datam=ma.masked_array(data,timeunits!=myunit)
                meanstore[i] = ma.average(datam)

            # construct new times list
            smyunit = str(myunit)
            if len(smyunit)==4:  # YYYY
                yyyy = int(myunit[0:4])
                mm = 1
                dd = 1
            if len(smyunit)==6:  # YYYYMM
                yyyy = int(smyunit[0:4])
                mm = int(smyunit[4:6])
                dd = 1
            if len(smyunit)==8:  # YYYYMMDD
                yyyy = int(smyunit[0:4])
                mm = int(smyunit[4:6])
                dd = int(smyunit[6:8])
            if len(smyunit)==3:  # Full time range
                # Need to set an appropriate time representing the mid-point of the entire time span
                dt = dateList[-1]-dateList[0]
                halfway = dateList[0]+(dt/2)
                yyyy = int(halfway.year)
                mm = int(halfway.month)
                dd = int(halfway.day)
  
            newTimesList.append(datetime.datetime(yyyy,mm,dd,0,0,0,0))
            i = i+1

    # 3D data arrays
    if data.ndim==3:

        #datamask = create_mask_using_threshold(data,threshold=0.75)

        # Create array to store the resulting data
        meanstore = numpy.zeros([len(numpy.unique(timeunits)),data.shape[1],data.shape[2]])
  
        # Calculate the means across each unique time unit
        i=0
        datamask_store = []
        for myunit in numpy.unique(timeunits):
            if processing_required:

                mask = numpy.zeros_like(data)
                mask[timeunits!=myunit,:,:] = 1.0

                # Calculate missing data mask within each time unit...
                datamask_at_this_timeunit = numpy.zeros_like(data)
                datamask_at_this_timeunit[:]= create_mask_using_threshold(data[timeunits==myunit,:,:],threshold=0.75)
                # Store results for masking later
                datamask_store.append(datamask_at_this_timeunit[0])

                # Calculate means for each pixel in this time unit, ignoring missing data (using masked array).
                datam = ma.masked_array(data,numpy.logical_or(mask,datamask_at_this_timeunit))
                meanstore[i,:,:] = ma.average(datam,axis=0)

            # construct new times list
            smyunit = str(myunit)
            if len(smyunit)==4:  # YYYY
                yyyy = int(smyunit[0:4])
                mm = 1
                dd = 1
            if len(smyunit)==6:  # YYYYMM
                yyyy = int(smyunit[0:4])
                mm = int(smyunit[4:6])
                dd = 1
            if len(smyunit)==8:  # YYYYMMDD
                yyyy = int(smyunit[0:4])
                mm = int(smyunit[4:6])
                dd = int(smyunit[6:8])
            if len(smyunit)==3:  # Full time range
                # Need to set an appropriate time representing the mid-point of the entire time span
                dt = dateList[-1]-dateList[0]
                halfway = dateList[0]+(dt/2)
                yyyy = int(halfway.year)
                mm = int(halfway.month)
                dd = int(halfway.day)

            newTimesList.append(datetime.datetime(yyyy,mm,dd,0,0,0,0))

            i += 1

        if not processing_required:
            meanstorem = data

        if processing_required:
            # Create masked array (using missing data mask defined above)
            datamask_store = numpy.array(datamask_store)
            meanstorem = ma.masked_array(meanstore, datamask_store)

    return meanstorem,newTimesList



def calc_running_accum_from_period_accum(data):
    '''
    Routine to calculate running total accumulations from individual period accumulations.
       e.g.  0,0,1,0,0,2,2,1,0,0
          -> 0,0,1,1,1,3,5,6,6,6
   
    Input:
         data: numpy array with time in the first axis
   
    Output:
         running_acc: running accumulations
    '''
    running_acc = numpy.zeros_like(data)

    if len(data.shape)==1:
        running_acc[0] = data[0]

    if len(data.shape)>1:
        running_acc[0,:] = data[0,:]

    for i in numpy.arange(data.shape[0]-1):
        if len(data.shape)==1:
            running_acc[i+1] = running_acc[i] + data[i+1]

        if len(data.shape)>1:
            running_acc[i+1,:] = running_acc[i,:] + data[i+1,:]

    return running_acc


def ignore_boundaries(data, rim=10):
    '''
    Routine to mask the lateral boundary regions of model data to ignore them from calculations.
    Input:
        data - a masked array of model data
        rim - (optional) number of grid points to ignore
   
    Output:
        data - data array with boundary region masked
    '''
    nx = data.shape[1]
    ny = data.shape[0]

    rimmask = numpy.zeros_like(data)
    for j in numpy.arange(rim):
        rimmask[j,0:nx-1] = 1.0

    for j in ny-1-numpy.arange(rim):
        rimmask[j,0:nx-1] = 1.0

    for i in numpy.arange(rim):
        rimmask[0:ny-1,i] = 1.0

    for i in nx-1-numpy.arange(rim):
        rimmask[0:ny-1,i] = 1.0

    data = ma.masked_array(data,mask=rimmask)

    return data

def decode_model_times(filelist, timeVarName):
    '''
    Routine to convert from model times ('hours since 1900...', 'days since ...') 
    into a python datetime structure
   
    Input:
        filelist - list of model files
        timeVarName - name of the time variable in the model files
   
    Output:
        times  - list of python datetime objects describing model data times
    '''

    f = Nio.open_file(filelist[0])
    xtimes = f.variables[timeVarName]
    timeFormat = xtimes.attributes['units']

    # search to check if 'since' appears in units
    try:
        sinceLoc = re.search('since',timeFormat).end()

    except:
        print 'Error decoding model times: time variable attributes do not contain "since"'
        return 0

    # search for 'seconds','minutes','hours', 'days', 'months', 'years' so know units
    units = ''
    try:
        mysearch = re.search('minutes',timeFormat).end()
        units = 'minutes'
    except:
        pass
    try:
        mysearch = re.search('hours',timeFormat).end()
        units = 'hours'
    except:
        pass
    try:
        mysearch = re.search('days',timeFormat).end()
        units = 'days'
    except:
        pass
    try:
        mysearch = re.search('months',timeFormat).end()
        units = 'months'
    except:
        pass
    try:
        mysearch = re.search('years',timeFormat).end()
        units = 'years'
    except:
        pass
   
    # cut out base time (the bit following 'since')
    base_time_string = string.lstrip(timeFormat[sinceLoc:])

    # decode base time
    base_time = decodeTimeFromString(base_time_string)


    times=[]
    for xtime in xtimes[:]:
        if units=='minutes':  
            dt = datetime.timedelta(minutes=xtime)
            new_time = base_time + dt

        if units=='hours':  
            dt = datetime.timedelta(hours=xtime)
            new_time = base_time + dt

        if units=='days':  
            dt = datetime.timedelta(days=xtime)
            new_time = base_time + dt

        if units=='months':   
            # NB. adding months in python is complicated as month length varies and hence ambigous.
            # Perform date arithmatic manually
             #  Assumption: the base_date will usually be the first of the month
            #              NB. this method will fail if the base time is on the 29th or higher day of month
            #                      -as can't have, e.g. Feb 31st.
            new_month = base_time.month + xtime % 12
            new_year = int(math.floor(base_time.year + xtime / 12.))
            new_time = datetime.datetime(new_year,new_month,base_time.day,base_time.hour,base_time.second,0)

        if units=='years':
            dt = datetime.timedelta(years=xtime)
            new_time = base_time + dt
         
        times.append(new_time)

    return times

def decodeTimeFromString(time_string):
    '''
    Decodes string into a python datetime object
    Method: tries a bunch of different time format possibilities and hopefully one of them will hit.
     
    Input:  
        time_string - a string that represents a date/time
    Output: 
        mytime - a python datetime object
    '''
    if '.' in time_string:
        time_string = time_string.split('.')[0]+'0'
    else:
        pass

    try:
        mytime = time.strptime(time_string, '%Y-%m-%d %H:%M:%S')
        mytime = datetime.datetime(*mytime[0:6])
        return mytime

    except ValueError:
        pass

    try:
        mytime = time.strptime(time_string, '%Y/%m/%d %H:%M:%S')
        mytime = datetime.datetime(*mytime[0:6])
        return mytime

    except ValueError:
        pass

    try:
        mytime = time.strptime(time_string, '%Y%m%d %H:%M:%S')
        mytime = datetime.datetime(*mytime[0:6])
        return mytime

    except ValueError:
        pass

    try:
        mytime = time.strptime(time_string, '%Y:%m:%d %H:%M:%S')
        mytime = datetime.datetime(*mytime[0:6])
        return mytime

    except ValueError:
        pass

    try:
        mytime = time.strptime(time_string, '%Y%m%d%H%M%S')
        mytime = datetime.datetime(*mytime[0:6])
        return mytime

    except ValueError:
        pass

    try:
        mytime = time.strptime(time_string, '%Y-%m-%d %H:%M')
        mytime = datetime.datetime(*mytime[0:6])
        return mytime

    except ValueError:
        pass

    try:
        mytime = time.strptime(time_string, '%Y-%m-%d')
        mytime = datetime.datetime(*mytime[0:6])
        return mytime

    except ValueError:
        pass

    print 'Error decoding time string:',time_string,' does not match a predefined time format'
    print '[Y-m-d H:M:S, Y/m/d H:M:S, Ymd H:M:S, Y:m:d H:M:S, YmdHMS, Y-m-d H:M, Y-m-d]'
    return 0

def regrid_wrapper(regrid_choice, obsdata, obslats, obslons, mdldata, mdllats, mdllons):
    '''
    Wrapper routine for regridding.
    Either regrids model to obs grid, or obs to model grid, depending on user choice
    Inputs:
        regrid_choice - [0] = Regrid obs data onto model grid
                      - [1] = Regrid model data onto obs grid
        obsdata,mdldata - data arrays
        obslats,obslons - observation lat,lon arrays
        mdllats,mdllons - model lat,lon arrays
    Output:
       rdata,rdata2 - regridded data
        lats,lons    - latitudes and longitudes of regridded data
    '''
    # Regrid obs data onto model grid
    if regrid_choice=='0':
        ndims = len(obsdata.shape)
        if ndims == 3:
            newshape = [obsdata.shape[0],mdldata.shape[1],mdldata.shape[2]]
            nT = obsdata.shape[0]
        if ndims == 2:
            newshape = [mdldata.shape[0],mdldata.shape[1]]
            nT = 0
        rdata = mdldata
        lats,lons = mdllats,mdllons
        # Create a new masked array with the required dimensions
        tmp = numpy.zeros(newshape)
        rdata2 = numpy.ma.MaskedArray(tmp,mask=(tmp==0))
        tmp = 0            # free up some memory
        rdata2[:] = 0.0
        if nT > 0:
            for t in numpy.arange(nT):
                rdata2[t,:,:] = do_regrid(obsdata[t,:,:],obslats[:,:],obslons[:,:],mdllats[:,:],mdllons[:,:])
        if nT == 0:
            rdata2[:,:] = do_regrid(obsdata[:,:],obslats[:,:],obslons[:,:],mdllats[:,:],mdllons[:,:])

    # Regrid model data onto obs grid
    if regrid_choice == '1':
        ndims = len(mdldata.shape)
        if ndims == 3:
            newshape = [mdldata.shape[0],obsdata.shape[1],obsdata.shape[2]]
            nT = obsdata.shape[0]
        if ndims == 2:
            newshape = [obsdata.shape[0],obsdata.shape[1]]
            nT = 0
        rdata2 = obsdata
        lats,lons = obslats,obslons
        tmp = numpy.zeros(newshape)
        rdata = numpy.ma.MaskedArray(tmp,mask=(tmp==0))
        tmp = 0 # free up some memory
        rdata[:] = 0.0
        if nT > 0:
            for t in numpy.arange(nT):
                rdata[t,:,:] = do_regrid(mdldata[t,:,:],mdllats[:,:],mdllons[:,:],obslats[:,:],obslons[:,:])
        if nT == 0:
            rdata[:,:] = do_regrid(mdldata[:,:],mdllats[:,:],mdllons[:,:],obslats[:,:],obslons[:,:])

    return rdata, rdata2, lats, lons

def regrid_space(oLats,oLons,iLats,iLons,iData):
    '''
    Routine for generic spatial interpolation for spatial regridding.
    Input:
        oLats, oLons: 2-d arrays for the latitudes and longitudes of the target grid system
        iLats, iLons: 2-d arrays for the latitudes and longitudes of the input grid system
        iData: 2-d arrays of the input (to be interpolated) data
    Output:
        rdata,rdata2 - regridded data
        lats,lons    - latitudes and longitudes of regridded data
    '''

    # Regrid obs data onto model grid
    if regrid_choice == '0':
        ndims = len(obsdata.shape)
        if ndims == 3:
            newshape = [obsdata.shape[0],mdldata.shape[1],mdldata.shape[2]]
            nT = obsdata.shape[0]
        if ndims == 2:
            newshape = [mdldata.shape[0],mdldata.shape[1]]
            nT = 0
        rdata = mdldata
        lats,lons = mdllats,mdllons
        # Create a new masked array with the required dimensions
        tmp = numpy.zeros(newshape)
        rdata2 = numpy.ma.MaskedArray(tmp,mask=(tmp==0))
        tmp = 0            # free up some memory
        rdata2[:] = 0.0
        if nT > 0:
            for t in numpy.arange(nT):
                rdata2[t,:,:] = do_regrid(obsdata[t,:,:],obslats[:,:],obslons[:,:],mdllats[:,:],mdllons[:,:])
        if nT == 0:
                rdata2[:,:] = do_regrid(obsdata[:,:],obslats[:,:],obslons[:,:],mdllats[:,:],mdllons[:,:])

    # Regrid model data onto obs grid
    if regrid_choice == '1':
        ndims = len(mdldata.shape)
        if ndims == 3:
            newshape = [mdldata.shape[0],obsdata.shape[1],obsdata.shape[2]]
            nT = obsdata.shape[0]
        if ndims == 2:
            newshape = [obsdata.shape[0],obsdata.shape[1]]
            nT = 0
        rdata2 = obsdata
        lats,lons = obslats,obslons
        tmp = numpy.zeros(newshape)
        rdata = numpy.ma.MaskedArray(tmp,mask=(tmp==0))
        tmp = 0 # free up some memory
        rdata[:] = 0.0
        if nT > 0:
            for t in numpy.arange(nT):
                rdata[t,:,:] = do_regrid(mdldata[t,:,:],mdllats[:,:],mdllons[:,:],obslats[:,:],obslons[:,:])
        if nT == 0:
            rdata[:,:] = do_regrid(mdldata[:,:],mdllats[:,:],mdllons[:,:],obslats[:,:],obslons[:,:])

    return rdata,rdata2,lats,lons

def extract_sub_time_selection(allTimes,subTimes,data):
    '''
    Routine to extract a sub-selection of times from a data array.
    e.g. suppose a data array has 30 time values for daily data for a whole month, 
    but you only want the data from the 5th-15th of the month.
   
    Input:
        allTimes - list of datetimes describing what times the data in the data array correspond to
        subTimes - the times you want to extract data from
        data     - the data array
   
    Output:
        subdata     - subselection of data array
    '''
    temp_index = numpy.intersect1d(allTimes,subTimes)
    subdata = data[temp_index,:,:]
    return subdata
