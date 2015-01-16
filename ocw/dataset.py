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

import ocw.utils as utils

from mpl_toolkits.basemap import shiftgrid

logger = logging.getLogger(__name__)

class Dataset:
    '''Container for a dataset's attributes and data.'''

    def __init__(self, lats, lons, times, values, variable=None, name=""):
        '''Default Dataset constructor

        :param lats: One dimensional numpy array of unique latitude values.
        :type lats: :class:`numpy.ndarray`

        :param lons: One dimensional numpy array of unique longitude values.
        :type lons: :class:`numpy.ndarray`

        :param times: One dimensional numpy array of unique python datetime 
            objects.
        :type times: :class:`numpy.ndarray`

        :param values: Three dimensional numpy array of parameter values with 
            shape [timesLength, latsLength, lonsLength]. 
        :type values: :class:`numpy.ndarray`

        :param variable: Name of the value variable.
        :type variable: :mod:`string`

        :param name: An optional string name for the Dataset.
        :type name: :mod:`string`

        :raises: ValueError
        '''
        self._validate_inputs(lats, lons, times, values)
        lats, lons, values = utils.normalize_lat_lon_values(lats, lons, values)

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
        :rtype: :func:`tuple` of the form (:class:`float`, :class:`float`,
            :class:`float`, :class:`float`).

        '''
        return (float(min(self.lats)), float(max(self.lats)),
                float(min(self.lons)), float(max(self.lons)))


    def time_range(self):
        '''Calculate the temporal range

        :returns: The start and end date of the Dataset's temporal range as 
            a tuple in the form (start_time, end_time).
        :rtype: :func:`tuple` of the form (:class:`datetime.datetime`,
            :class:`datetime.datetime`)
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
        :rtype: (:class:`float`, :class:`float`)
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
        :rtype: :mod:`string`
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

            logger.error(error)
            raise ValueError(error)

        return time_resolution

    def _validate_inputs(self, lats, lons, times, values):
        """Check that Dataset inputs are valid.
        
        :raises: ValueError
        """
        err_msg = None
        #Setup and Check parameter dimensionality is correct
        lat_dim = len(lats.shape)
        lon_dim = len(lons.shape)
        time_dim = len(times.shape)
        value_dim = len(values.shape)
        lat_count = lats.shape[0]
        lon_count = lons.shape[0]
        time_count = times.shape[0]
        
        if lat_dim != 1:
            err_msg = "Latitude Array should be 1 dimensional.  %s dimensions found." % lat_dim
        elif lon_dim != 1:
            err_msg = "Longitude Array should be 1 dimensional. %s dimensions found." % lon_dim
        elif time_dim != 1:
            err_msg = "Time Array should be 1 dimensional.  %s dimensions found." % time_dim
        elif value_dim != 3:
            err_msg = "Value Array should be 3 dimensional.  %s dimensions found." % value_dim
        # Finally check that the Values array conforms to the proper shape
        elif values.shape != (time_count, lat_count, lon_count):
            err_msg = """Value Array must be of shape (times, lats, lons).
Expected shape (%s, %s, %s) but received (%s, %s, %s)""" % (time_count,
                                                            lat_count,
                                                            lon_count,
                                                            values.shape[0],
                                                            values.shape[1],
                                                            values.shape[2])
        if err_msg:
            logger.error(err_msg)
            #raise ValueError(err_msg)
            print 'Warning: '+err_msg

    def __str__(self):
        lat_min, lat_max, lon_min, lon_max = self.spatial_boundaries()
        start, end = self.time_range()
        lat_range = "({}, {})".format(lat_min, lon_min)
        lon_range = "({}, {})".format(lon_min, lon_min)
        time_range = "({}, {})".format(start, end)

        formatted_repr = (
            "<Dataset - name: {}, "
            "lat-range: {}, "
            "lon-range: {}, "
            "time_range: {}, "
            "var: {}>"
        )

        return formatted_repr.format(
            self.name if self.name != "" else None,
            lat_range,
            lon_range,
            time_range,
            self.variable
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
        :type lat_min: :class:`float`
        
        :param lat_max: The maximum latitude bound.
        :type lat_max: :class:`float`

        :param lon_min: The minimum longitude bound.
        :type lon_min: :class:`float`
        
        :param lon_max: The maximum longitude bound.
        :type lon_max: :class:`float`

        :param start: The starting datetime bound.
        :type start: :class:`datetime.datetime`

        :param end: The ending datetime bound.
        :type end: :class:`datetime.datetime`

        :raises: ValueError
        '''
        self._lat_min = float(lat_min)
        self._lat_max = float(lat_max)
        self._lon_min = float(lon_min)
        self._lon_max = float(lon_max)
        self._start = start
        self._end = end

    @property
    def lat_min(self):
        return self._lat_min

    @lat_min.setter
    def lat_min(self, value):
        if not (-90 <= value <= 90 and value < self._lat_max):
            error = "Attempted to set lat_min to invalid value: %s" % (value)
            logger.error(error)
            raise ValueError(error)

        self._lat_min = value

    @property
    def lat_max(self):
        return self._lat_max

    @lat_max.setter
    def lat_max(self, value):
        if not (-90 <= value <= 90 and value > self._lat_min):
            error = "Attempted to set lat_max to invalid value: %s" % (value)
            logger.error(error)
            raise ValueError(error)

        self._lat_max = value

    @property
    def lon_min(self):
        return self._lon_min

    @lon_min.setter
    def lon_min(self, value):
        if not (-180 <= value <= 180 and value < self._lon_max):
            error = "Attempted to set lon_min to invalid value: %s" % (value)
            logger.error(error)
            raise ValueError(error)

        self._lon_min = value

    @property
    def lon_max(self):
        return self._lon_max

    @lon_max.setter
    def lon_max(self, value):
        if not (-180 <= value <= 180 and value > self._lon_min):
            error = "Attempter to set lon_max to invalid value: %s" % (value)
            logger.error(error)
            raise ValueError(error)

        self._lon_max = value

    @property
    def start(self):
        return self._start

    @start.setter
    def start(self, value):
        if not (type(value) is dt.datetime and value < self._end):
            error = "Attempted to set start to invalid value: %s" % (value)
            logger.error(error)
            raise ValueError(error)

        self._start = value

    @property
    def end(self):
        return self._end

    @end.setter
    def end(self, value):
        if not (type(value) is dt.datetime and value > self._start):
            error = "Attempted to set end to invalid value: %s" % (value)
            logger.error(error)
            raise ValueError(error)

        self._end = value

    def __str__(self):
        lat_range = "({}, {})".format(self._lat_min, self._lon_min)
        lon_range = "({}, {})".format(self._lon_min, self._lon_min)
        time_range = "({}, {})".format(self._start, self._end)

        formatted_repr = (
            "<Bounds - "
            "lat-range: {}, "
            "lon-range: {}, "
            "time_range: {}> "
        )

        return formatted_repr.format(
            lat_range,
            lon_range,
            time_range,
        )
