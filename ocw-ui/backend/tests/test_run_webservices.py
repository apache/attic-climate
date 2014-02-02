import os
import unittest
from webtest import TestApp

from ..run_webservices import app

test_app = TestApp(app)

class TestInitialization(unittest.TestCase):
    def test_status_page(self):
        response = test_app.get('/')

        self.assertEqual(response.status_int, 200)

class TestStaticEvalResults(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        if not os.path.exists('/tmp/ocw'): os.mkdir('/tmp/ocw')
        if not os.path.exists('/tmp/ocw/foo.txt'): 
            open('/tmp/ocw/foo.txt', 'a').close()

    @classmethod
    def tearDownClass(self):
        os.remove('/tmp/ocw/foo.txt')
        os.rmdir('/tmp/ocw')

    def test_static_eval_results_return(self):
        response = test_app.get('/static/eval_results//foo.txt')

        self.assertEqual(response.status_int, 200)
if __name__ == '__main__':
    unittest.main()
