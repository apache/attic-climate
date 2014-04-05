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

'''Unit tests for the Dataset.py module'''

import unittest
from ocw.dataset import Dataset, Bounds
import numpy as np
import datetime as dt

class TestDatasetAttributes(unittest.TestCase):
    def setUp(self):
        self.lat = np.array([10, 12, 14, 16, 18])
        self.lon = np.array([100, 102, 104, 106, 108])
        self.time = np.array([dt.datetime(2000, x, 1) for x in range(1, 13)])
        flat_array = np.array(range(300))
        self.value = flat_array.reshape(12, 5, 5)
        self.variable = 'prec'
        self.test_dataset = Dataset(self.lat, self.lon, self.time, 
                                    self.value, self.variable)

    def test_lats(self):
        self.assertItemsEqual(self.test_dataset.lats, self.lat)

    def test_lons(self):
        self.assertItemsEqual(self.test_dataset.lons, self.lon)

    def test_times(self):
        self.assertItemsEqual(self.test_dataset.times, self.time)

    def test_values(self):
        self.assertEqual(self.test_dataset.values.all(), self.value.all())

    def test_variable(self):
        self.assertEqual(self.test_dataset.variable, self.variable)

class TestInvalidDatasetInit(unittest.TestCase):
    def setUp(self):
        self.lat = np.array([10, 12, 14, 16, 18])
        self.lon = np.array([100, 102, 104, 106, 108])
        self.time = np.array([dt.datetime(2000, x, 1) for x in range(1, 13)])
        flat_array = np.array(range(300))
        self.value = flat_array.reshape(12, 5, 5)
        self.values_in_wrong_order = flat_array.reshape(5, 5, 12)

    def test_bad_lat_shape(self):
        self.lat = np.array([[1, 2], [3, 4]])
        with self.assertRaises(ValueError):
            Dataset(self.lat, self.lon, self.time, self.value, 'prec')

    def test_bad_lon_shape(self):
        self.lon = np.array([[1, 2], [3, 4]])
        with self.assertRaises(ValueError):
            Dataset(self.lat, self.lon, self.time, self.value, 'prec')

    def test_bad_times_shape(self):
        self.time = np.array([[1, 2], [3, 4]])
        with self.assertRaises(ValueError):
            Dataset(self.lat, self.lon, self.time, self.value, 'prec')

    def test_bad_values_shape(self):
        self.value = np.array([[1, 2], [2, 3], [3, 4], [4, 5]])
        with self.assertRaises(ValueError):
            Dataset(self.lat, self.lon, self.time, self.value, 'prec')

    def test_values_shape_mismatch(self):
        # If we change lats to this the shape of value will not match
        # up with the length of the lats array.
        self.lat = self.lat[:-2]
        with self.assertRaises(ValueError):
            Dataset(self.lat, self.lon, self.time, self.value, 'prec')
    
    def test_values_given_in_wrong_order(self):
         with self.assertRaises(ValueError):
            Dataset(self.lat, self.lon, self.time, self.values_in_wrong_order)

    def test_lons_values_incorrectly_gridded(self):
        times = np.array([dt.datetime(2000, x, 1) for x in range(1, 13)])
        lats = np.array(range(-30, 30))
        bad_lons = np.array(range(360))
        flat_array = np.array(range(len(times) * len(lats) * len(bad_lons)))
        values = flat_array.reshape(len(times), len(lats), len(bad_lons))

        ds = Dataset(lats, bad_lons, times, values)
        self.assertTrue(np.array_equal(ds.lons, range(-180, 180)))

class TestDatasetFunctions(unittest.TestCase):
    def setUp(self):
        self.lat = np.array([10, 12, 14, 16, 18])
        self.lon = np.array([100, 102, 104, 106, 108])
        self.time = np.array([dt.datetime(2000, x, 1) for x in range(1, 13)])
        flat_array = np.array(range(300))
        self.value = flat_array.reshape(12, 5, 5)
        self.variable = 'prec'
        self.test_dataset = Dataset(self.lat, self.lon, self.time, 
                                     self.value, self.variable)

    def test_spatial_boundaries(self):
        self.assertEqual(
            self.test_dataset.spatial_boundaries(), 
            (min(self.lat), max(self.lat), min(self.lon), max(self.lon)))

    def test_time_range(self):
        self.assertEqual(
            self.test_dataset.time_range(), 
            (dt.datetime(2000, 1, 1), dt.datetime(2000, 12, 1)))

    def test_spatial_resolution(self):
        self.assertEqual(self.test_dataset.spatial_resolution(), (2, 2))

    def test_temporal_resolution(self):
        self.assertEqual(self.test_dataset.temporal_resolution(), 'monthly')

class TestBounds(unittest.TestCase):
    def setUp(self):
        self.bounds = Bounds(-80, 80,                # Lats
                            -160, 160,               # Lons
                            dt.datetime(2000, 1, 1), # Start time
                            dt.datetime(2002, 1, 1)) # End time

    # Latitude tests
    def test_inverted_min_max_lat(self):
        with self.assertRaises(ValueError):
            self.bounds.lat_min = 81

        with self.assertRaises(ValueError):
            self.bounds.lat_max = -81

    # Lat Min
    def test_out_of_bounds_lat_min(self):
        with self.assertRaises(ValueError):
            self.bounds.lat_min = -91

        with self.assertRaises(ValueError):
            self.bounds.lat_min = 91

    # Lat Max
    def test_out_of_bounds_lat_max(self):
        with self.assertRaises(ValueError):
            self.bounds.lat_max = -91

        with self.assertRaises(ValueError):
            self.bounds.lat_max = 91

    # Longitude tests
    def test_inverted_max_max_lon(self):
        with self.assertRaises(ValueError):
            self.bounds.lon_min = 161

        with self.assertRaises(ValueError):
            self.bounds.lon_max = -161

    # Lon Min
    def test_out_of_bounds_lon_min(self):
        with self.assertRaises(ValueError):
            self.bounds.lon_min = -181

        with self.assertRaises(ValueError):
            self.bounds.lon_min = 181

    # Lon Max
    def test_out_of_bounds_lon_max(self):
        with self.assertRaises(ValueError):
            self.bounds.lon_max = -181

        with self.assertRaises(ValueError):
            self.bounds.lon_max = 181

    # Temporal tests
    def test_inverted_start_end_times(self):
        with self.assertRaises(ValueError):
            self.bounds.start = dt.datetime(2003, 1, 1)

        with self.assertRaises(ValueError):
            self.bounds.end = dt.datetime(1999, 1, 1)

    # Start tests
    def test_invalid_start(self):
        with self.assertRaises(ValueError):
            self.bounds.start = "This is not a date time object"

    # End tests
    def test_invalid_end(self):
        with self.assertRaises(ValueError):
            self.bounds.end = "This is not a date time object"

if __name__ == '__main__':
    unittest.main()
