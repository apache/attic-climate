# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

import calendar
from datetime import timedelta ,datetime
import re
import string

from ocw.dataset import Dataset
import ocw.utils as utils

import netCDF4
import numpy
import numpy.ma as ma
import glob

LAT_NAMES = ['x', 'rlat', 'rlats', 'lat', 'lats', 'latitude', 'latitudes']
LON_NAMES = ['y', 'rlon', 'rlons', 'lon', 'lons', 'longitude', 'longitudes']
TIME_NAMES = ['time', 'times', 'date', 'dates', 'julian']


def _get_netcdf_variable_name(valid_var_names, netcdf, netcdf_var):
    ''' Determine if one of a set of variable names are in a NetCDF Dataset. 

    Looks for an occurrence of a valid_var_name in the NetCDF variable data.
    This is useful for automatically determining the names of the lat, lon,
    and time variable names inside of a dataset object.

    :param valid_var_names: The possible variable names to search for in 
        the netCDF object.
    :type valid_var_names: List of Strings
    :param netcdf: The netCDF Dataset object in which to check for
        valid_var_names.
    :type netcdf: netcdf4.Dataset
    :param netcdf_var: The relevant variable name to search over in the 
        netcdf object. This is used to narrow down the search for valid
        variable names by first checking the desired variable's dimension
        values for one or more of the valid variable names.

    :returns: The variable from valid_var_names that it locates in 
        the netCDF object.

    :raises ValueError: When unable to locate a single matching variable
        name in the NetCDF Dataset from the supplied list of valid variable
        names.
    '''

    # Check for valid variable names in netCDF variable dimensions
    dimensions = netcdf.variables[netcdf_var].dimensions
    dims_lower = [dim.encode().lower() for dim in dimensions]

    intersect = set(valid_var_names).intersection(dims_lower)

    if len(intersect) == 1:
        # Retrieve the name of the dimension where we found the matching
        # variable name
        index = dims_lower.index(intersect.pop())
        dimension_name = dimensions[index].encode()

        # Locate all of the variables that share the dimension that we matched
        # earlier. If the dimension's name matches then that variable is
        # potentially what we want to return to the user.
        possible_vars = []
        for var in netcdf.variables.keys():
            var_dimensions = netcdf.variables[var].dimensions

            # Skip any dimensions are > 1D
            if len(var_dimensions) != 1:
                continue

            if var_dimensions[0].encode() == dimension_name:
                possible_vars.append(var)

        # If there are multiple variables with matching dimension names then we
        # aren't able to determining the correct variable name using the
        # variable dimensions. We need to try a different approach. Otherwise,
        # we're done!
        if len(possible_vars) == 1:
            return possible_vars[0]

    # Check for valid variable names in netCDF variable names
    variables = netcdf.variables.keys()
    vars_lower = [var.encode().lower() for var in variables]

    intersect = set(valid_var_names).intersection(vars_lower)

    if len(intersect) == 1:
        index = vars_lower.index(intersect.pop())
        return variables[index]

    # If we couldn't locate a single matching valid variable then we're unable
    # to automatically determine the variable names for the user.
    error = (
        "Unable to locate a single matching variable name from the "
        "supplied list of valid variable names. "
    )
    raise ValueError(error)

