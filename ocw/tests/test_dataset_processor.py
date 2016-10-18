#
#  Licensed to the Apache Software Foundation (ASF) under one or more
#  contributor license agreements.  See the NOTICE file distributed with
#  this work for additional information regarding copyright ownership.
#  The ASF licenses this file to You under the Apache License, Version 2.0
#  (the "License"); you may not use this file except in compliance with
#  the License.  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

import unittest
import datetime
import os

from ocw import dataset_processor as dp
from ocw import dataset as ds
from ocw.data_source import local
import numpy as np
import numpy.ma as ma

import logging
logging.basicConfig(level=logging.CRITICAL)


class TestTemporalSubset(unittest.TestCase):

    def setUp(self):
        self.ten_year_dataset = ten_year_monthly_dataset()

    def test_returned_dataset(self):
        self.dataset_times = np.array([datetime.datetime(year, month, 1)
                                       for year in range(2000, 2010)
                                       for month in range(1, 6)])
        self.tempSubset = dp.temporal_subset(self.ten_year_dataset, 1, 5)
        np.testing.assert_array_equal(
            self.dataset_times, self.tempSubset.times)

    def test_temporal_subset_with_average_time(self):
        self.dataset_times = np.array([datetime.datetime(year, 2, 1)
                                       for year in range(2000, 2010)])
        self.tempSubset = dp.temporal_subset(self.ten_year_dataset,
                                             1, 3,
                                             average_each_year=True)
        np.testing.assert_array_equal(self.dataset_times,
                                      self.tempSubset.times)

    def test_temporal_subset_with_average_values(self):
        self.tempSubset = dp.temporal_subset(self.ten_year_dataset,
                                             1, 3,
                                             average_each_year=True)
        self.dataset_values = np.ones([len(self.tempSubset.times),
                                       len(self.ten_year_dataset.lats),
                                       len(self.ten_year_dataset.lons)])
        np.testing.assert_array_equal(self.dataset_values,
                                      self.tempSubset.values)

    def test_temporal_subset_attributes(self):
        self.tempSubset = dp.temporal_subset(self.ten_year_dataset,
                                             1, 3,
                                             average_each_year=True)
        self.assertEqual(self.tempSubset.name, self.ten_year_dataset.name)
        self.assertEqual(self.tempSubset.variable,
                         self.ten_year_dataset.variable)
        self.assertEqual(self.tempSubset.units, self.ten_year_dataset.units)
        np.testing.assert_array_equal(self.tempSubset.lats,
                                      self.ten_year_dataset.lats)
        np.testing.assert_array_equal(self.tempSubset.lons,
                                      self.ten_year_dataset.lons)

    def test_temporal_subset_equal_start_end_month(self):
        self.dataset_times = np.array([datetime.datetime(year, 1, 1)
                                       for year in range(2000, 2010)])
        self.tempSubset = dp.temporal_subset(self.ten_year_dataset,
                                             1, 1,
                                             average_each_year=True)
        np.testing.assert_array_equal(self.dataset_times,
                                      self.tempSubset.times)

    def test_startMonth_greater_than_endMonth(self):
        self.dataset_times = np.array([datetime.datetime(year, month, 1)
                                       for year in range(2000, 2010)
                                       for month in [1, 8, 9, 10, 11, 12]])
        self.tempSubset = dp.temporal_subset(self.ten_year_dataset, 8, 1)
        np.testing.assert_array_equal(
            self.dataset_times, self.tempSubset.times)


