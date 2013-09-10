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
    Metric - Abstract Base Class from which all metrics must inherit.
'''

from abc import ABCMeta, abstractmethod

class Metric():
    '''Abstrace Base Class from which all metrics must inherit.'''
    __metaclass__ = ABCMeta

    def __init__(self, unary=False):
        '''Default constructor for a Metric.

        :param unary: Flag marking if the metric expects one or two operands.
                A "unary" metric processes only a single dataset at a time.
                By default a metric is expected to take two datasets.
        :type unary: Bool
        '''
        self.is_unary = unary

    @abstractmethod
    def run(self, datasets):
        '''Run the metric for some given dataset(s)

        :param datasets: The dataset(s) to be used in the current metric 
                run. If this is a "unary" metric then datasets[0] contains 
                the dataset to be used in the current run. If the metric is 
                binary, then datasets[0] contains the reference dataset and 
                datasets[1] contains the target dataset.
        :type datasets: Tuple
        :returns: An Array containing the results of running the metric.
        :trype: Numpy Array
        '''


class UnaryMetric():
    '''Abstract Base Class from which all unary metrics inherit.'''
    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    @abstactmethod
    def run(self, target_dataset):
        '''Run the metric for a given target dataset.

        :param target_dataset: The dataset on which the current metric will
            be run.

        :returns: The result of evaluating the metric on the target_dataset.
        '''


class Bias(Metric):
    '''Calculate the bias between a reference and target dataset.'''

    def __init__(self):
        '''Default constructor.

        .. note::
           Overrides Metric.__init__()
        '''
        self.is_unary = False

    def run(self, datasets):
        '''Calculate the bias between a reference and target dataset.

        .. note::
           Overrides Metric.run()

        :param datasets: The datasets to use in the current run. The 
                reference dataset is given in datasets[0] and the target 
                dataset is given in datasets[1].
        :type datasets: Tuple
        :returns: An array containing the difference between the reference 
                dataset and the target dataset.
        :rtype: Numpy Array
        '''
        return datasets[0].values - datasets[1].values


class TemporalStdDev(Metric):
    '''Calculate the standard deviation over the time.'''

    def __init__(self):
        '''Default constructor.

        .. note::
           Overrides Metric.__init__()
        '''
        self.is_unary = True

    def run(self, datasets):
        '''Calculate the temporal std. dev. for a datasets.

        .. note::
           Overrides Metric.run()

        :param datasets: The datasets on which to calculate the temporal
                std. dev. in datasets[0].
        :type datasets: Tuple
        :returns: An array containing the temporal std. dev.
        :rtype: Numpy Array
        '''
        return datasets[0].values.std(axi=0, ddof=1)
