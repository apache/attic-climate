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
        expected_return = {"listing": ["/bar/", "/baz.txt", "/test.txt"]}
        response = test_app.get('http://localhost:8082/dir/list//')
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

    def test_directory_validity_check(self):
        self.assertRaises(
            ValueError,
            _get_clean_directory_path,
            self.PATH_LEADER,
            '/bar/path/to/missing/directory'
        )
