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
from scipy.stats import rankdata
from scipy.ndimage import map_coordinates
import netCDF4
from matplotlib.path import Path

import logging

logger = logging.getLogger(__name__)

def temporal_subset(month_start, month_end, target_dataset, average_each_year=False):
    """ Temporally subset data given month_index.

    :param month_start: An integer for beginning month (Jan=1)
    :type month_start: :class:`int`

    :param month_end: An integer for ending month (Jan=1)
    :type month_end: :class:`int`

    :param target_dataset: Dataset object that needs temporal subsetting
    :type target_dataset: Open Climate Workbench Dataset Object

    :param average_each_year: If True, output dataset is averaged for each year
    :type average_each_year: :class:'boolean'

    :returns: A temporal subset OCW Dataset
    :rtype: Open Climate Workbench Dataset Object
    """

    if month_start > month_end:
        month_index = range(month_start,13)
        month_index.extend(range(1, month_end+1))
    else:
        month_index = range(month_start, month_end+1)

    dates = target_dataset.times
    months = np.array([d.month for d in dates])
    time_index = []
    for m_value in month_index:
        time_index = np.append(time_index, np.where(months == m_value)[0])
        if m_value == month_index[0]:
            time_index_first = np.min(np.where(months == m_value)[0])
        if m_value == month_index[-1]:
            time_index_last = np.max(np.where(months == m_value)[0])

    time_index = np.sort(time_index)

    time_index = time_index[np.where((time_index >= time_index_first) & (time_index <= time_index_last))]

    time_index = list(time_index)

    new_dataset = ds.Dataset(target_dataset.lats,
                             target_dataset.lons,
                             target_dataset.times[time_index],
                             target_dataset.values[time_index,:],
                             variable=target_dataset.variable,
                             units=target_dataset.units,
                             name=target_dataset.name)

    if average_each_year:
        nmonth = len(month_index)
        ntime  = new_dataset.times.size
        nyear = ntime/nmonth
        averaged_time = []              
        ny, nx = target_dataset.values.shape[1:]
        averaged_values =ma.zeros([nyear, ny, nx])
        for iyear in np.arange(nyear):
            # centered time index of the season between month_start and month_end in each year
            center_index = int(nmonth/2)+iyear*nmonth   
            if nmonth == 1:
                center_index = iyear
            averaged_time.append(new_dataset.times[center_index]) 
            averaged_values[iyear,:] = ma.average(new_dataset.values[nmonth*iyear:nmonth*iyear+nmonth,:], axis=0)
        new_dataset = ds.Dataset(target_dataset.lats,
                                 target_dataset.lons,
                                 np.array(averaged_time),
                                 averaged_values,
                                 variable=target_dataset.variable,
                                 units=target_dataset.units,
                                 name=target_dataset.name)
    
    return new_dataset

def temporal_rebin(target_dataset, temporal_resolution):     
    """ Rebin a Dataset to a new temporal resolution
    
    :param target_dataset: Dataset object that needs temporal rebinned
    :type target_dataset: :class:`dataset.Dataset`

    :param temporal_resolution: The new temporal resolution
    :type temporal_resolution: :mod:`string`               
    
    :returns: A new temporally rebinned Dataset
    :rtype: :class:`dataset.Dataset`
    """
    # Decode the temporal resolution into a string format that 
    # _rcmes_calc_average_on_new_time_unit_K() can understand

    binned_values, binned_dates = _rcmes_calc_average_on_new_time_unit(target_dataset.values, target_dataset.times, temporal_resolution)
    binned_dates = np.array(binned_dates)
    new_dataset = ds.Dataset(target_dataset.lats, 
                             target_dataset.lons, 
                             binned_dates, 
                             binned_values,
                             variable=target_dataset.variable,
                             units=target_dataset.units,
                             name=target_dataset.name,
                             origin=target_dataset.origin)
    
    return new_dataset

