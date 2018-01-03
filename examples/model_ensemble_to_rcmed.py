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
import math
import urllib
from os import path

import numpy as np

import ocw.data_source.local as local
import ocw.data_source.rcmed as rcmed
from ocw.dataset import Bounds as Bounds
import ocw.dataset_processor as dsp
import ocw.evaluation as evaluation
import ocw.metrics as metrics
import ocw.plotter as plotter
import ssl

if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

# File URL leader
FILE_LEADER = "http://zipper.jpl.nasa.gov/dist/"
# This way we can easily adjust the time span of the retrievals
YEARS = 1
# Two Local Model Files
FILE_1 = "AFRICA_KNMI-RACMO2.2b_CTL_ERAINT_MM_50km_1989-2008_tasmax.nc"
FILE_2 = "AFRICA_UC-WRF311_CTL_ERAINT_MM_50km-rg_1989-2008_tasmax.nc"
# Filename for the output image/plot (without file extension)
OUTPUT_PLOT = "tasmax_africa_bias_annual"

# Download necessary NetCDF file if not present
if path.exists(FILE_1):
    pass
else:
    urllib.urlretrieve(FILE_LEADER + FILE_1, FILE_1)

if path.exists(FILE_2):
    pass
else:
    urllib.urlretrieve(FILE_LEADER + FILE_2, FILE_2)


""" Step 1: Load Local NetCDF File into OCW Dataset Objects """
# Load local knmi model data
knmi_dataset = local.load_file(FILE_1, "tasmax")
knmi_dataset.name = "AFRICA_KNMI-RACMO2.2b_CTL_ERAINT_MM_50km_1989-2008_tasmax"

wrf311_dataset = local.load_file(FILE_2, "tasmax")
wrf311_dataset.name = "AFRICA_UC-WRF311_CTL_ERAINT_MM_50km-rg_1989-2008_tasmax"


""" Step 2: Fetch an OCW Dataset Object from the data_source.rcmed module """
print("Working with the rcmed interface to get CRU3.1 Daily-Max Temp")
metadata = rcmed.get_parameters_metadata()

cru_31 = [m for m in metadata if m['parameter_id'] == "39"][0]

""" The RCMED API uses the following function to query, subset and return the 
raw data from the database:

rcmed.parameter_dataset(dataset_id, parameter_id, min_lat, max_lat, min_lon, 
                        max_lon, start_time, end_time)

The first two required params are in the cru_31 variable we defined earlier
"""
# Must cast to int since the rcmed api requires ints
dataset_id = int(cru_31['dataset_id'])
parameter_id = int(cru_31['parameter_id'])

#  The spatial_boundaries() function returns the spatial extent of the dataset
min_lat, max_lat, min_lon, max_lon = wrf311_dataset.spatial_boundaries()

#  There is a boundry alignment issue with the datasets.  To mitigate this
#  we will use the math.floor() and math.ceil() functions to shrink the
#  boundries slighty.
min_lat = math.ceil(min_lat)
max_lat = math.floor(max_lat)
min_lon = math.ceil(min_lon)
max_lon = math.floor(max_lon)

print("Calculating the Maximum Overlap in Time for the datasets")

cru_start = datetime.datetime.strptime(cru_31['start_date'], "%Y-%m-%d")
cru_end = datetime.datetime.strptime(cru_31['end_date'], "%Y-%m-%d")
knmi_start, knmi_end = knmi_dataset.temporal_boundaries()
# Set the Time Range to be the year 1989
start_time = datetime.datetime(1989, 1, 1)
end_time = datetime.datetime(1989, 12, 1)

print("Time Range is: %s to %s" % (start_time.strftime("%Y-%m-%d"),
                                   end_time.strftime("%Y-%m-%d")))

print("Fetching data from RCMED...")
cru31_dataset = rcmed.parameter_dataset(dataset_id,
                                        parameter_id,
                                        min_lat,
                                        max_lat,
                                        min_lon,
                                        max_lon,
                                        start_time,
                                        end_time)

""" Step 3: Resample Datasets so they are the same shape """

