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
import urllib
import os
import datetime
from dateutil.relativedelta import relativedelta

import netCDF4
import numpy as np

from ocw.dataset import Dataset
import ocw.utils as utils

class TestDecodeTimes(unittest.TestCase):
    test_model = '../ocw-ui/backend/tests/example_data/lat_lon_time.nc'

    def setUp(self):
        self.netcdf = netCDF4.Dataset(os.path.abspath(self.test_model), mode='r')

    def test_proper_return_format(self):
        times = utils.decode_time_values(self.netcdf, 'time')

        self.assertTrue(all([type(x) is datetime.datetime for x in times]))

    def test_valid_time_processing(self):
        start_time = datetime.datetime.strptime('1989-01-01 00:00:00', '%Y-%m-%d %H:%M:%S')
        end_time = datetime.datetime.strptime('2008-12-01 00:00:00', '%Y-%m-%d %H:%M:%S')
        times = utils.decode_time_values(self.netcdf, 'time')

        self.assertEquals(times[0], start_time)
        self.assertEquals(times[-1], end_time)

class TestTimeUnitsParse(unittest.TestCase):
    def test_valid_parse(self):
        units = utils.parse_time_units('minutes since a made up date')

        self.assertEquals(units, 'minutes')

    def test_invalid_parse(self):
        self.assertRaises(
            ValueError,
            utils.parse_time_units,
            'parsecs since a made up date'
        )

class TestTimeBaseParse(unittest.TestCase):
    def test_valid_time_base(self):
        base_time = utils.parse_time_base('days since 1988-06-10 00:00:00')
        start_time = datetime.datetime.strptime('1988-06-10 00:00:00', '%Y-%m-%d %H:%M:%S')

        self.assertEquals(base_time, start_time)

    def test_invalid_time_base(self):
        self.assertRaises(
            ValueError,
            utils.parse_time_base,
            'days since 1988g06g10g00g00g00'
        )

class TestBaseTimeStringParse(unittest.TestCase):
    def test_valid_time_base_string_parse(self):
        base = utils.parse_base_time_string('days since 1988-06-10 00:00:00')
        
        self.assertEquals(base, '1988-06-10 00:00:00')

    def test_invalid_time_base_string_parse(self):
        self.assertRaises(
            ValueError,
            utils.parse_base_time_string,
            'this string is not valid'
        )

class TestNormalizeLatLonValues(unittest.TestCase):
    def setUp(self):
        times = np.array([datetime.datetime(2000, x, 1) for x in range(1, 13)])
        self.lats = np.arange(-30, 30)
        self.lons = np.arange(360)
        flat_array = np.arange(len(times) * len(self.lats) * len(self.lons))
        self.values = flat_array.reshape(len(times), len(self.lats), len(self.lons))
        self.lats2 = np.array([-30, 0, 30])
        self.lons2 = np.array([0, 100, 200, 300])
        self.values2 = np.arange(12).reshape(3, 4)
        self.lats_unsorted = np.array([-30, 20, -50])
        self.lons_unsorted = np.array([-30, 20, -50, 40])

    def test_full_lons_shift(self):
        lats, lons, values = utils.normalize_lat_lon_values(self.lats,
                                                            self.lons,
                                                            self.values)
        np.testing.assert_array_equal(lons, np.arange(-180, 180))
        
    def test_lats_reversed(self):
        lons2 = np.arange(-180, 180)
        lats, lons, values = utils.normalize_lat_lon_values(self.lats[::-1],
                                                            lons2,
                                                            self.values[:, ::-1, :])
        np.testing.assert_array_equal(lats, self.lats)
        np.testing.assert_array_equal(values, self.values)
    
    def test_lons_shift_values(self):
        expected_vals = np.array([[2, 3, 0, 1],
                                  [6, 7, 4, 5],
                                  [10, 11, 8, 9]])
        lats, lons, values = utils.normalize_lat_lon_values(self.lats2,
                                                            self.lons2,
                                                            self.values2)
        np.testing.assert_array_equal(values, expected_vals)
        
    def test_shift_and_reversed(self):
        expected_vals = np.array([[10, 11, 8, 9],
                                  [6, 7, 4, 5],
                                  [2, 3, 0, 1]])
        lats, lons, values = utils.normalize_lat_lon_values(self.lats2[::-1],
                                                            self.lons2,
                                                            self.values2)
        np.testing.assert_array_equal(values, expected_vals)
        
    def test_lats_not_sorted(self):
        self.assertRaises(ValueError, 
                          utils.normalize_lat_lon_values,
                          self.lats_unsorted,
                          self.lons2,
                          self.values2)
                          
    def test_lons_not_sorted(self):
        self.assertRaises(ValueError, 
                          utils.normalize_lat_lon_values,
                          self.lats2,
                          self.lons_unsorted,
                          self.values2)

