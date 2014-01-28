import unittest
from webtest import TestApp

import urllib

from ..run_webservices import app

test_app = TestApp(app)

class TestLatLonExtraction(unittest.TestCase):
    def test_successful_latlon_extract(self):
        pass

    def test_failure_latlon_extract(self):
        pass

if __name__ == '__main__':
    unittest.main()
