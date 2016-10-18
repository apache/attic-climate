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
import numpy.ma as ma
from scipy.stats import mstats


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
        :type target_dataset: :class:`dataset.Dataset`

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
        :type ref_dataset: :class:`dataset.Dataset`

        :param target_dataset: The Dataset to use as the target dataset when
            running the evaluation.
        :type target_dataset: :class:`dataset.Dataset`

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
        :type ref_dataset: :class:`dataset.Dataset`

        :param target_dataset: The target dataset to evaluate against the
            reference dataset in this metric run.
        :type target_dataset: :class:`dataset.Dataset`

        :returns: The difference between the reference and target datasets.
        :rtype: :class:`numpy.ndarray`
        '''
        return calc_bias(target_dataset.values, ref_dataset.values)


class SpatialPatternTaylorDiagram(BinaryMetric):
    ''' Calculate the target to reference ratio of spatial standard deviation and pattern correlation'''

    def run(self, ref_dataset, target_dataset):
        '''Calculate two metrics to plot a Taylor diagram to compare spatial patterns      

        .. note::
           Overrides BinaryMetric.run() 

        :param ref_dataset: The reference dataset to use in this metric run.
        :type ref_dataset: :class:`dataset.Dataset`

        :param target_dataset: The target dataset to evaluate against the
            reference dataset in this metric run.
        :type target_dataset: :class:`dataset.Dataset`

        :returns: standard deviation ratio, pattern correlation coefficient
        :rtype: :float:'float','float' 
        '''
        return ma.array([calc_stddev_ratio(target_dataset.values, ref_dataset.values), calc_correlation(target_dataset.values, ref_dataset.values)])


class TemporalStdDev(UnaryMetric):
    '''Calculate the standard deviation over the time.'''

    def run(self, target_dataset):
        '''Calculate the temporal std. dev. for a datasets.

        .. note::
           Overrides UnaryMetric.run()

        :param target_dataset: The target_dataset on which to calculate the 
            temporal standard deviation.
        :type target_dataset: :class:`dataset.Dataset`

        :returns: The temporal standard deviation of the target dataset
        :rtype: :class:`ndarray`
        '''
        return calc_stddev(target_dataset.values, axis=0)


class StdDevRatio(BinaryMetric):
    '''Calculate the standard deviation ratio between two datasets.'''

    def run(self, ref_dataset, target_dataset):
        '''Calculate the standard deviation ratio.

        .. note::
            Overrides BinaryMetric.run()

        :param ref_dataset: The reference dataset to use in this metric run.
        :type ref_dataset: :class:`dataset.Dataset`

        :param target_dataset: The target dataset to evaluate against the
            reference dataset in this metric run.
        :type target_dataset: :class:`dataset.Dataset`

        :returns: The standard deviation ratio of the reference and target
        '''

        return calc_stddev_ratio(target_dataset.values, ref_dataset.values)


class PatternCorrelation(BinaryMetric):
    '''Calculate the correlation coefficient between two datasets'''

    def run(self, ref_dataset, target_dataset):
        '''Calculate the correlation coefficient between two dataset.

        .. note::
           Overrides BinaryMetric.run()

        :param ref_dataset: The reference dataset to use in this metric run.
        :type ref_dataset: :class:`dataset.Dataset`

        :param target_dataset: The target dataset to evaluate against the
            reference dataset in this metric run.
        :type target_dataset: :class:`dataset.Dataset`

        :returns: The correlation coefficient between a reference and target dataset.
        '''
        # stats.pearsonr returns correlation_coefficient, 2-tailed p-value
        # We only care about the correlation coefficient
        # Docs at
        # http://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.pearsonr.html

        return calc_correlation(target_dataset.values, ref_dataset.values)


class TemporalCorrelation(BinaryMetric):
    '''Calculate the temporal correlation coefficients and associated
       confidence levels between two datasets, using Pearson's correlation.'''

    def run(self, reference_dataset, target_dataset):
        '''Calculate the temporal correlation coefficients and associated
           confidence levels between two datasets, using Pearson's correlation.

        .. note::
           Overrides BinaryMetric.run()

        :param reference_dataset: The reference dataset to use in this metric
            run
        :type reference_dataset: :class:`dataset.Dataset`

        :param target_dataset: The target dataset to evaluate against the
            reference dataset in this metric run
        :type target_dataset: :class:`dataset.Dataset`

        :returns: A 2D array of temporal correlation coefficients and a 2D
            array of confidence levels associated with the temporal correlation
            coefficients
        '''
        num_times, num_lats, num_lons = reference_dataset.values.shape
        coefficients = ma.zeros([num_lats, num_lons])
        for i in numpy.arange(num_lats):
            for j in numpy.arange(num_lons):
                coefficients[i, j] = calc_correlation(
                    target_dataset.values[:, i, j],
                    reference_dataset.values[:, i, j])
        return coefficients


