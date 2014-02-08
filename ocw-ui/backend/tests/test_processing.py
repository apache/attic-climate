import os
import unittest
from urllib import urlretrieve

from webtest import TestApp

from backend.run_webservices import app
import backend.processing as bp

import ocw.metrics as metrics

import numpy

test_app = TestApp(app)

FILE_LEADER = "http://zipper.jpl.nasa.gov/dist/"
FILE_1 = "AFRICA_KNMI-RACMO2.2b_CTL_ERAINT_MM_50km_1989-2008_tasmax.nc"
FILE_2 = "AFRICA_UC-WRF311_CTL_ERAINT_MM_50km-rg_1989-2008_tasmax.nc"

class TestLocalDatasetLoad(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        if not os.path.exists('test.nc'):
            urlretrieve(FILE_LEADER + FILE_1, 'test.nc')

    @classmethod
    def tearDownClass(self):
        if os.path.exists('test.nc'):
            os.remove('test.nc')

    def test_valid_load(self):
        dataset_object = {
            'id': os.path.abspath('test.nc'),
            'var_name': 'tasmax',
            'lat_name': 'lat',
            'lon_name': 'lon',
            'time_name': 'time'
        }

        dataset = bp._load_local_dataset_object(dataset_object)
        self.assertEqual(dataset.variable, dataset_object['var_name'])

class TestMetricLoad(unittest.TestCase):
    def test_get_valid_metric_options(self):
        metric_map = bp._get_valid_metric_options()
        bias = metric_map['Bias']()
        self.assertTrue(isinstance(bias, metrics.Bias))

    def test_valid_metric_load(self):
        metric_objs = bp._load_metrics(['Bias', 'TemporalStdDev'])
        self.assertTrue(isinstance(metric_objs[0], metrics.Bias))
        self.assertTrue(isinstance(metric_objs[1], metrics.TemporalStdDev))

    def test_invalid_metric_load(self):
        self.assertRaises(ValueError, bp._load_metrics, ['AAA'])

class TestSpatialRebinHelpers(unittest.TestCase):
    def test_latlon_bin_helper(self):
        eval_bounds = {
            'lat_min': -57.2,
            'lat_max': 58.2,
            'lon_min': -45.3,
            'lon_max': 39.2,
        }
        lat_step = 1
        lon_step = 1

        lats = numpy.arange(eval_bounds['lat_min'], eval_bounds['lat_max'])
        lons = numpy.arange(eval_bounds['lon_min'], eval_bounds['lon_max'])

        new_lats, new_lons = bp._calculate_new_latlon_bins(eval_bounds, lat_step, lon_step)