def load_file(file_path,
              variable_name,
              elevation_index=0,
              name='',
              lat_name=None,
              lon_name=None,
              time_name=None):
    ''' Load a NetCDF file into a Dataset.

    :param file_path: Path to the NetCDF file to load.
    :type file_path: :mod:`string`

    :param variable_name: The variable name to load from the NetCDF file.
    :type variable_name: :mod:`string`

    :param elevation_index: (Optional) The elevation index for which data should
        be returned. Climate data is often times 4 dimensional data. Some
        datasets will have readins at different height/elevation levels. OCW
        expects 3D data so a single layer needs to be stripped out when loading.
        By default, the first elevation layer is used. If desired you may
        specify the elevation value to use.
    :type elevation_index: :class:`int`

    :param name: (Optional) A name for the loaded dataset.
    :type name: :mod:`string`

    :param lat_name: (Optional) The latitude variable name to extract from the
        dataset.
    :type lat_name: :mod:`string`

    :param lon_name: (Optional) The longitude variable name to extract from the
        dataset.
    :type lon_name: :mod:`string`

    :param time_name: (Optional) The time variable name to extract from the
        dataset.
    :type time_name: :mod:`string`

    :returns: An OCW Dataset object with the requested variable's data from
        the NetCDF file.
    :rtype: :class:`dataset.Dataset`

    :raises ValueError: When the specified file path cannot be loaded by ndfCDF4
        or when the lat/lon/time variable name cannot be determined
        automatically.
    '''

    try:
        netcdf = netCDF4.Dataset(file_path, mode='r')
    except RuntimeError:
        err = "Dataset filepath is invalid. Please ensure it is correct."
        raise ValueError(err)
    except:
        err = (
            "The given file cannot be loaded. Please ensure that it is a valid "
            "NetCDF file. If problems persist, report them to the project's "
            "mailing list."
        )
        raise ValueError(err)

    if not lat_name:
        lat_name = _get_netcdf_variable_name(LAT_NAMES, netcdf, variable_name)
    if not lon_name:
        lon_name = _get_netcdf_variable_name(LON_NAMES, netcdf, variable_name)
    if not time_name:
        time_name = _get_netcdf_variable_name(TIME_NAMES, netcdf, variable_name)

    lats = netcdf.variables[lat_name][:]    
    lons = netcdf.variables[lon_name][:]
    time_raw_values = netcdf.variables[time_name][:]
    times = utils.decode_time_values(netcdf, time_name)
    times = numpy.array(times)
    values = ma.array(netcdf.variables[variable_name][:])

    # If the values are 4D then we need to strip out the elevation index
    if len(values.shape) == 4:
        # Determine the set of possible elevation dimension names excluding
        # the list of names that are used for the lat, lon, and time values.
        dims = netcdf.variables[variable_name].dimensions
        dimension_names = [dim_name.encode() for dim_name in dims]
        lat_lon_time_var_names = [lat_name, lon_name, time_name]

        elev_names = set(dimension_names) - set(lat_lon_time_var_names)

        # Grab the index value for the elevation values
        level_index = dimension_names.index(elev_names.pop())

        # Strip out the elevation values so we're left with a 3D array.
        if level_index == 0:
            values = values [elevation_index,:,:,:]
        elif level_index == 1:
            values = values [:,elevation_index,:,:]
        elif level_index == 2:
            values = values [:,:,elevation_index,:]
        else:
            values = values [:,:,:,elevation_index]

    return Dataset(lats, lons, times, values, variable_name, name=name)

