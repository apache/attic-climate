#!/usr/local/bin/python
'''This MetExtractor is built just for a specific MERRA Dataset
Inst6_3d_ana_Np: 6-hourly Instantaneous atmospheric analysis
From the command line you can pass in the target filename, and 
the output dir where you want the met file to be written.

All of the met filenames are <filename.ext>.met and will be
valid OODT cas-xml.

Author:  Cameron.E.Goodale@jpl.nasa.gov
Created: February 14, 2012
Updated: March 13, 2012

'''
import numpy
import numpy.ma as ma
import nio
import sys, datetime
import os.path as path  #work with filenames
from optparse import OptionParser
from time import time

# CAS Metadata Helper Module
import MetMaker as M


if len(sys.argv) == 1:
    print "No arguments found, use the -h option for more details"
    sys.exit(1)
  

# Options Parsing Block with Help
usage = "usage: ./MERRA_Extractor.py  [options] arg1 arg2"
parser = OptionParser(usage=usage)
parser.add_option("-f", "--file", dest="filename", help="File to Extract Metadata From")
parser.add_option("-p", "--param", dest="param", help="Name of the Parameter to extract")
parser.add_option("-o", "--output", dest="output", 
                      help="Directory where you want the output metadata files written")

(options, args) = parser.parse_args()

# dataset STATIC variables
t_name = 'TIME_EOSGRID'
lat_name = 'YDim_EOSGRID'
lon_name = 'XDim_EOSGRID'
h = 0
start_datetime = datetime.datetime(1979,1,1,0,0,0)

# Dictionary to hold the North American Region Bounding Box
# We can use these values to MASK the XDIM and YDim Arrays i think
NA_Region = {'westbc': -160,
             'eastbc': -30,
             'southbc': 20,
             'northbc': 60
             }

def createMaskedArray(one_d_arr, arr_min, arr_max):
    '''This will take in a 1 dimensional array object, and the valid value range for the
    array.
    Example: longitude array arr = [-180 ... 179.999]
            westbc value arr_min = -160
            eastbc value arr_max = -30
            return masked array = [--, --, ...-160 ... -30, --, ...--, --]
    '''
    min_masked = ma.masked_less(one_d_arr, arr_min)
    full_mask = ma.masked_greater(min_masked, arr_max)
    filled_mask = ma.filled(full_mask, 999)
    return filled_mask



def parse_file(f=options.filename, p=options.param, t=t_name, lat=lat_name, lon=lon_name):
    '''This function will return a set of pointers to critical nio Objects
    within the file:
    
    return PARAMETER_Obj, LAT_Obj, LON_Obj, TIME_Obj 
    '''
    # Open the File using Nio in READ-ONLY Mode
    fx = nio.open_file(f,'r')
    param_obj = fx.variables[p]
    lat_obj = fx.variables[lat]
    lon_obj = fx.variables[lon]
    time_obj = fx.variables[t]
    return param_obj, lat_obj, lon_obj, time_obj

def build_datapoint(pos_tuple, reading):
    '''This will take in an array position as a tuple along with a reading
    value and will return a string that conforms to the metadata ordering
    of 'lat,lon,height,time,reading' 
    example: '90.0,0.0,0,19970222T060000Z,251.486206527'
    pos_tuple ~ (time_pos, lat_pos, lon_pos) 
    '''
    global t
    global h
    global lat
    global lon
    global start_datetime
    tx = t[int(pos_tuple[0])]
    time_change = datetime.timedelta(minutes=tx)
    read_datetime = start_datetime+time_change
    time_string = read_datetime.strftime('%Y%m%dT%H%M%SZ')
    latx = lat[int(pos_tuple[1])]
    lonx = lon[int(pos_tuple[2])]
    met_val = '%s,%s,%s,%s,%s' % (latx, lonx, h, time_string,reading)
    return met_val

# DO STUFF BELOW HERE vvvvvv
# pluck the filename off the user input
filename = path.basename(options.filename)

# Open the file and get the important stuff out
full_param, nio_lat, nio_lon, full_time = parse_file()

# Converting Nio Objecting in Numpy arrays improves process speeds
# considerably
param = numpy.array(full_param)
t = numpy.array(full_time)
lat_full = numpy.array(nio_lat)
lon_full = numpy.array(nio_lon)

# Mask the Lat and Lon Arrays using the NA_Region Dict
lat = createMaskedArray(lat_full, NA_Region['southbc'], NA_Region['northbc'])
lon = createMaskedArray(lon_full, NA_Region['westbc'], NA_Region['eastbc'])

x = numpy.ndenumerate(param)
# declare empty list to append readings to
reading_list = []
for position,value in x:
    
    # ADD IN CHECK if position[1] OR position[2] are == '--' DON'T construct a reading
    if lat[int(position[1])] == 999:
        pass
    elif lon[int(position[2])] == 999:
        pass
    else:
        reading = build_datapoint(position,value)
        reading_list.append(reading)

# Build the Metadata Object up
met = M.CAS_Met()

# Populate with default Metadata values using met.add_met(key, val_list):
met.add_met('dataset_id', ['7'])
met.add_met('granule_filename', [filename])

# define the param_* key name and the description value
param_key = 'param_%s' % options.param
met.add_met(param_key, [full_param.standard_name]) 

# drop the reading list into the metadata object
data_key = 'data_%s' % options.param
met.add_met(data_key, reading_list)

# MERRA100.prod.assim.inst6_3d_ana_Np.19790101.hdf_<param_id>.met 
output_file = '%s/%s_%s.met' % (options.output, filename, options.param)
met.write_met(output_file)