class TestTemporalRebinWithTimeIndex(unittest.TestCase):

    def setUp(self):
        self.ten_year_dataset = ten_year_monthly_dataset()

    def test_time_dimension_multiple_of_orig_time_dimension(self):
        # ten_year_dataset.times.size is 120
        nt_avg = self.ten_year_dataset.times.size / 2
        # Temporal Rebin to exactly 2 (time) values
        dataset = dp.temporal_rebin_with_time_index(
            self.ten_year_dataset, nt_avg)
        start_time = self.ten_year_dataset.times[0]
        # First month of the middle year
        middle_element = self.ten_year_dataset.times.size / 2
        end_time = self.ten_year_dataset.times[middle_element]
        self.assertEqual(dataset.times.size,
                         self.ten_year_dataset.times.size / nt_avg)
        np.testing.assert_array_equal(dataset.times, [start_time, end_time])

    def test_time_dimension_not_multiple_of_orig_time_dimension(self):
        # ten_year_dataset.times.size is 120
        nt_avg = 11
        # Temporal Rebin to exactly 10 (time) values
        dataset = dp.temporal_rebin_with_time_index(
            self.ten_year_dataset, nt_avg)
        new_times = self.ten_year_dataset.times[::11][:-1]
        self.assertEqual(dataset.times.size,
                         self.ten_year_dataset.times.size / nt_avg)
        np.testing.assert_array_equal(dataset.times, new_times)

    def test_returned_dataset_attributes(self):
        nt_avg = 3
        dataset = dp.temporal_rebin_with_time_index(
            self.ten_year_dataset, nt_avg)
        new_times = self.ten_year_dataset.times[::3]
        new_values = self.ten_year_dataset.values[::3]
        self.assertEqual(self.ten_year_dataset.name, dataset.name)
        self.assertEqual(self.ten_year_dataset.origin, dataset.origin)
        self.assertEqual(self.ten_year_dataset.units, dataset.units)
        self.assertEqual(self.ten_year_dataset.variable, dataset.variable)
        np.testing.assert_array_equal(new_times, dataset.times)
        np.testing.assert_array_equal(new_values, dataset.values)
        np.testing.assert_array_equal(self.ten_year_dataset.lats, dataset.lats)
        np.testing.assert_array_equal(self.ten_year_dataset.lons, dataset.lons)


class TestVariableUnitConversion(unittest.TestCase):

    def setUp(self):
        self.ten_year_dataset = ten_year_monthly_dataset()
        self.ten_year_dataset.variable = 'temp'
        self.ten_year_dataset.units = 'celsius'

    def test_returned_variable_unit_celsius(self):
        ''' Tests returned dataset unit if original dataset unit is celcius '''
        dp.variable_unit_conversion(self.ten_year_dataset)
        self.assertEqual(self.ten_year_dataset.units, 'K')

    def test_returned_variable_unit_kelvin(self):
        ''' Tests returned dataset unit if original dataset unit is kelvin '''
        self.ten_year_dataset.units = 'K'
        another_dataset = dp.variable_unit_conversion(self.ten_year_dataset)
        self.assertEqual(another_dataset.units, self.ten_year_dataset.units)

    def test_temp_unit_conversion(self):
        ''' Tests returned dataset temp values '''
        self.ten_year_dataset.values = np.ones([
            len(self.ten_year_dataset.times),
            len(self.ten_year_dataset.lats),
            len(self.ten_year_dataset.lons)])
        values = self.ten_year_dataset.values + 273.15
        dp.variable_unit_conversion(self.ten_year_dataset)
        np.testing.assert_array_equal(self.ten_year_dataset.values, values)

    def test_returned_variable_unit_swe(self):
        ''' Tests returned dataset unit if original dataset unit is swe '''
        self.ten_year_dataset.variable = 'swe'
        self.ten_year_dataset.units = 'm'
        dp.variable_unit_conversion(self.ten_year_dataset)
        self.assertEqual(self.ten_year_dataset.variable, 'swe')
        self.assertEqual(self.ten_year_dataset.units, 'km')

    def test_returned_variable_unit_pr(self):
        '''
        Tests returned dataset unit if original dataset unit is kgm^-2s^-1
        '''
        self.ten_year_dataset.variable = 'pr'
        self.ten_year_dataset.units = 'kg m-2 s-1'
        dp.variable_unit_conversion(self.ten_year_dataset)
        self.assertEqual(self.ten_year_dataset.variable, 'pr')
        self.assertEqual(self.ten_year_dataset.units, 'mm/day')

    def test_water_flux_unit_conversion_swe(self):
        ''' Tests variable values in returned dataset '''
        self.ten_year_dataset.variable = 'swe'
        self.ten_year_dataset.units = 'm'
        values = self.ten_year_dataset.values + 999
        dp.variable_unit_conversion(self.ten_year_dataset)
        np.testing.assert_array_equal(self.ten_year_dataset.values, values)

    def test_water_flux_unit_conversion_pr(self):
        ''' Tests variable values in returned dataset '''
        self.ten_year_dataset.variable = 'pr'
        self.ten_year_dataset.units = 'kg m-2 s-1'
        values = self.ten_year_dataset.values + 86399
        dp.variable_unit_conversion(self.ten_year_dataset)
        np.testing.assert_array_equal(self.ten_year_dataset.values, values)


