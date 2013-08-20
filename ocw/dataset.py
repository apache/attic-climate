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

'''
Classes:
    Dataset - Container for a dataset's attributes and data.
    Bounds - Container for holding spatial and temporal bounds information
                for operations on a Dataset.
'''

import numpy
import logging
import datetime as dt

class Dataset:
    '''Container for a dataset's attributes and data.'''

    def __init__(self, lats, lons, times, values, variable=None, name=""):
        '''Default Dataset constructor

        :param lats: One dimensional numpy array of unique latitude values.
        :type lats: numpy array
        :param lons: One dimensional numpy array of unique longitude values.
        :type lons: numpy array
        :param times: One dimensional numpy array of unique python datetime 
            objects.
        :type times: numpy array
        :param values: Three dimensional numpy array of parameter values with 
            shape [timesLength, latsLength, lonsLength]. 
        :type values: numpy array
        :param variable: Name of the value variable.
        :type variable: string
        :param name: An optional string name for the Dataset.
        :type variable: string

        :raises: ValueError
        '''
        if self._inputs_are_invalid(lats, lons, times, values):
            err = "Dataset given improperly shaped array during initialization."
            raise ValueError(err)

        self.lats = lats
        self.lons = lons
        self.times = times
        self.values = values
        self.variable = variable
        self.name = name

    def spatial_boundaries(self):
        '''Calculate the spatial boundaries.

        :returns: The Dataset's bounding latitude and longitude values as a
            tuple in the form (min_lat, max_lat, min_lon, max_lon)
        :rtype: (float, float, float, float)

        '''
        return (min(self.lats), max(self.lats),
                min(self.lons), max(self.lons))


    def time_range(self):
        '''Calculate the temporal range

        :returns: The start and end date of the Dataset's temporal range as 
            a tuple in the form (start_time, end_time).
        :rtype: (datetime, datetime)
        '''
        sorted_time = numpy.sort(self.times)
        start_time = sorted_time[0]
        end_time = sorted_time[-1]

        return (start_time, end_time)


    def spatial_resolution(self):
        '''Calculate the latitudinal and longitudinal spatial resolution.

        .. warning:: This only works with properly gridded data.

        :returns: The Dataset's latitudinal and longitudinal spatial resolution
            as a tuple of the form (lat_resolution, lon_resolution).
        :rtype: (float, float)
        '''
        sorted_lats = numpy.sort(list(set(self.lats)))
        sorted_lons = numpy.sort(list(set(self.lons)))
        lat_resolution = sorted_lats[1] - sorted_lats[0]
        lon_resolution = sorted_lons[1] - sorted_lons[0]

        return (lat_resolution, lon_resolution)


    def temporal_resolution(self):
        '''Calculate the temporal resolution.

        :raises ValueError: If timedelta.days as calculated from the sorted \
            list of times is an unrecognized value a ValueError is raised.

        :returns: The temporal resolution.
        :rtype: string
        '''
        sorted_times = numpy.sort(self.times)
        time_resolution = sorted_times[1] - sorted_times[0]
        num_days = time_resolution.days

        if num_days == 0:
            num_hours = time_resolution.seconds / 3600
            time_resolution = 'hourly' if num_hours >= 1 else 'minutely'
        elif num_days == 1:
            time_resolution = 'daily'
        elif num_days <= 31:
            time_resolution = 'monthly'
        elif num_days > 31:
            time_resolution = 'yearly'
        else:
            error = (
                "Unable to calculate the temporal resolution for the "
                "dataset. The number of days between two time values is "
                "an unexpected value: " + str(num_days)
            )

            logging.error(error)
            raise ValueError(error)

        return time_resolution

    def _inputs_are_invalid(self, lats, lons, times, values):
        '''Check if Dataset input values are expected shape.
        
        :returns: True if the values are invalid, False otherwise.
        '''
        lats_shape = lats.shape
        lons_shape = lons.shape
        times_shape = times.shape
        values_shape = values.shape

        return (
            len(lats_shape) != 1 or len(lons_shape) != 1 or 
            len(times_shape) != 1 or len(values_shape) != 3 or
            values_shape != (times_shape[0], lats_shape[0], lons_shape[0])
        )


class Bounds(object):
    '''Container for holding spatial and temporal bounds information.

    Certain operations require valid bounding information to be present for
    correct functioning. Bounds guarantees that a function receives well 
    formed information without the need to do the validation manually.

    Spatial and temporal bounds must follow the following guidelines.

    * Latitude values must be in the range [-90, 90]
    * Longitude values must be in the range [-180, 180]
    * Lat/Lon Min values must be less than the corresponding Lat/Lon Max values.
    * Temporal bounds must a valid datetime object
    '''

    def __init__(self, lat_min, lat_max, lon_min, lon_max, start, end):
        '''Default Bounds constructor

        :param lat_min: The minimum latitude bound.
        :type lat_min: float
        
        :param lat_max: The maximum latitude bound.
        :type lat_max: float

        :param lon_min: The minimum longitude bound.
        :type lon_min: float
        
        :param lon_max: The maximum longitude bound.
        :type lon_max: float

        :param start: The starting datetime bound.
        :type start: datetime

        :param end: The ending datetime bound.
        :type end: datetime

        :raises: ValueError
        '''
        self._lat_min = lat_min
        self._lat_max = lat_max
        self._lon_min = lon_min
        self._lon_max = lon_max
        self._start = start
        self._end = end

    @property
    def lat_min(self):
        return self._lat_min

    @lat_min.setter
    def lat_min(self, value):
        if not (-90 <= value <= 90 and value < self._lat_max):
            raise ValueError("Attempted to set lat_min to invalid value.")

        self._lat_min = value

    @property
    def lat_max(self):
        return self._lat_max

    @lat_max.setter
    def lat_max(self, value):
        if not (-90 <= value <= 90 and value > self._lat_min):
            raise ValueError("Attempted to set lat_max to invalid value.")

        self._lat_max = value

    @property
    def lon_min(self):
        return self._lon_min

    @lon_min.setter
    def lon_min(self, value):
        if not (-180 <= value <= 180 and value < self._lon_max):
            raise ValueError("Attempted to set lon_min to invalid value.")

        self._lon_min = value

    @property
    def lon_max(self):
        return self._lon_max

    @lon_max.setter
    def lon_max(self, value):
        if not (-180 <= value <= 180 and value > self._lon_min):
            raise ValueError("Attempted to set lon_max to invalid value.")

        self._lon_max = value

    @property
    def start(self):
        return self._start

    @start.setter
    def start(self, value):
        if not (type(value) is dt.datetime and value < self._end):
            raise ValueError("Attempted to set start to invalid value")

        self._start = value

    @property
    def end(self):
        return self._end

    @end.setter
    def end(self, value):
        if not (type(value) is dt.datetime and value > self._start):
            raise ValueError("Attempted to set end to invalid value")

        self._end = value
