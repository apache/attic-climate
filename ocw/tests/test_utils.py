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

import netCDF4
import numpy as np

import ocw.utils as utils

class TestDecodeTimes(unittest.TestCase):
    test_model = '../ocw-ui/backend/tests/example_data/lat_lon_time.nc'

    def setUp(self):
        self.netcdf = netCDF4.Dataset(os.path.abspath(self.test_model), mode='r')

    def test_proper_return_format(self):
        times = utils.decode_time_values(self.netcdf, 'time')

        self.assertTrue(all([type(x) is datetime.datetime for x in times]))

    def test_valid_time_processing(self):
        start_time = datetime.datetime.strptime('1988-06-10 00:00:00', '%Y-%m-%d %H:%M:%S')
        end_time = datetime.datetime.strptime('2008-01-27 00:00:00', '%Y-%m-%d %H:%M:%S')
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
        self.lats = np.array(range(-30, 30))
        self.lons = np.array(range(360))
        flat_array = np.array(range(len(times) * len(self.lats) * len(self.lons)))
        self.values = flat_array.reshape(len(times), len(self.lats), len(self.lons))

    def test_full_lons_shift(self):
        lats, lons, values = utils.normalize_lat_lon_values(self.lats,
                                                            self.lons,
                                                            self.values)
        self.assertTrue(np.array_equal(lons, range(-180, 180)))

if __name__ == '__main__':
    unittest.main()
