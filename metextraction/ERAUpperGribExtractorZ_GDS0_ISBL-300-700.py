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
# all time elements are expressed in hours from 1800-01-01 00:00:0
raw_time = datetime.datetime(1800,1,1)

#target file path must be passed as the first command line arg
#target_filename = '/Users/cgoodale/upr.Apr1989.grib'
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
lon = f.variables['g0_lon_3']
lon_values = lon.get_value()

#this reads out the latitude values
lat = f.variables['g0_lat_2']
lat_values = lat.get_value()

#declare where time is stored
time = f.variables['initial_time0_hours']
time_values = time.get_value()

#declare the pressure levels
level = f.variables['lv_ISBL1']
level_values=level.get_value()

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

varx = 'Z_GDS0_ISBL' #we are only processing T_GDS0_ISBL in this extractor
var_object = var_names[varx]
########
#Declare attributes for parameter
########
var_name = var_object.long_name  #long name
short_name = varx    #short name
fill_value = str(var_object._FillValue[0])  # fill value as string
units = var_object.units
print "Processing..."
print "Long Name: "+var_name
#print "Short Name: "+short_name
#print "Units: " + units
print "Fill Value: " + fill_value
v = f.variables[varx]
time_range = range(len(v))
record_count = 0
for i in time_range:  #first block is TIME
    print i
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
        ######################
        #MAIN CODE LOOPING BLOCK#
        ######################
        
        for l in range(len(sub)):   #second block is Level
            sub_lvl = sub[l]
            pressure_level = level_values[l]
            #print "Pressure Level is: "+str(pressure_level)
            if str(pressure_level) in ['300','700']:   #Only grab levels 300 or 700
                #print "Found Pressure LEVELS!"
                for x in range(len(sub_lvl)):    #third block is LATITUDE
                    sub_val = x
                    sub_sub = sub_lvl[x]
                    latitude = lat_values[x]
                    lon_count=1
                    #print "Latitude is "+str(latitude)        
                    for b in range(len(sub_sub)):  #fourth block is LONGITUDE
                        sub_sub_val = b
                        reading = sub_sub[b]
                        longitude = lon_values[b]
                        if (longitude > 180):
                            longitude = longitude-360
                        cas_val_complete = str(latitude)+','+str(longitude)+','+str(pressure_level)+','+str(iso_time)+','+str(reading)
                        cas_value_out = cas_val_start+cas_val_complete+cas_val_end
                        record_count = record_count+1
                        #print "Record count is"+str(record_count)
                        #final output is (lat, lon, vertical,time,value) 
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

            ######################
            #MAIN CODE LOOPING BLOCK#
            ######################
            
            for l in range(len(sub)):   #second block is Level
                sub_lvl = sub[l]
                pressure_level = level_values[l]
                #print "Pressure Level is: "+str(pressure_level)
                if str(pressure_level) in ['300','700']:   #Only grab levels 300 or 700
                    #print "Found Pressure LEVELS!"
                    for x in range(len(sub_lvl)):    #third block is LATITUDE
                        sub_val = x
                        sub_sub = sub_lvl[x]
                        latitude = lat_values[x]
                        lon_count=1
                        #print "Latitude is "+str(latitude)        
                        for b in range(len(sub_sub)):  #fourth block is LONGITUDE
                            sub_sub_val = b
                            reading = sub_sub[b]
                            longitude = lon_values[b]
                            if (longitude > 180):
                                longitude = longitude-360
                            cas_val_complete = str(latitude)+','+str(longitude)+','+str(pressure_level)+','+str(iso_time)+','+str(reading)
                            cas_value_out = cas_val_start+cas_val_complete+cas_val_end
                            record_count = record_count+1
                            #print "Record count is"+str(record_count)
                            #final output is (lat, lon, vertical,time,value) 
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
            ######################
            #MAIN CODE LOOPING BLOCK#
            ######################
            
            for l in range(len(sub)):   #second block is Level
                sub_lvl = sub[l]
                pressure_level = level_values[l]
                #print "Pressure Level is: "+str(pressure_level)
                if str(pressure_level) in ['300','700']:   #Only grab levels 300 or 700
                    #print "Found Pressure LEVELS!"
                    for x in range(len(sub_lvl)):    #third block is LATITUDE
                        sub_val = x
                        sub_sub = sub_lvl[x]
                        latitude = lat_values[x]
                        lon_count=1
                        #print "Latitude is "+str(latitude)        
                        for b in range(len(sub_sub)):  #fourth block is LONGITUDE
                            sub_sub_val = b
                            reading = sub_sub[b]
                            longitude = lon_values[b]
                            if (longitude > 180):
                                longitude = longitude-360
                            cas_val_complete = str(latitude)+','+str(longitude)+','+str(pressure_level)+','+str(iso_time)+','+str(reading)
                            cas_value_out = cas_val_start+cas_val_complete+cas_val_end
                            record_count = record_count+1
                            #print "Record count is"+str(record_count)
                            #final output is (lat, lon, vertical,time,value) 
                            # surface readings dataset
                            cas_met.write(cas_value_out)
            met_out_counter = 0
            record_count = 0
            cas_met.write(cas_keyval_end)
            cas_met.write(cas_footer)
            cas_met.close()
            print "File "+str(met_out_filename)+" starting next....."
        







