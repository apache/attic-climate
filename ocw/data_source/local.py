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

import re
import netCDF4
from ocw.dataset import Dataset
import numpy
import numpy.ma as ma
from datetime import timedelta ,datetime
import calendar
import string


def get_time_base(time_format, since_index):
    '''Calculate time base from time data.

    :param time_format: Unit of time in netCDF
    :type time_format: String
    :param since_index: Index of word since in time unit
    :type since_index: Number

    :returns: Time base of time attribute in netCDF file
    :rtype: datetime
    '''

    time_base = string.lstrip(time_format[since_index:])
    time_base = time_base.split('.')[0] + '0' if "." in time_base else time_base
    TIME_FORMATS =[
                    '%Y:%m:%d %H:%M:%S', '%Y-%m-%d %H-%M-%S', '%Y/%m/%d %H/%M/%S','%Y-%m-%d %H:%M:%S', '%Y/%m/%d %H:%M:%S', '%Y%m%d %H:%M:%S',
                    '%Y%m%d%H%M%S', '%Y-%m-%d-%H-%M-%S', '%Y/%m/%d/%H/%M/%S', '%Y:%m:%d:%H:%M:%S', '%Y-%m-%d-%H:%M:%S', '%Y/%m/%d%H:%M:%S',
                    '%Y-%m-%d %H:%M','%Y/%m/%d %H:%M', '%Y:%m:%d %H:%M','%Y%m%d %H:%M',
                    '%Y-%m-%d', '%Y/%m/%d', '%Y:%m:%d', '%Y%m%d'
                    ]
    count = 0
    for format in TIME_FORMATS:
            try:
                time_base = datetime.strptime(time_base, format)
                break
            except:
                count = count + 1
                if count == len(TIME_FORMATS):
                    raise Exception("The time format is not found. Base time is " + str(time_base) + " .")

    return time_base


def get_time_step(netcdf, time_variable_name):
    '''Calculate time step from time data.

    :param netcdf: NetCDF dataset object
    :type netcdf: Object
    :param time_variable_name: NetCDF time variable name
    :type time_variable_name: String

    :returns: Step, unit and index of word since of netCDF time variable
            in form of (time_step, time_format, since_index)
    :rtype: (String, String, Number)
    '''

    try:
        time_format = netcdf.variables[time_variable_name].units.encode()
        since_index = re.search('since', time_format).end()
    except AttributeError:
        raise Exception('Time variable attributes cannot be decoded.')

    time_step = None
    TIME_UNITS = ('minutes', 'hours', 'days', 'months', 'years')
    for unit in TIME_UNITS:
        if re.search(unit, time_format):
            time_step = unit
            break

    return (time_step, time_format, since_index)


def calculate_time(netcdf, time_raw_values, time_variable_name):
    '''Convert time data from integer to python datetime.

    :param netcdf: NetCDF dataset object
    :type netcdf: Object
    :param times_raw_values: Integer list of raw time data
    :type times_raw_values: List
    :param time_variable_name: NetCDF time variable name
    :type time_variable_name: String

    :returns: List of converted datetime values
    :rtype: datetime list
    '''

    time_values = []

    time_step, time_format, since_index = get_time_step(netcdf, time_variable_name)
    time_base = get_time_base(time_format, since_index)
    time_step = time_step.lower()

    if 'min' in time_step:
        for time in time_raw_values:
            time_values.append(time_base + timedelta(minutes=int(time)))
    elif 'hour' in time_step:
        for time in time_raw_values:
            time_values.append(time_base + timedelta(hours=int(time)))
    elif 'day' in time_step:
        for time in time_raw_values:
            time_values.append(time_base + timedelta(days=int(time)))
    elif 'mon' in time_step:
        for time in time_raw_values:
            number_of_month = time_base.month -1 + int(time)
            new_year = time_base.year + number_of_month / 12
            new_month = number_of_month % 12 + 1
            new_day = min(time_base.day, calendar.monthrange(new_year,new_month)[1])
            time_values.append(datetime(new_year, new_month, new_day, time_base.hour, time_base.minute, time_base.second))
    elif 'year' or 'annual' in time_step:
        for time in time_raw_values:
            time_values.append(time_base + timedelta(years=int(time)))
    else:
        raise Exception("The time step cannot be defined.")

    return time_values


