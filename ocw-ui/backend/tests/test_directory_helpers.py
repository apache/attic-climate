import os
import unittest
from webtest import TestApp

from ..run_webservices import app
from ..directory_helpers import _get_clean_directory_path

test_app = TestApp(app)

class TestDirectoryPathList(unittest.TestCase):
    PATH_LEADER = '/usr/local/rcmes'

    if not os.path.exists(PATH_LEADER): os.mkdir(PATH_LEADER)
    if not os.path.exists(PATH_LEADER + '/bar'):
        os.mkdir(PATH_LEADER + '/bar')
    if not os.path.exists(PATH_LEADER + '/baz.txt'):
        open(PATH_LEADER + '/baz.txt', 'a').close()
    if not os.path.exists(PATH_LEADER + '/test.txt'):
        open(PATH_LEADER + '/test.txt', 'a').close()

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
    WORK_DIR = '/tmp/rcmes'

    def test_result_listing(self):
        if not os.path.exists(self.WORK_DIR): os.mkdir(self.WORK_DIR)
        if not os.path.exists(self.WORK_DIR + '/foo'): os.mkdir(self.WORK_DIR + '/foo')
        if not os.path.exists(self.WORK_DIR + '/bar'): os.mkdir(self.WORK_DIR + '/bar')

        expected_return = {'listing': ['/bar', '/foo']}
        response = test_app.get('http://localhost:8082/dir/results/')
        self.assertDictEqual(response.json, expected_return)

    def test_missing_work_dir_listing(self):
        if os.path.exists(self.WORK_DIR + '/foo'): os.rmdir(self.WORK_DIR + '/foo')
        if os.path.exists(self.WORK_DIR + '/bar'): os.rmdir(self.WORK_DIR + '/bar')
        if os.path.exists(self.WORK_DIR): os.rmdir(self.WORK_DIR)

        expected_return = {'listing': []}
        response = test_app.get('http://localhost:8082/dir/results/')
        self.assertDictEqual(response.json, expected_return)

class TestDirectoryPathCleaner(unittest.TestCase):
    PATH_LEADER = '/tmp/foo'
    VALID_CLEAN_DIR = '/tmp/foo/bar'

    if not os.path.exists(PATH_LEADER): os.mkdir(PATH_LEADER)
    if not os.path.exists(VALID_CLEAN_DIR): os.mkdir(VALID_CLEAN_DIR)

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
