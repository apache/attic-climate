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
YEARS = 3
# Two Local Model Files
MODEL = "AFRICA_KNMI-RACMO2.2b_CTL_ERAINT_MM_50km_1989-2008_tasmax.nc"
# Filename for the output image/plot (without file extension)
OUTPUT_PLOT = "cru_31_tmax_knmi_africa_bias_full"

# Download necessary NetCDF file if not present
if path.exists(MODEL):
    pass
else:
    urllib.urlretrieve(FILE_LEADER + MODEL, MODEL)

""" Step 1: Load Local NetCDF File into OCW Dataset Objects """
print("Loading %s into an OCW Dataset Object" % (MODEL,))
knmi_dataset = local.load_file(MODEL, "tasmax")
print("KNMI_Dataset.values shape: (times, lats, lons) - %s \n" %
      (knmi_dataset.values.shape,))

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

print("We are going to use the Model to constrain the Spatial Domain")
#  The spatial_boundaries() function returns the spatial extent of the dataset
print("The KNMI_Dataset spatial bounds (min_lat, max_lat, min_lon, max_lon) are: \n"
      "%s\n" % (knmi_dataset.spatial_boundaries(), ))
print("The KNMI_Dataset spatial resolution (lat_resolution, lon_resolution) is: \n"
      "%s\n\n" % (knmi_dataset.spatial_resolution(), ))
min_lat, max_lat, min_lon, max_lon = knmi_dataset.spatial_boundaries()

print("Calculating the Maximum Overlap in Time for the datasets")

cru_start = datetime.datetime.strptime(cru_31['start_date'], "%Y-%m-%d")
cru_end = datetime.datetime.strptime(cru_31['end_date'], "%Y-%m-%d")
knmi_start, knmi_end = knmi_dataset.temporal_boundaries()
# Grab the Max Start Time
start_time = max([cru_start, knmi_start])
# Grab the Min End Time
end_time = min([cru_end, knmi_end])
print("Overlap computed to be: %s to %s" % (start_time.strftime("%Y-%m-%d"),
                                            end_time.strftime("%Y-%m-%d")))
print("We are going to grab the first %s year(s) of data" % YEARS)
end_time = datetime.datetime(
    start_time.year + YEARS, start_time.month, start_time.day)
print("Final Overlap is: %s to %s" % (start_time.strftime("%Y-%m-%d"),
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
print("CRU31_Dataset.values shape: (times, lats, lons) - %s" %
      (cru31_dataset.values.shape,))
print("KNMI_Dataset.values shape: (times, lats, lons) - %s" %
      (knmi_dataset.values.shape,))
print("Our two datasets have a mis-match in time. We will subset on time to %s years\n" % YEARS)

# Create a Bounds object to use for subsetting
new_bounds = Bounds(lat_min=min_lat, lat_max=max_lat, lon_min=min_lon,
                    lon_max=max_lon, start=start_time, end=end_time)
knmi_dataset = dsp.subset(knmi_dataset, new_bounds)

print("CRU31_Dataset.values shape: (times, lats, lons) - %s" %
      (cru31_dataset.values.shape,))
print("KNMI_Dataset.values shape: (times, lats, lons) - %s \n" %
      (knmi_dataset.values.shape,))

print("Temporally Rebinning the Datasets to a Single Timestep")
# To run FULL temporal Rebinning
knmi_dataset = dsp.temporal_rebin(knmi_dataset, temporal_resolution='full')
cru31_dataset = dsp.temporal_rebin(cru31_dataset, temporal_resolution='full')

print("KNMI_Dataset.values shape: %s" % (knmi_dataset.values.shape,))
print("CRU31_Dataset.values shape: %s \n\n" % (cru31_dataset.values.shape,))

""" Spatially Regrid the Dataset Objects to a 1/2 degree grid """
# Using the bounds we will create a new set of lats and lons on 0.5 degree step
new_lons = np.arange(min_lon, max_lon, 0.5)
new_lats = np.arange(min_lat, max_lat, 0.5)

# Spatially regrid datasets using the new_lats, new_lons numpy arrays
print("Spatially Regridding the KNMI_Dataset...")
knmi_dataset = dsp.spatial_regrid(knmi_dataset, new_lats, new_lons)
print("Spatially Regridding the CRU31_Dataset...")
cru31_dataset = dsp.spatial_regrid(cru31_dataset, new_lats, new_lons)
print("Final shape of the KNMI_Dataset:%s" % (knmi_dataset.values.shape, ))
print("Final shape of the CRU31_Dataset:%s" % (cru31_dataset.values.shape, ))

""" Step 4:  Build a Metric to use for Evaluation - Bias for this example """
# You can build your own metrics, but OCW also ships with some common metrics
print("Setting up a Bias metric to use for evaluation")
bias = metrics.Bias()

""" Step 5: Create an Evaluation Object using Datasets and our Metric """
# The Evaluation Class Signature is:
# Evaluation(reference, targets, metrics, subregions=None)
# Evaluation can take in multiple targets and metrics, so we need to convert
# our examples into Python lists.  Evaluation will iterate over the lists
print("Making the Evaluation definition")
bias_evaluation = evaluation.Evaluation(knmi_dataset, [cru31_dataset], [bias])
print("Executing the Evaluation using the object's run() method")
bias_evaluation.run()

""" Step 6: Make a Plot from the Evaluation.results """
# The Evaluation.results are a set of nested lists to support many different
# possible Evaluation scenarios.
#
# The Evaluation results docs say:
# The shape of results is (num_metrics, num_target_datasets) if no subregion
# Accessing the actual results when we have used 1 metric and 1 dataset is
# done this way:
print("Accessing the Results of the Evaluation run")
results = bias_evaluation.results[0][0, :]

# From the bias output I want to make a Contour Map of the region
print("Generating a contour map using ocw.plotter.draw_contour_map()")

lats = new_lats
lons = new_lons
fname = OUTPUT_PLOT
# Using a 1 x 1 since we have a single Bias for the full time range
gridshape = (1, 1)
plot_title = "TASMAX Bias of KNMI Compared to CRU 3.1 (%s - %s)" % (
    start_time.strftime("%Y/%d/%m"), end_time.strftime("%Y/%d/%m"))
sub_titles = ["Full Temporal Range"]

plotter.draw_contour_map(results, lats, lons, fname,
                         gridshape=gridshape, ptitle=plot_title,
                         subtitles=sub_titles)
