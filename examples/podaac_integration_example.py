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

import ocw.data_source.podaac_datasource as podaac
import ocw.evaluation as evaluation
import ocw.metrics as metrics
import ocw.plotter as plotter

datasetId = 'PODAAC-CCF30-01XXX'
variable = 'uwnd'
name = 'PO.DAAC_test_dataset'
OUTPUT_PLOT = "ccmp_temporal_std"
""" Step 1: Load Local NetCDF Files into OCW Dataset Objects """
print("Loading %s dataset short name into a OCW dataset object." % datasetId)
ccmp_dataset = podaac.load_level4_granule(
    variable=variable, datasetId=datasetId, name=name)
print("CCMP_Dataset.values shape: (times, lats, lons) - %s \n" %
      (ccmp_dataset.values.shape,))

# Acessing latittudes and longitudes of netCDF file
lats = ccmp_dataset.lats
lons = ccmp_dataset.lons

""" Step 2:  Build a Metric to use for Evaluation - Temporal STD for this example """
# You can build your own metrics, but OCW also ships with some common metrics
print("Setting up a Temporal STD metric to use for evaluation")
std = metrics.TemporalStdDev()

""" Step 3: Create an Evaluation Object using Datasets and our Metric """
# The Evaluation Class Signature is:
# Evaluation(reference, targets, metrics, subregions=None)
# Evaluation can take in multiple targets and metrics, so we need to convert
# our examples into Python lists.  Evaluation will iterate over the lists
print("Making the Evaluation definition")
# Temporal STD Metric gets one target dataset then reference dataset
# should be None
std_evaluation = evaluation.Evaluation(None, [ccmp_dataset], [std])
print("Executing the Evaluation using the object's run() method")
std_evaluation.run()

""" Step 4: Make a Plot from the Evaluation.results """
# The Evaluation.results are a set of nested lists to support many different
# possible Evaluation scenarios.
#
# The Evaluation results docs say:
# The shape of results is (num_metrics, num_target_datasets) if no subregion
# Accessing the actual results when we have used 1 metric and 1 dataset is
# done this way:
print("Accessing the Results of the Evaluation run")
results = std_evaluation.unary_results[0][0]
print("The results are of type: %s" % type(results))
print("Generating a contour map using ocw.plotter.draw_contour_map()")

fname = OUTPUT_PLOT
gridshape = (4, 5)  # 20 Years worth of plots. 20 rows in 1 column
plot_title = "CCMP Temporal Standard Deviation"
sub_titles = range(2002, 2010, 1)

plotter.draw_contour_map(results, lats, lons, fname,
                         gridshape=gridshape, ptitle=plot_title,
                         subtitles=sub_titles)
