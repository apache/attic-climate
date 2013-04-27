#!/usr/local/bin/python

def write_cas_xml(data,latitudes,longitudes,iso_time,target_output_dir,filename,timetag,varx,var_name):

  #import system library
  import os
  import sys
  import datetime

  #import the PyNio and Numpy libraries
  import nio
  import numpy

  status = 0

  met_out_filename = str(timetag)+'.met'

  #create default cas metfile xml header
  cas_xml = '<?xml version="1.0" encoding="UTF-8"?>\n' \
          '<cas:metadata xmlns:cas="http://oodt.jpl.nasa.gov/1.0/cas">\n'
  # This is a unique ID that we assign to each dataset.  For MODIS
  # go ahead and use '5'... CRU precip = 6
  dataset_id = '6'
  cas_footer = '</cas:metadata>'
  cas_key_start = '<keyval>\n \t<key>'
  cas_key_end = '</key>\n'
  cas_val_start = '\t<val>'
  cas_val_end = '</val>\n'
  cas_keyval_end = '</keyval>\n'

  '''This section only gets written once to the
  met file initially as dataset information'''

  ########################################
  #open the target xml file and write in the xml header###
  ########################################
  #open the output file in write mode (hence the 'w' param)
  cas_met = open(target_output_dir+'/'+met_out_filename, "w")

  # write the cas xml header using variable 'cas_xml'
  cas_met.write(cas_xml)

  # just an fyi print out for testing.  comment out if you want
  print "writing out to "+str(met_out_filename)+"...."

  #write the dataset information into the file
  cas_met.write(cas_key_start+'dataset_id'+cas_key_end)
  cas_met.write(cas_val_start+dataset_id+cas_val_end+cas_keyval_end)      

  #write out the granule info to the file
  cas_met.write(cas_key_start+'granule_filename'+cas_key_end)

  #in the next line variable 'filename' is the filename
  #with extention so MODIS_2011_01_01.h5 would be typical
  cas_met.write(cas_val_start+filename+cas_val_end+cas_keyval_end)

  #the 'varx' was the name of the parameter being extracted
  #to keep things consistent we used the parameter name from the
  # source file (i.e.  hrf, SurfAirTemp_A, SurfAirTemp_D, etc....)
  cas_var_keys = cas_key_start+'param_'+varx+cas_key_end
  cas_met.write(cas_var_keys)

  #here 'var_name' was the longName of the variable again
  # from the file, we don't tranform or change it at all
  cas_title = cas_val_start+var_name+cas_val_end+cas_keyval_end
  cas_met.write(cas_title)
  cas_data_keys = cas_key_start+'data_'+varx+cas_key_end
  cas_met.write(cas_data_keys)

  '''So at this point you should have built a blob of xml that looks something like this

  <?xml version="1.0" encoding="UTF-8"?>
  <cas:metadata xmlns:cas="http://oodt.jpl.nasa.gov/1.0/cas">
  <keyval>
 	<key>dataset_id</key>
	<val>5</val>
  </keyval>
  <keyval>
 	<key>granule_filename</key>
	<val>sfc.nov2003.nc</val>
  </keyval>
  <keyval>
 	<key>param_d2m</key>
	<val>2 metre dewpoint temperature</val>
  </keyval>
  <keyval>
 	<key>data_d2m</key>


  You can see we have a kind of dangling key with no values...
  well that will be written to the output file next.

  '''
   	
  '''snippet of code where the final output string is formed and written
  to the target output file  this was taken from a nested looping statement
  so the first 4 lines were repeated for each reading'''

  pressure = '0'
  mdi = -9999

  for i in xrange(len(data)):

    #this formed the comma separated values in order latitude, longitude, pressure, time, value
    # the filemanager expects the values in this order.
    cas_val_complete = str(latitudes[i])+','+str(longitudes[i])+','+str(pressure)+','+str(iso_time)+','+str(data[i])
    #then we just box the values with the val_start and val_end variables deiclared above
    cas_value_out = cas_val_start+cas_val_complete+cas_val_end
    #then I just write the line to an open met file 
    cas_met.write(cas_value_out)
    '''this portion of the code will generate all the value lines you need to add after the
   'data_VARIABLE' key and should output something like this:

    <val>90.0,0.0,0,20031101T000000Z,253.344945847</val>
    <val>90.0,1.5,0,20031101T000000Z,253.344945847</val>
    <val>90.0,3.0,0,20031101T000000Z,253.344945847</val>
    <val>90.0,4.5,0,20031101T000000Z,253.344945847</val>
    <val>90.0,6.0,0,20031101T000000Z,253.344945847</val>

    again in order of   lat,
                                lon,
                                pressure(if none available then default to 0),
                                time (in ISO8601 format - YYYMMDDTHHMMSSZ the T and Z are static),
                                reading



    At this point you have a file that is almost complete..but we still have these
    dangling values....that could really use a keyval closing tag, which is what the
    block of code will do.
    '''

  cas_met.write(cas_keyval_end)

  # cas_footer is the matching xml closing tag to the header
  cas_met.write(cas_footer)

  # finally close out the file
  cas_met.close()
  status = 1

  return status


