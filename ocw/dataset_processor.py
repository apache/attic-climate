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

from ocw import dataset as ds

import datetime
import numpy as np
import numpy.ma as ma
import scipy.interpolate
import scipy.ndimage
from scipy.ndimage import map_coordinates
import netCDF4

import logging

logger = logging.getLogger(__name__)

def temporal_rebin(target_dataset, temporal_resolution):
    """ Rebin a Dataset to a new temporal resolution
    
    :param target_dataset: Dataset object that needs temporal rebinned
    :type target_dataset: :class:`dataset.Dataset`

    :param temporal_resolution: The new temporal bin size
    :type temporal_resolution: :class:`datetime.timedelta`
    
    :returns: A new temporally rebinned Dataset
    :rtype: :class:`dataset.Dataset`
    """
    # Decode the temporal resolution into a string format that 
    # _rcmes_calc_average_on_new_time_unit_K() can understand
    day_count = temporal_resolution.days
    time_unit = None
    if day_count == 1:
        time_unit = 'daily'
    elif day_count > 1 and day_count <= 31:
        time_unit = 'monthly'
    elif day_count > 31 and day_count <= 366:
        time_unit = 'annual'
    else:
        time_unit = 'full'

    masked_values = target_dataset.values.view(ma.MaskedArray)
    binned_values, binned_dates = _rcmes_calc_average_on_new_time_unit_K(masked_values, target_dataset.times, time_unit)
    binned_dates = np.array(binned_dates)
    new_dataset = ds.Dataset(target_dataset.lats, 
                             target_dataset.lons, 
                             binned_dates, 
                             binned_values,
                             target_dataset.variable,
                             target_dataset.units,
                             target_dataset.name)
    
    return new_dataset

def spatial_regrid(target_dataset, new_latitudes, new_longitudes):
    """ Regrid a Dataset using the new latitudes and longitudes

    :param target_dataset: Dataset object that needs spatially regridded
    :type target_dataset: :class:`dataset.Dataset`

    :param new_latitudes: Array of latitudes
    :type new_latitudes: :class:`numpy.ndarray`

    :param new_longitudes: Array of longitudes
    :type new_longitudes: :class:`numpy.ndarray`

    :returns: A new spatially regridded Dataset
    :rtype: :class:`dataset.Dataset`
    """
    # Make masked array of shape (times, new_latitudes,new_longitudes)
    new_values = ma.zeros([len(target_dataset.times), 
                           len(new_latitudes), 
                           len(new_longitudes)])

    # Create grids of the given lats and lons for the underlying API
    # NOTE: np.meshgrid() requires inputs (x, y) and returns data 
    #       of shape(y|lat|rows, x|lon|columns).  So we pass in lons, lats
    #       and get back data.shape(lats, lons)
    lons, lats = np.meshgrid(target_dataset.lons, target_dataset.lats)
    new_lons, new_lats = np.meshgrid(new_longitudes, new_latitudes)
    # Convert all lats and lons into Numpy Masked Arrays
    lats = ma.array(lats)
    lons = ma.array(lons)
    new_lats = ma.array(new_lats)
    new_lons = ma.array(new_lons)
    target_values = ma.array(target_dataset.values)
    
    # Call _rcmes_spatial_regrid on each time slice
    for i in range(len(target_dataset.times)):
        new_values[i] = _rcmes_spatial_regrid(target_values[i],
                                              lats,
                                              lons,
                                              new_lats,
                                              new_lons)
    
    # TODO: 
    # This will call down to the _congrid() function and the lat and lon 
    # axis will be adjusted with the time axis being held constant
    
    # Create a new Dataset Object to return using new data
    regridded_dataset = ds.Dataset(new_latitudes, 
                                   new_longitudes, 
                                   target_dataset.times, 
                                   new_values,
                                   target_dataset.variable,
                                   target_dataset.units,
                                   target_dataset.name)
    return regridded_dataset

