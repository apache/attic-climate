import os
import unittest
from urllib import urlretrieve

from webtest import TestApp

from ..run_webservices import app
from ..processing import _load_local_dataset_object

test_app = TestApp(app)

FILE_LEADER = "http://zipper.jpl.nasa.gov/dist/"
FILE_1 = "AFRICA_KNMI-RACMO2.2b_CTL_ERAINT_MM_50km_1989-2008_tasmax.nc"
FILE_2 = "AFRICA_UC-WRF311_CTL_ERAINT_MM_50km-rg_1989-2008_tasmax.nc"

def setUpModule(self):
    if not os.path.exists('test.nc'):
        urlretrieve(FILE_LEADER + FILE_1, 'test.nc')

def tearDownModule(self):
    if os.path.exists('test.nc'):
        os.remove('test.nc')

class TestLocalDatasetLoad(unittest.TestCase):
    def test_valid_load(self):
        dataset_object = {
            'id': os.path.abspath('test.nc'),
            'var_name': 'tasmax',
            'lat_name': 'lat',
            'lon_name': 'lon',
            'time_name': 'time'
        }

        dataset = _load_local_dataset_object(dataset_object)

        self.assertEqual(dataset.variable, dataset_object['var_name'])