def temporal_rebin_with_time_index(target_dataset, nt_average):
    """ Rebin a Dataset to a new temporal resolution

    :param target_dataset: Dataset object that needs temporal rebinned
    :type target_dataset: :class:`dataset.Dataset`

    :param nt_average: Time resolution for the output datasets. 
     It is the same as the number of time indicies to be averaged. (length of time dimension in the rebinned dataset) = (original time dimension length/nt_average)
    :type temporal_resolution: integer

    :returns: A new temporally rebinned Dataset
    :rtype: :class:`dataset.Dataset`
    """
    nt = target_dataset.times.size
    if nt % nt_average !=0:
        print 'Warning: length of time dimension must be a multiple of nt_average'
    # nt2 is the length of time dimension in the rebinned dataset
    nt2 = nt/nt_average
    binned_dates = target_dataset.times[np.arange(nt2)*nt_average]
    binned_values = ma.zeros(np.insert(target_dataset.values.shape[1:],0,nt2))
    for it in np.arange(nt2):
        binned_values[it,:] = ma.average(target_dataset.values[nt_average*it:nt_average*it+nt_average,:], axis=0)
    new_dataset = ds.Dataset(target_dataset.lats,
                             target_dataset.lons,
                             binned_dates,
                             binned_values,
                             variable=target_dataset.variable,
                             units=target_dataset.units,
                             name=target_dataset.name,
                             origin=target_dataset.origin)
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
    
    # Create grids of the given lats and lons for the underlying API
    # NOTE: np.meshgrid() requires inputs (x, y) and returns data
    #       of shape(y|lat|rows, x|lon|columns).  So we pass in lons, lats
    #       and get back data.shape(lats, lons)
    if target_dataset.lons.ndim ==1 and target_dataset.lats.ndim ==1:
        regular_grid = True
        lons, lats = np.meshgrid(target_dataset.lons, target_dataset.lats)
    else:
        regular_grid = False
        lons = target_dataset.lons
        lats = target_dataset.lats
    if new_longitudes.ndim ==1 and new_latitudes.ndim ==1:
        new_lons, new_lats = np.meshgrid(new_longitudes, new_latitudes)
    else:
        new_lons = new_longitudes
        new_lats = new_latitudes

    ny_old, nx_old = lats.shape
    ny_new, nx_new = new_lats.shape

    # Make masked array of shape (times, new_latitudes,new_longitudes)
    new_values = ma.zeros([len(target_dataset.times), 
                           ny_new, nx_new]) 
    # Make masked array of shape (times, new_latitudes,new_longitudes)
    new_values = ma.zeros([len(target_dataset.times), 
                           ny_new, nx_new])

    # Boundary vertices of target_dataset
    vertices = []

    if regular_grid: 
        vertices.append([lons[0,0], lats[0,0]])
        vertices.append([lons[-1,0], lats[-1,0]])
        vertices.append([lons[-1,-1], lats[-1,-1]])
        vertices.append([lons[0,-1], lats[0,-1]])
    else: 
        for iy in np.arange(ny_old):   # from south to north along the west boundary
            vertices.append([lons[iy,0], lats[iy,0]]) 
        for ix in np.arange(nx_old):   # from west to east along the north boundary
            vertices.append([lons[-1, ix], lats[-1, ix]])
        for iy in np.arange(ny_old)[::-1]:   # from north to south along the east boundary
            vertices.append([lons[iy, -1], lats[iy, -1]])
        for ix in np.arange(nx_old)[::-1]:   # from east to west along the south boundary
            vertices.append([lons[0, ix], lats[0, ix]])
    path = Path(vertices)

    # Convert new_lats and new_lons to float indices
    new_lons_indices = np.zeros(new_lons.shape)
    new_lats_indices = np.zeros(new_lats.shape)
  
    for iy in np.arange(ny_new):
        for ix in np.arange(nx_new):
            if path.contains_point([new_lons[iy,ix], new_lats[iy,ix]]): 
                if regular_grid:
                    new_lats_indices[iy,ix] = (ny_old -1.)*(new_lats[iy,ix] - lats.min())/(lats.max() - lats.min())  
                    new_lons_indices[iy,ix] = (nx_old -1.)*(new_lons[iy,ix] - lons.min())/(lons.max() - lons.min())  
                else:
                    distance_from_original_grids = ((lons - new_lons[iy,ix])**2.+(lats - new_lats[iy,ix])**2.)**0.5  
                    if np.min(distance_from_original_grids) == 0.:
                        new_lats_indices[iy,ix], new_lons_indices[iy,ix] = np.where(distance_from_original_grids ==0)
                    else:
                        distance_rank = rankdata(distance_from_original_grids.flatten(), method='ordinal').reshape(lats.shape)                
                        iy1, ix1 = np.where(distance_rank == 1) # the nearest grid point's indices 
                        iy2, ix2 = np.where(distance_rank == 4) # point [iy2, ix] is diagonally across from [iy1, ix1] 
                        dist1 = distance_from_original_grids[iy1,ix1]
                        dist2 = distance_from_original_grids[iy2,ix2]
                        new_lats_indices[iy,ix] = (dist1*iy2 + dist2*iy1)/(dist1+dist2) 
                        new_lons_indices[iy,ix] = (dist1*ix2 + dist2*ix1)/(dist1+dist2) 
            else:
                new_lats_indices[iy,ix] = -999.    
                new_lats_indices[iy,ix] = -999.    
    new_lats_indices = ma.masked_less(new_lats_indices, 0.)
    new_lons_indices = ma.masked_less(new_lons_indices, 0.)
                      
    # Regrid the data on each time slice
    for i in range(len(target_dataset.times)):
        if len(target_dataset.times) == 1:
            values_original = ma.array(target_dataset.values)
        else: 
            values_original = ma.array(target_dataset.values[i])
        for shift in (-1, 1):
            for axis in (0, 1):
                q_shifted = np.roll(values_original, shift=shift, axis=axis)
                idx = ~q_shifted.mask * values_original.mask
                values_original.data[idx] = q_shifted[idx]
        new_values[i] = map_coordinates(values_original, [new_lats_indices.flatten(), new_lons_indices.flatten()], order=1).reshape(new_lats.shape) 
        new_values[i] = ma.array(new_values[i], mask=new_lats_indices.mask)
        # Make a masking map using nearest neighbour interpolation -use this to determine locations with MDI and mask these
        qmdi = np.zeros_like(values_original)
        qmdi[values_original.mask == True] = 1.
        qmdi[values_original.mask == False] = 0.
        qmdi_r = map_coordinates(qmdi, [new_lats_indices.flatten(), new_lons_indices.flatten()], order=1).reshape(new_lats.shape)
        mdimask = (qmdi_r != 0.0)

        # Combine missing data mask, with outside domain mask define above.
        new_values[i].mask = np.logical_or(mdimask, new_values[i].mask)

    
    # TODO: 
    # This will call down to the _congrid() function and the lat and lon 
    # axis will be adjusted with the time axis being held constant
    
    # Create a new Dataset Object to return using new data
    regridded_dataset = ds.Dataset(new_latitudes, 
                                   new_longitudes, 
                                   target_dataset.times, 
                                   new_values,
                                   variable=target_dataset.variable,
                                   units=target_dataset.units,
                                   name=target_dataset.name,
                                   origin=target_dataset.origin)
    return regridded_dataset

