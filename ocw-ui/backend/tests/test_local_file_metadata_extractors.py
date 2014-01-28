import os
import unittest
from webtest import TestApp

import urllib

from ..run_webservices import app

test_app = TestApp(app)

class TestLatLonExtraction(unittest.TestCase):
    def test_successful_latlon_extract(self):
        expected_return = {
            "success": True,
            "lat_name": "lat",
            "lon_name": "lon",
            "lat_min": -45.759998321533203,
            "lat_max": -45.759998321533203,
            "lon_min": -24.639999389648438,
            "lon_max": 60.279998779296875
        }

        file_location = os.path.abspath('tests/example_data/lat_lon_time.nc')

        response = test_app.get('/lfme/list_latlon/' + file_location)

        self.assertDictEqual(expected_return, response.json)

    def test_failure_latlon_extract(self):
        pass

if __name__ == '__main__':
    unittest.main()
