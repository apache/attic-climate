
##############################################################################
# load required python modules
import sys
import os

##############################################################################
# all variables must be daily and should span 1960-1990 (for base-periods in percentile calcs)
# T files should be in units degrees Kelvin
# pr files should be in units mm/day
# there should be no leap year days (365day calender)
# grids should be regular latlon (not curvilinear)
# grids can be regional or global 

# input file locations
in_pre='/storage/users/pgibson/CPC_0.25_USA-Unified/CPC_pre_USA-unif_1948-2016_daily.nc'
var_name='tp'                                        # name of precip variable in in_pre
bp_start=1960                                        # start of base period
bp_end=1990                                          # end of base period

ofile_base=(in_pre.split("/")[5]).split("_pre")[0]   # strip directory and extension (after "USA")
print(ofile_base)

#############################################################################
# run functions from ETCCDI.py
# link to where ETCCDI python module is
sys.path.append(os.path.abspath("/home/pgibson/python/ETCCDI_functions/for_RCMES/"))
from ETCCDI_precip import *

# run base function file generation, specifying bp-start and end (except for tg)
gen_pre_basefiles(in_pre, bp_start, bp_end)

# run indices saving to netcdf (opt=0)
run_cdd(in_pre, var_name, ofile_base, 0)
run_cwd(in_pre, var_name, ofile_base, 0)
run_pd(in_pre, var_name, ofile_base, 0)
run_r10mm(in_pre, var_name, ofile_base, 0)
run_r20mm(in_pre, var_name, ofile_base, 0)
run_rx1day(in_pre, var_name, ofile_base, 0)
run_rx3day(in_pre, var_name, ofile_base, 0)
run_rx5day(in_pre, var_name, ofile_base, 0)
run_prcptot(in_pre, var_name, ofile_base, 0)
run_sdii(in_pre, var_name, ofile_base, 0)
run_r95p(in_pre, var_name, ofile_base, 0)
run_r95ptot(ofile_base, 0)
run_r99p(in_pre, var_name, ofile_base, 0)



