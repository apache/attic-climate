#!/usr/local/bin/python
'''This will take in a CERES file and extract all of the points
and output a metadata file for each parameter in the provided
directory with parameter_name_[#].met


Author:  Cameron.E.Goodale@jpl.nasa.gov
Created: March 28, 2012

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
usage = "usage: ./CERES_shortwave_longwave_Extractor.py  [options] arg1 arg2"
parser = OptionParser(usage=usage)
parser.add_option("-f", "--file", dest="filename", help="File to Extract Metadata From")
parser.add_option("-o", "--output", dest="output", 
                      help="Directory where you want the output metadata files written")

(options, args) = parser.parse_args()

def get_var_name(var):
    x = str(var).split('\n')[0].lstrip('Variable: ')
    return x

def write_metadata(var, readings, file_counter):
    met, data_key, var_str = build_metadata(var)
    # drop the reading list into the metadata object
    met.add_met(data_key, readings)
    output = '%s/%s_%s.met' % (path.abspath(options.output), var_str, file_counter)
    met.write_met(output)
    print 'wrote out %s to disk...' % output

def parse_time(t_obj):
    # Example: 'hours since 1960-1-1 00:00:0.0'
    t = t_obj.units.lstrip('hours since ').replace('0.0','00').split(' ')
    # Now we should have ['1960-1-1', '00:00:00'] but we cannot use the strptime
    # method because the day and month values are not 2 digit numbers
    d_list = t[0].split('-')
    y = int(d_list[0]); m = int(d_list[1]); d = int(d_list[2])
    t_list = t[1].split(':')
    h = int(t_list[0]); min = int(t_list[1]); s = int(t_list[2])
    start_datetime = datetime.datetime(y, m, d, h, min, s)
    return start_datetime


def extract_points(var, dims, t):
    # start = datetime.datetime(2000,3,1,0,0,0)
    _time = dims[0]
    _lat = dims[1]
    _lon = dims[2]
    # Need to parse the start from the time.units attribute
    start = parse_time(t)
    counter = 0
    file_counter = 0
    # NOTE FIX LONGITUDE BEFORE RETURNING    
    '''Need to build up a reading list to some limit, then we need to create the metadata
    object using build_metadata(var) function.  Then take the returned tuple and output the 
    final file with a filenumber counter included in the output filename'''
    reading_list = [] #empty list to append to
    for tup, value in numpy.ndenumerate(var):
        t = start + datetime.timedelta( hours=int(_time[ tup[0] ]) )
        iso_time = t.strftime('%Y%m%dT000000Z')
        lat = _lat[tup[1]]
        lon = _lon[tup[2]]
        # The fix is in here
        if lon > 180:
            lon = lon - 360
        else:
            pass
        reading = '%s,%s,0,%s,%s' % (lat,lon,iso_time,value)
        reading_list.append(reading)
        counter = counter + 1
        if counter < 700000:
            pass
        else:
            write_metadata(var, reading_list, file_counter)
            # Reset everything
            print 'Reseting everything for another run...'
            counter = 0
            file_counter = file_counter +1
            reading_list = []
            pass

    write_metadata(var, reading_list, file_counter)


def build_metadata(var_obj):
    var_string = get_var_name(var_obj)
    # Build a Metadata Object
    print 'building met for %s' % var_string
    met = M.CAS_Met()
    met.add_met('dataset_id', ['8'])
    filename = path.basename(options.filename)
    met.add_met('granule_filename', [filename])
    param_key = 'param_%s' % var_string
    met.add_met(param_key, [var_obj.standard_name])
    data_key = 'data_%s' % var_string
    return met, data_key, var_string


def filter_vars(vars):
    # dataset STATIC variables
    t_name, lat_name, lon_name = 'time', 'lat', 'lon'
    dimensions = [t_name, lat_name, lon_name]
    # Convert all dims into numpy arrays and group into a tuple
    _time = vars[t_name].get_value()
    _lat = vars[lat_name].get_value()
    _lon = vars[lon_name].get_value()
    dims = (_time, _lat, _lon)
    t = vars[t_name] # pass in the time nio object for timestamping readings later
    for name in vars:
        if name in dimensions:
            pass
        else:
            var = vars[name]
            # Removing list comprehension to allow easy file breaks
            # readings = [str(a) for a in extract_points(var, dims)]
            print 'Running extraction...'
            extract_points(var, dims, t)


def main():
    # Open the CERES File
    f = nio.open_file(options.filename)
    # filter the variables and extract the non-dimensional ones.
    vars = f.variables
    filter_vars(vars)




if __name__ == '__main__':
	main()
