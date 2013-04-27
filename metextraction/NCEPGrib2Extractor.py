#import system library
import sys

#import the PyNio and Numpy libraries
import nio
import numpy

#create default cas metfile xml header
cas_xml = '<?xml version="1.0" encoding="UTF-8"?>\n' \
          '<cas:metadata xmlns:cas="http://oodt.jpl.nasa.gov/1.0/cas">\n'
cas_footer = '</cas:metadata>'
cas_key_start = '<keyval>\n<key>'
cas_key_end = '</key>\n'
cas_val_start = '<val>'
cas_val_end = '</val>\n'
cas_keyval_end = '</keyval>\n'
cas_var = 'Variables'
cas_lon = 'Longitude'


#target file path must be passed as the first command line arg
target_filepath = sys.argv[1]
#target_filename = 'A09557-9610.grb2'

#output file path is the second command line arg
target_output = sys.argv[2]

#list of variables to process...need to look into this more.
varx2 = sys.argv[3]

#open the files and link it to variable 'f'
#f = nio.open_file('/Users/cgoodale/Projects/WRM/NCEP/'+target_filename)

f = nio.open_file(target_filepath)

#this will capture all variable names within a dictionary 
var_names = f.variables

#dictionary of dimensions
dim_names = f.dimensions

#this portion drills down to the base longitude array
lon = f.variables['g4_lon_2']
lon_values = lon.get_value()

#this reads out the latitude values
lat = f.variables['g4_lat_1']
lat_values = lat.get_value()

#this reads out the timestamp values
tim = f.variables['initial_time0_hours']
time_values = tim.get_value()

#val = v.get_value()  #this will read in the value of the variable as a numpy array
#this command will list out all the attributes of the variable
#dir(v)
#useful to know for interactive development


#####################################################
#open the target xml file and write in the xml header
#####################################################

#open the output file in write mode (hence the 'w' param)
cas_met = open('/Users/cgoodale/Desktop/pythonMetOut.xml', "w")
cas_met.write(cas_xml)

#initial declaration and writing of the keyval and key tags
#cas_variables = cas_key_start+'param_'cas_var+cas_key_end
#cas_met.write(cas_variables)

cas_met.write(cas_key_start+'granule_filename'+cas_key_end)
cas_met.write(cas_val_start+target_filename+cas_val_end+cas_keyval_end)



###############
#attempt to read out all points within a single 3
# dimensional numpy array
################

#loop over the var_names dictionary and write each variable to the
#target xml file as a variable

for key in var_names:
    varx = key
    if len(f.variables[varx].shape) == 3:    #we are only processing 3 dimensional arrays
        print varx
        var_object = var_names[varx]
        var_name = var_object.long_name
        cas_var_keys = cas_key_start+'param_'+varx+cas_key_end
        cas_met.write(cas_var_keys)
        #dims = var_object.dimensions
        #print dims+varx
        cas_title = cas_val_start+var_name+cas_val_end+cas_keyval_end
        cas_met.write(cas_title)
        #link each variables to v for data extraction
        v = f.variables[varx]
        #static opening key for each variable
        cas_data_keys = cas_key_start+'data_'+varx+cas_key_end
        cas_met.write(cas_data_keys)
        for i in range(len(v)):
            main_val = i
            sub = v[i]
            #print main_val
            for x in range(len(sub)):
                sub_val = x
                sub_sub = sub[x]
                #print str(main_val)+','+str(sub_val)
                for y in range(len(sub_sub)):
                    reading = sub_sub[y]
                    longitude = lon_values[y]
                    latitude = lat_values[x]
                    timestamp = time_values[i]
                    cas_val_complete = str(latitude)+','+str(longitude)+','+'0,'+str(timestamp)+','+str(reading)
                    cas_value_out = cas_val_start+cas_val_complete+cas_val_end
                    #final output is (lat, lon, height, time, value) HEIGHT IS HARDCODED at 0 for now.
                    cas_met.write(cas_value_out)
            cas_met.write(cas_keyval_end)


#loop over the lon_values array and output the longitude points to the
#cas xml file already open for writing after writing the keyval element

#cas_longitude = cas_key_start+cas_lon+cas_key_end
#cas_met.write(cas_longitude)

#for i in range(len(lon_values)):
#    lon32 = lon_values[i]
#    lonx = str(lon32)  #have to convert from numpy.float32 to string
#    cas_lon = cas_val_start+lonx+cas_val_end
#    cas_met.write(cas_lon)
#cas_met.write(cas_keyval_end)

#assign the variable long name to 'title' to be used in CAS xml output
#title = v.long_name

#create the long strung together title element
#cas_title = cas_key_start+'VariableLongName'+cas_key_end+title+cas_val_end

#bookend the title with the header and footer info
#fullout = cas_xml + cas_header + cas_title + cas_footer


#cas_met.write(cas_header)

cas_met.write(cas_footer)
cas_met.close()