def ensemble(datasets):
    """
    Generate a single dataset which is the mean of the input datasets

    An ensemble datasets combines input datasets assuming the all have
    similar shape, dimensions, and units. 
    
    :param datasets: Datasets to be used to compose the ensemble dataset from.
        All Datasets must be the same shape.
    :type datasets: :class:`list` of :class:`dataset.Dataset`
    
    :returns: New Dataset with a name of 'Dataset Ensemble'
    :rtype: :class:`dataset.Dataset`
    """
    _check_dataset_shapes(datasets)
    dataset_values = [dataset.values for dataset in datasets]
    ensemble_values = ma.mean(dataset_values, axis=0)
    
    # Build new dataset object from the input datasets and the ensemble values and return it
    ensemble_dataset = ds.Dataset(datasets[0].lats, 
                                  datasets[0].lons, 
                                  datasets[0].times,
                                  ensemble_values,
                                  units=datasets[0].units,
                                  name="Dataset Ensemble")
    
    return ensemble_dataset

def subset(subregion, target_dataset, subregion_name=None):
    '''Subset given dataset(s) with subregion information

    :param subregion: The Bounds with which to subset the target Dataset. 
    :type subregion: :class:`dataset.Bounds`

    :param target_dataset: The Dataset object to subset.
    :type target_dataset: :class:`dataset.Dataset`

    :param subregion_name: The subset-ed Dataset name
    :type subregion_name: :mod:`string`

    :returns: The subset-ed Dataset object
    :rtype: :class:`dataset.Dataset`

    :raises: ValueError
    '''

    if not subregion.start:
        subregion.start = target_dataset.times[0] 
        subregion.end = target_dataset.times[-1]
        
    # Ensure that the subregion information is well formed
    _are_bounds_contained_by_dataset(subregion, target_dataset)

    if not subregion_name:
        subregion_name = target_dataset.name

    if target_dataset.lats.ndim ==2 and target_dataset.lons.ndim ==2:
        target_dataset = temporal_slice(subregion.start, subregion.end, target_dataset)
        nt, ny, nx = target_dataset.values.shape
        y_index, x_index = np.where((target_dataset.lats >= subregion.lat_max) | (target_dataset.lats <= subregion.lat_min) |
                         (target_dataset.lons >= subregion.lon_max) | (target_dataset.lons <= subregion.lon_min)) 
        for it in np.arange(nt):
            target_dataset.values[it,y_index, x_index] = 1.e+20
        target_dataset.values = ma.masked_equal(target_dataset.values, 1.e+20)
        return target_dataset

    elif target_dataset.lats.ndim ==1 and target_dataset.lons.ndim ==1:
        # Get subregion indices into subregion data
        dataset_slices = _get_subregion_slice_indices(subregion, target_dataset)
       # Slice the values array with our calculated slice indices
        if target_dataset.values.ndim == 2:
            subset_values = ma.zeros([len(target_dataset.values[
                dataset_slices["lat_start"]:dataset_slices["lat_end"]]), 
                len(target_dataset.values[
                    dataset_slices["lon_start"]:dataset_slices["lon_end"]])])

            subset_values = target_dataset.values[
                dataset_slices["lat_start"]:dataset_slices["lat_end"] + 1,
                dataset_slices["lon_start"]:dataset_slices["lon_end"] + 1]

        elif target_dataset.values.ndim == 3:
            subset_values = ma.zeros([len(target_dataset.values[
                dataset_slices["time_start"]:dataset_slices["time_end"]]),
                len(target_dataset.values[
                dataset_slices["lat_start"]:dataset_slices["lat_end"]]), 
                len(target_dataset.values[
                dataset_slices["lon_start"]:dataset_slices["lon_end"]])])
        
            subset_values = target_dataset.values[
                dataset_slices["time_start"]:dataset_slices["time_end"] + 1,
                dataset_slices["lat_start"]:dataset_slices["lat_end"] + 1,
                dataset_slices["lon_start"]:dataset_slices["lon_end"] + 1]
            
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
            subset_values,
            variable=target_dataset.variable,
            units=target_dataset.units,
            name=subregion_name,
            origin=target_dataset.origin
        )

