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

#Apache OCW lib immports
import ocw.dataset_processor as dsp
import ocw.data_source.local as local
import ocw.data_source.rcmed as rcmed
import ocw.plotter as plotter
import ocw.utils as utils
from ocw.dataset import Bounds

import matplotlib.pyplot as plt
from matplotlib import rcParams
import numpy as np
import numpy.ma as ma
import yaml
from glob import glob
import operator
from dateutil import parser
from datetime import datetime
import os
import sys

from metrics_and_plots import *

import ssl
if hasattr(ssl, '_create_unverified_context'):
  ssl._create_default_https_context = ssl._create_unverified_context

config_file = str(sys.argv[1])

print 'Reading the configuration file ', config_file
config = yaml.load(open(config_file))
time_info = config['time']
temporal_resolution = time_info['temporal_resolution']

start_time = datetime.strptime(time_info['start_time'].strftime('%Y%m%d'),'%Y%m%d')
end_time = datetime.strptime(time_info['end_time'].strftime('%Y%m%d'),'%Y%m%d')

space_info = config['space']
min_lat = space_info['min_lat']
max_lat = space_info['max_lat']
min_lon = space_info['min_lon']
max_lon = space_info['max_lon']

""" Step 1: Load the reference data """
ref_data_info = config['datasets']['reference']
print 'Loading observation dataset:\n',ref_data_info
ref_name = ref_data_info['data_name']
if ref_data_info['data_source'] == 'local':
    ref_dataset = local.load_file(ref_data_info['path'],
                                  ref_data_info['variable'], name=ref_name)
elif ref_data_info['data_source'] == 'rcmed':
      ref_dataset = rcmed.parameter_dataset(ref_data_info['dataset_id'],
                                            ref_data_info['parameter_id'],
                                            min_lat, max_lat, min_lon, max_lon,
                                            start_time, end_time)
else:
    print ' '
    # TO DO: support ESGF

ref_dataset =  dsp.normalize_dataset_datetimes(ref_dataset, temporal_resolution)
if 'multiplying_factor' in ref_data_info.keys():
    ref_dataset.values = ref_dataset.values*ref_data_info['multiplying_factor']

""" Step 2: Load model NetCDF Files into OCW Dataset Objects """
model_data_info = config['datasets']['targets']
print 'Loading model datasets:\n',model_data_info
if model_data_info['data_source'] == 'local':
    model_datasets, model_names = local.load_multiple_files(file_path = model_data_info['path'],
                                                            variable_name =model_data_info['variable'])
else:
    print ' '
    # TO DO: support RCMED and ESGF
for idata,dataset in enumerate(model_datasets):
    model_datasets[idata] = dsp.normalize_dataset_datetimes(dataset, temporal_resolution)

""" Step 3: Subset the data for temporal and spatial domain """
# Create a Bounds object to use for subsetting
if time_info['maximum_overlap_period']:
    start_time, end_time = utils.get_temporal_overlap([ref_dataset]+model_datasets)
    print 'Maximum overlap period'
    print 'start_time:', start_time
    print 'end_time:', end_time

if temporal_resolution == 'monthly' and end_time.day !=1:
    end_time = end_time.replace(day=1)
if ref_data_info['data_source'] == 'rcmed':
    min_lat = np.max([min_lat, ref_dataset.lats.min()])
    max_lat = np.min([max_lat, ref_dataset.lats.max()])
    min_lon = np.max([min_lon, ref_dataset.lons.min()])
    max_lon = np.min([max_lon, ref_dataset.lons.max()])
bounds = Bounds(min_lat, max_lat, min_lon, max_lon, start_time, end_time)

if ref_dataset.lats.ndim !=2 and ref_dataset.lons.ndim !=2:
    ref_dataset = dsp.subset(bounds,ref_dataset)
for idata,dataset in enumerate(model_datasets):
    if dataset.lats.ndim !=2 and dataset.lons.ndim !=2:
        model_datasets[idata] = dsp.subset(bounds,dataset)

# Temporaly subset both observation and model datasets for the user specified season
month_start = time_info['month_start']
month_end = time_info['month_end']
average_each_year = time_info['average_each_year']

ref_dataset = dsp.temporal_subset(month_start, month_end,ref_dataset,average_each_year)
for idata,dataset in enumerate(model_datasets):
    model_datasets[idata] = dsp.temporal_subset(month_start, month_end,dataset,average_each_year)

# generate grid points for regridding
if config['regrid']['regrid_on_reference']:
    new_lat = ref_dataset.lats
    new_lon = ref_dataset.lons 
else:
    delta_lat = config['regrid']['regrid_dlat']
    delta_lon = config['regrid']['regrid_dlon']
    nlat = (max_lat - min_lat)/delta_lat+1
    nlon = (max_lon - min_lon)/delta_lon+1
    new_lat = np.linspace(min_lat, max_lat, nlat)
    new_lon = np.linspace(min_lon, max_lon, nlon)

# number of models
nmodel = len(model_datasets)
print 'Dataset loading completed'
print 'Observation data:', ref_name 
print 'Number of model datasets:',nmodel
for model_name in model_names:
    print model_name