class TestTemporalSlice(unittest.TestCase):

    def test_returned_dataset_times(self):
        ''' Tests returned dataset times values '''
        self.ten_year_dataset = ten_year_monthly_dataset()
        start_index = 1
        end_index = 4
        dates = np.array([datetime.datetime(2000, month, 1)
                          for month in range(start_index + 1, end_index + 2)])
        new_dataset = dp.temporal_slice(self.ten_year_dataset,
                                        start_index,
                                        end_index)
        np.testing.assert_array_equal(new_dataset.times, dates)

    def test_returned_dataset_values(self):
        ''' Tests returned dataset variable values '''
        self.ten_year_dataset = ten_year_monthly_dataset()
        start_index = 1
        end_index = 4
        values = self.ten_year_dataset.values[start_index:end_index + 1]
        new_dataset = dp.temporal_slice(self.ten_year_dataset,
                                        start_index,
                                        end_index)
        np.testing.assert_array_equal(new_dataset.values, values)


class TestEnsemble(unittest.TestCase):

    def test_unequal_dataset_shapes(self):
        self.ten_year_dataset = ten_year_monthly_dataset()
        self.two_year_dataset = two_year_daily_dataset()
        with self.assertRaises(ValueError):
            self.ensemble_dataset = dp.ensemble(
                [self.ten_year_dataset, self.two_year_dataset])

    def test_ensemble_logic(self):
        self.datasets = []
        self.datasets.append(build_ten_cube_dataset(1))
        self.datasets.append(build_ten_cube_dataset(2))
        self.three = build_ten_cube_dataset(3)
        self.datasets.append(self.three)
        self.datasets.append(build_ten_cube_dataset(4))
        self.datasets.append(build_ten_cube_dataset(5))
        self.ensemble = dp.ensemble(self.datasets)
        self.ensemble_flat = self.ensemble.values.flatten()
        self.three_flat = self.three.values.flatten()
        np.testing.assert_array_equal(self.ensemble_flat, self.three_flat)

    def test_ensemble_name(self):
        self.ensemble_dataset_name = "Dataset Ensemble"
        self.datasets = []
        self.datasets.append(build_ten_cube_dataset(1))
        self.datasets.append(build_ten_cube_dataset(2))
        self.ensemble = dp.ensemble(self.datasets)
        self.assertEquals(self.ensemble.name, self.ensemble_dataset_name)


class TestTemporalRebin(unittest.TestCase):

    def setUp(self):
        self.ten_year_monthly_dataset = ten_year_monthly_dataset()
        self.ten_year_annual_times = np.array(
            [datetime.datetime(year, 7, 2) for year in range(2000, 2010)])
        self.two_years_daily_dataset = two_year_daily_dataset()

    def test_monthly_to_annual_rebin(self):
        annual_dataset = dp.temporal_rebin(
            self.ten_year_monthly_dataset, "annual")
        np.testing.assert_array_equal(
            annual_dataset.times, self.ten_year_annual_times)

    def test_monthly_to_full_rebin(self):
        full_dataset = dp.temporal_rebin(self.ten_year_monthly_dataset, "full")
        full_times = [datetime.datetime(2005, 1, 1)]
        self.assertEqual(full_dataset.times, full_times)

    def test_daily_to_monthly_rebin(self):
        """
        This test takes a really long time to run.
        TODO: Figure out where the performance drag is
        """
        monthly_dataset = dp.temporal_rebin(
            self.two_years_daily_dataset, "monthly")
        bins = list(set([datetime.datetime(
                        time_reading.year, time_reading.month, 15)
                    for time_reading in self.two_years_daily_dataset.times]))
        bins = np.array(bins)
        bins.sort()
        np.testing.assert_array_equal(monthly_dataset.times, bins)

    def test_daily_to_annual_rebin(self):
        annual_dataset = dp.temporal_rebin(
            self.two_years_daily_dataset, "annual")
        bins = list(set([datetime.datetime(
                        time_reading.year, 7, 2)
                    for time_reading in self.two_years_daily_dataset.times]))
        bins = np.array(bins)
        bins.sort()
        np.testing.assert_array_equal(annual_dataset.times, bins)

    def test_non_rebin(self):
        """
        This will take a monthly dataset and ask for a monthly rebin of
        28 days. The resulting dataset should have the same time values
        """
        monthly_dataset = dp.temporal_rebin(
            self.ten_year_monthly_dataset, "monthly")
        bins = list(set([datetime.datetime(
                        time_reading.year, time_reading.month, 15)
                    for time_reading in self.ten_year_monthly_dataset.times]))
        bins = np.array(bins)
        bins.sort()
        np.testing.assert_array_equal(monthly_dataset.times, bins)

    def test_variable_propagation(self):
        annual_dataset = dp.temporal_rebin(self.ten_year_monthly_dataset,
                                           "annual")
        self.assertEquals(annual_dataset.name,
                          self.ten_year_monthly_dataset.name)
        self.assertEquals(annual_dataset.variable,
                          self.ten_year_monthly_dataset.variable)

    def test_daily_to_daily_rebin(self):
        daily_dataset = dp.temporal_rebin(
            self.two_years_daily_dataset, "daily")
        np.testing.assert_array_equal(
            daily_dataset.times, self.two_years_daily_dataset.times)

    def test_invalid_unit_rebin(self):
        with self.assertRaises(ValueError):
            dp.temporal_rebin(self.two_years_daily_dataset, "days")