def ensemble(datasets):
    """
    Generate a single dataset which is the mean of the input datasets
    
    :param datasets: Datasets to be used to compose the ensemble dataset from.
        All Datasets must be the same shape.
    :type datasets: :class:`list` of :class:`dataset.Dataset`
    
    :returns: New Dataset with a name of 'Dataset Ensemble'
    :rtype: :class:`dataset.Dataset`
    """
    _check_dataset_shapes(datasets)
    dataset_values = [dataset.values for dataset in datasets]
    ensemble_values = np.mean(dataset_values, axis=0)
    
    # Build new dataset object from the input datasets and the ensemble values and return it
    ensemble_dataset = ds.Dataset(datasets[0].lats, 
                                  datasets[0].lons, 
                                  datasets[0].times,
                                  ensemble_values,
                                  datasets[0].units,
                                  name="Dataset Ensemble")
    
    return ensemble_dataset

def subset(subregion, target_dataset):
    '''Subset given dataset(s) with subregion information

    :param subregion: The Bounds with which to subset the target Dataset. 
    :type subregion: :class:`dataset.Bounds`

    :param target_dataset: The Dataset object to subset.
    :type target_dataset: :class:`dataset.Dataset`

    :returns: The subset-ed Dataset object
    :rtype: :class:`dataset.Dataset`

    :raises: ValueError
    '''

    # Ensure that the subregion information is well formed
    _are_bounds_contained_by_dataset(subregion, target_dataset)

    # Get subregion indices into subregion data
    dataset_slices = _get_subregion_slice_indices(subregion, target_dataset)

    # Build new dataset with subset information
    return ds.Dataset(
        # Slice the lats array with our calculated slice indices
        target_dataset.lats[dataset_slices["lat_start"]: 
                            dataset_slices["lat_end"] + 1],
        # Slice the lons array with our calculated slice indices
        target_dataset.lons[dataset_slices["lon_start"]: 
                            dataset_slices["lon_end"] + 1],
        # Slice the times array with our calculated slice indices
        target_dataset.times[dataset_slices["time_start"]: 
                            dataset_slices["time_end"]+ 1],
        # Slice the values array with our calculated slice indices
        target_dataset.values[
            dataset_slices["time_start"]:dataset_slices["time_end"] + 1,
            dataset_slices["lat_start"]:dataset_slices["lat_end"] + 1,
            dataset_slices["lon_start"]:dataset_slices["lon_end"] + 1],
        target_dataset.variable,
        target_dataset.units,
        target_dataset.name
    )

def safe_subset(subregion, target_dataset):
    '''Safely subset given dataset with subregion information

    A standard subset requires that the provided subregion be entirely contained
    within the datasets bounds. `safe_subset` returns the overlap of the
    subregion and dataset without returning an error.

    :param subregion: The Bounds with which to subset the target Dataset.
    :type subregion: :class:`dataset.Bounds`

    :param target_dataset: The Dataset object to subset.
    :type target_dataset: :class:`dataset.Dataset`

    :returns: The subset-ed Dataset object
    :rtype: :class:`dataset.Dataset`
    '''

    lat_min, lat_max, lon_min, lon_max = target_dataset.spatial_boundaries()
    start, end = target_dataset.time_range()

    if subregion.lat_min < lat_min:
        subregion.lat_min = lat_min

    if subregion.lat_max > lat_max:
        subregion.lat_max = lat_max

    if subregion.lon_min < lon_min:
        subregion.lon_min = lon_min

    if subregion.lon_max > lon_max:
        subregion.lon_max = lon_max

    if subregion.start < start:
        subregion.start = start

    if subregion.end > end:
        subregion.end = end

    return subset(subregion, target_dataset)

def normalize_dataset_datetimes(dataset, timestep):
    ''' Normalize Dataset datetime values.

    Force daily to an hour time value of 00:00:00.
    Force monthly data to the first of the month at midnight.

    :param dataset: The Dataset which will have its time value normalized.
    :type dataset: :class:`dataset.Dataset`

    :param timestep: The timestep of the Dataset's values. Either 'daily' or
        'monthly'.
    :type timestep: :mod:`string`

    :returns: A new Dataset with normalized datetime values.
    :rtype: :class:`dataset.Dataset`
    '''
    new_times = _rcmes_normalize_datetimes(dataset.times, timestep)
    return ds.Dataset(
        dataset.lats,
        dataset.lons,
        np.array(new_times),
        dataset.values,
        dataset.variable,
        dataset.units,
        dataset.name
    )

