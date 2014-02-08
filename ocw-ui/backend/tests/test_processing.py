import os
import unittest
from urllib import urlretrieve

from webtest import TestApp

from backend.run_webservices import app
import backend.processing

import ocw.metrics as metrics

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

        dataset = backend.processing._load_local_dataset_object(dataset_object)
        self.assertEqual(dataset.variable, dataset_object['var_name'])

class TestMetricLoad(unittest.TestCase):
    def test_get_valid_metric_options(self):
        metric_map = backend.processing._get_valid_metric_options()
        bias = metric_map['Bias']()
        self.assertTrue(isinstance(bias, metrics.Bias))
