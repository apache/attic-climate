#
#  Licensed to the Apache Software Foundation (ASF) under one or more
#  contributor license agreements.  See the NOTICE file distributed with
#  this work for additional information regarding copyright ownership.
#  The ASF licenses this file to You under the Apache License, Version 2.0
#  (the "License"); you may not use this file except in compliance with
#  the License.  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

''' Provides endpoints for running an OCW evaluation. '''

from ast import literal_eval
from datetime import timedelta
import inspect
import sys

from bottle import Bottle, request

import ocw.data_source.local as local
import ocw.data_source.rcmed as rcmed
import ocw.dataset_processor as dsp
from ocw.evaluation import Evaluation
import ocw.metrics as metrics

processing_app = Bottle()

@processing_app.route('/run_evaluation/')
def run_evaluation():
    ''' Run an OCW Evaluation.

    run_evaluation expects the Evaluation parameters to be encoded in request
    parameters with the following format.

    ..sourcecode: javascript

        {
            reference_dataset: {
                // Id that tells us how we need to load this dataset.
                'data_source_id': 1 == local, 2 == rcmed, 

                // Dict of data_source specific identifying information.
                //
                // if data_source_id == 1 == local:
                // {
                //     'id': The path to the local file on the server for loading.
                //     'var_name': The variable data to pull from the file.      
                //     'lat_name': The latitude variable name.
                //     'lon_name': The longitude variable name.
                //     'time_name': The time variable name
                // }
                // 
                // if data_source_id == 2 == rcmed:
                // {
                //     'dataset_id': The dataset id to grab from RCMED.
                //     'parameter_id': The variable id value used by RCMED.
                // }
                'dataset_info': {..}
            },

            // The list of target datasets to use in the Evaluation. The data
            // format for the dataset objects should be the same as the 
            // reference_dataset above.
            'target_datasets': [{...}, {...}, ...],

            // All the datasets are re-bin to the reference dataset
            // before being added to an experiment. This step (in degrees)
            // is used when re-bin both the reference and target datasets.
            'spatial_rebin_lat_step': The lat degree step to use when re-bin,

            // Same as above, but for lon
            'spatial_rebin_lon_step': The lon degree step to use when re-bin,

            // The temporal resolution to use when doing a temporal re-bin 
            // This is a timedelta of days to use so daily == 1, monthly is
            // (1, 31], annual/yearly is (31, 366], and full is anything > 366.
            'temporal_resolution': Integer in range(1, 999),

            // A list of the metric class names to use in the evaluation. The
            // names must match the class name exactly.
            'metrics': [BiasMetric, TemporalStdDev, ...]

            // The bounding values used in the Evaluation. Note that lat values
            // should range from -180 to 180 and lon values from -90 to 90.
            'start_time': start time value in the format '%Y-%m-%d %H:%M:%S',
            'end_time': end time value in the format '%Y-%m-%d %H:%M:%S',
            'lat_min': The minimum latitude value,
            'lat_max': The maximum latitude value,
            'lon_min': The minimum longitude value,
            'lon_max': The maximum longitude value,

            // The degree step that the latitude and longitude values should be
            // re-binned to. Values must be > 0
            'lat_degree_step': Integer > 0,
            'lon_degree_step': Integer > 0,

            // NOTE: At the moment, subregion support is fairly minimal. This
            // will be addressed in the future. Ideally, the user should be able
            // to load a file that they have locally. That would change the
            // format that this data is passed.
            'subregion_information': Path to a subregion file on the server.
        }
    
    '''
    # TODO: validate input parameters and return an error if not valid

    eval_bounds = {
        'start_time': request.query.start_time,
        'end_time': request.query.end_time,
        'lat_min': request.query.lat_min,
        'lat_max': request.query.lat_max,
        'lon_min': request.query.lon_min,
        'lon_max': request.query.lon_max
    }

    # Load all the datasets
    ref_object = literal_eval(request.query['reference_dataset'])
    ref_dataset = _process_dataset_object(ref_object, eval_bounds)

    target_objects = literal_eval(request.query['target_datasets'])
    target_datasets = [_process_dataset_object(obj, eval_bounds) for obj in target_objects]

    # Do temporal re-bin based off of passed resolution
    time_delta = timedelta(days=request.query['temporal_resolution'])
    ref_dataset = dsp.temporal_rebin(ref_dataset, time_delta)
    target_datasets = [dsp.temporal_rebin(ds, time_delta) for ds in target_datasets]

    # Do spatial re=bin based off of reference dataset + lat/lon steps
    lat_step = request.query['lat_degree_step']
    lon_step = request.query['lon_degree_step']
    lat_bins, lon_bins = _calculate_new_latlon_bins(eval_bounds, lat_step, lon_step)
    ref_dataset = dsp.spatial_regrid(ref_dataset, lat_bins, lon_bins)
    target_datasets =  [dsp.spatial_regrid(ds, lat_bins, lon_bins) for ds in datasets]

    # Load metrics
    metrics = _load_metrics(request.query['metrics'])

    # Prime evaluation object with data
    # Run evaluation
    # Plot (I have no idea how this is going to work)

