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

import unittest

import toolkit.metrics

import numpy as np
import numpy.ma as ma


class TestCalcPdf(unittest.TestCase):
    
    def testUsingSettingsKwarg(self):

        # declare and initialize 1d arrays (mimick timeseries)
        good_pdf = '0.091'
      
        # declare and initialize  3d(time,lat,lon) type array
        evaluationDataset = np.arange(0, 12, 0.5)
        evaluationDataset = evaluationDataset.reshape(4, 2, 3)
        evaluationDataset = ma.array(evaluationDataset)
    
        referenceDataset = np.arange(10, 34)
        referenceDataset = referenceDataset.reshape(4, 2, 3)
        referenceDataset = ma.array(referenceDataset)

        settings = (3, 10, 20)

        pdf =  '%.3f' % toolkit.metrics.calcPdf(evaluationDataset, referenceDataset, settings)
        # Checking accuracy to 3 decimal places using a simple string comparison
        self.assertEqual(pdf, good_pdf)
        

if __name__ == '__main__':
    unittest.main()