class TemporalMeanBias(BinaryMetric):
    '''Calculate the bias averaged over time.'''

    def run(self, ref_dataset, target_dataset):
        '''Calculate the bias averaged over time.

        .. note::
           Overrides BinaryMetric.run()

        :param ref_dataset: The reference dataset to use in this metric run.
        :type ref_dataset: :class:`dataset.Dataset`

        :param target_dataset: The target dataset to evaluate against the
            reference dataset in this metric run.
        :type target_dataset: :class:`dataset.Dataset`

        :returns: The mean bias between a reference and target dataset over time.
        '''

        return calc_bias(target_dataset.values, ref_dataset.values, average_over_time=True)


class RMSError(BinaryMetric):
    '''Calculate the Root Mean Square Difference (RMS Error), with the mean
       calculated over time and space.'''

    def run(self, reference_dataset, target_dataset):
        '''Calculate the Root Mean Square Difference (RMS Error), with the mean
           calculated over time and space.

        .. note::
           Overrides BinaryMetric.run()

        :param reference_dataset: The reference dataset to use in this metric
            run
        :type reference_dataset: :class:`dataset.Dataset`

        :param target_dataset: The target dataset to evaluate against the
            reference dataset in this metric run
        :type target_dataset: :class:`dataset.Dataset`

        :returns: The RMS error, with the mean calculated over time and space
        '''

        return calc_rmse(target_dataset.values, reference_dataset.values)


def calc_bias(target_array, reference_array, average_over_time=False):
    ''' Calculate difference between two arrays

    :param target_array: an array to be evaluated, as model output
    :type target_array: :class:'numpy.ma.core.MaskedArray'

    :param reference_array: an array of reference dataset
    :type reference_array: :class:'numpy.ma.core.MaskedArray'

    :param average_over_time: if True, calculated bias is averaged for the axis=0
    :type average_over_time: 'bool'

    :returns: Biases array of the target dataset
    :rtype: :class:'numpy.ma.core.MaskedArray'
    '''

    bias = target_array - reference_array
    if average_over_time:
        return ma.average(bias, axis=0)
    else:
        return bias


def calc_stddev(array, axis=None):
    ''' Calculate a sample standard deviation of an array along the array

    :param array: an array to calculate sample standard deviation
    :type array: :class:'numpy.ma.core.MaskedArray'

    :param axis: Axis along which the sample standard deviation is computed.
    :type axis: 'int'

    :returns: sample standard deviation of array
    :rtype: :class:'numpy.ma.core.MaskedArray'
    '''

    if isinstance(axis, int):
        return ma.std(array, axis=axis, ddof=1)
    else:
        return ma.std(array, ddof=1)


def calc_stddev_ratio(target_array, reference_array):
    ''' Calculate ratio of standard deivations of the two arrays

    :param target_array: an array to be evaluated, as model output
    :type target_array: :class:'numpy.ma.core.MaskedArray'

    :param reference_array: an array of reference dataset
    :type reference_array: :class:'numpy.ma.core.MaskedArray'

    :param average_over_time: if True, calculated bias is averaged for the axis=0
    :type average_over_time: 'bool'

    :returns: (standard deviation of target_array)/(standard deviation of reference array)
    :rtype: :class:'float'
    '''

    return calc_stddev(target_array) / calc_stddev(reference_array)


def calc_correlation(target_array, reference_array):
    '''Calculate the correlation coefficient between two arrays.

    :param target_array: an array to be evaluated, as model output
    :type target_array: :class:'numpy.ma.core.MaskedArray'

    :param reference_array: an array of reference dataset
    :type reference_array: :class:'numpy.ma.core.MaskedArray'

    :returns: pearson's correlation coefficient between the two input arrays
    :rtype: :class:'numpy.ma.core.MaskedArray'
    '''

    return mstats.pearsonr(reference_array.flatten(), target_array.flatten())[0]


