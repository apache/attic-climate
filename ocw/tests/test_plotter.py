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

'''Unit tests for the plotter.py module'''

import unittest
import numpy as np
from ocw import plotter


class TestNiceIntervalsFunction(unittest.TestCase):

    def test_nice_intervals(self):
        test_array = np.arange(0, 30)
        expected_array = np.arange(0, 30, 3)[1::]
        nlev = 10
        result = plotter._nice_intervals(test_array, nlev)
        np.testing.assert_array_equal(result, expected_array)

    def test_even_nice_intervals(self):
        test_array = np.array([-2, 0, 2])
        expected_array = np.array([-2., -1., 0., 1., 2.])
        nlev = 4
        result = plotter._nice_intervals(test_array, nlev)
        np.testing.assert_array_equal(result, expected_array)

    def test_odd_nice_intervals(self):
        test_array = np.array([-2, 0, 2])
        expected_array = np.array([-2., -1., 0., 1., 2.])
        nlev = 5
        result = plotter._nice_intervals(test_array, nlev)
        np.testing.assert_array_equal(result, expected_array)


class TestBestGridShapeFunction(unittest.TestCase):

    def test_returned_shape_small(self):
        nplots = 2
        oldshape = (2, 2)
        expected_shape = (1, 2)
        new_shape = plotter._best_grid_shape(nplots, oldshape)
        self.assertEqual(new_shape, expected_shape)

    def test_returned_shape_large(self):
        nplots = 57
        oldshape = (220, 12)
        expected_shape = (5, 12)
        new_shape = plotter._best_grid_shape(nplots, oldshape)
        self.assertEqual(new_shape, expected_shape)

    def test_invalid_shape(self):
        nplots = 2532
        oldshape = (22, 12)
        with self.assertRaises(ValueError):
            plotter._best_grid_shape(nplots, oldshape)

    def test_equal_number_of_plots_and_old_shape(self):
        nplots = 4
        oldshape = (2, 2)
        expected_shape = (2, 2)
        new_shape = plotter._best_grid_shape(nplots, oldshape)
        self.assertEqual(new_shape, expected_shape)


class TestFigshapeFunction(unittest.TestCase):

    def test_small_gridshape_size(self):
        gridshape = (2, 2)
        expected_width = 8.5
        expected_height = 5.5
        width, height = plotter._fig_size(gridshape)
        self.assertEqual(width, expected_width)
        self.assertEqual(height, expected_height)

    def test_large_gridshape_size(self):
        gridshape = (567, 1223)
        expected_width = 17.0
        expected_height = 5.5
        width, height = plotter._fig_size(gridshape)
        self.assertEqual(width, expected_width)
        self.assertEqual(height, expected_height)

    def test_small_gridshape_with_aspect(self):
        gridshape = (2, 2)
        expected_width = 5.5
        expected_height = 5.5
        width, height = plotter._fig_size(gridshape, aspect=(4 / 3))
        self.assertEqual(width, expected_width)
        self.assertEqual(height, expected_height)

    def test_large_gridshape_with_aspect(self):
        gridshape = (567, 1223)
        expected_width = 11.0
        expected_height = 5.5
        width, height = plotter._fig_size(gridshape, aspect=(16 / 9))
        self.assertEqual(width, expected_width)
        self.assertEqual(height, expected_height)

if __name__ == '__main__':
    unittest.main()
