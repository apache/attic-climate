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

'''Unit test for the metrics.py module.'''

import unittest
import datetime as dt

from ocw.metrics import Bias, TemporalStdDev
from ocw.dataset import Dataset

import numpy as np
import numpy.testing as npt

class TestBias(unittest.TestCase):
    '''Test the metrics.Bias metric.'''
    def setUp(self):
        self.bias = Bias()
        #Initialize reference dataset
        self.reference_lat = np.array([10, 12, 14, 16, 18])
        self.reference_lon = np.array([100, 102, 104, 106, 108])
        self.reference_time = np.array([dt.datetime(2000, x, 1) for x in range(1, 13)])
        flat_array = np.array(range(300))
        self.reference_value = flat_array.reshape(12, 5, 5)
        self.reference_variable = 'prec'
        self.reference_dataset = Dataset(self.reference_lat, self.reference_lon,
            self.reference_time, self.reference_value, self.reference_variable)
        #Initialize target dataset
        self.target_lat = np.array([1, 2, 4, 6, 8])
        self.target_lon = np.array([10, 12, 14, 16, 18])
        self.target_time = np.array([dt.datetime(2001, x, 1) for x in range(1, 13)])
        flat_array = np.array(range(300, 600))
        self.target_value = flat_array.reshape(12, 5, 5)
        self.target_variable = 'tasmax'
        self.target_dataset = Dataset(self.target_lat, self.target_lon, self.target_time,
            self.target_value, self.target_variable)


    def test_function_run(self):
        '''Test bias function between reference dataset and target dataset.'''
        expected_result = np.zeros((12, 5, 5), dtype=np.int)
        expected_result.fill(-300)
        np.testing.assert_array_equal(self.bias.run(self.reference_dataset, self.target_dataset), expected_result)


class TestTemporalStdDev(unittest.TestCase):
    '''Test the metrics.TemporalStdDev metric.'''
    def setUp(self):
        self.temporal_std_dev = TemporalStdDev()
        #Initialize target dataset
        self.target_lat = np.array([10, 12, 14, 16, 18])
        self.target_lon = np.array([100, 102, 104, 106, 108])
        self.target_time = np.array([dt.datetime(2000, x, 1) for x in range(1, 13)])
        flat_array = np.array(range(300))
        self.target_value = flat_array.reshape(12, 5, 5)
        self.target_variable = 'prec'
        self.target_dataset = Dataset(self.target_lat, self.target_lon, self.target_time,
            self.target_value, self.target_variable)


    def test_function_run(self):
        '''Test TemporalStdDev function for target dataset.'''
        expected_result = np.zeros((5, 5),)
        expected_result.fill(90.13878189)
        npt.assert_almost_equal(self.temporal_std_dev.run(self.target_dataset), expected_result)

if __name__ == '__main__':
    unittest.main()
