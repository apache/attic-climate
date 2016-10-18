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

import unittest
import os
import netCDF4
import numpy as np
from ocw.dataset import Dataset
from ocw.dataset_loader import DatasetLoader


class TestDatasetLoader(unittest.TestCase):

    def setUp(self):
        # Read netCDF file
        self.file_path = create_netcdf_object()
        self.netCDF_file = netCDF4.Dataset(self.file_path, 'r')
        self.latitudes = self.netCDF_file.variables['latitude'][:]
        self.longitudes = self.netCDF_file.variables['longitude'][:]
        self.times = self.netCDF_file.variables['time'][:]
        self.alt_lats = self.netCDF_file.variables['alt_lat'][:]
        self.alt_lons = self.netCDF_file.variables['alt_lon'][:]
        self.values = self.netCDF_file.variables['value'][:]
        self.values2 = self.values + 1

        # Set up config
        self.config = {'file_path': self.file_path, 'variable_name': 'value'}
        self.new_data_source_config = {'loader_name': 'foo',
                                       'lats': self.latitudes,
                                       'lons': self.longitudes,
                                       'times': self.times,
                                       'values': self.values2,
                                       'variable': 'value'}

    def tearDown(self):
        os.remove(self.file_path)

    def testNewDataSource(self):
        '''
        Ensures that custom data source loaders can be added
        '''
        self.loader = DatasetLoader(self.new_data_source_config)

        # Here the data_source "foo" represents the Dataset constructor
        self.loader.add_source_loader('foo', build_dataset)
        self.loader.load_datasets()
        self.assertEqual(self.loader.datasets[0].origin['source'], 'foo')
        np.testing.assert_array_equal(self.loader.datasets[0].values,
                                      self.values2)

    def testExistingDataSource(self):
        '''
        Ensures that existing data source loaders can be added
        '''
        self.loader = DatasetLoader(self.config)
        self.loader.load_datasets()
        self.assertEqual(self.loader.datasets[0].origin['source'], 'local')
        np.testing.assert_array_equal(self.loader.datasets[0].values,
                                      self.values)

    def testMultipleDataSources(self):
        '''
        Test for when multiple dataset configs are specified
        '''
        self.loader = DatasetLoader(self.config, self.new_data_source_config)

        # Here the data_source "foo" represents the Dataset constructor
        self.loader.add_source_loader('foo', build_dataset)
        self.loader.load_datasets()
        self.assertEqual(self.loader.datasets[0].origin['source'],
                         'local')
        self.assertEqual(self.loader.datasets[1].origin['source'],
                         'foo')
        np.testing.assert_array_equal(self.loader.datasets[0].values,
                                      self.values)
        np.testing.assert_array_equal(self.loader.datasets[1].values,
                                      self.values2)


def build_dataset(*args, **kwargs):
    '''
    Wrapper to Dataset constructor from fictitious 'foo' data_source.
    '''
    origin = {'source': 'foo'}
    return Dataset(*args, origin=origin, **kwargs)


def create_netcdf_object():
    # To create the temporary netCDF file
    file_path = '/tmp/temporaryNetcdf.nc'
    netCDF_file = netCDF4.Dataset(file_path, 'w', format='NETCDF4')
    # To create dimensions
    netCDF_file.createDimension('lat_dim', 5)
    netCDF_file.createDimension('lon_dim', 5)
    netCDF_file.createDimension('time_dim', 3)
    # To create variables
    latitudes = netCDF_file.createVariable('latitude', 'd', ('lat_dim',))
    longitudes = netCDF_file.createVariable('longitude', 'd', ('lon_dim',))
    times = netCDF_file.createVariable('time', 'd', ('time_dim',))
    # unusual variable names to test optional arguments for Dataset constructor
    alt_lats = netCDF_file.createVariable('alt_lat', 'd', ('lat_dim',))
    alt_lons = netCDF_file.createVariable('alt_lon', 'd', ('lon_dim',))
    alt_times = netCDF_file.createVariable('alt_time', 'd', ('time_dim',))
    values = netCDF_file.createVariable('value', 'd',
                                        ('time_dim',
                                         'lat_dim',
                                         'lon_dim')
                                        )

    # To latitudes and longitudes for five values
    latitudes_data = np.arange(5.)
    longitudes_data = np.arange(150., 155.)
    # Three months of data.
    times_data = np.arange(3)
    # Create 150 values
    values_data = np.array([i for i in range(75)])
    # Reshape values to 4D array (level, time, lats, lons)
    values_data = values_data.reshape(len(times_data), len(latitudes_data),
                                      len(longitudes_data))

    # Ingest values to netCDF file
    latitudes[:] = latitudes_data
    longitudes[:] = longitudes_data
    times[:] = times_data
    alt_lats[:] = latitudes_data + 10
    alt_lons[:] = longitudes_data - 10
    alt_times[:] = times_data
    values[:] = values_data
    # Assign time info to time variable
    netCDF_file.variables['time'].units = 'months since 2001-01-01 00:00:00'
    netCDF_file.variables[
        'alt_time'].units = 'months since 2001-04-01 00:00:00'
    netCDF_file.variables['value'].units = 'foo_units'
    netCDF_file.close()
    return file_path

if __name__ == '__main__':
    unittest.main()
