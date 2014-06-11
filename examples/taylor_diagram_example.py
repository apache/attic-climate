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
import sys
from os import path
import urllib

import numpy

from ocw.dataset import Bounds
import ocw.data_source.local as local
import ocw.dataset_processor as dsp
import ocw.evaluation as evaluation
import ocw.metrics as metrics
import ocw.plotter as plotter

FILE_LEADER = "http://zipper.jpl.nasa.gov/dist/"
FILE_1 = "AFRICA_KNMI-RACMO2.2b_CTL_ERAINT_MM_50km_1989-2008_tasmax.nc"
FILE_2 = "AFRICA_UC-WRF311_CTL_ERAINT_MM_50km-rg_1989-2008_tasmax.nc"

# Download some example NetCDF files for the evaluation
################################################################################
if not path.exists(FILE_1):
    urllib.urlretrieve(FILE_LEADER + FILE_1, FILE_1)

if not path.exists(FILE_2):
    urllib.urlretrieve(FILE_LEADER + FILE_2, FILE_2)

# Load the example datasets into OCW Dataset objects. We want to load
# the 'tasmax' variable values. We'll also name the datasets for use
# when plotting.
################################################################################
knmi_dataset = local.load_file(FILE_1, "tasmax")
wrf_dataset = local.load_file(FILE_2, "tasmax")

knmi_dataset.name = "knmi"
wrf_dataset.name = "wrf"

# Date values from loaded datasets might not always fall on reasonable days.
# With monthly data, we could have data falling on the 1st, 15th, or some other
# day of the month. Let's fix that real quick.
################################################################################
knmi_dataset = dsp.normalize_dataset_datetimes(knmi_dataset, 'monthly')
wrf_dataset = dsp.normalize_dataset_datetimes(wrf_dataset, 'monthly')

# We're only going to run this evaluation over a years worth of data. We'll
# make a Bounds object and use it to subset our datasets.
################################################################################
subset = Bounds(-45, 42, -24, 60, datetime.datetime(1989, 1, 1), datetime.datetime(1989, 12, 1))
knmi_dataset = dsp.subset(subset, knmi_dataset)
wrf_dataset = dsp.subset(subset, wrf_dataset)

# Temporally re-bin the data into a monthly timestep.
################################################################################
knmi_dataset = dsp.temporal_rebin(knmi_dataset, datetime.timedelta(days=30))
wrf_dataset = dsp.temporal_rebin(wrf_dataset, datetime.timedelta(days=30))

# Spatially regrid the datasets onto a 1 degree grid.
################################################################################
# Get the bounds of the reference dataset and use it to create a new
# set of lat/lon values on a 1 degree step
# Using the bounds we will create a new set of lats and lons on 1 degree step
min_lat, max_lat, min_lon, max_lon = knmi_dataset.spatial_boundaries()
new_lons = numpy.arange(min_lon, max_lon, 1)
new_lats = numpy.arange(min_lat, max_lat, 1)

# Spatially regrid datasets using the new_lats, new_lons numpy arrays
knmi_dataset = dsp.spatial_regrid(knmi_dataset, new_lats, new_lons)
wrf_dataset = dsp.spatial_regrid(wrf_dataset, new_lats, new_lons)

# Load the metrics that we want to use for the evaluation.
################################################################################
sstdr = metrics.SpatialStdDevRatio()
pc = metrics.PatternCorrelation()

# Create our new evaluation object. The knmi dataset is the evaluations
# reference dataset. We then provide a list of 1 or more target datasets
# to use for the evaluation. In this case, we only want to use the wrf dataset.
# Then we pass a list of all the metrics that we want to use in the evaluation.
################################################################################
test_evaluation = evaluation.Evaluation(knmi_dataset, [wrf_dataset], [sstdr, pc])
test_evaluation.run()

# Pull our the evaluation results and prepare them for drawing a Taylor diagram.
################################################################################
spatial_stddev_ratio = test_evaluation.results[0][0]
# Pattern correlation results are a tuple, so we need to index and grab
# the component we care about.
spatial_correlation = test_evaluation.results[0][1][0]

taylor_data = numpy.array([[spatial_stddev_ratio], [spatial_correlation]]).transpose()

# Draw our taylor diagram!
################################################################################
plotter.draw_taylor_diagram(taylor_data,
                            [wrf_dataset.name],
                            knmi_dataset.name,
                            fname='taylor_plot',
                            fmt='png',
                            frameon=False)
