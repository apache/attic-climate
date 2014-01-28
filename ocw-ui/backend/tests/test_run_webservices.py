import unittest
from webtest import TestApp

from ..run_webservices import app

test_app = TestApp(app)

class TestInitialization(unittest.TestCase):
    def test_status_page(self):
        response = test_app.get('/')

        self.assertEqual(response.status_int, 200)

if __name__ == '__main__':
    unittest.main()