def calc_rmse(target_array, reference_array):
    ''' Calculate ratio of standard deivations of the two arrays

    :param target_array: an array to be evaluated, as model output
    :type target_array: :class:'numpy.ma.core.MaskedArray'

    :param reference_array: an array of reference dataset
    :type reference_array: :class:'numpy.ma.core.MaskedArray'

    :param average_over_time: if True, calculated bias is averaged for the axis=0
    :type average_over_time: 'bool'

    :returns: root mean square error
    :rtype: :class:'float'
    '''

    return (ma.mean((calc_bias(target_array, reference_array))**2))**0.5


def calc_histogram_overlap(hist1, hist2):
    ''' from Lee et al. (2014)
    :param hist1: a histogram array
    :type hist1: :class:'numpy.ndarray'
    :param hist2: a histogram array with the same size as hist1
    :type hist2: :class:'numpy.ndarray'
    '''

    hist1_flat = hist1.flatten()
    hist2_flat = hist2.flatten()

    if len(hist1_flat) != len(hist2_flat):
        err = "The two histograms have different sizes"
        raise ValueError(err)
    overlap = 0.
    for ii in len(hist1_flat):
        overlap = overlap + numpy.min(hist1_flat[ii], hist2_flat[ii])
    return overlap


def calc_joint_histogram(data_array1, data_array2, bins_for_data1, bins_for_data2):
    ''' Calculate a joint histogram of two variables in data_array1 and data_array2
    :param data_array1: the first variable
    :type data_array1: :class:'numpy.ma.core.MaskedArray'
    :param data_array2: the second variable
    :type data_array2: :class:'numpy.ma.core.MaskedArray'
    :param bins_for_data1: histogram bin edges for data_array1
    :type bins_for_data1: :class:'numpy.ndarray'
    :param bins_for_data2: histogram bin edges for data_array2
    :type bins_for_data2: :class:'numpy.ndarray'
    '''
    if ma.count_masked(data_array1) != 0 or ma.count_masked(data_array2) != 0:
        index = numpy.where((data_array1.mask == False) &
                            (data_array2.mask == False))
        new_array1 = data_array1[index]
        new_array2 = data_array2[index]
    else:
        new_array1 = data_array1.flatten()
        new_array2 = data_array2.flatten()

    histo2d, xedge, yedge = numpy.histogram2d(new_array1, new_array2, bins=[
                                              bins_for_data1, bins_for_data2])
    return histo2d


def wet_spell_analysis(reference_array, threshold=0.1, nyear=1, dt=3.):
    ''' Characterize wet spells using sub-daily (hourly) data

    :param reference_array: an array to be analyzed
    :type reference_array: :class:'numpy.ma.core.MaskedArray'

    :param threshold: the minimum amount of rainfall [mm/hour] 
    :type threshold: 'float'

    :param nyear: the number of discontinous periods 
    :type nyear: 'int'

    :param dt: the temporal resolution of reference_array
    :type dt: 'float'
    '''
    nt = reference_array.shape[0]
    if reference_array.ndim == 3:
        reshaped_array = reference_array.reshape[nt, reference_array.size / nt]
    else:
        reshaped_array = reference_array
    xy_indices = np.where(reshaped_array.mask[0, :] == False)[0]

    nt_each_year = nt / nyear
    spell_duration = []
    peak_rainfall = []
    total_rainfall = []

    for index in xy_indices:
        for iyear in np.arange(nyear):
            data0_temp = reshaped_array[nt_each_year * iyear:nt_each_year * (iyear + 1),
                                        index]
            # time indices when precipitation rate is smaller than the
            # threshold [mm/hr]
            t_index = np.where((data0_temp <= threshold) &
                               (data0_temp.mask == False))[0]
            t_index = np.insert(t_index, 0, 0)
            t_index = t_index + nt_each_year * iyear
            for it in np.arange(t_index.size - 1):
                if t_index[it + 1] - t_index[it] > 1:
                    data1_temp = data0_temp[t_index[it] + 1:t_index[it + 1]]
                    if not ma.is_masked(data1_temp):
                        spell_duration.append(
                            (t_index[it + 1] - t_index[it] - 1) * dt)
                        peak_rainfall.append(data1_temp.max())
                        total_rainfall.append(data1_temp.sum())
    return np.array(spell_duration), np.array(peak_rainfall), np.array(total_rainfall)
