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

from datetime import timedelta, datetime
import inspect
import sys
import os
import json

from bottle import Bottle, request, response

from config import WORK_DIR

import ocw.data_source.local as local
import ocw.data_source.rcmed as rcmed
import ocw.dataset_processor as dsp
from ocw.evaluation import Evaluation
from ocw.dataset import Bounds
import ocw.metrics as metrics
import ocw.plotter as plotter

import numpy as np

processing_app = Bottle()

@processing_app.hook('after_request')
def enable_cors():
    ''' Allow Cross-Origin Resource Sharing for all URLs. '''
    response.headers['Access-Control-Allow-Origin'] = '*'

@processing_app.route('/run_evaluation/', method='POST')
def run_evaluation():
    ''' Run an OCW Evaluation.

    run_evaluation expects the Evaluation parameters to be POSTed in
    the following format.

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
                //     'name': Optional dataset name
                // }
                //
                // if data_source_id == 2 == rcmed:
                // {
                //     'dataset_id': The dataset id to grab from RCMED.
                //     'parameter_id': The variable id value used by RCMED.
                //     'name': Optional dataset name
                // }
                'dataset_info': {..}
            },

            // The list of target datasets to use in the Evaluation. The data
            // format for the dataset objects should be the same as the
            // reference_dataset above.
            'target_datasets': [{...}, {...}, ...],

            // All the datasets are re-binned to the reference dataset
            // before being added to an experiment. This step (in degrees)
            // is used when re-binning both the reference and target datasets.
            'spatial_rebin_lat_step': The lat degree step. Integer > 0,

            // Same as above, but for lon
            'spatial_rebin_lon_step': The lon degree step. Integer > 0,

            // The temporal resolution to use when doing a temporal re-bin
            // This is a timedelta of days to use so daily == 1, monthly is
            // (1, 31], annual/yearly is (31, 366], and full is anything > 366.
            'temporal_resolution': Integer in range(1, 999),

            // A list of the metric class names to use in the evaluation. The
            // names must match the class name exactly.
            'metrics': [Bias, TemporalStdDev, ...]

            // The bounding values used in the Evaluation. Note that lat values
            // should range from -180 to 180 and lon values from -90 to 90.
            'start_time': start time value in the format '%Y-%m-%d %H:%M:%S',
            'end_time': end time value in the format '%Y-%m-%d %H:%M:%S',
            'lat_min': The minimum latitude value,
            'lat_max': The maximum latitude value,
            'lon_min': The minimum longitude value,
            'lon_max': The maximum longitude value,

            // NOTE: At the moment, subregion support is fairly minimal. This
            // will be addressed in the future. Ideally, the user should be able
            // to load a file that they have locally. That would change the
            // format that this data is passed.
            'subregion_information': Path to a subregion file on the server.
        }

    '''
    # TODO: validate input parameters and return an error if not valid

    eval_time_stamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    data = request.json

    eval_bounds = {
        'start_time': datetime.strptime(data['start_time'], '%Y-%m-%d %H:%M:%S'),
        'end_time': datetime.strptime(data['end_time'], '%Y-%m-%d %H:%M:%S'),
        'lat_min': float(data['lat_min']),
        'lat_max': float(data['lat_max']),
        'lon_min': float(data['lon_min']),
        'lon_max': float(data['lon_max'])
    }

    # Load all the datasets
    ref_dataset = _process_dataset_object(data['reference_dataset'], eval_bounds)

    target_datasets = [_process_dataset_object(obj, eval_bounds)
					   for obj
					   in data['target_datasets']]

    # Do temporal re-bin based off of passed resolution
    time_delta = timedelta(days=data['temporal_resolution'])
    ref_dataset = dsp.temporal_rebin(ref_dataset, time_delta)
    target_datasets = [dsp.temporal_rebin(ds, time_delta)
					   for ds
					   in target_datasets]

    ## Subset the datasets
    #subset = Bounds(eval_bounds['lat_min'],
                    #eval_bounds['lat_max'],
                    #eval_bounds['lon_min'],
                    #eval_bounds['lon_max'],
                    #eval_bounds['start_time'],
                    #eval_bounds['end_time'])

    #ref_dataset = dsp.subset(subset, ref_dataset)
    #target_datasets = [dsp.subset(subset, ds)
					   #for ds
					   #in target_datasets]

    # Do spatial re=bin based off of reference dataset + lat/lon steps
    lat_step = data['spatial_rebin_lat_step']
    lon_step = data['spatial_rebin_lon_step']
    lat_bins, lon_bins = _calculate_new_latlon_bins(eval_bounds,
													lat_step,
													lon_step)

    ref_dataset = dsp.spatial_regrid(ref_dataset, lat_bins, lon_bins)
    target_datasets =  [dsp.spatial_regrid(ds, lat_bins, lon_bins)
						for ds
						in target_datasets]

    # Load metrics
    loaded_metrics = _load_metrics(data['metrics'])

    # Prime evaluation object with data
    evaluation = Evaluation(ref_dataset, target_datasets, loaded_metrics)

    # Run evaluation
    evaluation.run()

    # Plot
    _generate_evaluation_plots(evaluation, lat_bins, lon_bins, eval_time_stamp)

    return json.dumps({'eval_work_dir': eval_time_stamp})

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
        //     'name': Optional dataset name
        // }
        //
        // if data_source_id == 2 == rcmed:
        // {
        //     'dataset_id': The dataset id to grab from RCMED.
        //     'parameter_id': The variable id value used by RCMED.
        //     'name': Optional dataset name
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
    dataset_info = dataset_object['dataset_info']

    # If we should load with local
    if source_id == 1:
        return _load_local_dataset_object(dataset_info)
    # If we should load with RCMED
    elif source_id == 2:
        return _load_rcmed_dataset_object(dataset_info, eval_bounds)
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
            'dataset_id': The path to the local file for loading,
            'var_name': The variable data to pull from the file,
            'lat_name': The latitude variable name,
            'lon_name': The longitude variable name,
            'time_name': The time variable name
            'name': Optional dataset name
        }
    :type dataset_info: Dictionary

    :returns: An ocw.dataset.Dataset object containing the requested information.

    :raises KeyError: If the required keys aren't present in the dataset_info.
    :raises ValueError: If data_source.local could not load the requested file.
    '''
    path = dataset_info['dataset_id']
    var_name = dataset_info['var_name']
    lat_name = dataset_info['lat_name']
    lon_name = dataset_info['lon_name']
    time_name = dataset_info['time_name']
    # If a name is passed for the dataset, use it. Otherwise, use the file name.
    name = (dataset_info['name'] 
            if 'name' in dataset_info.keys() 
            else path.split('/')[-1])

    dataset =  local.load_file(path, var_name)
    dataset.name = name
    return dataset

def _load_rcmed_dataset_object(dataset_info, eval_bounds):
    ''' Create an ocw.dataset.Dataset object from supplied data.

    :param dataset_info: The necessary data to load a RCMED dataset with
        ocw.data_source.rcmed. Must be of the form:
        {
            'dataset_id': The dataset id to grab from RCMED.
            'parameter_id': The variable id value used by RCMED.
            'name': Optional dataset name
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
    dataset = rcmed.parameter_dataset(dataset_info['dataset_id'],
								      dataset_info['parameter_id'],
								      eval_bounds['lat_min'],
								      eval_bounds['lat_max'],
								      eval_bounds['lon_min'],
								      eval_bounds['lon_max'],
								      eval_bounds['start_time'],
								      eval_bounds['end_time'])

    # If a name is passed for the dataset, use it. Otherwise, use the file name.
    if 'name'in dataset_info.keys():
        name = dataset_info['name']
    else:
        for m in rcmed.get_parameters_metadata():
            if m['parameter_id'] == str(dataset_info['parameter_id']):
                name = m['longname']
                break
        else:
            # If we can't find a name for the dataset, default to something...
            name = "RCMED dataset"

    dataset.name = name

    return dataset

def _calculate_new_latlon_bins(eval_bounds, lat_grid_step, lon_grid_step):
    ''' Calculate the new lat/lon ranges for spatial re-binning.

    :param eval_bounds: The time and lat/lon bounds for the evaluation.
        Must be of the form:
        {
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
    new_lats = np.arange(eval_bounds['lat_min'],
						 eval_bounds['lat_max'],
						 lat_grid_step)
    new_lons = np.arange(eval_bounds['lon_min'],
						 eval_bounds['lon_max'],
						 lon_grid_step)
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
    metrics_map = _get_valid_metric_options()
    possible_metrics = metrics_map.keys()

    for metric in metric_names:
        if metric not in possible_metrics:
            cur_frame = sys._getframe().f_code
            err = "{}.{}: Invalid metric name - {}".format(
            cur_frame.co_filename,
            cur_frame.co_name,
            metric
            )
            raise ValueError(err)

        instantiated_metrics.append(metrics_map[metric]())

    return instantiated_metrics

def _get_valid_metric_options():
    ''' Get valid metric options from the ocw.metrics module.

    :returns: A dictionary of metric (name, object) pairs
    '''
    invalid_metrics = ['Metric', 'UnaryMetric', 'BinaryMetric']
    return {name:obj
            for name, obj in inspect.getmembers(metrics)
            if inspect.isclass(obj) and name not in invalid_metrics}

def _generate_evaluation_plots(evaluation, lat_bins, lon_bins, eval_time_stamp):
    ''' Generate the Evaluation's plots

    .. note: This doesn't support graphing evaluations with subregion data.

    :param evaluation: A run Evaluation for which to generate plots.
    :type evaluation: ocw.evaluation.Evaluation
    :param lat_bins: The latitude bin values used in the evaluation.
    :type lat_bins: List
    :param lon_bins: The longitude bin values used in the evaluation.
    :type lon_bins: List
    :param eval_time_stamp: The time stamp for the directory where
        evaluation results should be saved.
    :type eval_time_stamp: Time stamp of the form '%Y-%m-%d_%H-%M-%S'

    :raises ValueError: If there aren't any results to graph.
    '''
    # Create time stamp version-ed WORK_DIR for plotting
    eval_path = os.path.join(WORK_DIR, eval_time_stamp)
    os.makedirs(eval_path)

    # TODO: Should be able to check for None here...
    if evaluation.results == [] and evaluation.unary_results == []:
        cur_frame = sys._getframe().f_code
        err = "{}.{}: No results to graph".format(cur_frame.co_filename,
												  cur_frame.co_name)
        raise ValueError(err)

    if evaluation.ref_dataset:
        grid_shape_dataset = evaluation.ref_dataset
    else:
        grid_shape_dataset = evaluation.target_datasets[0]

    grid_shape = _calculate_grid_shape(grid_shape_dataset)

    if evaluation.results != []:
        for dataset_index, dataset in enumerate(evaluation.target_datasets):
            for metric_index, metric in enumerate(evaluation.metrics):
                results = evaluation.results[dataset_index][metric_index]
                file_name = _generate_binary_eval_plot_file_path(evaluation,
																 dataset_index,
																 metric_index,
                                                                 eval_time_stamp)
                plot_title = _generate_binary_eval_plot_title(evaluation,
															  dataset_index,
															  metric_index)
                plotter.draw_contour_map(results,
										 lat_bins,
										 lon_bins,
										 fname=file_name,
										 ptitle=plot_title,
                                         gridshape=grid_shape)

    if evaluation.unary_results != []:
        for metric_index, metric in enumerate(evaluation.unary_metrics):
			cur_unary_results = evaluation.unary_results[metric_index]
			for result_index, result in enumerate(cur_unary_results):
				file_name = _generate_unary_eval_plot_file_path(evaluation,
																result_index,
																metric_index,
                                                                eval_time_stamp)
				plot_title = _generate_unary_eval_plot_title(evaluation,
															 result_index,
															 metric_index)

				plotter.draw_contrough_map(results,
										   lat_bins,
										   lon_bins,
										   fname=file_name,
										   ptitle=plot_title,
                                           gridshape=grid_shape)

def _calculate_grid_shape(reference_dataset, max_cols=6):
    ''' Calculate the plot grid shape given a reference dataset. 

    :param reference_dataset: The dataset from which to strip out temporal
        bin information and calculate grid shape.
    :type reference_dataset: ocw.dataset.Dataset
    :param max_cols: The maximum number of columns in the calculated grid shape.
        Note that the calculated shape with always have max_cols as its column
        count.
    :type max_cols: Integer > 0

    :returns: The grid shape to use as (num_rows, num_cols)
    '''
    total_temporal_bins = reference_dataset.values.shape[0]
    temporal_bins = total_temporal_bins

    num_rows = 1
    while temporal_bins > max_cols:
        temporal_bins -= max_cols
        num_rows += 1

    return _balance_grid_shape(total_temporal_bins, num_rows, max_cols)
    #return (num_rows, max_cols)

def _balance_grid_shape(total_temporal_bins, num_rows, num_cols):
    ''' Balance grid shape values to prevent large row/col discrepancies.

    Often times _calculate_grid_shape will result in values where there is a
    large difference between row/column count. This tries to balance out the
    shape so that it is as square as possible.

    :param total_temporal_bins: The total number of bins that the shape must
        fit.
    :type total_temporal_bins: Integer >= 1
    :params num_rows: The number of rows.
    :type num_rows: Integer >= 1
    :params num_cols: The number of columns.
    :type num_cols: Integer >= 1

    :returns: The adjusted shape values so the difference between the number
        of rows and the number of columns <= 1.
    '''
    while True:
        if abs(num_rows - num_cols) <= 1:
            # We might be able to reduce both.
            if total_temporal_bins < (num_rows - 1) * (num_cols - 1):
                num_rows -= 1
                num_cols -= 1
            # If not, then we're nearly done.
            else:
                # We might end up with a grid that is slightly too large. We
                # tend to favor larger column numbers rather than rows, so we'll
                # try to drop another column to get a tighter grid.
                if total_temporal_bins <= num_rows * (num_cols - 1):
                    num_cols -= 1

                # Favor more columns or more rows in the final layout.
                if num_rows > num_cols:
                    num_rows, num_cols = num_cols, num_rows

                break
        else:
            if num_rows > num_cols:
                # When we have a delta >= 2, first we try to drop just one of the values.
                if total_temporal_bins < (num_rows - 1) * num_cols:
                        num_rows -= 1
                # In certain cases we can't just drop a value yet we still have a delta
                # that is >= 2. In that situation we need to trade a value between them.
                elif total_temporal_bins < (num_rows - 1) * (num_cols + 1):
                    num_rows -= 1
                    num_cols += 1
            else:
                if total_temporal_bins < num_rows * (num_cols - 1):
                        num_cols -= 1
                elif total_temporal_bins < (num_rows + 1) * (num_cols - 1):
                    num_rows += 1
                    num_cols -= 1

    return (int(num_rows), int(num_cols))

def _generate_binary_eval_plot_file_path(evaluation, dataset_index,
                                         metric_index, time_stamp):
    ''' Generate a plot path for a given binary metric run.

    :param evaluation: The Evaluation object from which to pull name information.
    :type evaluation: ocw.evaluation.Evaluation
    :param dataset_index: The index of the target dataset to use when
		generating the name.
    :type dataset_index: Integer >= 0 < len(evaluation.target_datasets)
    :param metric_index: The index of the metric to use when generating the name.
    :type metric_index: Integer >= 0 < len(evaluation.metrics)

    :returns: The full path for the requested metric run. The paths will always
		be placed in the WORK_DIR set for the web services.
    '''
    plot_name = "{}_compared_to_{}_{}".format(
        evaluation.ref_dataset.name.lower(),
        evaluation.target_datasets[dataset_index].name.lower(),
        evaluation.metrics[metric_index].__class__.__name__.lower()
    )

    timestamped_workdir = os.path.join(WORK_DIR, time_stamp)
    return os.path.join(timestamped_workdir, plot_name)

def _generate_unary_eval_plot_file_path(evaluation, dataset_index,
                                        metric_index, time_stamp):
    ''' Generate a plot path for a given unary metric run.

    :param evaluation: The Evaluation object from which to pull name information.
    :type evaluation: ocw.evaluation.Evaluation
    :param dataset_index: The index of the target dataset to use when
		generating the name.
    :type dataset_index: Integer >= 0 < len(evaluation.target_datasets)
    :param metric_index: The index of the metric to use when generating the name.
    :type metric_index: Integer >= 0 < len(evaluation.metrics)

    :returns: The full path for the requested metric run. The paths will always
		be placed in the WORK_DIR set for the web services.
    '''
    metric = evaluation.unary_metrics[metric_index]
    timestamped_workdir = os.path.join(WORK_DIR, time_stamp)

    # Unary metrics can be run over both the reference dataset and the target
    # datasets. It's possible for an evaluation to only have one and not the
    # other. If there is a reference dataset then the 0th result index refers to
    # the result of the metric being run on the reference dataset. Any future
    # indexes into the target dataset list must then be offset by one. If
    # there's no reference dataset then we don't have to bother with any of this.
    if evaluation.ref_dataset:
        if dataset_index == 0:
            plot_name = "{}_{}".format(
                evaluation.ref_dataset.name.lower(),
                metric.__class__.__name__.lower()
            )

            return os.path.join(timestamped_workdir, plot_name)
        else:
            dataset_index -= 1

    plot_name = "{}_{}".format(
        evaluation.target_datasets[dataset_index].name.lower(),
        metric.__class__.__name__.lower()
    )

    return os.path.join(timestamped_workdir, plot_name)

def _generate_binary_eval_plot_title(evaluation, dataset_index, metric_index):
    ''' Generate a plot title for a given binary metric run.

    :param evaluation: The Evaluation object from which to pull name information.
    :type evaluation: ocw.evaluation.Evaluation
    :param dataset_index: The index of the target dataset to use when
		generating the name.
    :type dataset_index: Integer >= 0 < len(evaluation.target_datasets)
    :param metric_index: The index of the metric to use when generating the name.
    :type metric_index: Integer >= 0 < len(evaluation.metrics)

    :returns: The plot title for the requested metric run.
    '''
    return "{} of {} compared to {}".format(
        evaluation.metrics[metric_index].__class__.__name__,
        evaluation.ref_dataset.name,
        evaluation.target_datasets[dataset_index].name
    )

def _generate_unary_eval_plot_title(evaluation, dataset_index, metric_index):
    ''' Generate a plot title for a given unary metric run.

    :param evaluation: The Evaluation object from which to pull name information.
    :type evaluation: ocw.evaluation.Evaluation
    :param dataset_index: The index of the target dataset to use when
        generating the name.
    :type dataset_index: Integer >= 0 < len(evaluation.target_datasets)
    :param metric_index: The index of the metric to use when generating the name.
    :type metric_index: Integer >= 0 < len(evaluation.metrics)

    :returns: The plot title for the requested metric run.
    '''

    # Unary metrics can be run over both the reference dataset and the target
    # datasets. It's possible for an evaluation to only have one and not the
    # other. If there is a reference dataset then the 0th result index refers to
    # the result of the metric being run on the reference dataset. Any future
    # indexes into the target dataset list must then be offset by one. If
    # there's no reference dataset then we don't have to bother with any of this.
    if evaluation.ref_dataset:
        if dataset_index == 0:
            return "{} of {}".format(
                evaluation.unary_metrics[metric_index].__class__.__name__,
                evaluation.ref_dataset.name
            )
        else:
            dataset_index -= 1

    return "{} of {}".format(
        evaluation.unary_metrics[metric_index].__class__.__name__,
        evaluation.target_datasets[dataset_index].name
    )