""" Step 4: Spatial regriding of the reference datasets """
print 'Regridding datasets: ', config['regrid']
if not config['regrid']['regrid_on_reference']:
    ref_dataset = dsp.spatial_regrid(ref_dataset, new_lat, new_lon)
for idata,dataset in enumerate(model_datasets):
    model_datasets[idata] = dsp.spatial_regrid(dataset, new_lat, new_lon)

print 'Propagating missing data information'
ref_dataset = dsp.mask_missing_data([ref_dataset]+model_datasets)[0]
model_datasets = dsp.mask_missing_data([ref_dataset]+model_datasets)[1:]

""" Step 5: Checking and converting variable units """
print 'Checking and converting variable units'
ref_dataset = dsp.variable_unit_conversion(ref_dataset)
for idata,dataset in enumerate(model_datasets):
    model_datasets[idata] = dsp.variable_unit_conversion(dataset)
    

print 'Generating multi-model ensemble'
if len(model_datasets) >= 2.:
    model_datasets.append(dsp.ensemble(model_datasets))
    model_names.append('ENS')

""" Step 6: Generate subregion average and standard deviation """
if config['use_subregions']:
    # sort the subregion by region names and make a list
    subregions= sorted(config['subregions'].items(),key=operator.itemgetter(0))

    # number of subregions
    nsubregion = len(subregions)

    print 'Calculating spatial averages and standard deviations of ',str(nsubregion),' subregions'

    ref_subregion_mean, ref_subregion_std, subregion_array = utils.calc_subregion_area_mean_and_std([ref_dataset], subregions) 
    model_subregion_mean, model_subregion_std, subregion_array = utils.calc_subregion_area_mean_and_std(model_datasets, subregions) 

""" Step 7: Write a netCDF file """
workdir = config['workdir']
if workdir[-1] != '/':
    workdir = workdir+'/'
print 'Writing a netcdf file: ',workdir+config['output_netcdf_filename']
if not os.path.exists(workdir):
    os.system("mkdir "+workdir)

if config['use_subregions']:
    dsp.write_netcdf_multiple_datasets_with_subregions(ref_dataset, ref_name, model_datasets, model_names,
                                                       path=workdir+config['output_netcdf_filename'],
                                                       subregions=subregions, subregion_array = subregion_array, 
                                                       ref_subregion_mean=ref_subregion_mean, ref_subregion_std=ref_subregion_std,
                                                       model_subregion_mean=model_subregion_mean, model_subregion_std=model_subregion_std)
else:
    dsp.write_netcdf_multiple_datasets_with_subregions(ref_dataset, ref_name, model_datasets, model_names,
                                                       path=workdir+config['output_netcdf_filename'])

""" Step 8: Calculate metrics and draw plots """
nmetrics = config['number_of_metrics_and_plots']
if config['use_subregions']:
    Map_plot_subregion(subregions, ref_dataset, workdir)

if nmetrics > 0:
    print 'Calculating metrics and generating plots'
    for imetric in np.arange(nmetrics)+1:
        metrics_name = config['metrics'+'%1d' %imetric]
        plot_info = config['plots'+'%1d' %imetric]
        file_name = workdir+plot_info['file_name']

        print 'metrics '+str(imetric)+'/'+str(nmetrics)+': ', metrics_name
        if metrics_name == 'Map_plot_bias_of_multiyear_climatology':
            row, column = plot_info['subplots_array']
            if 'map_projection' in plot_info.keys():
                Map_plot_bias_of_multiyear_climatology(ref_dataset, ref_name, model_datasets, model_names,
                                          file_name, row, column, map_projection=plot_info['map_projection'])
            else:
                Map_plot_bias_of_multiyear_climatology(ref_dataset, ref_name, model_datasets, model_names,
                                          file_name, row, column)
        elif metrics_name == 'Taylor_diagram_spatial_pattern_of_multiyear_climatology':
            Taylor_diagram_spatial_pattern_of_multiyear_climatology(ref_dataset, ref_name, model_datasets, model_names,
                                      file_name)
        elif config['use_subregions']:
            if metrics_name == 'Timeseries_plot_subregion_interannual_variability' and average_each_year:
                row, column = plot_info['subplots_array']
                Time_series_subregion(ref_subregion_mean, ref_name, model_subregion_mean, model_names, False,
                                      file_name, row, column, x_tick=['Y'+str(i+1) for i in np.arange(model_subregion_mean.shape[1])])
            if metrics_name == 'Timeseries_plot_subregion_annual_cycle' and not average_each_year and month_start==1 and month_end==12:
                row, column = plot_info['subplots_array']
                Time_series_subregion(ref_subregion_mean, ref_name, model_subregion_mean, model_names, True,
                                      file_name, row, column, x_tick=['J','F','M','A','M','J','J','A','S','O','N','D'])
            if metrics_name == 'Portrait_diagram_subregion_interannual_variability' and average_each_year:
                Portrait_diagram_subregion(ref_subregion_mean, ref_name, model_subregion_mean, model_names, False,
                                      file_name)
            if metrics_name == 'Portrait_diagram_subregion_annual_cycle' and not average_each_year and month_start==1 and month_end==12:
                Portrait_diagram_subregion(ref_subregion_mean, ref_name, model_subregion_mean, model_names, True,
                                      file_name)
        else:
            print 'please check the currently supported metrics'