class TestRcmesSpatialRegrid(unittest.TestCase):

    def test_return_array_shape(self):
        spatial_values = np.ones([90, 180])
        spatial_values = ma.array(spatial_values)

        lat_range = ma.array(range(-89, 90, 2))
        lon_range = ma.array(range(-179, 180, 2))

        lons, lats = np.meshgrid(lon_range, lat_range)
        # Convert these to masked arrays
        lats = ma.array(lats)
        lons = ma.array(lons)

        lat2_range = np.array(range(-89, 90, 4))
        lon2_range = np.array(range(-179, 180, 4))

        lons2, lats2 = np.meshgrid(lon2_range, lat2_range)
        # Convert to masked arrays
        lats2 = ma.array(lats2)
        lons2 = ma.array(lons2)

        regridded_values = dp._rcmes_spatial_regrid(
            spatial_values, lats, lons, lats2, lons2)
        self.assertEqual(regridded_values.shape, lats2.shape)
        self.assertEqual(regridded_values.shape, lons2.shape)


class TestSpatialRegrid(unittest.TestCase):

    def setUp(self):
        self.input_dataset = ten_year_monthly_dataset()
        self.new_lats = np.array(range(-89, 90, 4))
        self.new_lons = np.array(range(-179, 180, 4))
        self.regridded_dataset = dp.spatial_regrid(
            self.input_dataset, self.new_lats, self.new_lons)

    def test_returned_lats(self):
        np.testing.assert_array_equal(
            self.regridded_dataset.lats, self.new_lats)

    def test_returned_lons(self):
        np.testing.assert_array_equal(
            self.regridded_dataset.lons, self.new_lons)

    def test_shape_of_values(self):
        regridded_data_shape = self.regridded_dataset.values.shape
        expected_data_shape = (len(self.input_dataset.times), len(
            self.new_lats), len(self.new_lons))
        self.assertSequenceEqual(regridded_data_shape, expected_data_shape)

    def test_variable_propagation(self):
        self.assertEquals(self.input_dataset.name, self.regridded_dataset.name)
        self.assertEquals(self.input_dataset.variable,
                          self.regridded_dataset.variable)

    def test_two_dimensional_lats_lons(self):
        self.input_dataset.lats = np.array(range(-89, 90, 2))
        self.input_dataset.lons = np.array(range(-179, 180, 4))
        self.input_dataset.lats = self.input_dataset.lats.reshape(2, 45)
        self.input_dataset.lons = self.input_dataset.lons.reshape(2, 45)
        new_dataset = dp.spatial_regrid(
            self.input_dataset, self.new_lats, self.new_lons)
        np.testing.assert_array_equal(new_dataset.lats, self.new_lats)


