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

OUTPUT_PLOT = "subregions"

# Spatial and temporal configurations
LAT_MIN = -45.0
LAT_MAX = 42.24
LON_MIN = -24.0
LON_MAX = 60.0
START_SUB = datetime.datetime(2000, 01, 1)
END_SUB = datetime.datetime(2007, 12, 31)

# regridding parameters
gridLonStep = 0.5
gridLatStep = 0.5

# Regrid
print("... regrid")
new_lats = np.arange(LAT_MIN, LAT_MAX, gridLatStep)
new_lons = np.arange(LON_MIN, LON_MAX, gridLonStep)

list_of_regions = [
    Bounds(-10.0, 0.0, 29.0, 36.5, START_SUB, END_SUB),
    Bounds(0.0, 10.0,  29.0, 37.5, START_SUB, END_SUB),
    Bounds(10.0, 20.0, 25.0, 32.5, START_SUB, END_SUB),
    Bounds(20.0, 33.0, 25.0, 32.5, START_SUB, END_SUB),
    Bounds(-19.3, -10.2, 12.0, 20.0, START_SUB, END_SUB),
    Bounds(15.0, 30.0, 15.0, 25.0, START_SUB, END_SUB),
    Bounds(-10.0, 10.0, 7.3, 15.0, START_SUB, END_SUB),
    Bounds(-10.9, 10.0, 5.0, 7.3,  START_SUB, END_SUB),
    Bounds(33.9, 40.0,  6.9, 15.0, START_SUB, END_SUB),
    Bounds(10.0, 25.0,  0.0, 10.0, START_SUB, END_SUB),
    Bounds(10.0, 25.0, -10.0,  0.0, START_SUB, END_SUB),
    Bounds(30.0, 40.0, -15.0,  0.0, START_SUB, END_SUB),
    Bounds(33.0, 40.0, 25.0, 35.0, START_SUB, END_SUB)]

# for plotting the subregions
plotter.draw_subregions(list_of_regions, new_lats,
                        new_lons, OUTPUT_PLOT, fmt='png')
