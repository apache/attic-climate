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
import numpy.ma as ma
from os import path
import urllib
import ssl
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context


# File URL leader
FILE_LEADER = "http://zipper.jpl.nasa.gov/dist/"
# Three Local Model Files
FILE_1 = "AFRICA_KNMI-RACMO2.2b_CTL_ERAINT_MM_50km_1989-2008_pr.nc"
FILE_2 = "AFRICA_ICTP-REGCM3_CTL_ERAINT_MM_50km-rg_1989-2008_pr.nc"
FILE_3 = "AFRICA_UCT-PRECIS_CTL_ERAINT_MM_50km_1989-2008_pr.nc"

LAT_MIN = -45.0
LAT_MAX = 42.24
LON_MIN = -24.0
LON_MAX = 60.0
START = datetime.datetime(2000, 01, 1)
END = datetime.datetime(2007, 12, 31)

EVAL_BOUNDS = Bounds(lat_min=LAT_MIN, lat_max=LAT_MAX,
                     lon_min=LON_MIN, lon_max=LON_MAX, start=START, end=END)

varName = 'pr'
gridLonStep = 0.44
gridLatStep = 0.44

# needed vars for the script
target_datasets = []
tSeries = []
results = []
labels = []  # could just as easily b the names for each subregion
region_counter = 0

# Download necessary NetCDF file if not present
if not path.exists(FILE_1):
    urllib.urlretrieve(FILE_LEADER + FILE_1, FILE_1)

if not path.exists(FILE_2):
    urllib.urlretrieve(FILE_LEADER + FILE_2, FILE_2)

if not path.exists(FILE_3):
    urllib.urlretrieve(FILE_LEADER + FILE_3, FILE_3)

""" Step 1: Load Local NetCDF File into OCW Dataset Objects and store in list"""
target_datasets.append(local.load_file(FILE_1, varName, name="KNMI"))
target_datasets.append(local.load_file(FILE_2, varName, name="REGCM"))
target_datasets.append(local.load_file(FILE_3, varName, name="UCT"))


""" Step 2: Fetch an OCW Dataset Object from the data_source.rcmed module """
print("Working with the rcmed interface to get CRU3.1 Daily Precipitation")
# the dataset_id and the parameter id were determined from
# https://rcmes.jpl.nasa.gov/content/data-rcmes-database
CRU31 = rcmed.parameter_dataset(
    10, 37, LAT_MIN, LAT_MAX, LON_MIN, LON_MAX, START, END)


""" Step 3: Processing datasets so they are the same shape ... """
print("Processing datasets so they are the same shape")
CRU31 = dsp.water_flux_unit_conversion(CRU31)
CRU31 = dsp.normalize_dataset_datetimes(CRU31, 'monthly')

for member, each_target_dataset in enumerate(target_datasets):
    target_datasets[member] = dsp.subset(target_datasets[member], EVAL_BOUNDS)
    target_datasets[member] = dsp.water_flux_unit_conversion(target_datasets[
                                                             member])
    target_datasets[member] = dsp.normalize_dataset_datetimes(
        target_datasets[member], 'monthly')

print("... spatial regridding")
new_lats = np.arange(LAT_MIN, LAT_MAX, gridLatStep)
new_lons = np.arange(LON_MIN, LON_MAX, gridLonStep)
CRU31 = dsp.spatial_regrid(CRU31, new_lats, new_lons)


for member, each_target_dataset in enumerate(target_datasets):
    target_datasets[member] = dsp.spatial_regrid(
        target_datasets[member], new_lats, new_lons)

# find climatology monthly for obs and models
CRU31.values, CRU31.times = utils.calc_climatology_monthly(CRU31)

for member, each_target_dataset in enumerate(target_datasets):
    target_datasets[member].values, target_datasets[
        member].times = utils.calc_climatology_monthly(target_datasets[member])

# make the model ensemble
target_datasets_ensemble = dsp.ensemble(target_datasets)
target_datasets_ensemble.name = "ENS"

# append to the target_datasets for final analysis
target_datasets.append(target_datasets_ensemble)

""" Step 4: Subregion stuff """
list_of_regions = [
    Bounds(-10.0, 0.0, 29.0, 36.5),
    Bounds(0.0, 10.0,  29.0, 37.5),
    Bounds(10.0, 20.0, 25.0, 32.5),
    Bounds(20.0, 33.0, 25.0, 32.5),
    Bounds(-19.3, -10.2, 12.0, 20.0),
    Bounds(15.0, 30.0, 15.0, 25.0),
    Bounds(-10.0, 10.0, 7.3, 15.0),
    Bounds(-10.9, 10.0, 5.0, 7.3),
    Bounds(33.9, 40.0,  6.9, 15.0),
    Bounds(10.0, 25.0,  0.0, 10.0),
    Bounds(10.0, 25.0, -10.0,  0.0),
    Bounds(30.0, 40.0, -15.0,  0.0),
    Bounds(33.0, 40.0, 25.0, 35.0)]

region_list = [["R" + str(i + 1)] for i in xrange(13)]

for regions in region_list:
    firstTime = True
    subset_name = regions[0] + "_CRU31"
    # labels.append(subset_name) #for legend, uncomment this line
    subset = dsp.subset(CRU31, list_of_regions[region_counter], subset_name)
    tSeries = utils.calc_time_series(subset)
    results.append(tSeries)
    tSeries = []
    firstTime = False
    for member, each_target_dataset in enumerate(target_datasets):
        subset_name = regions[0] + "_" + target_datasets[member].name
        # labels.append(subset_name) #for legend, uncomment this line
        subset = dsp.subset(target_datasets[member],
                            list_of_regions[region_counter],
                            subset_name)
        tSeries = utils.calc_time_series(subset)
        results.append(tSeries)
        tSeries = []

    plotter.draw_time_series(np.array(results), CRU31.times, labels, regions[
                             0], ptitle=regions[0], fmt='png')
    results = []
    tSeries = []
    labels = []
    region_counter += 1