def write_netcdf(dataset, path, compress=True):
    ''' Write a dataset to a NetCDF file.

    :param dataset: The dataset to write.
    :type dataset: :class:`dataset.Dataset`

    :param path: The output file path.
    :type path: :mod:`string`
    '''
    out_file = netCDF4.Dataset(path, 'w', format='NETCDF4')

    # Set attribute lenghts
    lat_len = len(dataset.lats)
    lon_len = len(dataset.lons)
    time_len = len(dataset.times)

    # Create attribute dimensions
    lat_dim = out_file.createDimension('lat', lat_len)
    lon_dim = out_file.createDimension('lon', lon_len)
    time_dim = out_file.createDimension('time', time_len)

    # Create variables
    lats = out_file.createVariable('lat', 'f8', ('lat',), zlib=compress)
    lons = out_file.createVariable('lon', 'f8', ('lon',), zlib=compress)
    times = out_file.createVariable('time', 'f8', ('time',), zlib=compress)

    var_name = dataset.variable if dataset.variable else 'var'
    values = out_file.createVariable(var_name,
                                    'f8',
                                    ('time', 'lat', 'lon'),
                                    zlib=compress)

    # Set the time variable units
    # We don't deal with hourly/minutely/anything-less-than-a-day data so
    # we can safely stick with a 'days since' offset here. Note that the
    # NetCDF4 helper date2num doesn't support 'months' or 'years' instead
    # of days.
    times.units = "days since %s" % dataset.times[0]

    # Store the dataset's values
    lats[:] = dataset.lats
    lons[:] = dataset.lons
    times[:] = netCDF4.date2num(dataset.times, times.units)
    values[:] = dataset.values

    out_file.close()

def unit_conversion(dataset):
    ''' convert the units of model water flux variables (precipitation, evaporation, runoff) into "mm/day" as necessary
        refactored from do_data_prep.py

    :param dataset: The dataset to convert.
    :type dataset: :class:`dataset.Dataset`

    returns: dataset with new units
    rtype(:class::`dataset.Dataset`)

    '''
    if ('pr' in dataset.variable) or ('precip' in dataset.variable) or ('evspsbl' in dataset.variable) or ('mrro' in dataset.variable)or ('mrros'in dataset.variable):
        if ('KG M-2 S-1' in dataset.units) or ('kg m-2 s-1' in dataset.units) or ('MM S-1' in dataset.units) or ('mm s-1' in dataset.units) or ('mm/sec' in dataset.units):
            dataset.values = 86400. * dataset.values
            dataset.units = 'mm/day'
        else:
            pass
    elif ('SWE' in dataset.variable) or ('swe' in dataset.variable):
        if (dataset.units=='m') or (dataset.units=='M') or (dataset.units=='meter') or (dataset.units=='METER'):
            dataset.values = 1.e3 * dataset.values
            dataset.units = 'km'
        else:
            pass

    return dataset


def _rcmes_normalize_datetimes(datetimes, timestep):
    """ Normalize Dataset datetime values.

    Force daily to an hour time value of 00:00:00.
    Force monthly data to the first of the month at midnight.

    :param datetimes: The datetimes to normalize.
    :type datetimes: List of `datetime` values.

    :param timestep: The flag for how to normalize the datetimes.
    :type timestep: String
    """
    normalDatetimes = []
    if timestep.lower() == 'monthly':
        for inputDatetime in datetimes:
            if inputDatetime.day != 1:
                # Clean the inputDatetime
                inputDatetimeString = inputDatetime.strftime('%Y%m%d')
                normalInputDatetimeString = inputDatetimeString[:6] + '01'
                inputDatetime = datetime.datetime.strptime(normalInputDatetimeString, '%Y%m%d')

            normalDatetimes.append(inputDatetime)

    elif timestep.lower() == 'daily':
        for inputDatetime in datetimes:
            if inputDatetime.hour != 0 or inputDatetime.minute != 0 or inputDatetime.second != 0:
                datetimeString = inputDatetime.strftime('%Y%m%d%H%M%S')
                normalDatetimeString = datetimeString[:8] + '000000'
                inputDatetime = datetime.datetime.strptime(normalDatetimeString, '%Y%m%d%H%M%S')

            normalDatetimes.append(inputDatetime)


    return normalDatetimes