# Main code section

import os
import glob
import datetime

import Nio
import numpy

datadir = '/nas/share4-cf/plean/CRU_TS_3.0/'
target_output_dir = '/nas/share4-cf/plean/CRU_TS_3.0/tavg_xml/'

# Create a list of files
myfile = datadir+'cru_ts_3_00.1901.2006.tmp.nc'

varname = 'tmp'

# Load in the data from the file
f = Nio.open_file(myfile)

# Create arrays of latitude and longitude values
print 'Loading lat/lon data'
lat = f.variables['lat'][:]
lon = f.variables['lon'][:]
lons,lats = numpy.meshgrid(lon,lat)

print 'Loading T_avg data'
long_var_name = f.variables[varname].long_name

data = f.variables[varname][:]

# Check that shape of array is as expected
if(data.shape[1]!=len(lat)):
     print 'Error: unexpected data array size -are all files for same area?'

if(data.shape[2]!=len(lon)):
     print 'Error: unexpected data array size -are all files for same area?'

# Deal with incorrect missing data flag.
#  NB. Read_Me_Pre_Release_TS_3_0.txt states that the missing data flag is incorrectly set in the netCDF files
#      The meta data says it is -9999, but in the data it is set to -999
#      This causes a few headaches with PyNIO as it has read in the data as a masked array 
#      with masks set where data=mdi flag.
# So to get around this we do the following:
#   1. In data array, set values to -9999 where they currently are -999
#   2. Recreate the mask using these new values.
print 'Fixing corrupted missing data issues'
data[numpy.where(data.data==-999)]=-9999
data.mask = (data==-9999)
# Unpack/Decode the data
scale_factor = f.variables[varname].scale_factor
data = data * scale_factor

# Convert units from degC to Kelvin
data = data +273.15

print data.max(),data.min()

# Comments about missing data
# NB. numpy reads the data in as a numpy masked array
#     missing data values are therefore masked and calculations not performed on them
# In the database we want to store a value even at missing data points so we use data.data[:,:]
# This gives a missing data value of -9999
# Quick sanity check on the data (make sure no obviously incorrect values)
if data.max()<0.0:
     print 'Problem encountered with data values: min data value = ',data.min()
     
# Remove the path from the filename so can pull specific characters from known locations within it
filename_only = os.path.basename(myfile)

# Extract the time from the filename
#  NB. times are stored as months since 1870-1-1
#  Adding months in datetime is tricky (as month definition is ambigous)
#  instead just do it the old fashioned way...
print 'Decoding times'
times = f.variables['time'][:]
base_year = 1870
myyears = base_year + numpy.floor(times/12.)
print myyears
mymonths = 1+times%12

# Loop through each file in turn
print 'Producing XML from data'
for mytime in xrange(len(times)):

   iso_time = str(int(myyears[mytime]))+str("%02i" % mymonths[mytime])+'01T000000Z'
   print iso_time

   print data.data[mytime,:,:].min(), data[mytime,:,:].min(),data.data[mytime,:,:].max()

   # Write XML
   write_cas_xml(data.data[mytime,:,:].ravel(),lats.ravel(),lons.ravel(),iso_time,target_output_dir,filename_only,mytime,varname,long_var_name)


print 'Finished'