class TestNormalizeDatasetDatetimes(unittest.TestCase):

    def setUp(self):
        self.monthly_dataset = ten_year_monthly_15th_dataset()
        self.daily_dataset = two_year_daily_2hr_dataset()

    def test_daily(self):
        new_ds = dp.normalize_dataset_datetimes(self.monthly_dataset, 'daily')

        # Check that all the days have been shifted to the first of the month
        self.assertTrue(all(x.hour == 0 for x in new_ds.times))

    def test_montly(self):
        new_ds = dp.normalize_dataset_datetimes(
            self.monthly_dataset, 'monthly')

        # Check that all the days have been shifted to the first of the month
        self.assertTrue(all(x.day == 1 for x in new_ds.times))

    def test_daily_time(self):
        # Test daily with time.hour != 0
        self.monthly_dataset.times = np.array([
                                              datetime.datetime(
                                                  year, month, 15, 5)
                                              for year in range(2000, 2010)
                                              for month in range(1, 13)])
        new_ds = dp.normalize_dataset_datetimes(self.monthly_dataset, 'daily')
        # Check that all the days have been shifted to the first of the month
        self.assertTrue(all(x.hour == 0 for x in new_ds.times))


class TestSubset(unittest.TestCase):

    def setUp(self):
        self.target_dataset = ten_year_monthly_dataset()
        self.name = 'foo'

        self.subregion = ds.Bounds(
            lat_min=-81, lat_max=81,
            lon_min=-161, lon_max=161,
            start=datetime.datetime(2001, 1, 1),
            end=datetime.datetime(2004, 1, 1)
        )
        self.non_exact_spatial_subregion = ds.Bounds(
            lat_min=-80.25, lat_max=80.5,
            lon_min=-160.25, lon_max=160.5,
            start=datetime.datetime(2001, 1, 1),
            end=datetime.datetime(2004, 1, 1)
        )
        self.non_exact_temporal_subregion = ds.Bounds(
            lat_min=-80.25, lat_max=80.5,
            lon_min=-160.25, lon_max=160.5,
            start=datetime.datetime(2001, 1, 15),
            end=datetime.datetime(2004, 2, 15)
        )

    def test_subset(self):
        subset = dp.subset(self.target_dataset, self.subregion)
        self.assertEqual(subset.lats.shape[0], 82)
        self.assertSequenceEqual(list(np.array(range(-81, 82, 2))),
                                 list(subset.lats))
        self.assertEqual(subset.lons.shape[0], 162)
        self.assertEqual(subset.times.shape[0], 37)
        self.assertEqual(subset.values.shape, (37, 82, 162))

    def test_subset_name(self):
        subset = dp.subset(self.target_dataset, self.subregion)
        self.assertEqual(subset.name, self.name)

    def test_subset_name_propagation(self):
        subset_name = 'foo_subset_name'
        subset = dp.subset(self.target_dataset, self.subregion, subset_name)
        self.assertEqual(subset.name, subset_name)

    def test_subset_using_non_exact_spatial_bounds(self):
        index_slices = dp._get_subregion_slice_indices(
            self.target_dataset, self.non_exact_spatial_subregion)
        control_index_slices = {"lat_start": 5,
                                "lat_end": 84,
                                "lon_start": 10,
                                "lon_end": 169,
                                "time_start": 12,
                                "time_end": 48}
        self.assertDictEqual(index_slices, control_index_slices)

    def test_subset_using_non_exact_temporal_bounds(self):
        index_slices = dp._get_subregion_slice_indices(
            self.target_dataset, self.non_exact_temporal_subregion)
        control_index_slices = {"lat_start": 5,
                                "lat_end": 84,
                                "lon_start": 10,
                                "lon_end": 169,
                                "time_start": 13,
                                "time_end": 49}
        self.assertDictEqual(index_slices, control_index_slices)

    def test_subset_without_start_index(self):
        self.subregion = ds.Bounds(
            lat_min=-81, lat_max=81,
            lon_min=-161, lon_max=161,
        )
        subset = dp.subset(self.target_dataset, self.subregion)
        times = np.array([datetime.datetime(year, month, 1)
                          for year in range(2000, 2010)
                          for month in range(1, 13)])
        self.assertEqual(subset.lats.shape[0], 82)
        self.assertSequenceEqual(list(np.array(range(-81, 82, 2))),
                                 list(subset.lats))
        self.assertEqual(subset.lons.shape[0], 162)
        self.assertEqual(subset.values.shape, (120, 82, 162))
        self.assertEqual(subset.times.shape[0], 120)
        np.testing.assert_array_equal(subset.times, times)