def load_files(file_path,
              filename_pattern,
              variable_name,
              elevation_index=0,
              name='',
              lat_name=None,
              lon_name=None,
              time_name=None,
              latitude_range=None,
              longitude_range=None):
    ''' Load multiple NetCDF files whose file names have common patterns into a Dataset.
    The dataset can be spatially subset.

    :param file_path: Directory to the NetCDF file to load.
    :type file_path: :mod:`string`

    :param filename_pattern: Path to the NetCDF file to load.
    :type filename_pattern: :list:`string`

    :param variable_name: The variable name to load from the NetCDF file.
    :type variable_name: :mod:`string`

    :param elevation_index: (Optional) The elevation index for which data should
        be returned. Climate data is often times 4 dimensional data. Some
        datasets will have readins at different height/elevation levels. OCW
        expects 3D data so a single layer needs to be stripped out when loading.
        By default, the first elevation layer is used. If desired you may
        specify the elevation value to use.
    :type elevation_index: :class:`int`

    :param name: (Optional) A name for the loaded dataset.
    :type name: :mod:`string`

    :param lat_name: (Optional) The latitude variable name to extract from the
        dataset.
    :type lat_name: :mod:`string`

    :param lon_name: (Optional) The longitude variable name to extract from the
        dataset.
    :type lon_name: :mod:`string`

    :param time_name: (Optional) The time variable name to extract from the
        dataset.
    :type time_name: :mod:`string`

    :param latitude_range: (Optional) southern and northern boundary of the sub-region
    :type latitude_range: :list:float   

    :param longitude_range: (Optional) western and eastern boundary of the sub-region
    :type longitude_range: :list:float   

    :returns: An OCW Dataset object with the requested variable's data from
        the NetCDF file.
    :rtype: :class:`dataset.Dataset`

    :raises ValueError: When the specified file path cannot be loaded by ndfCDF4
        or when the lat/lon/time variable name cannot be determined
        automatically.
    ''' 

    netcdf_files= []
    for pattern in filename_pattern:
        netcdf_files.extend(glob.glob(file_path+pattern))
    netcdf_files.sort() 
    print str(len(netcdf_files)), " files match the name pattern."
    print 'First file: ',netcdf_files[0]    
    print 'Last file: ',netcdf_files[-1]

    try:
        netcdf = netCDF4.Dataset(netcdf_files[0], mode='r')
    except RuntimeError:
        err = "Dataset filepath is invalid. Please ensure it is correct."
        raise ValueError(err)
    except:
        err = (
            "The given file cannot be loaded. Please ensure that it is a valid "
            "NetCDF file. If problems persist, report them to the project's "
            "mailing list."
        )
        raise ValueError(err)

    if not lat_name:
        lat_name = _get_netcdf_variable_name(LAT_NAMES, netcdf, variable_name)
    if not lon_name:
        lon_name = _get_netcdf_variable_name(LON_NAMES, netcdf, variable_name)
    if not time_name:
        time_name = _get_netcdf_variable_name(TIME_NAMES, netcdf, variable_name)

    lats = netcdf.variables[lat_name][:]
    lons = netcdf.variables[lon_name][:]

    if latitude_range and longitude_range:
        if lats.ndim == 1:
             x_index = numpy.where((lons>=numpy.min(longitude_range)) & (lons<=numpy.max(longitude_range)))[0]
             y_index = numpy.where((lats>=numpy.min(latitude_range)) & (lats<=numpy.max(latitude_range)))[0] 
             lats = lats[y_index]
             lons = lons[x_index]
        else:
             y_index,x_index = numpy.where((lons>=numpy.min(longitude_range)) & (lons<=numpy.max(longitude_range)) & (lats>=numpy.min(latitude_range)) & (lats<=numpy.max(latitude_range)))
             lats = lats[y_index, x_index]
             lons = lons[y_index, x_index]
    else:
        y_index = np.arange(lats.shape[0]) 
        x_index = np.arange(lons.shape[-1]) 

    time_raw_values = netcdf.variables[time_name]
    for attr, value in time_raw_values.__dict__.iteritems():
        if 'unit' in attr.lower():
            time_unit = value
    times = netCDF4.num2date(time_raw_values[:], units = time_unit)
    times = numpy.array(times)

    # check the variable structure before reading data from the open file 
    variable = netcdf.variables[variable_name]  
    # If the values are 4D then we need to strip out the elevation index
    if len(variable.shape) == 4:
        # Determine the set of possible elevation dimension names excluding
        # the list of names that are used for the lat, lon, and time values.
        dims = netcdf.variables[variable_name].dimensions
        dimension_names = [dim_name.encode() for dim_name in dims]
        lat_lon_time_var_names = [lat_name, lon_name, time_name]

        elev_names = set(dimension_names) - set(lat_lon_time_var_names)

        # Grab the index value for the elevation values
        level_index = dimension_names.index(elev_names.pop())

        # Strip out the elevation values so we're left with a 3D array.
        if level_index == 0:
            values = variable[elevation_index,:,y_index,x_index]
        elif level_index == 1:
            values = variable[:,elevation_index,y_index,x_index]
        else:
            raise ValueError('The structure of this variable does not follow the community standard')
        if len(netcdf_files) >1:
            for netcdf_file in netcdf_files[1:]:
                netcdf.close()
                netcdf = netCDF4.Dataset(netcdf_file, mode='r')
                time_raw_values = netcdf.variables[time_name]
                for attr, value in time_raw_values.__dict__.iteritems():
                    if 'unit' in attr.lower():
                        time_unit = value
                times = numpy.append(times, netCDF4.num2date(time_raw_values[:], units = time_unit))
                if level_index == 0:
                    values = numpy.concatenate((values, netcdf.variables[variable_name][elevation_index,:,y_index,x_index]), axis=0)
                elif level_index == 1:
                    values = numpy.concatenate((values, netcdf.variables[variable_name][:,elevation_index,y_index,x_index]), axis=0)

    elif len(variable.shape) == 3:
        values = variable[:,y_index,x_index]
        
        if len(netcdf_files) >1:
            for netcdf_file in netcdf_files[1:]:
                netcdf.close()
                netcdf = netCDF4.Dataset(netcdf_file, mode='r')
                time_raw_values = netcdf.variables[time_name]
                for attr, value in time_raw_values.__dict__.iteritems():
                    if 'unit' in attr.lower():
                        time_unit = value
                times = numpy.append(times, netCDF4.num2date(time_raw_values[:], units = time_unit))
                values = numpy.concatenate((values, netcdf.variables[variable_name][:,y_index,x_index]), axis=0)
    elif len(variable.shape) == 2:
        values = (variable[y_index,x_index]).reshape((1,y_index.size,x_index.size))
        if len(netcdf_files) >1:
            for netcdf_file in netcdf_files[1:]:
                netcdf.close()
                netcdf = netCDF4.Dataset(netcdf_file, mode='r')
                time_raw_values = netcdf.variables[time_name]
                for attr, value in time_raw_values.__dict__.iteritems():
                    if 'unit' in attr.lower():
                        time_unit = value
                times = numpy.append(times, netCDF4.num2date(time_raw_values[:], units = time_unit))
                values = numpy.concatenate((values, (netcdf.variables[variable_name][y_index,x_index]).reshape((1,y_index.size,x_index.size))), axis=0)
    return Dataset(lats, lons, times, values, variable_name, name=name)

