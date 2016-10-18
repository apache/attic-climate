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
        ref_dataset = self.test_dataset
        target_datasets = [self.test_dataset, self.another_test_dataset]
        metrics = [Bias(), Bias()]
        unary_metrics = [TemporalStdDev()]

        self.eval = Evaluation(ref_dataset,
                               target_datasets,
                               metrics + unary_metrics)

        self.assertEqual(self.eval.ref_dataset.variable, self.variable)

        # Make sure the two target datasets were added properly
        self.assertEqual(self.eval.target_datasets[0].variable, self.variable)
        self.assertEqual(self.eval.target_datasets[1].variable, self.other_var)

        # Make sure the three metrics were added properly
        # The two Bias metrics are "binary" metrics
        self.assertEqual(len(self.eval.metrics), 2)
        # TemporalStdDev is a "unary" metric and should be stored as such
        self.assertEqual(len(self.eval.unary_metrics), 1)
        self.eval.run()
        out_str = (
            "<Evaluation - ref_dataset: {}, "
            "target_dataset(s): {}, "
            "binary_metric(s): {}, "
            "unary_metric(s): {}, "
            "subregion(s): {}>"
        ).format(
            str(self.test_dataset),
            [str(ds) for ds in target_datasets],
            [str(m) for m in metrics],
            [str(u) for u in unary_metrics],
            None
        )
        self.assertEqual(str(self.eval), out_str)

    def test_valid_ref_dataset_setter(self):
        self.eval.ref_dataset = self.another_test_dataset
        self.assertEqual(self.eval.ref_dataset.variable,
                         self.another_test_dataset.variable)

    def test_invalid_ref_dataset(self):
        with self.assertRaises(TypeError):
            self.eval.ref_dataset = "This isn't a Dataset object"

    def test_valid_subregion(self):
        bound = Bounds(
            lat_min=-10, lat_max=10,
            lon_min=-20, lon_max=20,
            start=dt.datetime(2000, 1, 1), end=dt.datetime(2001, 1, 1))

        self.eval.subregions = [bound, bound]
        self.assertEquals(len(self.eval.subregions), 2)

    def test_invalid_subregion_bound(self):
        bound = "This is not a bounds object"

        with self.assertRaises(TypeError):
            self.eval.subregions = [bound]

    def test_add_ref_dataset(self):
        self.eval = Evaluation(self.test_dataset, [], [])

        self.assertEqual(self.eval.ref_dataset.variable, self.variable)

    def test_add_valid_dataset(self):
        self.eval.add_dataset(self.test_dataset)

        self.assertEqual(self.eval.target_datasets[0].variable,
                         self.variable)

    def test_add_invalid_dataset(self):
        with self.assertRaises(TypeError):
            self.eval.add_dataset('This is an invalid dataset')

    def test_add_datasets(self):
        self.eval.add_datasets([self.test_dataset, self.another_test_dataset])

        self.assertEqual(len(self.eval.target_datasets), 2)
        self.assertEqual(self.eval.target_datasets[0].variable,
                         self.variable)
        self.assertEqual(self.eval.target_datasets[1].variable,
                         self.other_var)

    def test_add_valid_metric(self):
        # Add a "binary" metric
        self.assertEqual(len(self.eval.metrics), 0)
        self.eval.add_metric(Bias())
        self.assertEqual(len(self.eval.metrics), 1)

        # Add a "unary" metric
        self.assertEqual(len(self.eval.unary_metrics), 0)
        self.eval.add_metric(TemporalStdDev())
        self.assertEqual(len(self.eval.unary_metrics), 1)

    def test_add_invalid_metric(self):
        with self.assertRaises(TypeError):
            self.eval.add_metric('This is an invalid metric')

    def test_add_metrics(self):
        self.assertEqual(len(self.eval.metrics), 0)
        self.eval.add_metrics([Bias(), Bias()])
        self.assertEqual(len(self.eval.metrics), 2)

    def test_invalid_evaluation_run(self):
        self.eval = Evaluation(None, [], [])
        self.assertEqual(self.eval.run(), None)

    def test_bias_output_shape(self):
        bias_eval = Evaluation(self.test_dataset, [
                               self.another_test_dataset], [Bias()])
        bias_eval.run()
        input_shape = tuple(self.test_dataset.values.shape)
        bias_results_shape = tuple(bias_eval.results[0][0].shape)
        self.assertEqual(input_shape, bias_results_shape)

    def test_result_shape(self):
        bias_eval = Evaluation(
            self.test_dataset,
            [self.another_test_dataset, self.another_test_dataset,
                self.another_test_dataset],
            [Bias(), Bias()]
        )
        bias_eval.run()

        # Expected result shape is
        # [bias, bias] where bias.shape[0] = number of datasets
        self.assertTrue(len(bias_eval.results) == 2)
        self.assertTrue(bias_eval.results[0].shape[0] == 3)

    def test_unary_result_shape(self):
        new_eval = Evaluation(
            self.test_dataset,
            [self.another_test_dataset, self.another_test_dataset,
                self.another_test_dataset, self.another_test_dataset],
            [TemporalStdDev()]
        )
        new_eval.run()

        # Expected result shape is
        # [stddev] where stddev.shape[0] = number of datasets

        self.assertTrue(len(new_eval.unary_results) == 1)
        self.assertTrue(new_eval.unary_results[0].shape[0] == 5)

    def test_subregion_result_shape(self):
        bound = Bounds(
            lat_min=10, lat_max=18,
            lon_min=100, lon_max=108,
            start=dt.datetime(2000, 1, 1), end=dt.datetime(2000, 3, 1))

        bias_eval = Evaluation(
            self.test_dataset,
            [self.another_test_dataset, self.another_test_dataset],
            [Bias()],
            [bound]
        )
        bias_eval.run()

        # Expected result shape is
        # [
        #       [   # Subregions cause this extra layer
        #           [number of targets, bias.run(reference, target1).shape]
        #       ]
        #   ],
        self.assertTrue(len(bias_eval.results) == 1)
        self.assertTrue(len(bias_eval.results[0]) == 1)
        self.assertTrue(bias_eval.results[0][0].shape[0] == 2)
        self.assertTrue(isinstance(bias_eval.results, type([])))

    def test_subregion_unary_result_shape(self):
        bound = Bounds(
            lat_min=10, lat_max=18,
            lon_min=100, lon_max=108,
            start=dt.datetime(2000, 1, 1), end=dt.datetime(2000, 3, 1))

        new_eval = Evaluation(
            self.test_dataset,
            [self.another_test_dataset, self.another_test_dataset],
            [TemporalStdDev(), TemporalStdDev()],
            [bound, bound, bound, bound, bound]
        )
        new_eval.run()

        # Expected result shape is
        # [
        #       [   # Subregions cause this extra layer
        #           [3, temporalstddev.run(reference).shape],
        #       ]
        # ]

        # 5 = number of subregions
        self.assertTrue(len(new_eval.unary_results) == 5)
        # number of metrics
        self.assertTrue(len(new_eval.unary_results[0]) == 2)
        self.assertTrue(isinstance(new_eval.unary_results, type([])))
        # number of datasets (ref + target)
        self.assertTrue(new_eval.unary_results[0][0].shape[0] == 3)


if __name__ == '__main__':
    unittest.main()
