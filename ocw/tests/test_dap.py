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
import ocw.data_source.dap as dap
from ocw.dataset import Dataset
import datetime as dt

class test_dap(unittest.TestCase):
    dataset = dap.load('http://test.opendap.org/dap/data/nc/sst.mnmean.nc.gz', 'sst')

    def test_dataset_is_returned(self):
        self.assertTrue(isinstance(self.dataset, Dataset))

    def test_correct_lat_shape(self):
        self.assertEquals(len(self.dataset.lats), 89)

    def test_correct_lon_shape(self):
        self.assertEquals(len(self.dataset.lons), 180)

    def test_correct_time_shape(self):
        self.assertEquals(len(self.dataset.times), 1857)

    def test_valid_date_conversion(self):
        start = dt.datetime(1854, 1, 1)
        self.assertTrue(start == self.dataset.times[0])

if __name__ == '__main__':
    unittest.main()