def _rcmes_spatial_regrid(spatial_values, lat, lon, lat2, lon2, order=1):
    '''
    Spatial regrid from one set of lat,lon values onto a new set (lat2,lon2)
    
    :param spatial_values: Values in a spatial grid that need to be regridded
    :type spatial_values: 2d masked numpy array.  shape (latitude, longitude)
    :param lat: Grid of latitude values which map to the spatial values
    :type lat: 2d numpy array. shape(latitudes, longitudes)
    :param lon: Grid of longitude values which map to the spatial values
    :type lon: 2d numpy array. shape(latitudes, longitudes)
    :param lat2: Grid of NEW latitude values to regrid the spatial_values onto
    :type lat2: 2d numpy array. shape(latitudes, longitudes)
    :param lon2: Grid of NEW longitude values to regrid the spatial_values onto
    :type lon2: 2d numpy array. shape(latitudes, longitudes)
    :param order: Interpolation order flag.  1=bi-linear, 3=cubic spline
    :type order: [optional] Integer

    :returns: 2d masked numpy array with shape(len(lat2), len(lon2))
    :rtype: (float, float) 
    '''

    nlat = spatial_values.shape[0]
    nlon = spatial_values.shape[1]
    #print nlat, nlon, "lats, lons - incoming dataset"

    nlat2 = lat2.shape[0]
    nlon2 = lon2.shape[1]
    #print nlat2, nlon2, "NEW lats, lons - for the new grid output"

    # To make our lives easier down the road, let's 
    # turn these into arrays of x & y coords
    loni = lon2.ravel()
    lati = lat2.ravel()

    loni = loni.copy() # NB. it won't run unless you do this...
    lati = lati.copy()

    # Now, we'll set points outside the boundaries to lie along an edge
    loni[loni > lon.max()] = lon.max()
    loni[loni < lon.min()] = lon.min()
    
    # To deal with the "hard" break, we'll have to treat y differently,
    # so we're just setting the min here...
    lati[lati > lat.max()] = lat.max()
    lati[lati < lat.min()] = lat.min()
    
    
    # We need to convert these to (float) indicies
    #   (xi should range from 0 to (nx - 1), etc)
    loni = (nlon - 1) * (loni - lon.min()) / (lon.max() - lon.min())
    
    # Deal with the "hard" break in the y-direction
    lati = (nlat - 1) * (lati - lat.min()) / (lat.max() - lat.min())
    
    """
    TODO: Review this docstring and see if it still holds true.  
    NOTE:  This function doesn't use MDI currently.  These are legacy comments
    
    Notes on dealing with MDI when regridding data.
     Method adopted here:
       Use bilinear interpolation of data by default (but user can specify other order using order=... in call)
       Perform bilinear interpolation of data, and of mask.
       To be conservative, new grid point which contained some missing data on the old grid is set to missing data.
               -this is achieved by looking for any non-zero interpolated mask values.
       To avoid issues with bilinear interpolation producing strong gradients leading into the MDI,
        set values at MDI points to mean data value so little gradient visible = not ideal, but acceptable for now.
    
    Set values in MDI so that similar to surroundings so don't produce large gradients when interpolating
    Preserve MDI mask, by only changing data part of masked array object.
    """
    for shift in (-1, 1):
        for axis in (0, 1):
            q_shifted = np.roll(spatial_values, shift=shift, axis=axis)
            idx = ~q_shifted.mask * spatial_values.mask
            spatial_values.data[idx] = q_shifted[idx]

    # Now we actually interpolate
    # map_coordinates does cubic interpolation by default, 
    # use "order=1" to preform bilinear interpolation instead...
    
    regridded_values = map_coordinates(spatial_values, [lati, loni], order=order)
    regridded_values = regridded_values.reshape([nlat2, nlon2])

    # Set values to missing data outside of original domain
    regridded_values = ma.masked_array(regridded_values, mask=np.logical_or(np.logical_or(lat2 >= lat.max(), 
                                                              lat2 <= lat.min()), 
                                                np.logical_or(lon2 <= lon.min(), 
                                                              lon2 >= lon.max())))
    
    # Make second map using nearest neighbour interpolation -use this to determine locations with MDI and mask these
    qmdi = np.zeros_like(spatial_values)
    qmdi[spatial_values.mask == True] = 1.
    qmdi[spatial_values.mask == False] = 0.
    qmdi_r = map_coordinates(qmdi, [lati, loni], order=order)
    qmdi_r = qmdi_r.reshape([nlat2, nlon2])
    mdimask = (qmdi_r != 0.0)
    
    # Combine missing data mask, with outside domain mask define above.
    regridded_values.mask = np.logical_or(mdimask, regridded_values.mask)

    return regridded_values