def temporal_slice(start_time_index, end_time_index, target_dataset):
    '''Temporally slice given dataset(s) with subregion information. This does not
    spatially subset the target_Dataset

    :param start_time_index: time index of the start time
    :type start_time_index: :class:'int'

    :param end_time_index: time index of the end time
    :type end_time_index: :class:'int'

    :param target_dataset: The Dataset object to subset.
    :type target_dataset: :class:`dataset.Dataset`

    :returns: The subset-ed Dataset object
    :rtype: :class:`dataset.Dataset`

    :raises: ValueError
    '''

    timeStart = min(np.nonzero(target_dataset.times >= start_time_index)[0])
    timeEnd = max(np.nonzero(target_dataset.times <= end_time_index)[0])
    target_dataset.times = target_dataset.times[timeStart:timeEnd+1]
    target_dataset.values = target_dataset.values[timeStart:timeEnd+1,:]

    return target_dataset

def safe_subset(subregion, target_dataset, subregion_name=None):
    '''Safely subset given dataset with subregion information

    A standard subset requires that the provided subregion be entirely contained
    within the datasets bounds. `safe_subset` returns the overlap of the
    subregion and dataset without returning an error.

    :param subregion: The Bounds with which to subset the target Dataset.
    :type subregion: :class:`dataset.Bounds`

    :param target_dataset: The Dataset object to subset.
    :type target_dataset: :class:`dataset.Dataset`

    :param subregion_name: The subset-ed Dataset name
    :type subregion_name: :mod:`string`

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

    if subregion.start: 
        if subregion.start < start:
            subregion.start = start

    if subregion.end:
        if subregion.end > end:
            subregion.end = end

    return subset(subregion, target_dataset, subregion_name)

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
        variable=dataset.variable,
        units=dataset.units,
        name=dataset.name,
        origin=dataset.origin
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
    values.units = dataset.units

    out_file.close()

def write_netcdf_multiple_datasets_with_subregions(ref_dataset, ref_name, 
                                                   model_dataset_array, model_names,
                                                   path,
                                                   subregions = None, subregion_array = None,
                                                   ref_subregion_mean = None, ref_subregion_std = None, 
                                                   model_subregion_mean = None, model_subregion_std = None):
    #Write multiple reference and model datasets and their subregional means and standard deivations in a NetCDF file.

    #:To be updated 
    #
    out_file = netCDF4.Dataset(path, 'w', format='NETCDF4')

    dataset = ref_dataset
    # Set attribute lenghts
    nobs = 1
    nmodel = len(model_dataset_array)
    lat_len, lon_len = dataset.values.shape[1:]
    lat_ndim = dataset.lats.ndim
    lon_ndim = dataset.lons.ndim
    time_len = len(dataset.times)

    if not subregions == None:
        nsubregion = len(subregions)
                 
    # Create attribute dimensions
    lat_dim = out_file.createDimension('y', lat_len)
    lon_dim = out_file.createDimension('x', lon_len)
    time_dim = out_file.createDimension('time', time_len)

    # Create variables and store the values
    if lat_ndim ==2:
        lats = out_file.createVariable('lat', 'f8', ('y','x'))
    else:
        lats = out_file.createVariable('lat', 'f8', ('y'))
    lats[:] = dataset.lats
    if lon_ndim ==2:
        lons = out_file.createVariable('lon', 'f8', ('y','x'))
    else:
        lons = out_file.createVariable('lon', 'f8', ('x'))
    lons[:] = dataset.lons
    times = out_file.createVariable('time', 'f8', ('time',))
    times.units = "days since %s" % dataset.times[0]
    times[:] = netCDF4.date2num(dataset.times, times.units)

    #mask_array = np.zeros([time_len, lat_len, lon_len])
    #for iobs in np.arange(nobs):
    #    index = np.where(ref_dataset_array[iobs].values.mask[:] == True)
    #    mask_array[index] = 1
    out_file.createVariable(ref_name, 'f8', ('time','y','x'))
    out_file.variables[ref_name][:] = ref_dataset.values
    out_file.variables[ref_name].units = ref_dataset.units
    for imodel in np.arange(nmodel):
        out_file.createVariable(model_names[imodel], 'f8', ('time','y','x'))
        #out_file.variables[model_names[imodel]][:] = ma.array(model_dataset_array[imodel].values, mask = mask_array)
        out_file.variables[model_names[imodel]][:] = model_dataset_array[imodel].values
        out_file.variables[model_names[imodel]].units = model_dataset_array[imodel].units

    if not subregions == None:
        out_file.createVariable('subregion_array', 'i4', ('y','x'))
        out_file.variables['subregion_array'][:] = subregion_array[:]
        nsubregion = len(subregions)
        out_file.createDimension('nsubregion', nsubregion)
        out_file.createDimension('nobs', nobs)
        out_file.createDimension('nmodel', nmodel)
        out_file.createVariable('obs_subregion_mean', 'f8', ('nobs','time','nsubregion'))
        out_file.variables['obs_subregion_mean'][:] = ref_subregion_mean[:]
        out_file.createVariable('obs_subregion_std', 'f8', ('nobs','time','nsubregion'))
        out_file.variables['obs_subregion_std'][:] = ref_subregion_std[:]
        out_file.createVariable('model_subregion_mean', 'f8', ('nmodel','time','nsubregion'))
        out_file.variables['model_subregion_mean'][:] = model_subregion_mean[:]
        out_file.createVariable('model_subregion_std', 'f8', ('nmodel','time','nsubregion'))
        out_file.variables['model_subregion_std'][:] = model_subregion_std[:]

    out_file.close()

def water_flux_unit_conversion(dataset):
    ''' Convert water flux variables units as necessary

    Convert full SI units water flux units to more common units.

    :param dataset: The dataset to convert.
    :type dataset: :class:`dataset.Dataset`

    :returns: A Dataset with values converted to new units.
    :rtype: :class:`dataset.Dataset`
    '''
    water_flux_variables = ['pr', 'prec','evspsbl', 'mrro', 'swe']
    variable = dataset.variable.lower()

    if any(sub_string in variable for sub_string in water_flux_variables):
        dataset_units = dataset.units.lower()
        if variable in 'swe':
            if any(unit in dataset_units for unit in ['m', 'meter']):
                dataset.values = 1.e3 * dataset.values
                dataset.units = 'km'
        else:
            if any(unit in dataset_units 
                for unit in ['kg m-2 s-1', 'mm s-1', 'mm/sec']):
                dataset.values = 86400. * dataset.values
                dataset.units = 'mm/day'

    return dataset

def temperature_unit_conversion(dataset):
    ''' Convert temperature units as necessary

    Automatically convert Celcius to Kelvin in the given dataset.

    :param dataset: The dataset for which units should be updated.
    :type dataset; :class:`dataset.Dataset`

    :returns: The dataset with (potentially) updated units.
    :rtype: :class:`dataset.Dataset`
    '''
    temperature_variables = ['temp','tas','tasmax','taxmin','T','tg']
    variable = dataset.variable.lower()

    if any(sub_string in variable for sub_string in temperature_variables):
        dataset_units = dataset.units.lower()
        if dataset_units == 'c' or dataset_units == 'celsius':
            dataset.values = 273.15 + dataset.values
            dataset.units = 'K'

    return dataset

def variable_unit_conversion(dataset):
    ''' Convert water flux or temperature variables units as necessary
    
    For water flux variables, convert full SI units water flux units to more common units.
    For temperature, convert Celcius to Kelvin.

    :param dataset: The dataset to convert.
    :type dataset: :class:`dataset.Dataset`

    :returns: A Dataset with values converted to new units.
    :rtype: :class:`dataset.Dataset`
    '''

    dataset = water_flux_unit_conversion(dataset)
    dataset = temperature_unit_conversion(dataset)
    
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

def mask_missing_data(dataset_array):
    ''' Check missing values in observation and model datasets.
    If any of dataset in dataset_array has missing values at a grid point,
    the values at the grid point in all other datasets are masked.
    :param dataset_array: an array of OCW datasets
    '''
    mask_array = np.zeros(dataset_array[0].values.shape)
    for dataset in dataset_array:
        index = np.where(dataset.values.mask == True)
        if index[0].size >0:
            mask_array[index] = 1
    masked_array = []
    for dataset in dataset_array:
        dataset.values = ma.array(dataset.values, mask=mask_array)
        masked_array.append(dataset)
    return [masked_dataset for masked_dataset in masked_array]


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

def _rcmes_calc_average_on_new_time_unit(data, dates, unit):
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
        return -1,-1

    nt, ny, nx = data.shape
    if unit == 'full':
        new_data = ma.mean(data, axis=0)
        new_date = [dates[dates.size/2]]
    if unit == 'annual':
        years = [d.year for d in dates]
        years_sorted = np.unique(years)
        new_data = ma.zeros([years_sorted.size, ny, nx])
        it = 0
        new_date = []
        for year in years_sorted:
            index = np.where(years == year)[0]
            new_data[it,:] = ma.mean(data[index,:], axis=0)
            new_date.append(datetime.datetime(year=year, month=7, day=2))
            it = it+1
    if unit == 'monthly':
        years = [d.year for d in dates]
        years_sorted = np.unique(years)
        months = [d.month for d in dates]
        months_sorted = np.unique(months)
        
        new_data = ma.zeros([years_sorted.size*months_sorted.size, ny, nx])
        it = 0
        new_date = []
        for year in years_sorted:
            for month in months_sorted:
                index = np.where((years == year) & (months == month))[0]
                new_data[it,:] = ma.mean(data[index,:], axis=0)
                new_date.append(datetime.datetime(year=year, month=month, day=15))
                it = it+1   
    if unit == 'daily':
        days = [d.year*10000.+d.month*100.+d.day for d in dates] 
        days_sorted = np.unique(days)

        new_data = ma.zeros([days_sorted.size, ny, nx])
        it = 0
        new_date = []
        for day in days_sorted:
            index = np.where(days = day)[0]
            new_data[it,:] = ma.mean(data[index,:], axis=0)
            new_date.append(datetime.datetime(year=day/10000, month=(day % 10000)/100, day=day % 100))
            it = it+1
        
    return new_data, np.array(new_date)

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
        return -1,-1

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
    if not np.round(lat_min,3) <= np.round(bounds.lat_min,3) <= np.round(lat_max,3):
        error = "bounds.lat_min: %s is not between lat_min: %s and lat_max: %s" % (bounds.lat_min, lat_min, lat_max)
        errors.append(error)

    if not np.round(lat_min,3) <= np.round(bounds.lat_max,3) <= np.round(lat_max,3):
        error = "bounds.lat_max: %s is not between lat_min: %s and lat_max: %s" % (bounds.lat_max, lat_min, lat_max)
        errors.append(error)

    if not np.round(lon_min,3) <= np.round(bounds.lon_min,3) <= np.round(lon_max,3):
        error = "bounds.lon_min: %s is not between lon_min: %s and lon_max: %s" % (bounds.lon_min, lon_min, lon_max)
        errors.append(error)

    if not np.round(lon_min,3) <= np.round(bounds.lon_max,3) <= np.round(lon_max,3):
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

