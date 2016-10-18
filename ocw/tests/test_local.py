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

import datetime
import unittest
import os
import urllib
import numpy
import netCDF4

import ocw.data_source.local as local


class test_load_file(unittest.TestCase):

    def setUp(self):
        # Read netCDF file
        self.file_path = create_netcdf_object()
        self.netCDF_file = netCDF4.Dataset(self.file_path, 'r')
        self.latitudes = self.netCDF_file.variables['latitude'][:]
        self.longitudes = self.netCDF_file.variables['longitude'][:]
        self.alt_lats = self.netCDF_file.variables['alt_lat'][:]
        self.alt_lons = self.netCDF_file.variables['alt_lon'][:]
        self.values = self.netCDF_file.variables['value'][:]
        self.variable_name_list = ['latitude',
                                   'longitude', 'time', 'level', 'value']
        self.possible_value_name = ['latitude', 'longitude', 'time', 'level']

    def tearDown(self):
        os.remove(self.file_path)

    def test_load_invalid_file_path(self):
        self.invalid_netcdf_path = '/invalid/path'
        with self.assertRaises(ValueError):
            local.load_file(file_path=self.invalid_netcdf_path,
                            variable_name='test variable')

    def test_function_load_file_lats(self):
        """To test load_file function for latitudes"""
        self.assertItemsEqual(local.load_file(
            self.file_path, "value").lats, self.latitudes)

    def test_function_load_file_lons(self):
        """To test load_file function for longitudes"""
        self.assertItemsEqual(local.load_file(
            self.file_path, "value").lons, self.longitudes)

    def test_function_load_file_times(self):
        """To test load_file function for times"""
        newTimes = datetime.datetime(2001, 1, 1), datetime.datetime(
            2001, 2, 1), datetime.datetime(2001, 3, 1)
        self.assertItemsEqual(local.load_file(
            self.file_path, "value").times, newTimes)

    def test_function_load_file_alt_lats(self):
        """To test load_file function for lats with different variable names"""
        self.assertItemsEqual(local.load_file(
            self.file_path, "value", lat_name="alt_lat").lats, self.alt_lats)

    def test_function_load_file_alt_lons(self):
        """To test load_file function for lons with different variable names"""
        self.assertItemsEqual(local.load_file(
            self.file_path, "value", lon_name="alt_lon").lons, self.alt_lons)

    def test_function_load_file_alt_times(self):
        """To test load_file function for times with different variable names"""
        newTimes = datetime.datetime(2001, 4, 1), datetime.datetime(
            2001, 5, 1), datetime.datetime(2001, 6, 1)
        self.assertItemsEqual(local.load_file(
            self.file_path, "value", time_name="alt_time").times, newTimes)

    def test_function_load_file_values(self):
        """To test load_file function for values"""
        new_values = self.values[:, 0, :, :]
        self.assertTrue(numpy.allclose(local.load_file(
            self.file_path, "value").values, new_values))

    def test_custom_dataset_name(self):
        """Test adding a custom name to a dataset"""
        ds = local.load_file(self.file_path, 'value', name='foo')
        self.assertEqual(ds.name, 'foo')

    def test_dataset_origin(self):
        ds = local.load_file(self.file_path, 'value', elevation_index=1)
        expected_keys = set(['source', 'path', 'lat_name', 'lon_name',
                             'time_name', 'elevation_index'])
        self.assertEqual(set(ds.origin.keys()), expected_keys)
        self.assertEqual(ds.origin['source'], 'local')


class TestLoadMultipleFiles(unittest.TestCase):

    def setUp(self):
        # Read netCDF file
        self.file_path = create_netcdf_object()
        self.netCDF_file = netCDF4.Dataset(self.file_path, 'r')
        self.latitudes = self.netCDF_file.variables['latitude'][:]
        self.longitudes = self.netCDF_file.variables['longitude'][:]
        self.values = self.netCDF_file.variables['value'][:]
        self.variable_name_list = ['latitude',
                                   'longitude', 'time', 'level', 'value']
        self.possible_value_name = ['latitude', 'longitude', 'time', 'level']

    def tearDown(self):
        os.remove(self.file_path)

    def test_function_load_multiple_files_data_name(self):
        dataset = local.load_multiple_files(self.file_path, "value")
        self.assertEqual([dataset[0].name], ['data'])

    def test_function_load_multiple_files_lons(self):
        """To test load_multiple_file function for longitudes"""
        dataset = local.load_multiple_files(self.file_path, "value")
        self.assertItemsEqual(dataset[0].lons, self.longitudes)

    def test_function_load_multiple_files_times(self):
        """To test load_multiple_files function for times"""
        dataset = local.load_multiple_files(self.file_path, "value")

        newTimes = datetime.datetime(2001, 1, 1), datetime.datetime(
            2001, 2, 1), datetime.datetime(2001, 3, 1)
        self.assertItemsEqual(dataset[0].times, newTimes)

    def test_function_load_multiple_files_values(self):
        """To test load_multiple_files function for values"""
        new_values = self.values[:, 0, :, :]
        dataset = local.load_multiple_files(
            self.file_path, "value")
        self.assertTrue(numpy.allclose(dataset[0].values, new_values))

    def test_load_multiple_files_custom_dataset_name(self):
        """Test adding a custom name to a dataset"""
        dataset = local.load_multiple_files(self.file_path,
                                            "value",
                                            dataset_name='foo')
        self.assertEqual(dataset[0].name, 'foo')

    def test_dataset_origin(self):
        dataset = local.load_multiple_files(self.file_path, 'value')
        expected_keys = set(['source', 'path', 'lat_name', 'lon_name',
                             'time_name'])
        self.assertEqual(set(dataset[0].origin.keys()), expected_keys)
        self.assertEqual(dataset[0].origin['source'], 'local')


