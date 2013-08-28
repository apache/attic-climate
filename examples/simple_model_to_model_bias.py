import datetime
import ocw.data_source.local as local
import ocw.dataset_processor as dsp

# Two Local Model Files 
FILE_1 = "AFRICA_KNMI-RACMO2.2b_CTL_ERAINT_MM_50km_1989-2008_tasmax.nc"
FILE_2 = "AFRICA_UC-WRF311_CTL_ERAINT_MM_50km-rg_1989-2008_tasmax.nc"
# Load the Files into OCW Objects Using the local from ocw.data_source
dataset_1 = local.load_file(FILE_1, "tasmax")
dataset_2 = local.load_file(FILE_2, "tasmax")
# Do Temporal Rebinning to an Annual Time Step using dataset_processor
dataset_1 = dsp.temporal_rebin(dataset_1, datetime.timedelta(days=365))
dataset_2 = dsp.temporal_rebin(dataset_2, datetime.timedelta(days=365))
