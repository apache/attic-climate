'''This is the Snow Water Equivalent Extractor

Usage:  python SWEExtractor.py /path/to/file.nc /output/directory

Example:  python SWEExtractor.py /home/cgoodale/2000-sweb.nc /home/cgoodale 

'''

# Python Module Imports

import sys
import nio
import numpy
from datetime import timedelta, datetime

met_counter = 0 # this will be used to keep output .met filenames unique

# Custom Function Definitions

def decode_core_time_attrib():
    time_format = '%Y,%m,%d,%H,%M'
    base_time_string = f.variables['time'].units
    # Remove 'minutes since '
    base_time = base_time_string.replace('minutes since ','')
    # Replace : - and empty space with a comma to conver to csv
    base_time_csv = base_time.replace(':',',').replace('-',',').replace(' ',',')
    base_time_datetime = datetime.strptime(base_time_csv, time_format)
    return base_time_datetime

def decode_time(time_value):
    '''This function will take in a raw time value
    and return a fully formed ISO Time formatted
    string which can then be used within the output
    *met xml file for ingestion'''
    real_time_value = BASE_TIME+timedelta(minutes=time_value)    
    # Reformat the time to ISO format
    iso_base_time = real_time_value.isoformat()+'Z'
    # Reformat into CAS Compliant Format
    iso_time = iso_base_time.replace('-','').replace(':','')
    return iso_time

def build_value_array(variable):
    '''Take in a variable name and this will return a simple
    array with all raw values for the variable populated from
    the nio object'''
    varx = f.variables[variable]
    return varx

def set_cas_value(position, value):
    '''Function to run against a numpy.ndenumerate(swe_array)
    where the array shape is (time, lat, lon).  This will return
    a string which contains the fully assembled CAS xml <val>
    tag which can be directly written out to the target xml file'''
    time = str(decode_time(TIME[position[0]]))
    lat = str(LAT[position[1]])
    lon = str(LON[position[2]])
    vertical = '0'  # No Vertical needed for SWE so hardcoded as string zero '0'
    value_list = [lat,lon,vertical,time,str(value)]
    return cas_value_maker(value_list)

def cas_value_maker(x):
    '''take list [lat,lon,vertical,time,value] and return a fully formed
    CAS xml compliant <val>.......</val> xml element'''
    xml_value = cas_val_start+x[0]+','+x[1]+','+x[2]+','+x[3]+','+x[4]+cas_val_end
    #print xml_value
    return xml_value

############ REPLACE THESE WITH CMD LINE ARGS ##################
################################################################
#target file path must be passed as the first command line arg
#target_filename = '/home/cgoodale/2000-sweb.nc'
target_filename = sys.argv[1]
filename_split = target_filename.split('/')
filename = filename_split[(len(filename_split)-1)]

# Open source file to extract data from
f = nio.open_file(target_filename)
#output file path is the second command line arg
#target_output = '/home/cgoodale'
target_output = sys.argv[2]

met_out_filename = filename+str(met_counter)+'.met'
################################################################


#  START PROCESSING

# Set the base time for the dataset
BASE_TIME = decode_core_time_attrib()

LAT = build_value_array('lat')
LON = build_value_array('lon')
TIME = build_value_array('time')
SWEB = build_value_array('sweb')

# OPEN THE OUTPUT *.met file
cas_met = open(target_output+'/'+met_out_filename, "w")

# CAS XML Format Variables
cas_xml = '<?xml version="1.0" encoding="UTF-8"?>\n' \
          '<cas:metadata xmlns:cas="http://oodt.jpl.nasa.gov/1.0/cas">\n'
dataset_id = '9'
cas_footer = '</cas:metadata>'
cas_key_start = '<keyval>\n \t<key>'
cas_key_end = '</key>\n'
cas_val_start = '\t<val>'
cas_val_end = '</val>\n'
cas_keyval_end = '</keyval>\n'
cas_var = 'Variables'
cas_lon = 'Longitude'
varx = 'sweb'  #just processing the sweb parameter
var_name = SWEB.long_name

def set_cas_header():
	cas_met.write(cas_xml)  # Write in the cas met xml header information
	cas_met.write(cas_key_start+'dataset_id'+cas_key_end)
	cas_met.write(cas_val_start+dataset_id+cas_val_end+cas_keyval_end)
	cas_met.write(cas_key_start+'granule_filename'+cas_key_end)
	cas_met.write(cas_val_start+filename+cas_val_end+cas_keyval_end)
	cas_var_keys = cas_key_start+'param_'+varx+cas_key_end
	cas_met.write(cas_var_keys)
	cas_title = cas_val_start+var_name+cas_val_end+cas_keyval_end
	cas_met.write(cas_title)
	cas_data_keys = cas_key_start+'data_'+varx+cas_key_end
	cas_met.write(cas_data_keys)

def set_cas_footer():
	cas_met.write(cas_keyval_end)
	cas_met.write(cas_footer)
	cas_met.close()


#initially setup the cas_header
set_cas_header()

val_counter = 0  # this is a simple counter to track progress when making xml

# Build a Numpy Enumerate Object to feed into 'set_cas_value()' method
print 'Building the numpy array object...this will take a little while...'
swe_array = numpy.ndenumerate(SWEB)
print 'Okay with that complete, now let\'s start writing out some values'


for position, value in swe_array:
	cas_value_output = set_cas_value(position, value)
	cas_met.write(cas_value_output) # write the new xml into the file
	val_counter +=1
	if val_counter%1000000==0:   #check if counter is divisible by 1M
		print 'Writing out file with '+str(val_counter)+' values'
		set_cas_footer() #complete the file and close it out
		#open a new metfile with an increase file counter
		met_counter +=1 # increase met_counter global var
		met_out_filename = filename+str(met_counter)+'.met'
		cas_met = open(target_output+'/'+met_out_filename, "w")
		#write in the header information...again
		set_cas_header()
		#let it go back up to the parent for loop

# Write out the end of the file
set_cas_footer()