class TestReshapeMonthlyToAnnually(unittest.TestCase):
    ''' Testing function 'reshape_monthly_to_annually' from ocw.utils.py '''

    def setUp(self):
        self.lat = np.array([10, 12, 14, 16, 18])
        self.lon = np.array([100, 102, 104, 106, 108])
        self.time = np.array([datetime.datetime(2000, 1, 1) + relativedelta(months = x) for x in range(24)])
        flat_array = np.array(range(600))
        self.value = flat_array.reshape(24, 5, 5)
        self.variable = 'prec'
        self.test_dataset = Dataset(self.lat, self.lon, self.time, 
                                    self.value, self.variable)

    def test_reshape_full_year(self):
        new_times = np.array([datetime.datetime(1, 1, 1) + relativedelta(months = x) for x in range(12)])
        new_values = self.value.reshape(2, 12, 5, 5)
        values,times = utils.reshape_monthly_to_annually(self.test_dataset)
        np.testing.assert_array_equal(values, new_values)
        np.testing.assert_array_equal(times, new_times)

    def test_reshape_not_full_year(self):
        new_time = np.array([datetime.datetime(2000, 1, 1) + relativedelta(months = x) for x in range(26)])
        flat_array = np.array(range(650))
        value = flat_array.reshape(26, 5, 5)
        bad_dataset = Dataset(self.lat, self.lon, new_time, value, self.variable)

        self.assertRaises(ValueError, utils.reshape_monthly_to_annually, bad_dataset)

class TestCalcClimatologyYear(unittest.TestCase):
    ''' Testing function 'calc_climatology_year' from ocw.utils.py '''

    def setUp(self):
        self.lat = np.array([10, 12, 14, 16, 18])
        self.lon = np.array([100, 102, 104, 106, 108])
        self.time = np.array([datetime.datetime(2000, 1, 1) + relativedelta(months = x) for x in range(24)])
        flat_array = np.array(range(600))
        self.value = flat_array.reshape(24, 5, 5)
        self.variable = 'prec'
        self.test_dataset = Dataset(self.lat, self.lon, self.time,
                                    self.value, self.variable)

    def test_annually_mean(self):
        annually_mean = np.append(np.arange(137.5, 162.5, 1), np.arange(437.5, 462.5, 1))
        annually_mean.shape = (2, 5, 5)
        np.testing.assert_array_equal(
            utils.calc_climatology_year(self.test_dataset)[0], annually_mean)

    def test_total_mean(self):
        total_mean = np.arange(287.5, 312.5, 1)
        total_mean.shape = (5, 5)
        np.testing.assert_array_equal(
            utils.calc_climatology_year(self.test_dataset)[1], total_mean)


class TestCalcClimatologyMonthly(unittest.TestCase):
    ''' Tests the 'calc_climatology_monthly' method from ocw.utils.py '''

    def setUp(self):
        self.lats = np.array([10, 20, 30, 40, 50])
        self.lons = np.array([20, 30, 40, 50, 60])
        start_date = datetime.datetime(2000, 1, 1)
        self.times = np.array([start_date + relativedelta(months=x)
                               for x in range(36)])
        self.values = np.array([1]*300 + [2]*300 + [0]*300).reshape(36, 5, 5)
        self.variable = 'testdata'
        self.dataset = Dataset(self.lats, self.lons, self.times,
                               self.values, self.variable)

    def test_calc_climatology_monthly(self):
        expected_result = np.ones(300).reshape(12, 5, 5)
        actual_result = utils.calc_climatology_monthly(self.dataset)
        np.testing.assert_array_equal(actual_result, expected_result)
        

if __name__ == '__main__':
    unittest.main()
