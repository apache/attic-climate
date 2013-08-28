import datetime

import numpy as np

import ocw.data_source.local as local
import ocw.dataset_processor as dsp
import ocw.evaluation as eval
import ocw.metrics as metrics

# Two Local Model Files 
FILE_1 = "AFRICA_KNMI-RACMO2.2b_CTL_ERAINT_MM_50km_1989-2008_tasmax.nc"
FILE_2 = "AFRICA_UC-WRF311_CTL_ERAINT_MM_50km-rg_1989-2008_tasmax.nc"

""" Step 1: Load Local NetCDF Files into OCW Dataset Objects """
print("Loading %s into an OCW Dataset Object" % (FILE_1,))
knmi_dataset = local.load_file(FILE_1, "tasmax")
print("KNMI_Dataset.values shape: (times, lats, lons) - %s \n" % (knmi_dataset.values.shape,))

print("Loading %s into an OCW Dataset Object" % (FILE_2,))
wrf_dataset = local.load_file(FILE_2, "tasmax")
print("WRF_Dataset.values shape: (times, lats, lons) - %s \n" % (wrf_dataset.values.shape,))



""" Step 2: Temporally Rebin the Data into an Annual Timestep """
print("Temporally Rebinning the Datasets to an Annual Timestep")
knmi_dataset = dsp.temporal_rebin(knmi_dataset, datetime.timedelta(days=365))
wrf_dataset = dsp.temporal_rebin(wrf_dataset, datetime.timedelta(days=365))
print("KNMI_Dataset.values shape: %s" % (knmi_dataset.values.shape,))
print("WRF_Dataset.values shape: %s \n\n" % (wrf_dataset.values.shape,))



""" Step 3: Spatially Regrid the Dataset Objects to a 1 degree grid """
#  The spatial_boundaries() function returns the spatial extent of the dataset
print("The KNMI_Dataset spatial bounds (min_lat, max_lat, min_lon, max_lon) are: \n"
      "%s\n" % (knmi_dataset.spatial_boundaries(), ))
print("The KNMI_Dataset spatial resolution (lat_resolution, lon_resolution) is: \n"
      "%s\n\n" % (knmi_dataset.spatial_resolution(), ))

min_lat, max_lat, min_lon, max_lon = knmi_dataset.spatial_boundaries()

# Using the bounds we will create a new set of lats and lons on 1 degree step
new_lons = np.arange(min_lon, max_lon, 1)
new_lats = np.arange(min_lat, max_lat, 1)

# Spatially regrid datasets using the new_lats, new_lons numpy arrays
print("Spatially Regridding the KNMI_Dataset...")
knmi_dataset = dsp.spatial_regrid(knmi_dataset, new_lats, new_lons)
print("Final shape of the KNMI_Dataset: \n"
      "%s\n" % (knmi_dataset.values.shape, ))
print("Spatially Regridding the WRF_Dataset...")
wrf_dataset = dsp.spatial_regrid(wrf_dataset, new_lats, new_lons)
print("Final shape of the WRF_Dataset: \n"
      "%s\n" % (wrf_dataset.values.shape, ))

""" Step 4:  Build a Metric to use for Evaluation - Bias for this example """
# You can build your own metrics, but OCW also ships with some common metrics
bias = metrics.Bias()

""" Step 5: Create an Evaluation Object using Datasets and our Metric """
# The Evaluation Class Signature is:
# Evaluation(reference, targets, metrics, subregions=None)
# Evaluation can take in multiple targets and metrics, so we need to convert
# our examples into Python lists.  Evaluation will iterate over the lists
bias_evaluation = eval.Evaluation(knmi_dataset, [wrf_dataset], [bias])
bias_evaluation.run()