class TestSafeSubset(unittest.TestCase):

    def setUp(self):
        lats = np.array(range(-60, 61, 1))
        lons = np.array(range(-170, 171, 1))
        times = np.array([datetime.datetime(year, month, 1)
                          for year in range(2000, 2010)
                          for month in range(1, 13)])
        values = np.ones([len(times), len(lats), len(lons)])
        self.target_dataset = ds.Dataset(lats,
                                         lons,
                                         times,
                                         values,
                                         variable="test variable name",
                                         units='test variable units',
                                         name='foo')

        self.spatial_out_of_bounds = ds.Bounds(
            lat_min=-65, lat_max=65,
            lon_min=-180, lon_max=180,
            start=datetime.datetime(2001, 1, 1),
            end=datetime.datetime(2004, 1, 1)
        )

        self.temporal_out_of_bounds = ds.Bounds(
            lat_min=-40, lat_max=40,
            lon_min=-160.25, lon_max=160.5,
            start=datetime.datetime(1999, 1, 15),
            end=datetime.datetime(2222, 2, 15)
        )

        self.everything_out_of_bounds = ds.Bounds(
            lat_min=-65, lat_max=65,
            lon_min=-180, lon_max=180,
            start=datetime.datetime(1999, 1, 15),
            end=datetime.datetime(2222, 2, 15)
        )

    def test_partial_spatial_overlap(self):
        '''Ensure that safe_subset can handle out of bounds spatial values'''
        ds = dp.safe_subset(self.target_dataset, self.spatial_out_of_bounds)
        spatial_bounds = ds.spatial_boundaries()
        self.assertEquals(spatial_bounds[0], -60)
        self.assertEquals(spatial_bounds[1], 60)
        self.assertEquals(spatial_bounds[2], -170)
        self.assertEquals(spatial_bounds[3], 170)

    def test_partial_temporal_overlap(self):
        '''Ensure that safe_subset can handle out of bounds temporal values'''
        ds = dp.safe_subset(self.target_dataset, self.temporal_out_of_bounds)
        temporal_bounds = ds.temporal_boundaries()
        start = datetime.datetime(2000, 1, 1)
        end = datetime.datetime(2009, 12, 1)

        self.assertEquals(temporal_bounds[0], start)
        self.assertEquals(temporal_bounds[1], end)

    def test_entire_bounds_overlap(self):
        ds = dp.safe_subset(self.target_dataset, self.everything_out_of_bounds)
        spatial_bounds = ds.spatial_boundaries()
        temporal_bounds = ds.temporal_boundaries()
        start = datetime.datetime(2000, 1, 1)
        end = datetime.datetime(2009, 12, 1)

        self.assertEquals(spatial_bounds[0], -60)
        self.assertEquals(spatial_bounds[1], 60)
        self.assertEquals(spatial_bounds[2], -170)
        self.assertEquals(spatial_bounds[3], 170)
        self.assertEquals(temporal_bounds[0], start)
        self.assertEquals(temporal_bounds[1], end)


class TestFailingSubset(unittest.TestCase):

    def setUp(self):
        self.target_dataset = ten_year_monthly_dataset()
        self.target_dataset.lats = np.array(range(-89, 88, 2))
        self.target_dataset.lons = np.array(range(-179, 178, 2))

        self.subregion = ds.Bounds(
            lat_min=-81, lat_max=81,
            lon_min=-161, lon_max=161,
            start=datetime.datetime(2001, 1, 1),
            end=datetime.datetime(2004, 1, 1)
        )

    def test_out_of_dataset_bounds_lat_min(self):
        self.subregion.lat_max = -90
        with self.assertRaises(ValueError):
            dp.subset(self.target_dataset, self.subregion)

    def test_out_of_dataset_bounds_lat_max(self):
        self.subregion.lat_min = 90
        with self.assertRaises(ValueError):
            dp.subset(self.target_dataset, self.subregion)

    def test_out_of_dataset_bounds_lon_min(self):
        self.subregion.lon_max = -180
        with self.assertRaises(ValueError):
            dp.subset(self.target_dataset, self.subregion)

    def test_out_of_dataset_bounds_lon_max(self):
        self.subregion.lon_min = 180
        with self.assertRaises(ValueError):
            dp.subset(self.target_dataset, self.subregion)

    def test_out_of_dataset_bounds_start(self):
        self.subregion.start = datetime.datetime(1999, 1, 1)
        with self.assertRaises(ValueError):
            dp.subset(self.target_dataset, self.subregion)

    def test_out_of_dataset_bounds_end(self):
        self.subregion.end = datetime.datetime(2011, 1, 1)
        with self.assertRaises(ValueError):
            dp.subset(self.target_dataset, self.subregion)


