import os
from ast import literal_eval
import unittest
from webtest import TestApp

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

    def test_successful_latlon_extract_jsonp(self):
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

        response = test_app.get('/lfme/list_latlon/' + file_location + '?callback=test_callback')

        json = response.text

        # Strip out the callback functino and the json string from the response
        # and check for proper content.
        callback = json[:json.index('(')]
        json = json[json.index('(') + 1 : json.rindex(')')]
        json = literal_eval(json)

        self.assertDictEqual(expected_return, json)
        self.assertEqual(callback, "test_callback")

    def test_failure_latlon_extract(self):
        expected_return = {
            "success": False,
            "variables": ["invalid_lon", "invalid_time", "invalid_lat"]
        }

        file_location = os.path.abspath('tests/example_data/lat_lon_time_invalid.nc')

        response = test_app.get('/lfme/list_latlon/' + file_location)

        self.assertDictEqual(expected_return, response.json)

    def test_failure_latlon_extract_jsonp(self):
        expected_return = {
            "success": False,
            "variables": ["invalid_lon", "invalid_time", "invalid_lat"]
        }

        file_location = os.path.abspath('tests/example_data/lat_lon_time_invalid.nc')

        response = test_app.get('/lfme/list_latlon/' + file_location + '?callback=test_callback')
        json = response.text

        # Strip out the callback functino and the json string from the response
        # and check for proper content.
        callback = json[:json.index('(')]
        json = json[json.index('(') + 1 : json.rindex(')')]
        json = literal_eval(json)

        self.assertDictEqual(expected_return, json)
        self.assertEqual(callback, "test_callback")

class TestTimeExtraction(unittest.TestCase):
    def test_successful_time_extract(self):
        expected_return = {
            "success": True,
            "time_name": "time",
            "start_time": "1988-06-10 00:00:00",
            "end_time": "2008-01-27 00:00:00"
        }

        file_location = os.path.abspath('tests/example_data/lat_lon_time.nc')

        response = test_app.get('/lfme/list_time/' + file_location)

        self.assertDictEqual(expected_return, response.json)

	def test_successful_time_extract_jsonp(self):
		expected_return = {
			"success": True,
			"time_name": "time",
			"start_time": "1988-06-10 00:00:00",
			"end_time": "2008-01-27 00:00:00"
		}

        file_location = os.path.abspath('tests/example_data/lat_lon_time.nc')

        response = test_app.get('/lfme/list_time/' + file_location + '?callback=test_callback')
        json = response.text

        # Strip out the callback functino and the json string from the response
        # and check for proper content.
        callback = json[:json.index('(')]
        json = json[json.index('(') + 1 : json.rindex(')')]
        json = literal_eval(json)

        self.assertDictEqual(expected_return, json)
        self.assertEqual(callback, "test_callback")

    def test_failure_time_extract(self):
        expected_return = {
            "success": False,
            "variables": ["invalid_lon", "invalid_time", "invalid_lat"]
        } 

        file_location = os.path.abspath('tests/example_data/lat_lon_time_invalid.nc')

        response = test_app.get('/lfme/list_time/' + file_location)

        self.assertDictEqual(expected_return, response.json)

	def test_failure_time_extract_jsonp(self):
		expected_return = {
			"success": False,
			"variables": ["invalid_lon", "invalid_time", "invalid_lat"]
		}

        file_location = os.path.abspath('tests/example_data/lat_lon_time_invalid.nc')

        response = test_app.get('/lfme/list_time/' + file_location + '?callback=test_callback')
        json = response.text

        # Strip out the callback functino and the json string from the response
        # and check for proper content.
        callback = json[:json.index('(')]
        json = json[json.index('(') + 1 : json.rindex(')')]
        json = literal_eval(json)

        self.assertDictEqual(expected_return, json)
        self.assertEqual(callback, "test_callback")

class TestVariableExtraction(unittest.TestCase):
    def test_successful_variable_extract(self):
        expected_return = {
            'success': True,
            'variables': ['lat', 'lon', 'time']
        }

        file_location = os.path.abspath('tests/example_data/lat_lon_time.nc')

        response = test_app.get('/lfme/list_vars/' + file_location)

        self.assertDictEqual(expected_return, response.json)

    def test_successful_variable_extract_jsonp(self):
        expected_return = {
            'success': True,
            'variables': ['lat', 'lon', 'time']
        }

        file_location = os.path.abspath('tests/example_data/lat_lon_time.nc')

        response = test_app.get('/lfme/list_vars/' + file_location + '?callback=test_callback')
        json = response.text

        # Strip out the callback functino and the json string from the response
        # and check for proper content.
        callback = json[:json.index('(')]
        json = json[json.index('(') + 1 : json.rindex(')')]
        json = literal_eval(json)

        self.assertDictEqual(expected_return, json)
        self.assertEqual(callback, "test_callback")

    def test_failure_variable_extract(self):
        expected_return = {'success': False}

        response = test_app.get('/lfme/list_vars/' + 'fake_path')

        self.assertDictEqual(expected_return, response.json)

    def test_failure_variable_extract_jsonp(self):
        expected_return = {'success': False}

        response = test_app.get('/lfme/list_vars//fakepath?callback=test_callback')
        json = response.text

        # Strip out the callback functino and the json string from the response
        # and check for proper content.
        callback = json[:json.index('(')]
        json = json[json.index('(') + 1 : json.rindex(')')]
        json = literal_eval(json)

        self.assertDictEqual(expected_return, json)
        self.assertEqual(callback, "test_callback")

if __name__ == '__main__':
    unittest.main()
