#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
import os
import unittest

from utils import misc
import ConfigParser

class TestReadSubRegionsFile(unittest.TestCase):

    def setUp(self):
        self.badFilename = '/tmp/fail.txt'
        self.validSubRegionsFile = './files/validSubRegions.cfg'

    def testMissingFileException(self):
        with self.assertRaises(Exception):
            misc.readSubRegionsFile(self.badFilename)
    
class TestParseSubRegions(unittest.TestCase):
    
    def setUp(self):
        self.userConfig = ConfigParser.SafeConfigParser()
        self.userConfig.optionxform = str # This is so the case is preserved on the items in the config file
        self.missingSubRegion = './files/missingSubRegionParam.cfg'
    
    def testMissingSubRegionParameter(self):
        self.userConfig.read(self.missingSubRegion)
        self.missingSubRegionParam = misc.configToDict(self.userConfig.items('SUB_REGION'))
        self.assertFalse(misc.parseSubRegions(self.missingSubRegionParam))

class TestIsDirGood(unittest.TestCase):
    
    def setUp(self):
        self.goodDir = '/tmp'
        self.unwriteableDir = '/usr'
        self.unwritableMissingDir = '/usr/test_bad_direcory'
        self.writeableMissingDir = '/tmp/test_good_directory'
        
    def tearDown(self):
        if os.path.exists(self.writeableMissingDir):
            os.rmdir(self.writeableMissingDir)

    def testGoodDirExists(self):
        self.assertTrue(misc.isDirGood(self.goodDir))
    
    def testGoodDirDoesNotExist(self):
        self.assertTrue(misc.isDirGood(self.writeableMissingDir))

    def testUnwriteableDir(self):
        with self.assertRaises(OSError):
            misc.isDirGood(self.unwriteableDir)
    
    def testUnwritableMissingDir(self):
        with self.assertRaises(OSError):
            misc.isDirGood(self.unwritableMissingDir)

if __name__ == '__main__':
    unittest.main()
