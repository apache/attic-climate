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

'''
Classes: 
    Evaluation - Container for running an evaluation
'''

import logging
from metrics import Metric, UnaryMetric, BinaryMetric
from dataset import Dataset, Bounds
import ocw.dataset_processor as DSP

import numpy.ma as ma

logger = logging.getLogger(__name__)


class Evaluation(object):
    '''Container for running an evaluation

    An *Evaluation* is the running of one or more metrics on one or more 
    target datasets and a (possibly optional) reference dataset. Evaluation
    can handle two types of metrics, ``unary`` and ``binary``. The validity
    of an Evaluation is dependent upon the number and type of metrics as well
    as the number of datasets.

    A ``unary`` metric is a metric that runs over a single dataset. If you add
    a ``unary`` metric to the Evaluation you are only required to add a 
    reference dataset or a target dataset. If there are multiple datasets
    in the evaluation then the ``unary`` metric is run over all of them.

    A ``binary`` metric is a metric that runs over a reference dataset and
    target dataset. If you add a ``binary`` metric you are required to add a
    reference dataset and at least one target dataset. The ``binary`` metrics
    are run over every (reference dataset, target dataset) pair in the
    Evaluation.

    An Evaluation must have at least one metric to be valid. 
    '''

    def __init__(self, reference, targets, metrics, subregions=None):
        '''Default Evaluation constructor.

        :param reference: The reference Dataset for the evaluation.
        :type reference: :class:`dataset.Dataset`

        :param targets: A list of one or more target datasets for the 
                evaluation.
        :type targets: :class:`list` of :class:`dataset.Dataset`

        :param metrics: A list of one or more Metric instances to run 
                in the evaluation.
        :type metrics: :class:`list` of :mod:`metrics`

        :param subregions: (Optional) Subregion information to use in the
                evaluation. A subregion is specified with a Bounds object.
        :type subregions: :class:`list` of :class:`dataset.Bounds`

        :raises: ValueError 
        '''
        #: The reference dataset.
        self._ref_dataset = reference
        #: The target dataset(s) which should each be compared with
        #: the reference dataset when the evaluation is run.
        self.target_datasets = []
        self.add_datasets(targets)

        #: The list of "binary" metrics (A metric which takes two Datasets)
        #: that the Evaluation should use.
        self.metrics = []
        #: The list of "unary" metrics (A metric which takes one Dataset) that
        #: the Evaluation should use.
        self.unary_metrics = []

        # Metrics need to be added to specific lists depending on whether they
        # are "binary" or "unary" metrics.
        self.add_metrics(metrics)

        #: An optional list of subregion bounds to use when running the
        #: evaluation.
        self._subregions = subregions

        #: A list containing the results of running regular metric evaluations.
        #: The shape of results is ``(num_target_datasets, num_metrics)`` if
        #: the user doesn't specify subregion information. Otherwise the shape
        #: is ``(num_target_datasets, num_metrics, num_subregions)``.
        self.results = []
        #: A list containing the results of running the unary metric
        #: evaluations. The shape of unary_results is
        #: ``(num_targets, num_metrics)`` where ``num_targets =
        #: num_target_ds + (1 if ref_dataset != None else 0``
        self.unary_results = []

    @property
    def ref_dataset(self):
        return self._ref_dataset

    @ref_dataset.setter
    def ref_dataset(self, value):
        if not isinstance(value, Dataset):
            error = (
                "Cannot add a dataset that isn't an instance of Dataset. "
                "Please consult the documentation for additional help."
            )
            raise TypeError(error)
        self._ref_dataset = value

    @property
    def subregions(self):
        return self._subregions

    @subregions.setter
    def subregions(self, value):
        # If the value is None, we don't need to check that it's well formed!
        if value:
            # All of the values passed in the iterable better be Bounds!
            if not all([isinstance(bound, Bounds) for bound in value]):
                error = (
                    "Found invalid subregion information. Expected "
                    "value to be an instance of Bounds."
                )
                raise TypeError(error)
        self._subregions = value

    def add_dataset(self, target_dataset):
        '''Add a Dataset to the Evaluation.

        A target Dataset is compared against the reference dataset when the 
        Evaluation is run with one or more metrics.

        :param target_dataset: The target Dataset to add to the Evaluation.
        :type target_dataset: :class:`dataset.Dataset`

        :raises ValueError: If a dataset to add isn't an instance of Dataset.
        '''
        if not isinstance(target_dataset, Dataset):
            error = (
                "Cannot add a dataset that isn't an instance of Dataset. "
                "Please consult the documentation for additional help."
            )
            logger.error(error)
            raise TypeError(error)

        self.target_datasets.append(target_dataset)

    def add_datasets(self, target_datasets):
        '''Add multiple Datasets to the Evaluation.

        :param target_datasets: The list of datasets that should be added to 
            the Evaluation.
        :type target_datasets: :class:`list` of :class:`dataset.Dataset`

        :raises ValueError: If a dataset to add isn't an instance of Dataset.
        '''
        for target in target_datasets:
            self.add_dataset(target)

    def add_metric(self, metric):
        '''Add a metric to the Evaluation.

        A metric is an instance of a class which inherits from metrics.Metric.

        :param metric: The metric instance to add to the Evaluation.
        :type metric: :mod:`metrics`

        :raises ValueError: If the metric to add isn't a class that inherits
                from metrics.Metric.
        '''
        if not isinstance(metric, Metric):
            error = (
                "Cannot add a metric that doesn't inherit from Metric. "
                "Please consult the documentation for additional help."
            )
            logger.error(error)
            raise TypeError(error)

        if isinstance(metric, UnaryMetric):
            self.unary_metrics.append(metric)
        else:
            self.metrics.append(metric)

    def add_metrics(self, metrics):
        '''Add multiple metrics to the Evaluation.

        A metric is an instance of a class which inherits from metrics.Metric.

        :param metrics: The list of metric instances to add to the Evaluation.
        :type metrics: :class:`list` of :mod:`metrics`

        :raises ValueError: If a metric to add isn't a class that inherits
                from metrics.Metric.
        '''
        for metric in metrics:
            self.add_metric(metric)

    def run(self):
        '''Run the evaluation.

        There are two phases to a run of the Evaluation. First, if there are
        any "binary" metrics they are run through the evaluation. Binary
        metrics are only run if there is a reference dataset and at least one
        target dataset.

        If there is subregion information provided then each dataset is subset
        before being run through the binary metrics. 

        ..note:: Only the binary metrics are subset with subregion information.

        Next, if there are any "unary" metrics they are run. Unary metrics are
        only run if there is at least one target dataset or a reference dataset.
        '''
        if not self._evaluation_is_valid():
            error = "The evaluation is invalid. Check the docs for help."
            logger.warning(error)
            return

        if self._should_run_regular_metrics():
            if self.subregions:
                self.results = self._run_subregion_evaluation()
            else:
                self.results = self._run_no_subregion_evaluation()

        if self._should_run_unary_metrics():
            if self.subregions:
                self.unary_results = self._run_subregion_unary_evaluation()
            else:
                self.unary_results = self._run_unary_metric_evaluation()

    def _evaluation_is_valid(self):
        '''Check if the evaluation is well-formed.

        * If there are no metrics or no datasets it's invalid.
        * If there is a unary metric there must be a reference dataset or at
            least one target dataset.
        * If there is a regular metric there must be a reference dataset and
            at least one target dataset.
        '''
        run_reg = self._should_run_regular_metrics()
        run_unary = self._should_run_unary_metrics()
        reg_valid = self.ref_dataset != None and len(self.target_datasets) > 0
        unary_valid = self.ref_dataset != None or len(self.target_datasets) > 0

        if run_reg and run_unary:
            return reg_valid and unary_valid
        elif run_reg:
            return reg_valid
        elif run_unary:
            return unary_valid
        else:
            return False

    def _should_run_regular_metrics(self):
        return len(self.metrics) > 0

    def _should_run_unary_metrics(self):
        return len(self.unary_metrics) > 0

    def _run_subregion_evaluation(self):
        results = []
        new_refs = [DSP.subset(self.ref_dataset, s) for s in self.subregions]

        for target in self.target_datasets:
            results.append([])
            new_targets = [DSP.subset(target, s) for s in self.subregions]

            for metric in self.metrics:
                results[-1].append([])

                for i in range(len(self.subregions)):
                    new_ref = new_refs[i]
                    new_tar = new_targets[i]

                    run_result = metric.run(new_ref, new_tar)
                    results[-1][-1].append(run_result)
        return convert_evaluation_result(results, subregion=True)

    def _run_no_subregion_evaluation(self):
        results = []
        for target in self.target_datasets:
            results.append([])
            for metric in self.metrics:
                run_result = metric.run(self.ref_dataset, target)
                results[-1].append(run_result)
        return convert_evaluation_result(results)

    def _run_unary_metric_evaluation(self):
        unary_results = []
        for metric in self.unary_metrics:
            unary_results.append([])
            # Unary metrics should be run over the reference Dataset also
            if self.ref_dataset:
                unary_results[-1].append(metric.run(self.ref_dataset))

            for target in self.target_datasets:
                unary_results[-1].append(metric.run(target))
        return convert_unary_evaluation_result(unary_results)

    def _run_subregion_unary_evaluation(self):
        unary_results = []
        if self.ref_dataset:
            new_refs = [DSP.subset(self.ref_dataset, s)
                        for s in self.subregions]

        new_targets = [
            [DSP.subset(t, s) for s in self.subregions]
            for t in self.target_datasets
        ]

        for metric in self.unary_metrics:
            unary_results.append([])

            for i in range(len(self.subregions)):
                unary_results[-1].append([])

                if self.ref_dataset:
                    unary_results[-1][-1].append(metric.run(new_refs[i]))

                for t in range(len(self.target_datasets)):
                    unary_results[-1][-1].append(metric.run(new_targets[t][i]))

        return convert_unary_evaluation_result(unary_results, subregion=True)

    def __str__(self):
        formatted_repr = (
            "<Evaluation - ref_dataset: {}, "
            "target_dataset(s): {}, "
            "binary_metric(s): {}, "
            "unary_metric(s): {}, "
            "subregion(s): {}>"
        )

        return formatted_repr.format(
            str(self._ref_dataset),
            [str(ds) for ds in self.target_datasets],
            [str(m) for m in self.metrics],
            [str(m) for m in self.unary_metrics],
            str(self.subregions)
        )


