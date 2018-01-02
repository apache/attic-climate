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

import os
import numpy
import logging
import datetime as dt
from mpl_toolkits.basemap import Basemap
import netCDF4

import ocw
import ocw.utils as utils

logger = logging.getLogger(__name__)


class Dataset:
    '''Container for a dataset's attributes and data.'''

    def __init__(self, lats, lons, times, values, variable=None, units=None,
                 origin=None, name=""):
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

        :param units: Name of the value units
        :type units: :mod:`string`

        :param name: An optional string name for the Dataset.
        :type name: :mod:`string`

        :param origin: An optional object used to specify information on where
            this dataset was loaded from.
        :type origin: :class:`dict`

        :raises: ValueError
        '''
        self._validate_inputs(lats, lons, times, values)
        lats, lons, values = utils.normalize_lat_lon_values(lats, lons, values)

        self.lats = lats
        self.lons = lons
        self.times = times
        self.values = values
        self.variable = variable
        self.units = units
        self.name = name
        self.origin = origin

    def spatial_boundaries(self):
        '''Calculate the spatial boundaries.

        :returns: The Dataset's bounding latitude and longitude values as a
            tuple in the form (min_lat, max_lat, min_lon, max_lon)
        :rtype: :func:`tuple` of the form (:class:`float`, :class:`float`,
            :class:`float`, :class:`float`).

        '''
        return (float(numpy.min(self.lats)), float(numpy.max(self.lats)),
                float(numpy.min(self.lons)), float(numpy.max(self.lons)))

    def temporal_boundaries(self):
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

           If self.lats and self.lons are from curvilinear coordinates,
           the output resolutions are approximate values.

        :returns: The Dataset's latitudinal and longitudinal spatial resolution
            as a tuple of the form (lat_resolution, lon_resolution).
        :rtype: (:class:`float`, :class:`float`)
        '''

        if self.lats.ndim == 1 and self.lons.ndim == 1:
            sorted_lats = numpy.sort(list(set(self.lats)))
            sorted_lons = numpy.sort(list(set(self.lons)))
            lat_resolution = sorted_lats[1] - sorted_lats[0]
            lon_resolution = sorted_lons[1] - sorted_lons[0]
        if self.lats.ndim == 2 and self.lons.ndim == 2:
            lat_resolution = self.lats[1, 1] - self.lats[0, 0]
            lon_resolution = self.lons[1, 1] - self.lons[0, 0]

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

        return time_resolution

    def _validate_inputs(self, lats, lons, times, values):
        """Check that Dataset inputs are valid.

        :raises: ValueError
        """
        err_msg = None
        # Setup and Check parameter dimensionality is correct
        lat_dim = len(lats.shape)
        lon_dim = len(lons.shape)
        time_dim = len(times.shape)
        value_dim = len(values.shape)
        lat_count = lats.shape[0]
        lon_count = lons.shape[0]

        if lat_dim == 2 and lon_dim == 2:
            lon_count = lons.shape[1]
        time_count = times.shape[0]

        if time_dim != 1:
            err_msg = ("Time Array should be 1 dimensional.  %s dimensions"
                       " found." % time_dim)
        elif value_dim < 2:
            err_msg = ("Value Array should be at least 2 dimensional."
                       "  %s dimensions found." % value_dim)
        # Finally check that the Values array conforms to the proper shape
        if value_dim == 2:
            if (values.shape[0] != time_count and
                    values.shape != (lat_count, lon_count)):
                err_msg = """Value Array must be of shape (lats, lons) or (times, locations).
                Expected shape (%s, %s) but received (%s, %s)""" % (
                    lat_count,
                    lon_count,
                    values.shape[0],
                    values.shape[1])
        if (value_dim == 3 and
                values.shape != (time_count, lat_count, lon_count)):
            err_msg = """Value Array must be of shape (times, lats, lons).
            Expected shape (%s, %s, %s) but received (%s, %s, %s)""" % (
                time_count,
                lat_count,
                lon_count,
                values.shape[0],
                values.shape[1],
                values.shape[2])
        if err_msg:
            logger.error(err_msg)
            raise ValueError(err_msg)

    def __str__(self):
        lat_min, lat_max, lon_min, lon_max = self.spatial_boundaries()
        start, end = self.temporal_boundaries()
        lat_range = "({}, {})".format(lat_min, lon_min)
        lon_range = "({}, {})".format(lon_min, lon_min)
        temporal_boundaries = "({}, {})".format(start, end)

        formatted_repr = (
            "<Dataset - name: {}, "
            "lat-range: {}, "
            "lon-range: {}, "
            "temporal_boundaries: {}, "
            "var: {}, "
            "units: {}>"
        )

        return formatted_repr.format(
            self.name if self.name != "" else None,
            lat_range,
            lon_range,
            temporal_boundaries,
            self.variable,
            self.units
        )


