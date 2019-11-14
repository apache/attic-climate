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
import datetime as dt
try:
    import ocw.data_source.dap as dap
except ImportError:
    warnings.warn('dap loaders missing. If this is needed, upgrade to python >=3.5.x.')
import platform
from ocw.dataset import Dataset

@unittest.skipIf(platform.python_version() < (3.5), "Pydap not supported in Python < 3.5")
class TestDap(unittest.TestCase):

    @classmethod
    def setUpClass(cls):

        cls.url = 'http://test.opendap.org/opendap/data/ncml/agg/dated/'\
                  'CG2006158_120000h_usfc.nc'
        cls.name = 'foo'
        '''
        The following exception handling should be removed once the opendap servers
        are working fine. The following code was added to fix the build temporarily
        More information - https://github.com/apache/climate/pull/419
        '''
        try :
            cls.dataset = dap.load(cls.url, 'CGusfc', name=cls.name)
        # The tests will be skipped if any exception is raised
        except Exception as e:
            raise unittest.SkipTest(e)
        '''
        # The tests fail for this dataset since the dataset does not have a time(1D) variable.
        # The tests fail because dap.py assumes that the openDAP datasets necessarily have the 
        # three variables 1D variables lat, lon and time and the lines 53,54 and 55 are written
        # on the same assumption.   
        cls.url2 = 'http://opendap-uat.jpl.nasa.gov/opendap/GeodeticsGravity/'\
                   'tellus/L3/mascon/RL05/JPL/CRI/netcdf/CLM4.SCALE_FACTOR.JPL.MSCNv01CRIv01.nc'
        cls.name2 = 'foo2'
        cls.dataset2 = dap.load(cls.url2, 'scale_factor', name=cls.name)'''

    @unittest.skipIf(platform.python_version() < (3.5), "Pydap not supported in Python < 3.5")
    def test_dataset_is_returned(self):
        self.assertTrue(isinstance(self.dataset, Dataset))

    @unittest.skipIf(platform.python_version() < (3.5), "Pydap not supported in Python < 3.5")
    def test_correct_lat_shape(self):
        self.assertEquals(len(self.dataset.lats), 29)

    @unittest.skipIf(platform.python_version() < (3.5), "Pydap not supported in Python < 3.5")
    def test_correct_lon_shape(self):
        self.assertEquals(len(self.dataset.lons), 26)

    @unittest.skipIf(platform.python_version() < (3.5), "Pydap not supported in Python < 3.5")
    def test_correct_time_shape(self):
        self.assertEquals(len(self.dataset.times), 1)

    @unittest.skipIf(platform.python_version() < (3.5), "Pydap not supported in Python < 3.5")
    def test_valid_date_conversion(self):
        start = dt.datetime(2006, 6, 7, 12)
        self.assertTrue(start == self.dataset.times[0])

    @unittest.skipIf(platform.python_version() < (3.5), "Pydap not supported in Python < 3.5")
    def test_custom_dataset_name(self):
        self.assertEquals(self.dataset.name, self.name)

    @unittest.skipIf(platform.python_version() < (3.5), "Pydap not supported in Python < 3.5")
    def test_dataset_origin(self):
        self.assertEquals(self.dataset.origin['source'], 'dap')
        self.assertEquals(self.dataset.origin['url'], self.url)

if __name__ == '__main__':
    unittest.main()