def convert_evaluation_result(evaluation_result, subregion=False):
    if not subregion:
        nmodel = len(evaluation_result)
        nmetric = len(evaluation_result[0])
        results = []
        for imetric in range(nmetric):
            if evaluation_result[0][imetric].ndim != 0:
                result_shape = list(evaluation_result[0][imetric].shape)
                result_shape.insert(0, nmodel)
                result = ma.zeros(result_shape)
                for imodel in range(nmodel):
                    result[imodel, :] = evaluation_result[imodel][imetric]
            else:
                result = ma.zeros(nmodel)
                for imodel in range(nmodel):
                    result[imodel] = evaluation_result[imodel][imetric]
            results.append(result)
        return results
    else:
        nmodel = len(evaluation_result)
        nmetric = len(evaluation_result[0])
        nsubregion = len(evaluation_result[0][0])

        results = []
        for isubregion in range(nsubregion):
            subregion_results = []
            for imetric in range(nmetric):
                if evaluation_result[0][imetric][isubregion].ndim != 0:
                    result_shape = list(evaluation_result[0][
                                        imetric][isubregion].shape)
                    result_shape.insert(0, nmodel)
                    result = ma.zeros(result_shape)
                    for imodel in range(nmodel):
                        result[imodel, :] = evaluation_result[
                            imodel][imetric][isubregion]
                else:
                    result = ma.zeros(nmodel)
                    for imodel in range(nmodel):
                        result[imodel] = evaluation_result[
                            imodel][imetric][isubregion]
                subregion_results.append(result)
            results.append(subregion_results)
        return results


