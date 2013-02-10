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
            
        

if __name__ == '__main__':
    unittest.main()