class Bounds(object):
    '''Container for holding spatial and temporal bounds information.

    Certain operations require valid bounding information to be present for
    correct functioning. Bounds guarantees that a function receives well
    formed information without the need to do the validation manually.

    boundary_type may be one of the following:
    * 'rectangular'
    * 'CORDEX (CORDEX region name)': pre-defined CORDEX boundary
    * 'us_states': an array of US states abbreviation is required (ex) us_states = ['CA','NV'])
    * 'countries': an array of county names is required (ex) countries = ['United States','Canada','Mexico']
    * 'user': user_mask_file in a netCDF format with two dimensional mask variable is required.

    If boundary_type == 'rectangular', spatial and temporal bounds must follow the following guidelines.

    * Latitude values must be in the range [-90, 90]
    * Longitude values must be in the range [-180, 180]
    * Lat/Lon Min values must be less than the corresponding Lat/Lon Max
      values.

    Temporal bounds must a valid datetime object
    '''

    def __init__(self, boundary_type='rectangular',
                 us_states=None, countries=None,
                 user_mask_file=None, mask_variable_name=None, longitude_name=None, latitude_name=None,
                 lat_min=-90, lat_max=90, lon_min=-180, lon_max=180,
                 start=None, end=None):
        '''Default Bounds constructor
        :param boundary_type: The type of spatial subset boundary.
        :type boundary_type: :mod:`string`


        :param lat_min: The minimum latitude bound.
        :type lat_min: :class:`float`

        :param lat_min: The minimum latitude bound.
        :type lat_min: :class:`float`

        :param lat_max: The maximum latitude bound.
        :type lat_max: :class:`float`

        :param lon_min: The minimum longitude bound.
        :type lon_min: :class:`float`

        :param lon_max: The maximum longitude bound.
        :type lon_max: :class:`float`

        :param start: An optional datetime object for the starting
                      datetime bound.
        :type start: :class:`datetime.datetime`

        :param end: An optional datetime object for the ending datetime bound.
        :type end: :class:`datetime.datetime`

        :raises: ValueError
        '''
        self.boundary_type = boundary_type
        if start:
            self._start = start
        else:
            self._start = None

        if end:
            self._end = end
        else:
            self._end = None

        if boundary_type == 'us_states':
            self.masked_regions = utils.shapefile_boundary(
                boundary_type, us_states)
        if boundary_type == 'countries':
            self.masked_regions = utils.shapefile_boundary(
                boundary_type, countries)
        if boundary_type == 'user':
            file_object = netCDF4.Dataset(user_mask_file)
            self.mask_variable = file_object.variables[mask_variable_name][:]
            mask_longitude = file_object.variables[longitude_name][:]
            mask_latitude = file_object.variables[latitude_name][:]
            if mask_longitude.ndim == 1 and mask_latitude.ndim == 1:
                self.mask_longitude, self.mask_latitude = numpy.meshgrid(
                    mask_longitude, mask_latitude)
            elif mask_longitude.ndim == 2 and mask_latitude.ndim == 2:
                self.mask_longitude = mask_longitude
                self.mask_latitude = mask_latitude
        if boundary_type == 'rectangular':
            if not (-90 <= float(lat_min) <= 90) or float(lat_min) > float(lat_max):
                error = "Attempted to set lat_min to invalid value: %s" % (
                    lat_min)
                logger.error(error)
                raise ValueError(error)
            if not (-90 <= float(lat_max) <= 90):
                error = "Attempted to set lat_max to invalid value: %s" % (
                    lat_max)
                logger.error(error)
                raise ValueError(error)
            if not (-180 <= float(lon_min) <= 180) or float(lon_min) > float(lon_max):
                error = "Attempted to set lon_min to invalid value: %s" % (
                    lon_min)
                logger.error(error)
                raise ValueError(error)
            if not (-180 <= float(lon_max) <= 180):
                error = "Attempted to set lat_max to invalid value: %s" % (
                    lon_max)
                logger.error(error)
                raise ValueError(error)

            self.lat_min = float(lat_min)
            self.lat_max = float(lat_max)
            self.lon_min = float(lon_min)
            self.lon_max = float(lon_max)
        if boundary_type[:6].upper() == 'CORDEX':
            self.lat_min, self.lat_max, self.lon_min, self.lon_max = utils.CORDEX_boundary(
                boundary_type[6:].replace(" ", "").lower())

    @property
    def start(self):
        return self._start

    @start.setter
    def start(self, value):
        if self._end:
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
        if self._start:
            if not (type(value) is dt.datetime and value > self._start):
                error = "Attempted to set end to invalid value: %s" % (value)
                logger.error(error)
                raise ValueError(error)

        self._end = value
