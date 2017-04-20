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

import datetime as dt
import logging

import yaml

logging.basicConfig()
logger = logging.getLogger(__name__)


def export_evaluation_to_config(evaluation, file_path='./exported_eval.yaml'):
    ''' Export an evaluation to a config file

    :param evaluation: The evaluation object to export.
    :type evaluation: :class:`evaluation.Evaluation`

    :param file_path: Optional file path where the config file should be saved.
    :type file_path: :mod:`string`
    '''
    config = {}

    config['evaluation'] = generate_evaluation_information(evaluation)
    config['datasets'] = generate_dataset_information(evaluation)
    config['metrics'] = generate_metric_information(evaluation)
    config['subregions'] = generate_subregion_information(evaluation)

    yaml.dump(config, file(file_path, 'w'))


def generate_dataset_information(evaluation):
    ''' Generate dataset config file output for a given Evaluation object.

    :param evaluation: The evaluation object from which to extract metrics.
    :type evaluation: :class:`evaluation.Evaluation`

    :returns: A :func:`dict` of dataset configuration information for export
        to a configuration file.
    :rtype: :func:`dict`
    '''
    datasets = {}

    if evaluation.ref_dataset:
        datasets['reference'] = generate_dataset_config(evaluation.ref_dataset)

    if len(evaluation.target_datasets) > 0:
        datasets['targets'] = [
            generate_dataset_config(target)
            for target in evaluation.target_datasets
        ]

    return datasets


def generate_dataset_config(dataset):
    ''' Generate dataset config file output for a given Dataset object.

    :param dataset: The dataset from which to extract configuration
        information.
    :type dataset: :class:`dataset.Dataset`

    :returns: :func:`dict` containing necessary information for
        dataset to be saved into a configuration object.

    :raises AttributeError: If dataset does not contain expected source data.
    '''
    dataset_source = dataset.origin['source']

    if dataset_source == 'local':
        info = _extract_local_dataset_info(dataset)
    elif dataset_source == 'rcmed':
        info = _extract_rcmed_dataset_info(dataset)
    elif dataset_source == 'esgf':
        info = _extract_esgf_dataset_info(dataset)
    elif dataset_source == 'dap':
        info = _extract_dap_dataset_info(dataset)
    else:
        err = (
            "Unexpected source in dataset origin information."
            "Found {}."
        ).format(dataset_source)
        logger.error(err)
        raise AttributeError(err)

    info['optional_args']['name'] = dataset.name
    info['optional_args']['units'] = dataset.units

    return info


def generate_metric_information(evaluation):
    ''' Generate metric config file output from a given Evaluation object.

    :param evaluation: The evaluation object from which to extract metrics.
    :type evaluation: :class:`evaluation.Evaluation`

    :returns: A :func:`list` of :mod:`metrics` object names for output into
        a configuration file.
    :rtype: :func:`list` of :mod:`metrics`
    '''
    unary_metrics = [x.__class__.__name__ for x in evaluation.unary_metrics]
    binary_metrics = [x.__class__.__name__ for x in evaluation.metrics]

    return unary_metrics + binary_metrics


def generate_evaluation_information(evaluation):
    ''' Generate evaluation-related config file output.

    Attempts to parse out temporal and spatial rebinning/regridding information
    from the supplied evaluation object. If no datasets can be found, values
    are defaulted to sane defaults or (potentially) excluded entirely.

    It's important to note that this function does its best to extrapolate the
    configuration information. It's possible that you will encounter a scenario
    where the guessed values are not what you want/expect. Please double
    check the output before blinding trusting what this generates.

    :param evaluation: The evaluation object from which to extract metrics.
    :type evaluation: :class:`evaluation.Evaluation`

    :returns: A dictionary of valid `evaluation` section settings for export
        to a configuration file.
    :rtype: :func:`dict`
    '''
    eval_config = {
        'temporal_time_delta': 999,
        'spatial_regrid_lats': (-90, 90, 1),
        'spatial_regrid_lons': (-180, 180, 1),
        'subset': [-90, 90, -180, 180, "1500-01-01", "2500-01-01"],
    }

    datasets = []

    if evaluation.ref_dataset:
        datasets.append(evaluation.ref_dataset)

    if evaluation.target_datasets:
        datasets += evaluation.target_datasets

    if len(datasets) > 0:
        eval_config['temporal_time_delta'] = _calc_temporal_bin_size(datasets)

        lats, lons = _calc_spatial_lat_lon_grid(datasets)
        eval_config['spatial_regrid_lats'] = lats
        eval_config['spatial_regrid_lons'] = lons

        eval_config['subset'] = _calc_subset_config(datasets)

    return eval_config