def _rcmes_create_mask_using_threshold(masked_array, threshold=0.5):
    '''Mask an array if percent of values missing data is above a threshold.

    For each value along an axis, if the proportion of steps that are missing
    data is above ``threshold`` then the value is marked as missing data.

    ..note:: The 0th axis is currently always used.

    :param masked_array: Masked array of data
    :type masked_array: Numpy Masked Array
    :param threshold: (optional) Threshold proportion above which a value is
        marked as missing data.
    :type threshold: Float

    :returns: A Numpy array describing the mask for masked_array.
    '''

    # try, except used as some model files don't have a full mask, but a single bool
    #  the except catches this situation and deals with it appropriately.
    try:
        nT = masked_array.mask.shape[0]

        # For each pixel, count how many times are masked.
        nMasked = masked_array.mask[:, :, :].sum(axis=0)

        # Define new mask as when a pixel has over a defined threshold ratio of masked data
        #   e.g. if the threshold is 75%, and there are 10 times,
        #        then a pixel will be masked if more than 5 times are masked.
        mymask = nMasked > (nT * threshold)

    except:
        mymask = np.zeros_like(masked_array.data[0, :, :])

    return mymask


def _rcmes_calc_average_on_new_time_unit_K(data, dates, unit):
    """ Rebin 3d array and list of dates using the provided unit parameter
    
    :param data: Input data that needs to be averaged 
    :type data: 3D masked numpy array of shape (times, lats, lons)
    :param dates: List of dates that correspond to the given data values
    :type dates: Python datetime objects
    :param unit: Time unit to average the data into
    :type unit: String matching one of these values : full | annual | monthly | daily
    
    :returns: meanstorem, newTimesList
    :rtype: 3D numpy masked array the same shape as the input array, list of python datetime objects
    """

    # Check if the user-selected temporal grid is valid. If not, EXIT
    acceptable = (unit=='full')|(unit=='annual')|(unit=='monthly')|(unit=='daily')
    if not acceptable:
        print 'Error: unknown unit type selected for time averaging: EXIT'
        return -1,-1,-1,-1

    # Calculate arrays of: annual timeseries: year (2007,2007),
    #                      monthly time series: year-month (200701,200702),
    #                      daily timeseries:  year-month-day (20070101,20070102) 
    #  depending on user-selected averaging period.

    # Year list
    if unit=='annual':
        timeunits = np.array([int(d.strftime("%Y")) for d in dates])
        unique_times = np.unique(timeunits)
         
    # YearMonth format list
    if unit=='monthly':
        timeunits = np.array([int(d.strftime("%Y%m")) for d in dates])
        unique_times = np.unique(timeunits)

    # YearMonthDay format list
    if unit=='daily':
        timeunits = np.array([int(d.strftime("%Y%m%d")) for d in dates])
        unique_times = np.unique(timeunits)


    # TODO: add pentad setting using Julian days?

    # Full list: a special case
    if unit == 'full':
        #  Calculating means data over the entire time range: i.e., annual-mean climatology
        timeunits = []
        for i in np.arange(len(dates)):
            timeunits.append(999)  # i.e. we just want the same value for all times.
        timeunits = np.array(timeunits, dtype=int)
        unique_times = np.unique(timeunits)

    # empty list to store new times
    newTimesList = []

    # Decide whether or not you need to do any time averaging.
    #   i.e. if data are already on required time unit then just pass data through and 
    #        calculate and return representative datetimes.
    processing_required = True
    if len(timeunits)==(len(unique_times)):
        processing_required = False

    # 1D data arrays, i.e. time series
    if data.ndim==1:
        # Create array to store the resulting data
        meanstore = np.zeros(len(unique_times))
  
        # Calculate the means across each unique time unit
        i=0
        for myunit in unique_times:
            if processing_required:
                datam=ma.masked_array(data,timeunits!=myunit)
                meanstore[i] = ma.average(datam)
            
            # construct new times list
            yyyy, mm, dd = _create_new_year_month_day(myunit, dates)
            newTimesList.append(datetime.datetime(yyyy,mm,dd,0,0,0,0))
            i = i+1

    # 3D data arrays
    if data.ndim==3:
        # Create array to store the resulting data
        meanstore = np.zeros([len(unique_times),data.shape[1],data.shape[2]])
  
        # Calculate the means across each unique time unit
        i=0
        datamask_store = []
        for myunit in unique_times:
            if processing_required:
                mask = np.zeros_like(data)
                mask[timeunits!=myunit,:,:] = 1.0
                # Calculate missing data mask within each time unit...
                datamask_at_this_timeunit = np.zeros_like(data)
                datamask_at_this_timeunit[:]= _rcmes_create_mask_using_threshold(data[timeunits==myunit,:,:],threshold=0.75)
                # Store results for masking later
                datamask_store.append(datamask_at_this_timeunit[0])
                # Calculate means for each pixel in this time unit, ignoring missing data (using masked array).
                datam = ma.masked_array(data,np.logical_or(mask,datamask_at_this_timeunit))
                meanstore[i,:,:] = ma.average(datam,axis=0)
            # construct new times list
            yyyy, mm, dd = _create_new_year_month_day(myunit, dates)
            newTimesList.append(datetime.datetime(yyyy,mm,dd))
            i += 1

        if not processing_required:
            meanstorem = data

        if processing_required:
            # Create masked array (using missing data mask defined above)
            datamask_store = np.array(datamask_store)
            meanstorem = ma.masked_array(meanstore, datamask_store)

    return meanstorem, newTimesList

