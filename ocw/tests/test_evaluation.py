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

'''Unit tests for the Evaluation.py module'''

import unittest
import numpy as np
import datetime as dt
from ocw.dataset import Dataset, Bounds
from ocw.evaluation import Evaluation
from ocw.metrics import Bias, TemporalStdDev

class TestEvaluation(unittest.TestCase):
    def setUp(self):
        self.eval = Evaluation(None, [], [])

        lat = np.array([10, 12, 14, 16, 18])
        lon = np.array([100, 102, 104, 106, 108])
        time = np.array([dt.datetime(2000, x, 1) for x in range(1, 13)])
        flat_array = np.array(range(300))
        value = flat_array.reshape(12, 5, 5)
        self.variable = 'prec'
        self.other_var = 'temp'
        self.test_dataset = Dataset(lat, lon, time, value, self.variable)
        self.another_test_dataset = Dataset(lat, lon, time, value, 
                self.other_var)

    def test_init(self):
        self.assertEquals(self.eval.ref_dataset, None)
        self.assertEquals(self.eval.target_datasets, [])
        self.assertEquals(self.eval.metrics, [])
        self.assertEquals(self.eval.unary_metrics, [])

    def test_full_init(self):
        self.eval = Evaluation(
                        self.test_dataset,           
                        [self.test_dataset, self.another_test_dataset], 
                        [Bias(), Bias(), TemporalStdDev()])                    

        self.assertEqual(self.eval.ref_dataset.variable, self.variable)

        # Make sure the two target datasets were added properly
        self.assertEqual(self.eval.target_datasets[0].variable, self.variable)
        self.assertEqual(self.eval.target_datasets[1].variable, self.other_var)

        # Make sure the three metrics were added properly
        # The two Bias metrics are "binary" metrics
        self.assertEqual(len(self.eval.metrics), 2)
        # TemporalStdDev is a "unary" metric and should be stored as such
        self.assertEqual(len(self.eval.unary_metrics), 1)

    def test_invalid_ref_dataset(self):
        with self.assertRaises(TypeError):
            self.eval.ref_dataset = "This isn't a Dataset object"

    def test_valid_subregion(self):
        bound = Bounds(
                -10, 10, 
                -20, 20, 
                dt.datetime(2000, 1, 1), dt.datetime(2001, 1, 1))

        self.eval.subregions = [bound, bound]
        self.assertEquals(len(self.eval.subregions), 2)

    def test_invalid_subregion_bound(self):
        bound = "This is not a bounds object"

        with self.assertRaises(TypeError):
            self.eval.subregions = [bound]

    def test_add_ref_dataset(self):
        self.eval = Evaluation(self.test_dataset, [], [])

        self.assertEqual(self.eval.ref_dataset.variable, self.variable)

    def test_add_dataset(self):
        self.eval.add_dataset(self.test_dataset)

        self.assertEqual(self.eval.target_datasets[0].variable, 
                self.variable)

    def test_add_datasets(self):
        self.eval.add_datasets([self.test_dataset, self.another_test_dataset])

        self.assertEqual(len(self.eval.target_datasets), 2)
        self.assertEqual(self.eval.target_datasets[0].variable, 
                self.variable)
        self.assertEqual(self.eval.target_datasets[1].variable, 
                self.other_var)

    def test_add_metric(self):
        # Add a "binary" metric
        self.assertEqual(len(self.eval.metrics), 0)
        self.eval.add_metric(Bias())
        self.assertEqual(len(self.eval.metrics), 1)

        # Add a "unary" metric
        self.assertEqual(len(self.eval.unary_metrics), 0)
        self.eval.add_metric(TemporalStdDev())
        self.assertEqual(len(self.eval.unary_metrics), 1)

    def test_add_metrics(self):
        self.assertEqual(len(self.eval.metrics), 0)
        self.eval.add_metrics([Bias(), Bias()])
        self.assertEqual(len(self.eval.metrics), 2)

if __name__  == '__main__':
    unittest.main()