class TestLoadDatasetFromMultipleNetcdfFiles(unittest.TestCase):

    def setUp(self):
        self.file_path = create_netcdf_object()
        self.netCDF_file = netCDF4.Dataset(self.file_path, 'r+')
        self.latitudes = self.netCDF_file.variables['latitude'][:]
        self.longitudes = self.netCDF_file.variables['longitude'][:]
        self.alt_lats = self.netCDF_file.variables['alt_lat'][:]
        self.alt_lons = self.netCDF_file.variables['alt_lon'][:]
        self.values = self.netCDF_file.variables['value'][:]
        self.variable_name_list = ['latitude',
                                   'longitude', 'time', 'level', 'value']
        self.possible_value_name = ['latitude', 'longitude', 'time', 'level']
        self.dataset = local.load_dataset_from_multiple_netcdf_files(
            variable_name='value',
            file_path='',
            filename_pattern=[
                self.file_path])
        self.alt_dataset = local.load_dataset_from_multiple_netcdf_files(
            variable_name='value',
            lat_name='alt_lat',
            lon_name='alt_lon',
            time_name='alt_time',
            file_path='',
            filename_pattern=[
                self.file_path])

    def tearDown(self):
        os.remove(self.file_path)

    def test_variable_name(self):
        self.assertEqual(self.dataset.variable, 'value')

    def test_function_load_dataset_from_multiple_netcdf_files_lats(self):
        """To test load_multiple_files function for times"""
        _, self.latitudes = numpy.meshgrid(self.longitudes, self.latitudes)
        numpy.testing.assert_array_equal(self.dataset.lats, self.latitudes)

    def test_function_load_dataset_from_multiple_netcdf_files_lons(self):
        """To test load_multiple_files function for times"""
        self.longitudes, _ = numpy.meshgrid(self.longitudes, self.latitudes)
        numpy.testing.assert_array_equal(self.dataset.lons, self.longitudes)

    def test_function_load_dataset_from_multiple_netcdf_files_times(self):
        """To test load_multiple_files function for times"""
        newTimes = datetime.datetime(2001, 1, 1), datetime.datetime(
            2001, 2, 1), datetime.datetime(2001, 3, 1)
        self.assertItemsEqual(self.dataset.times, newTimes)

    def test_function_load_dataset_from_multiple_netcdf_files_alt_lats(self):
        """To test load_multiple_files function for non-default lats"""
        _, self.alt_lats = numpy.meshgrid(self.alt_lons, self.alt_lats)
        numpy.testing.assert_array_equal(self.alt_dataset.lats, self.alt_lats)

    def test_function_load_dataset_from_multiple_netcdf_files_alt_lons(self):
        """To test load_multiple_files function for non-default lons"""
        self.alt_lons, _ = numpy.meshgrid(self.alt_lons, self.alt_lats)
        numpy.testing.assert_array_equal(self.alt_dataset.lons, self.alt_lons)

    def test_function_load_dataset_from_multiple_netcdf_files_alt_times(self):
        """To test load_multiple_files function for non-default times"""
        newTimes = datetime.datetime(2001, 4, 1), datetime.datetime(
            2001, 5, 1), datetime.datetime(2001, 6, 1)
        self.assertItemsEqual(self.alt_dataset.times, newTimes)

    def test_function_load_dataset_from_multiple_netcdf_files_values(self):
        """To test load_multiple_files function for values"""
        new_values = self.values[:, 0, :, :]
        self.assertTrue(numpy.allclose(self.dataset.values, new_values))


class test_get_netcdf_variable_names(unittest.TestCase):
    file_path = "http://zipper.jpl.nasa.gov/dist/"
    test_model = "AFRICA_KNMI-RACMO2.2b_CTL_ERAINT_MM_50km_1989-2008_tasmax.nc"

    def setUp(self):
        urllib.urlretrieve(self.file_path + self.test_model, self.test_model)
        self.invalid_netcdf_path = create_invalid_dimensions_netcdf_object()
        self.netcdf = netCDF4.Dataset(self.test_model, mode='r')

    def tearDown(self):
        os.remove(self.invalid_netcdf_path)
        os.remove(self.test_model)

    def test_valid_latitude(self):
        self.lat = local._get_netcdf_variable_name(local.LAT_NAMES,
                                                   self.netcdf,
                                                   "tasmax")
        self.assertEquals(self.lat, "rlat")

    def test_invalid_dimension_latitude(self):
        self.netcdf = netCDF4.Dataset(self.invalid_netcdf_path, mode='r')
        self.lat = local._get_netcdf_variable_name(local.LAT_NAMES,
                                                   self.netcdf,
                                                   "value")
        self.assertEquals(self.lat, "latitude")

    def test_dimension_variable_name_mismatch(self):
        self.netcdf = netCDF4.Dataset(self.invalid_netcdf_path, mode='r')
        self.lat = local._get_netcdf_variable_name(
            ["lat_dim"] + local.LAT_NAMES,
            self.netcdf,
            "value")
        self.assertEquals(self.lat, "latitude")

    def test_no_match_latitude(self):
        with self.assertRaises(ValueError):
            self.lat = local._get_netcdf_variable_name(['notAVarName'],
                                                       self.netcdf,
                                                       "tasmax")