def _create_new_year_month_day(time_unit, dates):
    smyunit = str(time_unit)
    if len(smyunit)==4:  # YYYY
        yyyy = int(smyunit[0:4])
        mm = 1
        dd = 1
    elif len(smyunit)==6:  # YYYYMM
        yyyy = int(smyunit[0:4])
        mm = int(smyunit[4:6])
        dd = 1
    elif len(smyunit)==8:  # YYYYMMDD
        yyyy = int(smyunit[0:4])
        mm = int(smyunit[4:6])
        dd = int(smyunit[6:8])
    elif len(smyunit)==3:  # Full time range
        # Need to set an appropriate time representing the mid-point of the entire time span
        dt = dates[-1]-dates[0]
        halfway = dates[0]+(dt/2)
        yyyy = int(halfway.year)
        mm = int(halfway.month)
        dd = int(halfway.day)
    
    return (yyyy, mm, dd)

def _congrid(a, newdims, method='linear', centre=False, minusone=False):
    '''
    This function is from http://wiki.scipy.org/Cookbook/Rebinning - Example 3
    It has been refactored and changed a bit, but the original functionality
    has been preserved.
    
    Arbitrary resampling of source array to new dimension sizes.
    Currently only supports maintaining the same number of dimensions.
    To use 1-D arrays, first promote them to shape (x,1).
    
    Uses the same parameters and creates the same co-ordinate lookup points
    as IDL''s congrid routine, which apparently originally came from a VAX/VMS
    routine of the same name.

    method:
    neighbour - closest value from original data
    nearest and linear - uses n x 1-D interpolations using
                         scipy.interpolate.interp1d
    (see Numerical Recipes for validity of use of n 1-D interpolations)
    spline - uses ndimage.map_coordinates

    centre:
    True - interpolation points are at the centres of the bins
    False - points are at the front edge of the bin

    minusone:
    For example- inarray.shape = (i,j) & new dimensions = (x,y)
    False - inarray is resampled by factors of (i/x) * (j/y)
    True - inarray is resampled by(i-1)/(x-1) * (j-1)/(y-1)
    This prevents extrapolation one element beyond bounds of input array.
    '''
    if not a.dtype in [np.float64, np.float32]:
        a = np.cast[float](a)

    # this will merely take the True/False input and convert it to an array(1) or array(0)
    m1 = np.cast[int](minusone)
    # this also casts the True False input into a floating point number of 0.5 or 0.0
    ofs = np.cast[int](centre) * 0.5

    old = np.array( a.shape )
    ndims = len( a.shape )
    if len( newdims ) != ndims:
        print "[congrid] dimensions error. " \
              "This routine currently only supports " \
              "rebinning to the same number of dimensions."
        return None
    newdims = np.asarray( newdims, dtype=float )
    dimlist = []

    if method == 'neighbour':
        newa = _congrid_neighbor(a, newdims, m1, ofs)

    elif method in ['nearest','linear']:
        # calculate new dims
        for i in range( ndims ):
            base = np.arange( newdims[i] )
            dimlist.append( (old[i] - m1) / (newdims[i] - m1) \
                            * (base + ofs) - ofs )
        # specify old dims
        olddims = [np.arange(i, dtype = np.float) for i in list( a.shape )]

        # first interpolation - for ndims = any
        mint = scipy.interpolate.interp1d( olddims[-1], a, kind=method )
        newa = mint( dimlist[-1] )

        trorder = [ndims - 1] + range( ndims - 1 )
        for i in range( ndims - 2, -1, -1 ):
            newa = newa.transpose( trorder )

            mint = scipy.interpolate.interp1d( olddims[i], newa, kind=method )
            newa = mint( dimlist[i] )

        if ndims > 1:
            # need one more transpose to return to original dimensions
            newa = newa.transpose( trorder )

        return newa
    elif method in ['spline']:
        oslices = [ slice(0, j) for j in old ]
        oldcoords = np.ogrid[oslices]
        nslices = [ slice(0, j) for j in list(newdims) ]
        newcoords = np.mgrid[nslices]

        newcoords_dims = range(np.rank(newcoords))
        #make first index last
        newcoords_dims.append(newcoords_dims.pop(0))
        newcoords_tr = newcoords.transpose(newcoords_dims)
        # makes a view that affects newcoords

        newcoords_tr += ofs

        deltas = (np.asarray(old) - m1) / (newdims - m1)
        newcoords_tr *= deltas

        newcoords_tr -= ofs

        newa = scipy.ndimage.map_coordinates(a, newcoords)
        return newa
    else:
        print "Congrid error: Unrecognized interpolation type.\n", \
              "Currently only \'neighbour\', \'nearest\',\'linear\',", \
              "and \'spline\' are supported."
        return None

