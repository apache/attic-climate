#import system library
import sys
import datetime

#import the PyNio and Numpy libraries
import nio
import numpy

#create default cas metfile xml header
cas_xml = '<?xml version="1.0" encoding="UTF-8"?>\n' \
          '<cas:metadata xmlns:cas="http://oodt.jpl.nasa.gov/1.0/cas">\n'
dataset_id = '5'
cas_footer = '</cas:metadata>'
cas_key_start = '<keyval>\n \t<key>'
cas_key_end = '</key>\n'
cas_val_start = '\t<val>'
cas_val_end = '</val>\n'
cas_keyval_end = '</keyval>\n'
cas_var = 'Variables'
cas_lon = 'Longitude'

met_out_counter=0
met_out_id = 0
#set starting time which all time elements are based on
# all time elements are expressed in hours from 1900-01-01 00:00:0
raw_time = datetime.datetime(1900,1,1)

#target file path must be passed as the first command line arg
#target_filename = '/usr/local/wrm/data/ERASURF/sfc.nov2003.nc'
target_filename = sys.argv[1]
filename_split = target_filename.split('/')
filename = filename_split[(len(filename_split)-1)]

met_out_filename = filename+'.'+str(met_out_id)+'.met'

#output file path is the second command line arg
target_output = sys.argv[2]
#target_output = '/Users/cgoodale/Desktop'

#max records per .met file
#record_max = sys.argv[3]
record_max = 500000

#list of variables to process...need to look into this more.
#varx2 = sys.argv[3]

record_count = 0
var_count = 0

#open the files and link it to variable 'f'
f = nio.open_file (target_filename)

#f = nio.open_file(target_filename)

#this will capture all variable names within a dictionary 
var_names = f.variables

#dictionary of dimensions
dim_names = f.dimensions

#this portion drills down to the base longitude array
lon = f.variables['longitude']
lon_values = lon.get_value()

#this reads out the latitude values
lat = f.variables['latitude']
lat_values = lat.get_value()

#declare where time is stored
time = f.variables['time']
time_values = time.get_value()

#val = v.get_value()  #this will read in the value of the variable as a numpy array
#this command will list out all the attributes of the variable
#dir(v)
#useful to know for interactive development

###############
#attempt to read out all points within a single 3
# dimensional numpy array
################

#loop over the var_names dictionary and write each variable to the
#target xml file as a variable

varx = 'd2m' #we are only processing d2m in this extractor
var_object = var_names[varx]
########
#Declare attributes for parameter
########
var_name = var_object.long_name  #long name
short_name = varx    #short name
missing_value = str(var_object.missing_value[0])  #missing value as string
fill_value = str(var_object._FillValue[0])  # fill value as string
units = var_object.units



################
#Transforming the reading values using the add_offset
# and scale_factor attributes of the variable being processed
# we are going to apply the scale FIRST then ADD the offset value
# we shall also ignore any _FillValue s.
################
scaleFactor = float(f.variables[varx].scale_factor) #must apply the scale factor to the resulting reading
offSet = float(var_object.add_offset) #this value must be added to the final reading value.
fillValue = float(var_object._FillValue)  #this will be used in comparison later on in the code
################




