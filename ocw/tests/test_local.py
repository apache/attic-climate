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
import numpy
import numpy.ma as ma
import os
import netCDF4
import datetime
from data_source.local import *


class test_load_file(unittest.TestCase):


    def setUp(self):
        #To create the temporary netCDF file
        self.file_path = os.getcwd() + '/temporaryNetcdf.nc'
        netCDF_file = netCDF4.Dataset(self.file_path, 'w',  format='NETCDF4')
        #To create dimensions
        netCDF_file.createDimension('lat_dim', 5)
        netCDF_file.createDimension('lon_dim', 5)
        netCDF_file.createDimension('time_dim', 3)
        netCDF_file.createDimension('level_dim', 2)
        #To create variables
        latitudes = netCDF_file.createVariable('latitude', 'd', ('lat_dim',))
        longitudes = netCDF_file.createVariable('longitude', 'd', ('lon_dim',))
        times = netCDF_file.createVariable('time', 'd', ('time_dim',))
        levels = netCDF_file.createVariable('level', 'd', ('level_dim',))
        values = netCDF_file.createVariable('value', 'd', ('level_dim', 'time_dim', 'lat_dim', 'lon_dim'))
        #To latitudes and longitudes for five values
        self.latitudes = range(0,5)
        self.longitudes = range(200,205)
        #Three months of data
        self.times = range(3)
        #Two levels
        self.levels = [100, 200]
        #Create 150 values
        self.values = numpy.array([i for i in range(150)])
        #Reshape values to 4D array (level, time, lats, lons)
        self.values = self.values.reshape(len(self.levels), len(self.times),len(self.latitudes),len(self.longitudes))
        #Ingest values to netCDF file
        latitudes[:] = self.latitudes
        longitudes[:] = self.longitudes
        times[:] = self.times
        levels[:] = self.levels
        values[:] = self.values
        #Assigne time info to time variable
        netCDF_file.variables['time'].units = 'months since 2001-01-01 00:00:00' 
        netCDF_file.close()
        #Read netCDF file
        self.netCDF_file = netCDF4.Dataset(self.file_path, 'r')
        self.user_value_variable_name = 'value'
        self.variable_name_list = ['latitude', 'longitude', 'time', 'level', 'value']
        self.possible_value_name = ['latitude', 'longitude', 'time', 'level']


    def tearDown(self):
        '''To remove the temporary netCDF file'''
        os.remove(self.file_path)


    def test_function_load_file_lats(self):
        '''To test load_file function for latitudes'''
        self.assertItemsEqual(load_file(self.file_path, None).lats, self.latitudes)


    def test_function_load_file_lons(self):
        '''To test load_file function for longitudes'''
        self.assertItemsEqual(load_file(self.file_path, None).lons, self.longitudes)


    def test_function_load_file_times(self):
        '''To test load_file function for times'''
        newTimes = datetime(2001,01,01), datetime(2001,02,01), datetime(2001,03,01)
        self.assertItemsEqual(load_file(self.file_path, None).times, newTimes)


    def test_function_load_file_values(self):
        '''To test load_file function for values'''
        new_values = self.values[0,:,:,:]
        self.assertTrue(numpy.allclose(load_file(self.file_path, None).values, new_values))


if __name__ == '__main__':
    unittest.main()