class TestNetCDFWrite(unittest.TestCase):

    def setUp(self):
        self.ds = ten_year_monthly_dataset()
        self.ds_2d = ten_year_monthly_dataset(latlon2d=True)
        self.file_name = 'test.nc'

    def tearDown(self):
        if os.path.isfile(self.file_name):
            os.remove(self.file_name)

    def test_file_write(self):
        dp.write_netcdf(self.ds, self.file_name)
        self.assertTrue(os.path.isfile(self.file_name))

    def test_file_write_2d(self):
        dp.write_netcdf(self.ds_2d, self.file_name)
        self.assertTrue(os.path.isfile(self.file_name))

    def test_file_write(self):
        dp.write_netcdf(self.ds, self.file_name)
        self.assertTrue(os.path.isfile(self.file_name))

    def test_that_file_contents_are_valid(self):
        dp.write_netcdf(self.ds, self.file_name)
        new_ds = local.load_file(self.file_name, self.ds.variable)

        self.assertEqual(self.ds.variable, new_ds.variable)
        np.testing.assert_array_equal(self.ds.lats, new_ds.lats)
        np.testing.assert_array_equal(self.ds.lons, new_ds.lons)
        np.testing.assert_array_equal(self.ds.times, new_ds.times)
        np.testing.assert_array_equal(self.ds.values, new_ds.values)


def ten_year_monthly_dataset(latlon2d=False):
    lats = np.array(range(-89, 90, 2))
    lons = np.array(range(-179, 180, 2))
    # Need separate variable for input lats / lons because dataset only
    # makes shallow copies of them.
    ilats, ilons = lats, lons
    # For testing 2D lat lon grids
    if latlon2d:
        lons2, lats2 = np.meshgrid(lons, lats)
        ilats, ilons = lats2, lons2
    # Ten Years of monthly data
    times = np.array([datetime.datetime(year, month, 1)
                      for year in range(2000, 2010) for month in range(1, 13)])
    values = np.ones([len(times), len(lats), len(lons)])
    input_dataset = ds.Dataset(ilats,
                               ilons,
                               times,
                               values,
                               variable="test variable name",
                               units='test variable units',
                               name='foo')
    return input_dataset


def ten_year_monthly_15th_dataset():
    lats = np.array(range(-89, 90, 2))
    lons = np.array(range(-179, 180, 2))
    # Ten Years of monthly 15th data
    times = np.array([datetime.datetime(year, month, 15)
                      for year in range(2000, 2010) for month in range(1, 13)])
    values = np.ones([len(times), len(lats), len(lons)])
    input_dataset = ds.Dataset(lats,
                               lons,
                               times,
                               values,
                               variable="test variable name",
                               units='test variable units')
    return input_dataset


def two_year_daily_dataset():
    lats = np.array(range(-89, 90, 2))
    lons = np.array(range(-179, 180, 2))
    times = np.array([datetime.datetime(2001, 1, 1) +
                      datetime.timedelta(days=d) for d in range(730)])
    values = np.ones([len(times), len(lats), len(lons)])
    dataset = ds.Dataset(lats, lons, times, values,
                         variable='random data', units='test variable units')
    return dataset


def two_year_daily_2hr_dataset():
    lats = np.array(range(-89, 90, 2))
    lons = np.array(range(-179, 180, 2))
    times = np.array([datetime.datetime(2001, 1, 1) +
                      datetime.timedelta(days=d, hours=2) for d in range(730)])
    values = np.ones([len(times), len(lats), len(lons)])
    dataset = ds.Dataset(lats, lons, times, values,
                         variable='random data', units='test variable units')
    return dataset


def build_ten_cube_dataset(value):
    lats = np.array(range(-89, 90, 18))
    lons = np.array(range(-179, 180, 36))
    times = np.array([datetime.datetime(year, 1, 1)
                      for year in range(2000, 2010)])
    values = np.ones([len(times), len(lats), len(lons)])
    values = values * value
    dataset = ds.Dataset(lats, lons, times, values)
    return dataset

if __name__ == '__main__':
    unittest.main()
