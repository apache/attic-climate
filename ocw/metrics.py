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
import ocw.utils as utils
import numpy
from scipy import stats

class Metric(object):
    '''Base Metric Class'''
    __metaclass__ = ABCMeta


class UnaryMetric(Metric):
    '''Abstract Base Class from which all unary metrics inherit.'''
    __metaclass__ = ABCMeta

    @abstractmethod
    def run(self, target_dataset):
        '''Run the metric for a given target dataset.

        :param target_dataset: The dataset on which the current metric will
            be run.
        :type target_dataset: ocw.dataset.Dataset object

        :returns: The result of evaluating the metric on the target_dataset.
        '''


class BinaryMetric(Metric):
    '''Abstract Base Class from which all binary metrics inherit.'''
    __metaclass__ = ABCMeta

    @abstractmethod
    def run(self, ref_dataset, target_dataset):
        '''Run the metric for the given reference and target datasets.

        :param ref_dataset: The Dataset to use as the reference dataset when
            running the evaluation.
        :type ref_dataset: ocw.dataset.Dataset object
        :param target_dataset: The Dataset to use as the target dataset when
            running the evaluation.
        :type target_dataset: ocw.dataset.Dataset object

        :returns: The result of evaluation the metric on the reference and 
            target dataset.
        '''


class Bias(BinaryMetric):
    '''Calculate the bias between a reference and target dataset.'''

    def run(self, ref_dataset, target_dataset):
        '''Calculate the bias between a reference and target dataset.

        .. note::
           Overrides BinaryMetric.run()

        :param ref_dataset: The reference dataset to use in this metric run.
        :type ref_dataset: ocw.dataset.Dataset object
        :param target_dataset: The target dataset to evaluate against the
            reference dataset in this metric run.
        :type target_dataset: ocw.dataset.Dataset object

        :returns: The difference between the reference and target datasets.
        :rtype: Numpy Array
        '''
        return ref_dataset.values - target_dataset.values


class TemporalStdDev(UnaryMetric):
    '''Calculate the standard deviation over the time.'''

    def run(self, target_dataset):
        '''Calculate the temporal std. dev. for a datasets.

        .. note::
           Overrides UnaryMetric.run()

        :param target_dataset: The target_dataset on which to calculate the 
            temporal standard deviation.
        :type target_dataset: ocw.dataset.Dataset object

        :returns: The temporal standard deviation of the target dataset
        :rtype: Numpy Array
        '''
        return target_dataset.values.std(axis=0, ddof=1)


class StdDevRatio(BinaryMetric):
    '''Calculate the standard deviation ratio between two datasets.'''

    def run(self, ref_dataset, target_dataset):
        '''Calculate the standard deviation ratio.

        .. note::
            Overrides BinaryMetric.run()

        :param ref_dataset: The reference dataset to use in this metric run.
        :type ref_dataset: ocw.dataset.Dataset object
        :param target_dataset: The target dataset to evaluate against the
            reference dataset in this metric run.
        :type target_dataset: ocw.dataset.Dataset object

        :returns: The standard deviation ratio of the reference and target
        '''
        return target_dataset.values.std() / ref_dataset.values.std()


class PatternCorrelation(BinaryMetric):
    '''Calculate the correlation coefficient between two datasets'''

    def run(self, ref_dataset, target_dataset):
        '''Calculate the correlation coefficient between two dataset.

        .. note::
           Overrides BinaryMetric.run()

        :param ref_dataset: The reference dataset to use in this metric run.
        :type ref_dataset: ocw.dataset.Dataset object
        :param target_dataset: The target dataset to evaluate against the
            reference dataset in this metric run.
        :type target_dataset: ocw.dataset.Dataset object

        :returns: The correlation coefficient between a reference and target dataset.
        '''
        # stats.pearsonr returns correlation_coefficient, 2-tailed p-value
        # We only care about the correlation coefficient
        # Docs at http://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.pearsonr.html
        return stats.pearsonr(ref_dataset.values.flatten(), target_dataset.values.flatten())[0]