def _process_dataset_object(dataset_object, eval_bounds):
    ''' Convert an dataset object representation into an OCW Dataset

    The dataset_object must contain two pieces of information. The 
    `data_source_id` tells how to load the dataset, and the `dataset_info`
    contains all the information necessary for the load. 

    .. sourcecode: javascript

        // Id that tells us how we need to load this dataset.
        'data_source_id': 1 == local, 2 == rcmed, 

        // Dict of data_source specific identifying information.
        //
        // if data_source_id == 1 == local:
        // {
        //     'id': The path to the local file on the server for loading.
        //     'var_name': The variable data to pull from the file.      
        //     'lat_name': The latitude variable name.
        //     'lon_name': The longitude variable name.
        //     'time_name': The time variable name
        // }
        // 
        // if data_source_id == 2 == rcmed:
        // {
        //     'dataset_id': The dataset id to grab from RCMED.
        //     'parameter_id': The variable id value used by RCMED.
        // }
        'dataset_info': {..}

    :param dataset_object: Dataset information of the above form to be 
        loaded into an OCW Dataset object.
    :type dataset_object: Dictionary
    :param eval_bounds: The evaluation bounds for this Evaluation. These
        are needed to load RCMED datasets.
    :type eval_bounds: Dictionary

    :returns: dataset_object converted to an ocw.Dataset

    :raises KeyError: If dataset_object is malformed and doesn't contain the 
        keys `data_source_id` or `dataset_info`.
    :raises ValueError: If the data_source_id isn't valid.

    '''
    source_id = int(dataset_object['data_source_id'])
    dataset_info = dataste_object['dataset_info']

    # If we should load with local
    if source_id == 1:
        _load_local_dataset_object(dataset_info)
    # If we should load with RCMED
    elif source_id == 2:
        _load_rcmed_dataset_object(dataset_info, eval_bounds)
    else:
        cur_frame = sys._getframe().f_code
        err = "{}.{}: Invalid data_source_id - {}".format(
            cur_frame.co_filename,
            cur_frame.co_name,
            source_id
        )
        raise ValueError(err)

def _load_local_dataset_object(dataset_info):
    ''' Create an ocw.dataset.Dataset object from supplied data.

    .. note: At the moment, data_source.local cannot take advantage of all the
        supplied variable names. This functionality will be added in the future.
        However, in the mean time, it is expected that the dataset_info object
        still contain all the appropriate keys.

    :param dataset_info: The necessary data to load a local dataset with
        ocw.data_source.local. Must be of the form:
        {
            'id': The path to the local file for loading,
            'var_name': The variable data to pull from the file,
            'lat_name': The latitude variable name,
            'lon_name': The longitude variable name,
            'time_name': The time variable name
        }
    :type dataset_info: Dictionary

    :returns: An ocw.dataset.Dataset object containing the requested information.

    :raises KeyError: If the required keys aren't present in the dataset_info.
    :raises ValueError: If data_source.local could not load the requested file.
    '''
    path = dataset_info['id']
    var_name = dataset_info['var_name']
    lat_name = dataset_info['lat_name']
    lon_name = dataset_info['lon_name']
    time_name = dataset_info['time_name']

    return local.load_file(path, var_name)