def generate_subregion_information(evaluation):
    ''' Generate subregion config file output from a given Evaluation object.

    :param evaluation: The evaluation object from which to extract metrics.
    :type evaluation: :class:`evaluation.Evaluation`

    :returns: A :func:`list` of :func:`list` objects containing bounding
        box info for export into a configuration file
    :rtype: :func:`list` of :func:`list`
    '''
    subregions = []
    for s in evaluation.subregions:
        subregions.append([s.lat_min, s.lat_max, s.lon_min, s.lon_max])

    return subregions


def _extract_local_dataset_info(dataset):
    ''''''
    dataset_info = {'optional_args': {}}

    dataset_info['data_source'] = 'local'
    dataset_info['file_count'] = 1
    dataset_info['path'] = dataset.origin['path']
    dataset_info['variable'] = dataset.variable

    dataset_info['optional_args']['lat_name'] = dataset.origin['lat_name']
    dataset_info['optional_args']['lon_name'] = dataset.origin['lon_name']
    dataset_info['optional_args']['time_name'] = dataset.origin['time_name']

    if 'elevation_index' in dataset.origin:
        elev = dataset.origin['elevation_index']
        dataset_info['optional_args']['elevation_index'] = elev

    return dataset_info


def _extract_rcmed_dataset_info(dataset):
    ''''''
    dataset_info = {'optional_args': {}}

    min_lat, max_lat, min_lon, max_lon = dataset.spatial_boundaries()
    start_time, end_time = dataset.temporal_boundaries()

    dataset_info['data_source'] = 'rcmed'
    dataset_info['dataset_id'] = dataset.origin['dataset_id']
    dataset_info['parameter_id'] = dataset.origin['parameter_id']
    dataset_info['min_lat'] = min_lat
    dataset_info['max_lat'] = max_lat
    dataset_info['min_lon'] = min_lon
    dataset_info['max_lon'] = max_lon
    dataset_info['start_time'] = str(start_time)
    dataset_info['end_time'] = str(end_time)

    return dataset_info


def _extract_esgf_dataset_info(dataset):
    ''''''
    dataset_info = {'optional_args': {}}

    dataset_info['data_source'] = 'esgf'
    dataset_info['dataset_id'] = dataset.origin['dataset_id']
    dataset_info['variable'] = dataset.origin['variable']
    dataset_info['esgf_username'] = 'Put your ESGF Username here'
    dataset_info['esgf_password'] = 'Put your ESGF Password here'

    return dataset_info


def _extract_dap_dataset_info(dataset):
    ''''''
    dataset_info = {'optional_args': {}}

    dataset_info['data_source'] = 'dap'
    dataset_info['url'] = dataset.origin['url']
    dataset_info['variable'] = dataset.variable

    return dataset_info


def _calc_temporal_bin_size(datasets):
    ''''''
    times = datasets[0].times
    time_delta = times[1] - times[0]

    if time_delta.days == 0:
        return 1
    elif time_delta.days <= 31:
        return 31
    elif time_delta.days <= 366:
        return 366
    else:
        return 999


def _calc_spatial_lat_lon_grid(datasets):
    ''''''
    lat_min, lat_max, lon_min, lon_max = datasets[0].spatial_boundaries()

    lats = datasets[0].lats
    lons = datasets[0].lons
    # These explicit float casts are needed to ensure that the type of the
    # lat/lon steps are not numpy values. PyYAML will choke on export if it
    # encounters a Numpy value.
    lat_step = float(abs(lats[1] - lats[0]))
    lon_step = float(abs(lons[1] - lons[0]))

    # We need to add an extra step value onto the end so when we generate a
    # range with these values we don't lose one that we're expecting.
    if lat_max != 90:
        lat_max += lat_step
    if lon_max != 180:
        lon_max += lon_step

    return ((lat_min, lat_max, lat_step), (lon_min, lon_max, lon_step))


def _calc_subset_config(datasets):
    ''''''
    lat_min = 90
    lat_max = -90
    lon_min = 180
    lon_max = -180
    start = dt.datetime(2500, 1, 1)
    end = dt.datetime(1500, 1, 1)

    for ds in datasets:
        ds_lat_min, ds_lat_max, ds_lon_min, ds_lon_max = ds.spatial_boundaries()
        ds_start, ds_end = ds.temporal_boundaries()

        if ds_lat_min < lat_min:
            lat_min = ds_lat_min

        if ds_lat_max > lat_max:
            lat_max = ds_lat_max

        if ds_lon_min < lon_min:
            lon_min = ds_lon_min

        if ds_lon_max > lon_max:
            lon_max = ds_lon_max

        if ds_start < start:
            start = ds_start

        if ds_end > end:
            end = ds_end

    return [lat_min, lat_max, lon_min, lon_max, str(start), str(end)]
