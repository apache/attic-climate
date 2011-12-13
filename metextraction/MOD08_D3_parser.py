#!/usr/local/bin/python

def write_cas_xml(data,latitudes,longitudes,iso_time,target_output_dir,filename,varx,var_name):

  #import system library
  import os
  import sys
  import datetime

  #import the PyNio and Numpy libraries
  import nio
  import numpy

  status = 0

  met_out_filename = os.path.splitext(filename)[0]+'.met'

  #create default cas metfile xml header
  cas_xml = '<?xml version="1.0" encoding="UTF-8"?>\n' \
          '<cas:metadata xmlns:cas="http://oodt.jpl.nasa.gov/1.0/cas">\n'
  # This is a unique ID that we assign to each dataset.  For MODIS
  # go ahead and use '5'
  dataset_id = '5'
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

datadir = '/nas/share4-cf/plean/MODIS/MOD08_D3/cloud_fraction_mean/'
target_output_dir = '/nas/share4-cf/plean/MODIS/MOD08_D3/cloud_fraction_mean/xml/'

# Create a list of files
myfilelist = glob.glob(datadir+'*hdf')

# Create arrays of latitude and longitude values
#  NB. these HDF files don't appear to have lat/lon stored in them 
#       (or at least Nio can't access them)
#      Therefore we need to construct arrays of lat/lon to go with the data.
#      We already know that this is on a 1x1deg grid.
lat = numpy.arange(180)-89.5
lon = numpy.arange(360)-179.5
lons,lats = numpy.meshgrid(lon,lat)
# flip latitudes so correctly aligned with data points
lats = -lats

varname = 'Cloud_Fraction_Mean'

# Loop through each file in turn
for myfile in myfilelist:
   print myfile

   # Load in the data from the file
   f = Nio.open_file(myfile)

   long_var_name = f.variables[varname].long_name

   data = f.variables[varname][:]

   # Check that shape of array is as expected
   if(data.shape[0]!=180):
        print 'Error: unexpected data array size -are all files for same area?'
        break
   if(data.shape[1]!=360):
        print 'Error: unexpected data array size -are all files for same area?'
        break

   # Unpack/Decode the data
   scale_factor = f.variables[varname].scale_factor
   add_offset = f.variables[varname].add_offset
   data = data * (scale_factor - add_offset)  #NB. this is correct and a special case (taken from file documentation)

   print data.max(),data.min()

   # Comments about missing data
   # NB. numpy reads the data in as a numpy masked array
   #     missing data values are therefore masked and calculations not performed on them
   # In the database we want to store a value even at missing data points so we use data.data[:,:]
   # This gives a missing data value of -9999

   # Quick sanity check on the data (make sure no obviously incorrect values)
   if data.max()>1.0:
        print 'Problem encountered with data values: max data value = ',data.max()
        break
   if data.max()<0.0:
        print 'Problem encountered with data values: min data value = ',data.min()
        break

   # Remove the path from the filename so can pull specific characters from known locations within it
   filename_only = os.path.basename(myfile)

   # Extract the time from the filename
   myyear = int(filename_only[10:14])
   myday_of_year = int(filename_only[14:17])

   # Create a datetime object of the time
   #  Method: we know the year and the day of the year
   #          To create the required datetime just add day_of_year 
   #          to a base_time set to midnight Jan 1st of that year.
   first_day_of_year = datetime.datetime(myyear,1,1,0,0,0)
   time_delta = datetime.timedelta(days=(myday_of_year-1))   #NB. -1 so if day 1, doesn't add 1 to Jan 1st
   mydate = first_day_of_year + time_delta

   iso_time = str(mydate.year)+str("%02i" % mydate.month)+str("%02i" % mydate.day)+'T'+str("%02i" % mydate.hour)+str("%02i" % mydate.minute)+'00Z'

   # Write XML
   write_cas_xml(data.data.ravel(),lats.ravel(),lons.ravel(),iso_time,target_output_dir,filename_only,varname,long_var_name)


print 'Finished'