def _check_dataset_shapes(datasets):
    """ If the  datasets are not the same shape throw a ValueError Exception
    
    :param datasets: OCW Datasets to check for a consistent shape
    :type datasets: List of OCW Dataset Objects
    
    :raises: ValueError
    """
    dataset_shape = None
    for dataset in datasets:
        if dataset_shape == None:
            dataset_shape = dataset.values.shape
        else:
            if dataset.values.shape != dataset_shape:
                msg = "%s != %s" % (dataset.values.shape, dataset_shape)
                raise ValueError("Input datasets must be the same shape for an ensemble :: ", msg)
            else:
                pass


def _congrid_neighbor(values, new_dims, minus_one, offset):
    """ Use the nearest neighbor to create a new array
    
    :param values: Array of values that need to be interpolated
    :type values: Numpy ndarray
    :param new_dims: Longitude resolution in degrees
    :type new_dims: float
    :param lat_resolution: Latitude resolution in degrees
    :type lat_resolution: float
    
    :returns: A new spatially regridded Dataset
    :rtype: Open Climate Workbench Dataset Object
    """
    ndims = len( values.shape )
    dimlist = []
    old_dims = np.array( values.shape )
    for i in range( ndims ):
        base = np.indices(new_dims)[i]
        dimlist.append( (old_dims[i] - minus_one) / (new_dims[i] - minus_one) \
                        * (base + offset) - offset )
    cd = np.array( dimlist ).round().astype(int)
    new_values = values[list( cd )]
    return new_values    

