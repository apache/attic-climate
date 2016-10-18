# Apache OCW lib immports
from ocw.dataset import Dataset, Bounds
import ocw.data_source.local as local
import ocw.data_source.rcmed as rcmed
import ocw.dataset_processor as dsp
import ocw.evaluation as evaluation
import ocw.metrics as metrics
import ocw.plotter as plotter
import ocw.utils as utils

import datetime
import numpy as np
import urllib

from os import path
import ssl
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context


# File URL leader
FILE_LEADER = "http://zipper.jpl.nasa.gov/dist/"
# Three Local Model Files
FILE_1 = "AFRICA_KNMI-RACMO2.2b_CTL_ERAINT_MM_50km_1989-2008_pr.nc"
FILE_2 = "AFRICA_ICTP-REGCM3_CTL_ERAINT_MM_50km-rg_1989-2008_pr.nc"
FILE_3 = "AFRICA_UCT-PRECIS_CTL_ERAINT_MM_50km_1989-2008_pr.nc"
# Filename for the output image/plot (without file extension)
OUTPUT_PLOT = "pr_africa_taylor"

# Spatial and temporal configurations
LAT_MIN = -45.0
LAT_MAX = 42.24
LON_MIN = -24.0
LON_MAX = 60.0
START = datetime.datetime(2000, 01, 1)
END = datetime.datetime(2007, 12, 31)
EVAL_BOUNDS = Bounds(lat_min=LAT_MIN, lat_max=LAT_MAX,
                     lon_min=LON_MIN, lon_max=LON_MAX, start=START, end=END)

# variable that we are analyzing
varName = 'pr'

# regridding parameters
gridLonStep = 0.5
gridLatStep = 0.5

# some vars for this evaluation
target_datasets_ensemble = []
target_datasets = []
ref_datasets = []

# Download necessary NetCDF file if not present
if path.exists(FILE_1):
    pass
else:
    urllib.urlretrieve(FILE_LEADER + FILE_1, FILE_1)

if path.exists(FILE_2):
    pass
else:
    urllib.urlretrieve(FILE_LEADER + FILE_2, FILE_2)

if path.exists(FILE_3):
    pass
else:
    urllib.urlretrieve(FILE_LEADER + FILE_3, FILE_3)

""" Step 1: Load Local NetCDF File into OCW Dataset Objects and store in list"""
target_datasets.append(local.load_file(FILE_1, varName, name="KNMI"))
target_datasets.append(local.load_file(FILE_2, varName, name="REGM3"))
target_datasets.append(local.load_file(FILE_3, varName, name="UCT"))


""" Step 2: Fetch an OCW Dataset Object from the data_source.rcmed module """
print("Working with the rcmed interface to get CRU3.1 Monthly Mean Precipitation")
# the dataset_id and the parameter id were determined from
# https://rcmes.jpl.nasa.gov/content/data-rcmes-database
CRU31 = rcmed.parameter_dataset(
    10, 37, LAT_MIN, LAT_MAX, LON_MIN, LON_MAX, START, END)

""" Step 3: Resample Datasets so they are the same shape """
print("Resampling datasets ...")
print("... on units")
CRU31 = dsp.water_flux_unit_conversion(CRU31)
print("... temporal")
CRU31 = dsp.temporal_rebin(CRU31, temporal_resolution='monthly')

for member, each_target_dataset in enumerate(target_datasets):
    target_datasets[member] = dsp.water_flux_unit_conversion(target_datasets[
                                                             member])
    target_datasets[member] = dsp.temporal_rebin(
        target_datasets[member], temporal_resolution='monthly')
    target_datasets[member] = dsp.subset(target_datasets[member], EVAL_BOUNDS)

# Regrid
print("... regrid")
new_lats = np.arange(LAT_MIN, LAT_MAX, gridLatStep)
new_lons = np.arange(LON_MIN, LON_MAX, gridLonStep)
CRU31 = dsp.spatial_regrid(CRU31, new_lats, new_lons)

for member, each_target_dataset in enumerate(target_datasets):
    target_datasets[member] = dsp.spatial_regrid(
        target_datasets[member], new_lats, new_lons)

# find the mean values
# way to get the mean. Note the function exists in util.py as def
# calc_climatology_year(dataset):
CRU31.values = utils.calc_temporal_mean(CRU31)

# make the model ensemble
target_datasets_ensemble = dsp.ensemble(target_datasets)
target_datasets_ensemble.name = "ENS"

# append to the target_datasets for final analysis
target_datasets.append(target_datasets_ensemble)

for member, each_target_dataset in enumerate(target_datasets):
    target_datasets[member].values = utils.calc_temporal_mean(target_datasets[
                                                              member])

allNames = []

for target in target_datasets:
    allNames.append(target.name)

# calculate the metrics
taylor_diagram = metrics.SpatialPatternTaylorDiagram()


# create the Evaluation object
RCMs_to_CRU_evaluation = evaluation.Evaluation(CRU31,  # Reference dataset for the evaluation
                                               # 1 or more target datasets for
                                               # the evaluation
                                               target_datasets,
                                               # 1 or more metrics to use in
                                               # the evaluation
                                               [taylor_diagram])  # , mean_bias,spatial_std_dev_ratio, pattern_correlation])
RCMs_to_CRU_evaluation.run()

taylor_data = RCMs_to_CRU_evaluation.results[0]

plotter.draw_taylor_diagram(taylor_data,
                            allNames,
                            "CRU31",
                            fname=OUTPUT_PLOT,
                            fmt='png',
                            frameon=False)
