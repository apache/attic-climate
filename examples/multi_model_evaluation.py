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

import datetime
import urllib
import numpy as np
from os import path


# import Apache OCW dependences
import ocw.data_source.local as local
import ocw.data_source.rcmed as rcmed
from ocw.dataset import Bounds as Bounds
import ocw.dataset_processor as dsp
import ocw.evaluation as evaluation
import ocw.metrics as metrics
import ocw.plotter as plotter
import ocw.utils as utils
import ssl
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

# File URL leader
FILE_LEADER = "http://zipper.jpl.nasa.gov/dist/"
# Three Local Model Files
FILE_1 = "AFRICA_KNMI-RACMO2.2b_CTL_ERAINT_MM_50km_1989-2008_pr.nc"
FILE_2 = "AFRICA_UCT-PRECIS_CTL_ERAINT_MM_50km_1989-2008_pr.nc"
# Filename for the output image/plot (without file extension)
OUTPUT_PLOT = "pr_africa_bias_annual"
# variable that we are analyzing
varName = 'pr'
# Spatial and temporal configurations
LAT_MIN = -45.0
LAT_MAX = 42.24
LON_MIN = -24.0
LON_MAX = 60.0
START = datetime.datetime(2000, 1, 1)
END = datetime.datetime(2007, 12, 31)
EVAL_BOUNDS = Bounds(lat_min=LAT_MIN, lat_max=LAT_MAX,
                     lon_min=LON_MIN, lon_max=LON_MAX, start=START, end=END)

# regridding parameters
gridLonStep = 0.5
gridLatStep = 0.5

# list for all target_datasets
target_datasets = []
# list for names for all the datasets
allNames = []


# Download necessary NetCDF file if not present
if path.exists(FILE_1):
    pass
else:
    urllib.urlretrieve(FILE_LEADER + FILE_1, FILE_1)

if path.exists(FILE_2):
    pass
else:
    urllib.urlretrieve(FILE_LEADER + FILE_2, FILE_2)


""" Step 1: Load Local NetCDF File into OCW Dataset Objects and store in list"""
target_datasets.append(local.load_file(FILE_1, varName, name="KNMI"))
target_datasets.append(local.load_file(FILE_2, varName, name="UCT"))


""" Step 2: Fetch an OCW Dataset Object from the data_source.rcmed module """
print("Working with the rcmed interface to get CRU3.1 Monthly Mean Precipitation")
# the dataset_id and the parameter id were determined from
# https://rcmes.jpl.nasa.gov/content/data-rcmes-database
CRU31 = rcmed.parameter_dataset(
    10, 37, LAT_MIN, LAT_MAX, LON_MIN, LON_MAX, START, END)

""" Step 3: Resample Datasets so they are the same shape """
print("Resampling datasets")
CRU31 = dsp.water_flux_unit_conversion(CRU31)
CRU31 = dsp.temporal_rebin(CRU31, datetime.timedelta(days=30))

for member, each_target_dataset in enumerate(target_datasets):
    target_datasets[member] = dsp.subset(target_datasets[member], EVAL_BOUNDS)
    target_datasets[member] = dsp.water_flux_unit_conversion(target_datasets[
                                                             member])
    target_datasets[member] = dsp.temporal_rebin(
        target_datasets[member], datetime.timedelta(days=30))


""" Spatially Regrid the Dataset Objects to a user defined  grid """
# Using the bounds we will create a new set of lats and lons
print("Regridding datasets")
new_lats = np.arange(LAT_MIN, LAT_MAX, gridLatStep)
new_lons = np.arange(LON_MIN, LON_MAX, gridLonStep)
CRU31 = dsp.spatial_regrid(CRU31, new_lats, new_lons)

for member, each_target_dataset in enumerate(target_datasets):
    target_datasets[member] = dsp.spatial_regrid(
        target_datasets[member], new_lats, new_lons)

# make the model ensemble
target_datasets_ensemble = dsp.ensemble(target_datasets)
target_datasets_ensemble.name = "ENS"

# append to the target_datasets for final analysis
target_datasets.append(target_datasets_ensemble)

# find the mean value
# way to get the mean. Note the function exists in util.py
_, CRU31.values = utils.calc_climatology_year(CRU31)

for member, each_target_dataset in enumerate(target_datasets):
    _, target_datasets[member].values = utils.calc_climatology_year(target_datasets[
                                                                    member])

for target in target_datasets:
    allNames.append(target.name)

# determine the metrics
mean_bias = metrics.Bias()

# create the Evaluation object
RCMs_to_CRU_evaluation = evaluation.Evaluation(CRU31,  # Reference dataset for the evaluation
                                               # list of target datasets for
                                               # the evaluation
                                               target_datasets,
                                               # 1 or more metrics to use in
                                               # the evaluation
                                               [mean_bias])
RCMs_to_CRU_evaluation.run()

# extract the relevant data from RCMs_to_CRU_evaluation.results
# the results returns a list (num_target_datasets, num_metrics). See docs for further details
# remove the metric dimension
rcm_bias = RCMs_to_CRU_evaluation.results[0]

plotter.draw_contour_map(rcm_bias, new_lats, new_lons, gridshape=(
    2, 3), fname=OUTPUT_PLOT, subtitles=allNames, cmap='coolwarm_r')
