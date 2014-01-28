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

import ocw.utils as utils

class TestDecodeTimes(unittest.TestCase):
    test_model = "../ocw-ui/backend/tests/example_data/lat_lon_time.nc"

    def setUp(self):
        self.netcdf = netCDF4.Dataset(os.path.abspath(self.test_model), mode='r')

    def test_proper_return_format(self):
        times = utils.decode_time_values(self.netcdf, 'time')

        self.assertTrue(all([type(x) is datetime.datetime for x in times]))

if __name__ == '__main__':
    unittest.main()