def convert_unary_evaluation_result(evaluation_result, subregion=False):
    if not subregion:
        nmetric = len(evaluation_result)
        nmodel = len(evaluation_result[0])
        results = []
        for imetric in range(nmetric):
            if evaluation_result[imetric][0].ndim != 0:
                result_shape = list(evaluation_result[imetric][0].shape)
                result_shape.insert(0, nmodel)
                result = ma.zeros(result_shape)
                for imodel in range(nmodel):
                    result[imodel, :] = evaluation_result[imetric][imodel]
            else:
                result = ma.zeros(nmodel)
                for imodel in range(nmodel):
                    result[imodel] = evaluation_result[imetric][imodel]
            results.append(result)
        return results
    else:
        nmetric = len(evaluation_result)
        nsubregion = len(evaluation_result[0])
        nmodel = len(evaluation_result[0][0])

        results = []
        for isubregion in range(nsubregion):
            subregion_results = []
            for imetric in range(nmetric):
                if evaluation_result[imetric][isubregion][0].ndim != 0:
                    result_shape = list(evaluation_result[imetric][
                                        isubregion][0].shape)
                    result_shape.insert(0, nmodel)
                    result = ma.zeros(result_shape)
                    for imodel in range(nmodel):
                        result[imodel, :] = evaluation_result[
                            imetric][isubregion][imodel]
                else:
                    result = ma.zeros(nmodel)
                    for imodel in range(nmodel):
                        result[imodel] = evaluation_result[
                            imetric][isubregion][imodel]
                subregion_results.append(result)
            results.append(subregion_results)
        return results