def _load_rcmed_dataset_object(dataset_info, eval_bounds):
    ''' Create an ocw.dataset.Dataset object from supplied data.

    :param dataset_info: The necessary data to load a RCMED dataset with
        ocw.data_source.rcmed. Must be of the form:
        {
            'dataset_id': The dataset id to grab from RCMED.
            'parameter_id': The variable id value used by RCMED.
        }
    :type dataset_info: Dictionary

    :param eval_bounds: The time, lat, and lon bounds values for this Evaluation.
        Must be of the form:
        {
            'start_time': request.query.start_time,
            'end_time': request.query.end_time,
            'lat_min': request.query.lat_min,
            'lat_max': request.query.lat_max,
            'lon_min': request.query.lon_min,
            'lon_max': request.query.lon_max
        }
    ;type eval_bounds: Dictionary

    :returns: An ocw.dataset.Dataset object containing the requested information.

    :raises KeyError: If the required keys aren't present in the dataset_info or
        eval_bounds objects.
    '''
    return rcmed.parameter_dataset(
        dataset_info['dataset_id'],
        dataset_info['parameter_id'],
        eval_bounds['lat_min'],
        eval_bounds['lat_max'],
        eval_bounds['lon_min'],
        eval_bounds['lon_max'],
        eval_bounds['start_time'],
        eval_bounds['end_time']
    )

def _calculate_new_latlon_bins(eval_bounds, lat_grid_step, lon_grid_step):
    ''' Calculate the new lat/lon ranges for spatial re-binning.

    :param eval_bounds: The time and lat/lon bounds for the evaluation.
        Must be of the form:
        {
            'start_time': request.query.start_time,
            'end_time': request.query.end_time,
            'lat_min': request.query.lat_min,
            'lat_max': request.query.lat_max,
            'lon_min': request.query.lon_min,
            'lon_max': request.query.lon_max
        }
    :type eval_bounds: Dictionary
    :param lat_grid_step: The degree step between successive latitude values
        in the newly created bins.
    :type lat_grid_step: Integer > 0
    :param lon_grid_step: The degree step between successive longitude values
        in the newly created bins.
    :type lat_grid_step: Integer > 0

    :returns: The new lat/lon value lists as a tuple of the form (new_lats, new_lons)
    '''
    new_lats = np.arange(eval_bounds['min_lat'], eval_bounds['max_lat'], lat_grid_step)
    new_lons = np.arange(eval_bounds['min_lon'], eval_bounds['max_lon'], lon_grid_step)
    return (new_lats, new_lons)

def _load_metrics(metric_names):
    ''' Load and create an instance of each requested metric.

    :param metric_names: The names of the metrics that should be loaded and 
        instantiated from ocw.metrics for use in an evaluation.
    :type metric_names: List

    :returns: A List of Metric objects

    :raises ValueError: If a metric name cannot be matched.
    '''
    instantiated_metrics = []
    possible_metrics = _get_valid_metric_options()
    for metric in metric_names:
        if metric not in possible_metrics:
            cur_frame = sys._getframe().f_code
            err = "{}.{}: Invalid metric name - {}".format(
            cur_frame.co_filename,
            cur_frame.co_name,
            metric
            )
            raise ValueError(err)

        metric_class = _load_metric_class_from_name(metric)
        instantiated_metrics.append(metric_class())

    return instantiated_metrics

def _get_valid_metric_options():
    ''' Get valid metric names from the ocw.metrics module.

    :returns: A dictionary of metric name, object pairs
    '''
    invalid_metrics = ['Metric', 'UnaryMetric', 'BinaryMetric']
    return {name:obj
            for name, obj in inspect.getmembers(metrics)
            if inspect.isclass(obj) and name not in invalid_metrics}

def _load_metric_class_from_name(metric_name):
    ''' Load a metric class by name from ocw.metrics.

    :param metric_name: The name of the metric class to load from ocw.metrics.
    :type metric_name: String

    :returns: The loaded metric Class
    '''
    module = __import__('ocw.metrics', fromlist=[metric_name])
    return getattr(module, metric_name)
