import os
from urllib import urlretrieve

FILE_LEADER = "http://zipper.jpl.nasa.gov/dist/"
FILE_1 = "AFRICA_KNMI-RACMO2.2b_CTL_ERAINT_MM_50km_1989-2008_tasmax.nc"
FILE_2 = "AFRICA_UC-WRF311_CTL_ERAINT_MM_50km-rg_1989-2008_tasmax.nc"

def setup_package():
    if not os.path.exists('/tmp/d1.nc'):
        urlretrieve(FILE_LEADER + FILE_1, '/tmp/d1.nc')

    if not os.path.exists('/tmp/d2.nc'):
        urlretrieve(FILE_LEADER + FILE_2, '/tmp/d2.nc')

    if not os.path.exists('/tmp/ocw'):
        os.mkdir('/tmp/ocw')