print("Temporally Rebinning the Datasets to an Annual Timestep")
# To run annual temporal Rebinning,
knmi_dataset = dsp.temporal_rebin(knmi_dataset, temporal_resolution='annual')
wrf311_dataset = dsp.temporal_rebin(
    wrf311_dataset, temporal_resolution='annual')
cru31_dataset = dsp.temporal_rebin(cru31_dataset, temporal_resolution='annual')

# Rebinning annual pushes the start date to the middle of the year
# i.e. 1989-07-02 and effectively makes a single entry for the year.
start_time, end_time = knmi_dataset.temporal_boundaries()
end_time = start_time

# Running Temporal Rebin early helps negate the issue of datasets being on different
# days of the month (1st vs. 15th)
# Create a Bounds object to use for subsetting
new_bounds = Bounds(lat_min=min_lat, lat_max=max_lat, lon_min=min_lon,
                    lon_max=max_lon, start=start_time, end=end_time)

# Subset our model datasets so they are the same size
knmi_dataset = dsp.subset(knmi_dataset, new_bounds)
wrf311_dataset = dsp.subset(wrf311_dataset, new_bounds)

""" Spatially Regrid the Dataset Objects to a 1/2 degree grid """
# Using the bounds we will create a new set of lats and lons on 1/2 degree step
new_lons = np.arange(min_lon, max_lon, 0.5)
new_lats = np.arange(min_lat, max_lat, 0.5)

# Spatially regrid datasets using the new_lats, new_lons numpy arrays
knmi_dataset = dsp.spatial_regrid(knmi_dataset, new_lats, new_lons)
wrf311_dataset = dsp.spatial_regrid(wrf311_dataset, new_lats, new_lons)
cru31_dataset = dsp.spatial_regrid(cru31_dataset, new_lats, new_lons)

# Generate an ensemble dataset from knmi and wrf models
ensemble_dataset = dsp.ensemble([knmi_dataset, wrf311_dataset])

""" Step 4:  Build a Metric to use for Evaluation - Bias for this example """
print("Setting up a Bias metric to use for evaluation")
bias = metrics.Bias()

""" Step 5: Create an Evaluation Object using Datasets and our Metric """
# The Evaluation Class Signature is:
# Evaluation(reference, targets, metrics, subregions=None)
# Evaluation can take in multiple targets and metrics, so we need to convert
# our examples into Python lists.  Evaluation will iterate over the lists
print("Making the Evaluation definition")
bias_evaluation = evaluation.Evaluation(cru31_dataset,
                                        [knmi_dataset, wrf311_dataset,
                                            ensemble_dataset],
                                        [bias])
print("Executing the Evaluation using the object's run() method")
bias_evaluation.run()

""" Step 6: Make a Plot from the Evaluation.results """
# The Evaluation.results are a set of nested lists to support many different
# possible Evaluation scenarios.
#
# The Evaluation results docs say:
# The shape of results is (num_target_datasets, num_metrics) if no subregion
# Accessing the actual results when we have used 3 datasets and 1 metric is
# done this way:
print("Accessing the Results of the Evaluation run")
results = bias_evaluation.results[0]

# From the bias output I want to make a Contour Map of the region
print("Generating a contour map using ocw.plotter.draw_contour_map()")

lats = new_lats
lons = new_lons
fname = OUTPUT_PLOT
gridshape = (3, start_time.year - end_time.year + 1)  # Using a 3 x N since we have a N year(s) of data for 3 models
plotnames = ["KNMI", "WRF311", "ENSEMBLE"]
for i in np.arange(3):
    plot_title = "TASMAX Bias of CRU 3.1 vs. %s (%s - %s)" % (
        plotnames[i], start_time.strftime("%Y/%d/%m"), end_time.strftime("%Y/%d/%m"))
    output_file = "%s_%s" % (fname, plotnames[i].lower())
    print "creating %s" % (output_file,)
    plotter.draw_contour_map(results[i, :], lats, lons, output_file,
                             gridshape=gridshape, ptitle=plot_title)