print "Processing..."
print "Long Name: "+var_name
#print "Short Name: "+short_name
#print "MIssing Value: "+missing_value
#print "Units: " + units
#print "Fill Value: " + fill_value
v = f.variables[varx]
time_range = range(len(v))
record_count = 0
for i in time_range:  #first block is TIME
    #print i
    if (i+1) == len(v):
        #print "LAST TIME SLOT"
        #print "len(v) is: "+ str(len(v))
        #print "i+1 is: " + str(i+1)
        record_count = record_max+1
        main_val = i
        sub = v[i]
        timex = int(time_values[i])  #read time value at index i and conver to int
        time_reading = datetime.timedelta(hours=timex)  #create timedelta for reading
        final_time = raw_time + time_reading  #makes the true time the reading was taken
        time_split = str(final_time).split('-')
        timex_split = time_split[2].split(':')
        timet_split = timex_split[0].split()
        #Fully split and re-assembled ISO time format
        iso_time = time_split[0]+time_split[1]+timet_split[0]+'T'+timet_split[1]+timex_split[1]+timex_split[2]+'Z'
        print "Last Block Variable Name is "+varx+" and ISOTime is "+iso_time
        for x in range(len(sub)):    #second block is LATITUDE
            sub_val = x
            sub_sub = sub[x]
            latitude = lat_values[x]
            lon_count=1
            #print "Latitude is "+str(latitude)        
            for b in range(len(sub_sub)):  #third block is LONGITUDE
                sub_sub_val = b
                reading = sub_sub[b]
                if (reading != fillValue):
                    reading = (reading * scaleFactor) + offSet
                longitude = lon_values[b]
                if (longitude > 180):
                    longitude = longitude-360
                cas_val_complete = str(latitude)+','+str(longitude)+',0,'+str(iso_time)+','+str(reading)
                cas_value_out = cas_val_start+cas_val_complete+cas_val_end
                record_count = record_count+1
                #print "Record count is"+str(record_count)
                #final output is (lat, lon, vertical,time,value) vertical is hard coded as 0 for ERA
                # surface readings dataset
                cas_met.write(cas_value_out)   
        cas_met.write(cas_keyval_end)
        cas_met.write(cas_footer)
        cas_met.close()
        #print cas_val_complete
        #print "EOF"
    else:
        #print "bottom loop"
        if record_count < record_max:
            if met_out_counter == 0:
                ########################################
                #open the target xml file and write in the xml header###
                ########################################
                #open the output file in write mode (hence the 'w' param)
                cas_met = open(target_output+'/'+met_out_filename, "w")
                cas_met.write(cas_xml)
                print "writing out to "+str(met_out_filename)+"...."
                #write the dataset information into the file
                cas_met.write(cas_key_start+'dataset_id'+cas_key_end)
                cas_met.write(cas_val_start+dataset_id+cas_val_end+cas_keyval_end)      
                #initial declaration and writing of the keyval and key tags
                #cas_variables = cas_key_start+'param_'cas_var+cas_key_end
                #cas_met.write(cas_variables)
                cas_met.write(cas_key_start+'granule_filename'+cas_key_end)
                cas_met.write(cas_val_start+filename+cas_val_end+cas_keyval_end)
                cas_var_keys = cas_key_start+'param_'+varx+cas_key_end
                cas_met.write(cas_var_keys)
                cas_title = cas_val_start+var_name+cas_val_end+cas_keyval_end
                cas_met.write(cas_title)
                cas_data_keys = cas_key_start+'data_'+varx+cas_key_end
                cas_met.write(cas_data_keys)
                met_out_counter = met_out_counter +1
                met_out_id = met_out_id +1
                # redefine met_out_filename with new id
                met_out_filename = filename+'.'+str(met_out_id)+'.met'
            #Do all the work within each time block
            #link each variables to v for data extraction
            var_count = 1  #need for mid file variable change
            main_val = i
            sub = v[i]
            timex = int(time_values[i])  #read time value at index i and conver to int
            time_reading = datetime.timedelta(hours=timex)  #create timedelta for reading
            final_time = raw_time + time_reading  #makes the true time the reading was taken
            time_split = str(final_time).split('-')
            timex_split = time_split[2].split(':')
            timet_split = timex_split[0].split()
            #Fully split and re-assembled ISO time format
            iso_time = time_split[0]+time_split[1]+timet_split[0]+'T'+timet_split[1]+timex_split[1]+timex_split[2]+'Z'
            #print "Variable Name is "+varx+" and ISOTime is "+iso_time
            for x in range(len(sub)):    #second block is LATITUDE
                sub_val = x
                sub_sub = sub[x]
                latitude = lat_values[x]
                lon_count=1
                #print "Latitude is "+str(latitude)        
                for b in range(len(sub_sub)):  #third block is LONGITUDE
                    sub_sub_val = b
                    reading = sub_sub[b]
                    #print "Reading is " +str(reading)+" before we apply the transformation"
                    if (reading != fillValue):
                        reading = (reading * scaleFactor) + offSet
                    #print "Transformed Reading is now "+str(reading)+" which should have the computation completed"
                    longitude = lon_values[b]
                    if (longitude > 180):
                        longitude = longitude-360
                    cas_val_complete = str(latitude)+','+str(longitude)+',0,'+str(iso_time)+','+str(reading)
                    cas_value_out = cas_val_start+cas_val_complete+cas_val_end
                    record_count = record_count+1
                    #print "Record count is"+str(record_count)
                    #final output is (lat, lon, vertical,time,value) vertical is hard coded as 0 for ERA
                    # surface readings dataset
                    cas_met.write(cas_value_out)
        else:  #Process the last block of time.  Then reset all counters to start the
            #process over again for next met file
            #Do all the work within each time block
            #link each variables to v for data extraction
            var_count = 1  #need for mid file variable change
            main_val = i
            sub = v[i]
            timex = int(time_values[i])  #read time value at index i and conver to int
            time_reading = datetime.timedelta(hours=timex)  #create timedelta for reading
            final_time = raw_time + time_reading  #makes the true time the reading was taken
            time_split = str(final_time).split('-')
            timex_split = time_split[2].split(':')
            timet_split = timex_split[0].split()
            #Fully split and re-assembled ISO time format
            iso_time = time_split[0]+time_split[1]+timet_split[0]+'T'+timet_split[1]+timex_split[1]+timex_split[2]+'Z'
            #print "ELSE Block Variable Name is "+varx+" and ISOTime is "+iso_time
            for x in range(len(sub)):    #second block is LATITUDE
                sub_val = x
                sub_sub = sub[x]
                latitude = lat_values[x]
                lon_count=1
                #print "Latitude is "+str(latitude)        
                for b in range(len(sub_sub)):  #third block is LONGITUDE
                    sub_sub_val = b
                    reading = sub_sub[b]
                    if (reading != fillValue):
                        reading = (reading * scaleFactor) + offSet
                    longitude = lon_values[b]
                    if (longitude > 180):
                        longitude = longitude-360
                    cas_val_complete = str(latitude)+','+str(longitude)+',0,'+str(iso_time)+','+str(reading)
                    cas_value_out = cas_val_start+cas_val_complete+cas_val_end
                    record_count = record_count+1
                    #print "Record count is"+str(record_count)
                    #final output is (lat, lon, vertical,time,value) vertical is hard coded as 0 for ERA
                    # surface readings dataset
                    cas_met.write(cas_value_out)   
            met_out_counter = 0
            record_count = 0
            cas_met.write(cas_keyval_end)
            cas_met.write(cas_footer)
            cas_met.close()
            print "File "+str(met_out_filename)+" starting next....."
        