def create_netcdf_object():
    # To create the temporary netCDF file
    file_path = '/tmp/temporaryNetcdf.nc'
    netCDF_file = netCDF4.Dataset(file_path, 'w', format='NETCDF4')
    # To create dimensions
    netCDF_file.createDimension('lat_dim', 5)
    netCDF_file.createDimension('lon_dim', 5)
    netCDF_file.createDimension('time_dim', 3)
    netCDF_file.createDimension('level_dim', 2)
    # To create variables
    latitudes = netCDF_file.createVariable('latitude', 'd', ('lat_dim',))
    longitudes = netCDF_file.createVariable('longitude', 'd', ('lon_dim',))
    times = netCDF_file.createVariable('time', 'd', ('time_dim',))
    # unusual variable names to test optional arguments for Dataset constructor
    alt_lats = netCDF_file.createVariable('alt_lat', 'd', ('lat_dim',))
    alt_lons = netCDF_file.createVariable('alt_lon', 'd', ('lon_dim',))
    alt_times = netCDF_file.createVariable('alt_time', 'd', ('time_dim',))
    levels = netCDF_file.createVariable('level', 'd', ('level_dim',))
    values = netCDF_file.createVariable('value', 'd',
                                        ('time_dim',
                                         'level_dim',
                                         'lat_dim',
                                         'lon_dim')
                                        )

    # To latitudes and longitudes for five values
    latitudes_data = numpy.arange(5.)
    longitudes_data = numpy.arange(150., 155.)
    # Three months of data.
    times_data = numpy.arange(3)
    # Two levels
    levels_data = [100, 200]
    # Create 150 values
    values_data = numpy.array([i for i in range(150)])
    # Reshape values to 4D array (level, time, lats, lons)
    values_data = values_data.reshape(len(times_data), len(
        levels_data), len(latitudes_data), len(longitudes_data))

    # Ingest values to netCDF file
    latitudes[:] = latitudes_data
    longitudes[:] = longitudes_data
    times[:] = times_data
    alt_lats[:] = latitudes_data + 10
    alt_lons[:] = longitudes_data - 10
    alt_times[:] = times_data
    levels[:] = levels_data
    values[:] = values_data
    # Assign time info to time variable
    netCDF_file.variables['time'].units = 'months since 2001-01-01 00:00:00'
    netCDF_file.variables[
        'alt_time'].units = 'months since 2001-04-01 00:00:00'
    netCDF_file.variables['value'].units = 'foo_units'
    netCDF_file.close()
    return file_path


def create_invalid_dimensions_netcdf_object():
    # To create the temporary netCDF file
    file_path = '/tmp/temporaryNetcdf.nc'
    netCDF_file = netCDF4.Dataset(file_path, 'w', format='NETCDF4')
    # To create dimensions
    netCDF_file.createDimension('lat_dim', 5)
    netCDF_file.createDimension('lon_dim', 5)
    netCDF_file.createDimension('time_dim', 3)
    netCDF_file.createDimension('level_dim', 2)
    # To create variables
    latitudes = netCDF_file.createVariable('latitude', 'd', ('lat_dim',))
    longitudes = netCDF_file.createVariable('longitude', 'd', ('lon_dim',))
    times = netCDF_file.createVariable('time', 'd', ('time_dim',))
    levels = netCDF_file.createVariable('level', 'd', ('level_dim',))
    values = netCDF_file.createVariable('value',
                                        'd',
                                        ('level_dim',
                                         'time_dim',
                                         'lat_dim',
                                         'lon_dim')
                                        )
    # To latitudes and longitudes for five values
    latitudes = range(0, 5)
    longitudes = range(200, 205)
    # Three months of data
    times = range(3)
    # Two levels
    levels = [100, 200]
    # Create 150 values
    values = numpy.array([i for i in range(150)])
    # Reshape values to 4D array (level, time, lats, lons)
    values = values.reshape(len(levels), len(
        times), len(latitudes), len(longitudes))
    # Ingest values to netCDF file
    latitudes[:] = latitudes
    longitudes[:] = longitudes
    times[:] = times
    levels[:] = levels
    values[:] = values
    # Assign time info to time variable
    netCDF_file.variables['time'].units = 'months since 2001-01-01 00:00:00'
    netCDF_file.close()
    return file_path


if __name__ == '__main__':
    unittest.main()
