'''
Author:  Cameron Goodale
Creation Date:  March 14, 2011
Last Updated:  March 14, 2011

Pre-requisite is having NumPY and PyNIO installed.

This script requires the filepath to a single NetCDF file of
TRMM monthly precipitation data, and the path where the output
CAS *.met file will be written

Example:

TRMM_MonthlyPcp_Extractor.py '/path/to/filename.nc' '/paht/to/output/dir'

This will return a complete CAS metadata xml file which will be 
written to the output path you choose.  It will be given the form
of input_filename.met
'''
#module imports needed
import numpy
import Nio
import datetime
import sys
import os

#check to see if 2 parameters have been passed
if len(sys.argv) != 3:
	sys.exit( "You seem to be passing in the wrong number of arguments\
 for this script. The 2 we are excepting in order are: \
'/path/to/filename.nc' '/output/dir/path/'")

#variable list
target_file = sys.argv[1]
output_path = sys.argv[2]

#FOR TESTING ONLY
#output_path = '/Users/cgoodale/Desktop'
#target_file = '/usr/local/wrm/data/TRMM/3B43.990201.6.nc'

f = Nio.open_file(target_file)

#Setup Variables from the Nio object
lat =f.variables['latitude']
lon = f.variables['longitude']
varx = f.variables['pcp']

#transform the input filename into the metadata output filename
filename = os.path.basename(target_file)
metfile = filename.split('.nc')
metfile = metfile[0]+'.met'


#CAS XML vars
#create default cas metfile xml header
cas_xml = '<?xml version="1.0" encoding="UTF-8"?>\n' \
          '<cas:metadata xmlns:cas="http://oodt.jpl.nasa.gov/1.0/cas">\n'
cas_keyval_end = '</keyval>\n'
cas_footer = '</cas:metadata>'

def CASKey(key):
	cas_key_start = '<keyval>\n \t<key>'
	cas_key_end = '</key>\n'
	key_out = cas_key_start+key+cas_key_end
	return key_out

def CASValue(value):
	cas_val_start = '\t<val>'
	cas_val_end = '</val>\n'
	val_out = cas_val_start+value+cas_val_end
	return val_out

def GetTime(Nio_object):
        timex = Nio_object.variables['time']
        time_unit = timex.units
        time_unit = time_unit.split() #break into a list
        raw_time = time_unit[2]  #isolate the time value
        raw_time = raw_time.split('-')  #break down into a simple list
        time_object = datetime.datetime(int(raw_time[0]),
                                        int(raw_time[1]),
                                        int(raw_time[2]))
        time_output = str(time_object.isoformat())+'Z'
        return time_output

def MakeMetadata():
        cas_file = open(output_path+'/'+metfile, "w")
        cas_file.write(cas_xml)  #write in the cas xml header
        cas_file.write(CASKey('dataset_id')) #write in the dataset_id
        cas_file.write(CASValue('3')) #dataset_ID set as 3
        cas_file.write(cas_keyval_end)
        cas_file.write(CASKey('granule_filename'))
        cas_file.write(CASValue(filename))
        cas_file.write(cas_keyval_end)
        cas_file.write(CASKey('param_pcp'))
        cas_file.write(CASValue('monthly_precipitation'))
        cas_file.write(cas_keyval_end)
        cas_file.write(CASKey('data_pcp'))
        lat_block = varx[0]  #jump into latitude dimension
        lat_size = len(lat_block)
        for x in range(lat_size):
                latitude = lat[x] #assign latitude from the variable
                lon_block = lat_block[x] #jump into the longitude dimension
                lon_size = len(lon_block)
                for y in range(lon_size):
                        longitude = lon[y]
                        if lon_block[y] != '-9999':
                                reading = str((lon_block[y]*24)) #assign reading
                        else:
                                reading = str(lon_block[y]) #don't x24
                        latx = str(latitude)
                        lonx = str(longitude)
                        timex = main_time
                        output = latx+','+lonx+',0,'+timex+','+reading
                        final_out = CASValue(output)
                        cas_file.write(final_out)
        cas_file.write(cas_keyval_end)
        cas_file.write(cas_footer)
        cas_file.close()     

#single time variable per file declared here
main_time = GetTime(f)
main_time = main_time.replace(':','')
main_time = main_time.replace('-','')

MakeMetadata()