class TemporalMeanBias(BinaryMetric):
    '''Calculate the bias averaged over time.'''

    def run(self, ref_dataset, target_dataset, absolute=False):
        '''Calculate the bias averaged over time.

        .. note::
           Overrides BinaryMetric.run()

        :param ref_dataset: The reference dataset to use in this metric run.
        :type ref_dataset: ocw.dataset.Dataset object
        :param target_dataset: The target dataset to evaluate against the
            reference dataset in this metric run.
        :type target_dataset: ocw.dataset.Dataset object

        :returns: The mean bias between a reference and target dataset over time.
        '''

        diff = ref_dataset.values - target_dataset.values
        if absolute:
            diff = abs(diff)
        mean_bias = diff.mean(axis=0)

        return mean_bias


class SpatialMeanOfTemporalMeanBias(BinaryMetric):
    '''Calculate the bias averaged over time and domain.'''

    def run(self, reference_dataset, target_dataset):
        '''Calculate the bias averaged over time and domain.

        .. note::
           Overrides BinaryMetric.run()

        :param ref_dataset: The reference dataset to use in this metric run
        :type ref_dataset: ocw.dataset.Dataset object
        :param target_dataset: The target dataset to evaluate against the
            reference dataset in this metric run
        :type target_dataset: ocw.dataset.Dataset object

        :returns: The bias averaged over time and domain
        '''

        bias = reference_dataset.values - target_dataset.values
        return bias.mean()


class RMSError(BinaryMetric):
    '''Calculate the Root Mean Square Difference (RMS Error), with the mean
       calculated over time and space.'''

    def run(self, eval_dataset, ref_dataset):
        '''Calculate the Root Mean Square Difference (RMS Error), with the mean
           calculated over time and space.

        .. note::
           Overrides BinaryMetric.run()

        :param eval_dataset: The dataset to evaluate against the reference
            dataset
        :type eval_dataset: ocw.dataset.Dataset object
        :param ref_dataset: The reference dataset for the metric
        :type target_dataset: ocw.dataset.Dataset object

        :returns: The RMS error, with the mean calculated over time and space
        '''

        sqdiff = (eval_dataset.values - ref_dataset.values) ** 2
        return numpy.sqrt(sqdiff.mean())

class calcTemporalCorrelation(BinaryMetric):
    '''Calculate the temporal correlation (pearson's linear correlation coefficient) coefficient
    
    def run(self, eval_dataset, ref_dataset):
    '''Assumption(s) ::
        The first dimension of two datasets is the time axis.
    
    Input ::
        evaluationData - model data array of any shape (N dimensional)
        referenceData- observation data array of any shape (N dimensional)
            
    Output::
        temporalCorelation - A (N-1)-D array of temporal correlation coefficients at each subregion
        sigLev - A (N-1)-D array of confidence levels related to temporalCorelation 
    
    sigLev: the correlation between model and observation is significant at sigLev * 100 %
    '''
   
    ndim = eval_dataset.values.ndim
    if  ndim == 3:  # when the observational and model data are three dimensional arrays
        nt, ny, nx = ref_dataset.values.shape
        temporal_correlation = np.zeros([ny,nx])
        siglev = np.zeros([ny, nx])
        for iy in np.arange(ny):
            for ix in np.arange(nx):
                temporal_correlation[iy, ix], siglev[iy,ix] = stats.pearsonr(eval_dataset.values[:,iy,ix]),
                                                                             ref_dataset.values[:,iy,ix])  
                siglev[iy,ix] = 1.0- siglev[iy,ix]
        
    if ndim == 1:  # when two time series are given
        temporal_correlation = 0.
        siglev = 0.
        temporal_correlation, siglev = stats.pearsonr(eval_dataset.values, ref_dataset.values)
        siglev = 1.0 - siglev 
    
    return temporal_correlation, siglev     
