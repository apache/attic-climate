import os
import unittest
from urllib import urlretrieve
import datetime as dt

from webtest import TestApp

from backend.run_webservices import app
import backend.processing as bp

import ocw.metrics as metrics
import ocw.data_source.rcmed as rcmed

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

class TestDatasetProessingHelper(unittest.TestCase):
    def test_invalid_process_dataset_objects(self):
        invalid_dataset_object = {'data_source_id': 3, 'dataset_info': {}}
        self.assertRaises(
                ValueError,
                bp._process_dataset_object,
                invalid_dataset_object, 'fake parameter')

class TestRCMEDDatasetLoad(unittest.TestCase):
    def test_valid_load(self):
        metadata = rcmed.get_parameters_metadata()
        # Load TRMM from RCMED
        dataset_dat = [m for m in metadata if m['parameter_id'] == '36'][0]

        dataset_info = {
            'dataset_id': int(dataset_dat['dataset_id']),
            'parameter_id': int(dataset_dat['parameter_id'])
        }

        eval_bounds = {
            'start_time': dt.datetime(1998, 02, 01),
            'end_time': dt.datetime(1998, 03, 01),
            'lat_min': -10,
            'lat_max': 10,
            'lon_min': -15,
            'lon_max': 15
        }

        dataset = bp._load_rcmed_dataset_object(dataset_info, eval_bounds)
        lat_min, lat_max, lon_min, lon_max = dataset.spatial_boundaries()
        start_time, end_time = dataset.time_range()

        self.assertTrue(eval_bounds['lat_min'] <= lat_min)
        self.assertTrue(eval_bounds['lat_max'] >= lat_max)
        self.assertTrue(eval_bounds['lon_min'] <= lon_min)
        self.assertTrue(eval_bounds['lon_max'] >= lon_max)
        self.assertTrue(eval_bounds['start_time'] <= start_time)
        self.assertTrue(eval_bounds['end_time'] >= end_time)

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