def get_lat_name(variable_names):
    '''Find the latitude variable name

    :param variable_names: List of netCDF variables' name
    :type variable_names: List

    :returns: Latitude variable name
    :rtype: String
    '''

    common_name = set(['lat', 'lats', 'latitude', 'latitudes']).intersection(variable_names)
    if len(common_name) !=1:
        raise Exception("Unable to autodetect latitude variable name.")
    else:
        lat_variable_name = common_name.pop()

    return lat_variable_name


def get_lon_name(variable_names):
    '''Find the longitude variable name

    :param variable_names: List of netCDF variables' name
    :type variable_names: List

    :returns: Longitude variable name
    :rtype: String
    '''

    common_name = set(['lon', 'lons', 'longitude', 'longitudes']).intersection(variable_names)
    if len(common_name) !=1:
        raise Exception("Unable to autodetect longitude variable name.")
    else:
        lon_variable_name = common_name.pop()

    return lon_variable_name


def get_time_name(variable_names):
    '''Find the time variable name.

    :param: variableNameList: List of netCDF variables' name
    :type variable_names: List

    :returns: Time variable name
    :rtype: String
    '''

    common_name = set(['time', 'times', 'date', 'dates', 'julian']).intersection(variable_names)
    if len(common_name) !=1:
        raise Exception("Unable to autodetect time variable name.")
    else:
        time_variable_name = common_name.pop()

    return time_variable_name


def get_level_name(variable_names):
    '''Find the level variable name.

    :param variable_names: List of netCDF variables' name
    type variable_names: List

    :returns: Level variable name
    :rtype: String
    '''

    level_variable_name = None
    common_name = set(['lev', 'level', 'levels', 'height', 'heights', 'elev', 'elevation', 'elevations']).intersection(variable_names)
    if len(common_name) !=1:
        pass
    else:
        level_variable_name = common_name.pop()

    return level_variable_name


def get_value_name(possible_value_name):
    '''Find the value variable name.

    :param possible_value_name: List of all value variable names
    :type possible_value_name: List

    :returns: Value variable name
    :rtype: String
    '''

    if len(possible_value_name) == 1:
        value_variable_name = possible_value_name[0]
    else:
        raise Exception("The given value variable name does not match with existing variables name.")

    return value_variable_name


def load_file(file_path, variable_name=None):
    '''Load netCDF file, get the all variables name and get the data.

    :param file_path: NetCDF directory with file name
    :type file_path: String
    :param variable_name[optional]: The given (by user) value variable name
    :type variable_name: String

    :returns: A dataset object from dataset.py
    :rtype: Object
    '''

    try:
        netcdf = netCDF4.Dataset(file_path, mode='r')
    except:
        raise Exception("The given file cannot be loaded (Only netCDF file can be supported).")

    variable_names = [variable.encode() for variable in netcdf.variables.keys()]
    variable_names = [variable.lower() for variable in variable_names]

    lat_variable_name = get_lat_name(variable_names)
    lon_variable_name = get_lon_name(variable_names)
    time_variable_name = get_time_name(variable_names)
    level_variable_name = get_level_name(variable_names)

    if variable_name in variable_names:
        value_variable_name = variable_name
    else:
        possible_value_name = list(set(variable_names) - set([lat_variable_name, lon_variable_name, time_variable_name, level_variable_name]))
        value_variable_name = get_value_name(possible_value_name)

    lats = netcdf.variables[lat_variable_name][:]    
    lons = netcdf.variables[lon_variable_name][:]
    time_raw_values = netcdf.variables[time_variable_name][:]
    times = calculate_time(netcdf, time_raw_values, time_variable_name)
    times = numpy.array(times)
    values = ma.array(netcdf.variables[value_variable_name][:])

    return Dataset(lats, lons, times, values, value_variable_name)
