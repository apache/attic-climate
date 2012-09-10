import os
import unittest
import Nio as nio

import storage.files as files


class TestGetVariableByType(unittest.TestCase):

    def setUp(self):
        self.badFilename = '/tmp/fail.txt'
        self.missingVariable = 'missing'

    def testNioRaisesException(self):
        with self.assertRaises(Exception):
            files.getVariableByType(self.badFilename, 'time')
        
    def testTimeVariableNames(self):
        self.variableList = files.VARIABLE_NAMES['time']
        for variable in self.variableList:
            testFile = self.makeNioFile(variable)
            timeVariable = files.getVariableByType(testFile, 'time')
            os.remove(testFile)
            self.assertEqual(timeVariable, variable)
    
    def testLatitudeVariableNames(self):
        self.variableList = files.VARIABLE_NAMES['latitude']
        for variable in self.variableList:
            testFile = self.makeNioFile(variable)
            timeVariable = files.getVariableByType(testFile, 'latitude')
            os.remove(testFile)
            self.assertEqual(timeVariable, variable)

    def testLongitudeVariableNames(self):
        self.variableList = files.VARIABLE_NAMES['longitude']
        for variable in self.variableList:
            testFile = self.makeNioFile(variable)
            timeVariable = files.getVariableByType(testFile, 'longitude')
            os.remove(testFile)
            self.assertEqual(timeVariable, variable)

    def testTimeVariableMissing(self):
        testFile = self.make5VariableNioFile()
        testVariable = files.getVariableByType(testFile, 'time')
        os.remove(testFile)
        self.assertEqual(len(testVariable), 5)
    
    def makeNioFile(self, variableName):
        filename = '/tmp/good_%s.nc' % variableName
        f = nio.open_file(filename, 'w')
        f.create_dimension('test_dimension', 1)
        f.create_variable(variableName,'l',('test_dimension',))
        f.close()
        return filename
    
    def make5VariableNioFile(self):
        filename = '/tmp/5_variables.nc'
        f = nio.open_file(filename, 'w')
        f.create_dimension('dimension_one', 1)
        f.create_variable('one', 'l', ('dimension_one',))
        f.create_variable('two', 'l', ('dimension_one',))
        f.create_variable('three', 'l', ('dimension_one',))
        f.create_variable('four', 'l', ('dimension_one',))
        f.create_variable('five', 'l', ('dimension_one',))
        f.close()
        return filename

if __name__ == '__main__':
    unittest.main()
