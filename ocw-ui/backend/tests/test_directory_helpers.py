import os
import re
import unittest
from webtest import TestApp

from ..run_webservices import app
from ..directory_helpers import _get_clean_directory_path

test_app = TestApp(app)
WORK_DIR = '/tmp/ocw'

class TestDirectoryPathList(unittest.TestCase):
    PATH_LEADER = '/usr/local/ocw'

    @classmethod
    def setUpClass(self):
        if not os.path.exists(self.PATH_LEADER): os.mkdir(self.PATH_LEADER)
        if not os.path.exists(self.PATH_LEADER + '/bar'):
            os.mkdir(self.PATH_LEADER + '/bar')
        if not os.path.exists(self.PATH_LEADER + '/baz.txt'):
            open(self.PATH_LEADER + '/baz.txt', 'a').close()
        if not os.path.exists(self.PATH_LEADER + '/test.txt'):
            open(self.PATH_LEADER + '/test.txt', 'a').close()

    @classmethod
    def tearDownClass(self):
        os.remove(self.PATH_LEADER + '/test.txt')
        os.remove(self.PATH_LEADER + '/baz.txt')
        os.rmdir(self.PATH_LEADER + '/bar')
        os.rmdir(self.PATH_LEADER)

    def test_valid_path_listing(self):
        expected_return = {'listing': ['/bar/', '/baz.txt', '/test.txt']}
        response = test_app.get('http://localhost:8082/dir/list//')
        self.assertDictEqual(response.json, expected_return)

    def test_invalid_path_listing(self):
        expected_return = {'listing': []}
        response = test_app.get('http://localhost:8082/dir/list//usr/local')
        self.assertDictEqual(response.json, expected_return)

    def test_nonexistent_path_listing(self):
        expected_return = {'listing': []}
        response = test_app.get('http://localhost:8082/dir/list//fake/path')
        self.assertDictEqual(response.json, expected_return)

class TestResultDirectoryList(unittest.TestCase):
    def setUp(self):
        if not os.path.exists(WORK_DIR + '/foo'): os.mkdir(WORK_DIR + '/foo')
        if not os.path.exists(WORK_DIR + '/bar'): os.mkdir(WORK_DIR + '/bar')

    @classmethod
    def tearDownClass(self):
        if os.path.exists(WORK_DIR + '/foo'): os.rmdir(WORK_DIR + '/foo')
        if os.path.exists(WORK_DIR + '/bar'): os.rmdir(WORK_DIR + '/bar')

    def test_result_listing(self):
        expected_return = {'listing': ['bar', 'foo']}
        response = test_app.get('http://localhost:8082/dir/results/')
        response_json = self.clean_result_listing_json(response.json)
        self.assertDictEqual(response_json, expected_return)

    def test_missing_work_dir_listing(self):
        if os.path.exists(WORK_DIR + '/foo'): os.rmdir(WORK_DIR + '/foo')
        if os.path.exists(WORK_DIR + '/bar'): os.rmdir(WORK_DIR + '/bar')

        expected_return = {'listing': []}
        response = test_app.get('http://localhost:8082/dir/results/')
        response_json = self.clean_result_listing_json(response.json)
        self.assertDictEqual(response_json, expected_return)

    def clean_result_listing_json(self, response_json):
        # The working directory that is being pulled for results is the actual directory
        # that OCW uses when running evaluations on the system. It's possible that these
        # tests are being run on a system where actual results are run. If that's the case,
        # the listings for actual runs need to be removed before the results are check. The
        # standard form for a result directory is a timestamp of YYYY-MM-DD_HH-MM-SS.
        valid_directory = re.compile(r"\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}", re.UNICODE)
        response_json['listing'] = [folder
                                    for folder in response_json['listing']
                                    if not re.search(valid_directory, folder)]
        return response_json

class TestResultResultRetrieval(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        if not os.path.exists(WORK_DIR + '/foo'): os.mkdir(WORK_DIR + '/foo')

        if not os.path.exists(WORK_DIR + '/foo/baz.txt'):
            open(WORK_DIR + '/foo/baz.txt', 'a').close()
        if not os.path.exists(WORK_DIR + '/foo/test.txt'):
            open(WORK_DIR + '/foo/test.txt', 'a').close()

    @classmethod
    def tearDownClass(self):
        os.remove(WORK_DIR + '/foo/baz.txt')
        os.remove(WORK_DIR + '/foo/test.txt')
        os.rmdir(WORK_DIR + '/foo')

    def test_no_test_directory_retreival(self):
        expected_return = {'listing': []}
        response = test_app.get('http://localhost:8082/dir/results//bar')

        response_json = response.json
        self.assertDictEqual(response_json, expected_return)

    def test_results_retreival(self):
        expected_return = {'listing': ['foo/baz.txt', 'foo/test.txt']}
        response = test_app.get('http://localhost:8082/dir/results//foo')
        response_json = response.json
        self.assertDictEqual(response_json, expected_return)

class TestDirectoryPathCleaner(unittest.TestCase):
    PATH_LEADER = '/tmp/foo'
    VALID_CLEAN_DIR = '/tmp/foo/bar'

    @classmethod
    def setUpClass(self):
        if not os.path.exists(self.PATH_LEADER): os.mkdir(self.PATH_LEADER)
        if not os.path.exists(self.VALID_CLEAN_DIR): os.mkdir(self.VALID_CLEAN_DIR)

    @classmethod
    def tearDownClass(self):
        os.rmdir(self.VALID_CLEAN_DIR)
        os.rmdir(self.PATH_LEADER)

    def test_valid_directory_path(self):
        clean_path = _get_clean_directory_path(self.PATH_LEADER, '/bar')
        self.assertEquals(clean_path, self.VALID_CLEAN_DIR)

    def test_duplicate_slash_removal(self):
        clean_path = _get_clean_directory_path(self.PATH_LEADER, '//bar')
        self.assertEquals(clean_path, self.VALID_CLEAN_DIR)

        clean_path = _get_clean_directory_path(self.PATH_LEADER, '/////bar')
        self.assertEquals(clean_path, self.VALID_CLEAN_DIR)

    def test_relative_path_removal(self):
        clean_path = _get_clean_directory_path(self.PATH_LEADER, '/../bar')
        self.assertEquals(clean_path, self.VALID_CLEAN_DIR)

        clean_path = _get_clean_directory_path(self.PATH_LEADER, '/./bar')
        self.assertEquals(clean_path, self.VALID_CLEAN_DIR)

        clean_path = _get_clean_directory_path(self.PATH_LEADER, '/.././bar')
        self.assertEquals(clean_path, self.VALID_CLEAN_DIR)