def _are_bounds_contained_by_dataset(bounds, dataset):
    '''Check if a Dataset fully contains a bounds.

    :param bounds: The Bounds object to check.
    :type bounds: Bounds
    :param dataset: The Dataset that should be fully contain the 
        Bounds
    :type dataset: Dataset

    :returns: True if the Bounds are contained by the Dataset, Raises
        a ValueError otherwise
    '''
    lat_min, lat_max, lon_min, lon_max = dataset.spatial_boundaries()
    start, end = dataset.time_range()
    errors = []

    # TODO:  THIS IS TERRIBLY inefficent and we need to use a geometry lib instead in the future
    if not lat_min <= bounds.lat_min <= lat_max:
        error = "bounds.lat_min: %s is not between lat_min: %s and lat_max: %s" % (bounds.lat_min, lat_min, lat_max)
        errors.append(error)

    if not lat_min <= bounds.lat_max <= lat_max:
        error = "bounds.lat_max: %s is not between lat_min: %s and lat_max: %s" % (bounds.lat_max, lat_min, lat_max)
        errors.append(error)

    if not lon_min <= bounds.lon_min <= lon_max:
        error = "bounds.lon_min: %s is not between lon_min: %s and lon_max: %s" % (bounds.lon_min, lon_min, lon_max)
        errors.append(error)

    if not lon_min <= bounds.lon_max <= lon_max:
        error = "bounds.lon_max: %s is not between lon_min: %s and lon_max: %s" % (bounds.lon_max, lon_min, lon_max)
        errors.append(error)

    if not start <= bounds.start <= end:
        error = "bounds.start: %s is not between start: %s and end: %s" % (bounds.start, start, end)
        errors.append(error)

    if not start <= bounds.end <= end:
        error = "bounds.end: %s is not between start: %s and end: %s" % (bounds.end, start, end)
        errors.append(error)

    if len(errors) == 0:
        return True
    else:
        error_message = '\n'.join(errors)
        raise ValueError(error_message)

def _get_subregion_slice_indices(subregion, target_dataset):
    '''Get the indices for slicing Dataset values to generate the subregion.

    :param subregion: The Bounds that specify the subset of the Dataset 
        that should be extracted.
    :type subregion: Bounds
    :param target_dataset: The Dataset to subset.
    :type target_dataset: Dataset

    :returns: The indices to slice the Datasets arrays as a Dictionary.
    '''
    latStart = min(np.nonzero(target_dataset.lats >= subregion.lat_min)[0])
    latEnd = max(np.nonzero(target_dataset.lats <= subregion.lat_max)[0])

    lonStart = min(np.nonzero(target_dataset.lons >= subregion.lon_min)[0])
    lonEnd = max(np.nonzero(target_dataset.lons <= subregion.lon_max)[0])


    timeStart = min(np.nonzero(target_dataset.times >= subregion.start)[0])
    timeEnd = max(np.nonzero(target_dataset.times <= subregion.end)[0])

    return {
        "lat_start"  : latStart,
        "lat_end"    : latEnd,
        "lon_start"  : lonStart,
        "lon_end"    : lonEnd,
        "time_start" : timeStart,
        "time_end"   : timeEnd
    }

