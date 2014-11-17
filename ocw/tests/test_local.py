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
import urllib
import netCDF4
import datetime
import inspect
import test_local # Import test_local so we can use inspect to get the path 
import ocw.data_source.local as local


class test_load_file(unittest.TestCase):

    def setUp(self):
        #Read netCDF file
        self.file_path = create_netcdf_object()
        self.netCDF_file = netCDF4.Dataset(self.file_path, 'r')
        self.latitudes = self.netCDF_file.variables['latitude'][:]
        self.longitudes = self.netCDF_file.variables['longitude'][:]
        self.values = self.netCDF_file.variables['value'][:]
        self.variable_name_list = ['latitude', 'longitude', 'time', 'level', 'value']
        self.possible_value_name = ['latitude', 'longitude', 'time', 'level']
        
    def tearDown(self):
        os.remove(self.file_path)
    

    def test_function_load_file_lats(self):
        '''To test load_file function for latitudes'''
        self.assertItemsEqual(local.load_file(self.file_path, "value").lats, self.latitudes)


    def test_function_load_file_lons(self):
        '''To test load_file function for longitudes'''
        self.assertItemsEqual(local.load_file(self.file_path, "value").lons, self.longitudes)


    def test_function_load_file_times(self):
        '''To test load_file function for times'''
        newTimes = datetime.datetime(2001,01,01), datetime.datetime(2001,02,01), datetime.datetime(2001,03,01)
        self.assertItemsEqual(local.load_file(self.file_path, "value").times, newTimes)


    def test_function_load_file_values(self):
        '''To test load_file function for values'''
        new_values = self.values[0,:,:,:]
        self.assertTrue(numpy.allclose(local.load_file(self.file_path, "value").values, new_values))

    def test_custom_dataset_name(self):
        '''Test adding a custom name to a dataset'''
        ds = local.load_file(self.file_path, 'value', name='foo')
        self.assertEqual(ds.name, 'foo')

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
        self.lat = local._get_netcdf_variable_name(
                                        local.LAT_NAMES, 
                                        self.netcdf, 
                                        "tasmax")
        self.assertEquals(self.lat, "rlat")

    def test_invalid_dimension_latitude(self):
        self.netcdf = netCDF4.Dataset(self.invalid_netcdf_path, mode='r')
        self.lat = local._get_netcdf_variable_name(
                                        local.LAT_NAMES,
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
            self.lat = local._get_netcdf_variable_name(
                                            ['notAVarName'],
                                            self.netcdf, 
                                            "tasmax")

def create_netcdf_object():
        #To create the temporary netCDF file
        file_path = '/tmp/temporaryNetcdf.nc'
        netCDF_file = netCDF4.Dataset(file_path, 'w',  format='NETCDF4')
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
        latitudes = range(0,5)
        longitudes = range(200,205)
        #Three months of data
        #Two levels
        levels = [100, 200]
        #Create 150 values
        values = numpy.array([i for i in range(150)])
        #Reshape values to 4D array (level, time, lats, lons)
        values = values.reshape(len(levels), len(times),len(latitudes),len(longitudes))
        #Ingest values to netCDF file
        latitudes[:] = latitudes
        longitudes[:] = longitudes
        times[:] = numpy.array(range(3))
        levels[:] = levels
        values[:] = values
        #Assign time info to time variable
        netCDF_file.variables['time'].units = 'months since 2001-01-01 00:00:00' 
        netCDF_file.close()
        return file_path

def create_invalid_dimensions_netcdf_object():
        #To create the temporary netCDF file
        file_path = '/tmp/temporaryNetcdf.nc'
        netCDF_file = netCDF4.Dataset(file_path, 'w', format='NETCDF4')
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
        latitudes = range(0,5)
        longitudes = range(200,205)
        #Three months of data
        times = range(3)
        #Two levels
        levels = [100, 200]
        #Create 150 values
        values = numpy.array([i for i in range(150)])
        #Reshape values to 4D array (level, time, lats, lons)
        values = values.reshape(len(levels), len(times),len(latitudes),len(longitudes))
        #Ingest values to netCDF file
        latitudes[:] = latitudes
        longitudes[:] = longitudes
        times[:] = times
        levels[:] = levels
        values[:] = values
        #Assign time info to time variable
        netCDF_file.variables['time'].units = 'months since 2001-01-01 00:00:00' 
        netCDF_file.close()
        return file_path


if __name__ == '__main__':
    unittest.main()
