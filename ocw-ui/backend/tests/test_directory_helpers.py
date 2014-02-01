import os
import unittest
from webtest import TestApp

from ..run_webservices import app
from ..directory_helpers import _get_clean_directory_path

test_app = TestApp(app)

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
