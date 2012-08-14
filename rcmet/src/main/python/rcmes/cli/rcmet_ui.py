#!/usr/local/bin/python
""" 
    Step by Step Wizard that demonstrates how the underlying RCMES code can
    be used to generate climate dataset intercomparisons
"""
# Empty dictionaries to collect all of the user's inputs 
options = {}
mask = {}
model = {}
params = {}
settings = {}

def rcmet_ui():
  ###################################################################################################
  #
  # Command Line User interface for RCMET.
  # Collects user options then runs RCMET to perform processing.
  # 
  # Duplicates job of GUI.
  #
  # Peter Lean   March 2011
  #
  ###################################################################################################
  
  # Native Python Module Imports
  import glob
  import datetime
  import time
  import sys

  # RCMES Imports
  import rcmes.files
  import rcmes.process
  import do_rcmes_processing_sub
  from rcmes import RCMED

  print 'Regional Climate Model Evaluation System BETA'


  print "Establishing a connection to RCMED.."
  try:
      database = RCMED()
  except:
      sys.exit()


  ###################################################################################################
  # Section 0: Collect directories to store RCMET working files.
  ###################################################################################################
  settings['work_dir'] = raw_input('Please enter workdir:\n> ')   # This is where the images are created/stored
  settings['cache_dir'] = raw_input('Please enter cachedir:\n> ') # This is where the database cache files are stored

  ###################################################################################################
  # Section 1a: Enter model file/s
  ###################################################################################################
  filelist_instructions = raw_input('Please enter model file (or specify multiple files using wildcard):\n> ')
  settings['file_list'] = glob.glob(filelist_instructions)

  ###################################################################################################
  # Section 1b (i): 
  #     Attempt to auto-detect latitude and longitude variable names
  #     and lat,lon limits from first file in settings['file_list'] 
  ###################################################################################################
  status, model['lat_variable'], model['lon_variable'], params['lat_min'], params['lat_max'], params['lon_min'], params['lon_max'], var_name_list = rcmes.files.find_latlon_var_from_file(settings['file_list'])

  ###################################################################################################
  # Section 1b (ii)
  #     If unable to auto-detect latitude and longitude variables from file,
  #     then ask user to select from which variable corresponds to latitude and
  #     which corresponds to longitude (from a list of available variables in the file).  
  ###################################################################################################
  if status==0:
        print 'Could not find latitude and longitude data in the file.'
        counter = 0
        for myvar in var_name_list:
           print '[',counter,']',myvar
           counter += 1

        user_var_choice = raw_input('Please help, by selecting which of the above variables in the file is the latitude variable:\n (or if the latitudes and longitudes are stored in a separate file enter "z")\n> ').lower()

        if user_var_choice == 'z':
                lat_filename_instructions = raw_input('Please enter the full path of the file containing the latitudes and longitudes:\n> ')
                latlon_filelist = glob.glob(lat_filename_instructions)
                status, model['lat_variable'], model['lon_variable'], params['lat_min'], params['lat_max'], params['lon_min'], params['lon_max'], new_var_name_list = rcmes.files.find_latlon_var_from_file(latlon_filelist)

        ##################################################
        # Section 1b (iii)
        ##################################################
        if user_var_choice != 'z':
          try:
            model['lat_variable'] = var_name_list[int(user_var_choice)]
          except:
            model['lat_variable'] = var_name_list[int(raw_input('Are you sure? The previous selection did not work, please try again:\n> '))]

          try:
            model['lon_variable'] = var_name_list[int(raw_input('..and which of the above variables is the longitude variable?\n> '))]
          except:
            model['lon_variable'] = var_name_list[int(raw_input('Are you sure? The previous selection did not work, please try again:\n> '))]

          # Find lat/lon ranges by loading the data using the user supplied variable names
          params['lat_min'],params['lat_max'], params['lon_min'], params['lon_max'] = rcmes.files.find_latlon_ranges(settings['file_list'], lat_var_name, lon_var_name) 


  print 'Found latitude and longitude variables in model data files: '
  print 'Lat/Lon variable names : ',model['lat_variable'], model['lon_variable']
  print 'Minimum Latitude: ',params['lat_min']
  print 'Maximum Latitude: ',params['lat_max']
  print 'Minimum Longitude: ',params['lon_min']
  print 'Maximum Longitude: ',params['lon_max']

  ###################################################################################################
  # Section 1c (i) Attempt to auto-detect the time variable in the file.
  #     NB. name of time variable needs to passed into RCMET.
  ###################################################################################################
  status, model['time_variable'], var_name_list = rcmes.files.find_time_var_name_from_file(settings['file_list'])

  print 'Found time variable name :',model['time_variable']
  if status==0:
        print 'Could not find time data in the file.'
        counter = 0
        for myvar in var_name_list:
           print '[',counter,']',myvar
           counter += 1

        try:
           model['time_variable'] = var_name_list[int(raw_input('Please help, by selecting which of the above variables in the file is the time variable:\n> '))]
        except:
           model['time_variable'] = var_name_list[int(raw_input('There was a problem with your selection, please try again:\n> '))]

  ###################################################################################################
  # Section 1c (ii): Attempt to decode model times into a python datetime object.
  ###################################################################################################
  try:
    modelTimes = rcmes.process.decode_model_times(settings['file_list'],model['time_variable'])
    modelStartTime = min(modelTimes)
    modelEndTime = max(modelTimes)

    print 'Model times decoded:'
    print 'First model time : ',modelStartTime.strftime("%Y/%m/%d %H:%M")
    print 'Last model time : ', modelEndTime.strftime("%Y/%m/%d %H:%M")
  except:
    print 'Error: there was a problem decoding the model times.'

  ###################################################################################################
  # Section 2a: Select which model variable to use for evaluation (from list of variables in file)
  ###################################################################################################
  counter = 0
  for myvar in var_name_list:
      print '[',counter,']',myvar
      counter += 1

  user_var_choice = raw_input('Which variable would you like to evaluate?\n> ')
  try:
    model['var_name'] = var_name_list[int(user_var_choice)]
  except:
    user_var_choice = raw_input('There was a problem with that selection, please try again:\n> ')    
    model['var_name'] = var_name_list[int(user_var_choice)]

  ###################################################################################################
  # Ask user if the above variable is precipitation data 
  # (as this needs some special treatment by RCMET, e.g. color tables, unit conversion etc)
  ###################################################################################################
  options['precip'] = False
  precip_choice = raw_input('Is this precipitation data? [y/n]\n> ').lower()
  if precip_choice=='y':
        options['precip'] = True

  ###################################################################################################
  # Section 3a: Select observation dataset from database
  ###################################################################################################


  ###################################################################################################
  # META DATA API GOES HERE! HARD CODED HERE FOR NOW. 
  # (WILL EVENTUALLY BE PICKED UP DYNAMICALLY FROM DATABASE)
  
  parameters = database.params
  
  # db_datasets = ['TRMM','ERA-Interim','AIRS','MODIS','URD','CRU']
  # replace with list comprehension
  db_datasets = [parameter['longName'] for parameter in parameters]
  
  
  # db_dataset_ids = [3,1,2,5,4,6]
  # db_dataset_startTimes = [datetime.datetime(1998,1,1,0,0,0,0),datetime.datetime(1989,01,01,0,0,0,0),datetime.datetime(2002,8,31,0,0,0,0),datetime.datetime(2000,2,24,0,0,0,0),datetime.datetime(1948,1,1,0,0,0,0),datetime.datetime(1901,1,1,0,0,0,0)]
  # db_dataset_endTimes = [datetime.datetime(2010,1,1,0,0,0,0),datetime.datetime(2009,12,31,0,0,0,0),datetime.datetime(2010,1,1,0,0,0,0),datetime.datetime(2010,5,30,0,0,0,0),datetime.datetime(2010,1,1,0,0,0,0),datetime.datetime(2006,12,1,0,0,0,0)]

  db_parameters = [['daily precip','monthly precip'],['2m temp','2m dew point'],['2m temp'],['cloud fraction'],['precip'],['tavg','tmax','tmin','precip']]

  # db_parameter_ids = [[14,36],[12,13],[15],[31],[30],[33,34,35,32]]
  db_parameter_ids = [parameter['parameter_id'] for parameter in parameters]

  # Not sure this is needed anymore since we have a parameters list object to work with
  db_dataset_ids = [parameter['dataset_id'] for parameter in parameters]
  
  try:
      db_dataset_startTimes = [datetime.datetime.strptime(parameter['start_date'], '%Y-%m-%d') for parameter in parameters]
  except:
      print "Error parsing the start dates from RCMED. Expected Format 'YYYY-MM-DD'"
  
  try:
      db_dataset_endTimes = [datetime.datetime.strptime(parameter['end_date'], '%Y-%m-%d') for parameter in parameters]
  except:
      print "Error parsing the end dates from RCMED. Expected Format 'YYYY-MM-DD'" 

  db_parameters = [parameter['dataset_id'] for parameter in parameters]
  
  
  
  # META DATA API GOES HERE!
  ###################################################################################################


  ###################################################################################################
  # Section 3b: Select Dataset from list
  ###################################################################################################
  """
  counter = 0
  for dataset in db_datasets:
     print '[',counter,'] ',dataset
     counter += 1
  REPLACED WITH THIS"""
  for parameter in parameters:
      """( 38 ) - CRU3.1 Daily-Mean Temperature : monthly"""
      print "({:^2}) - {:<35} :: {:<10}".format(parameter['parameter_id'], parameter['longName'], parameter['timestep'])

  try:
    dataset_choice = int(raw_input('Please select which observational dataset you wish to compare against:\n> ')) 
    selection = next((p for p in parameters if p['parameter_id'] == dataset_choice), None)
    params['obs_dataset_id'] = selection['dataset_id']
    obsStartTime = datetime.datetime.strptime(selection['start_date'], "%Y-%m-%d")
    obsEndTime = datetime.datetime.strptime(selection['end_date'], "%Y-%m-%d")
    params['obs_param_id'] = selection['parameter_id']
    #params['obs_dataset_id'] = db_dataset_ids[int(dataset_choice)]
    #obsStartTime = db_dataset_startTimes[int(dataset_choice)]
    #obsEndTime = db_dataset_endTimes[int(dataset_choice)]

  except:
    dataset_choice = raw_input('There was a problem with your selection, please try again:\n> ') 
    selection = next((p for p in parameters if p['parameter_id'] == dataset_choice), None)
    params['obs_dataset_id'] = selection['dataset_id']
    obsStartTime = datetime.datetime.strptime(selection['start_date'], "%Y-%m-%d")
    obsEndTime = datetime.datetime.strptime(selection['end_date'], "%Y-%m-%d")
    params['obs_param_id'] = selection['parameter_id']
    #params['obs_dataset_id'] = db_dataset_ids[int(dataset_choice)]
    #obsStartTime = db_dataset_startTimes[int(dataset_choice)]
    #obsEndTime = db_dataset_endTimes[int(dataset_choice)]


  """ This Section has been removed.  In the previous step the DataSet
  ###################################################################################################
  # Section 3c: Select Parameter from list of available parameters in dataset (selected above)
  ###################################################################################################
  
   
  AND Parameter are Selected at the sametime.  These variables have been
  declared in that section
   
  counter = 0
  for parameter in db_parameters[int(dataset_choice)]:
     print '[',counter,'] ',parameter
     counter += 1

  try:
    params['obs_param_id'] = db_parameter_ids[int(dataset_choice)][int(raw_input('Please select a parameter:\n> '))]
  except:
    params['obs_param_id'] = db_parameter_ids[int(dataset_choice)][int(raw_input('There was a problem with your selection, please try again:\n> '))]
  """

  ###################################################################################################
  # Section 4: Select time range to evaluate (defaults to overlapping times between model and obs)
  ###################################################################################################

  # Calculate overlap
  params['start_time'] = max(modelStartTime, obsStartTime)
  params['end_time'] = min(modelEndTime, obsEndTime)

  print 'Model time range: ',modelStartTime.strftime("%Y/%m/%d %H:%M"),modelEndTime.strftime("%Y/%m/%d %H:%M")
  print 'Obs time range: ',obsStartTime.strftime("%Y/%m/%d %H:%M"), obsEndTime.strftime("%Y/%m/%d %H:%M")
  print 'Overlapping time range: ',params['start_time'].strftime("%Y/%m/%d %H:%M"), params['end_time'].strftime("%Y/%m/%d %H:%M")

  # If want sub-selection then enter start and end times manually
  choice = raw_input('Do you want to only evaluate data from a sub-selection of this time range? [y/n]\n> ').lower()
  if choice=='y':
      startTime_string = raw_input('Please enter the start time in the format YYYYMMDDHHmm:\n> ')
      try:
         params['start_time'] = datetime.datetime(*time.strptime(startTime_string, "%Y%m%d%H%M")[:6])
      except:
         print 'There was a problem with your entry'

      endTime_string = raw_input('Please enter the end time in the format YYYYMMDDHHmm:\n> ')
      try:
         params['end_time'] = datetime.datetime(*time.strptime(endTime_string, "%Y%m%d%H%M")[:6])
      except:
         print 'There was a problem with your entry'

      print 'Selected time range: ',params['start_time'].strftime("%Y/%m/%d %H:%M"), params['end_time'].strftime("%Y/%m/%d %H:%M")
  
  ###################################################################################################
  # Section 5: Select Spatial Regridding options
  ###################################################################################################
  print 'Spatial regridding options: '
  print '[0] Use Observational grid'
  print '[1] Use Model grid'
  print '[2] Define new regular lat/lon grid to use'
  try:
     options['regrid'] = int(raw_input('Please make a selection from above:\n> '))
  except:
     options['regrid'] = int(raw_input('There was a problem with your selection, please try again:\n> '))

  if options['regrid']>2:
    try:
     options['regrid'] = int(raw_input('That was not an option, please make a selection from the list above:\n> '))
    except:
     options['regrid'] = int(raw_input('There was a problem with your selection, please try again:\n> '))

  if options['regrid']==0:
    options['regrid'] = 'obs'

  if options['regrid']==1:
    options['regrid'] = 'model'

  # If requested, get new grid parameters
  if options['regrid']==2:
    options['regrid'] = 'regular'
    params['lon_min'] = float(raw_input('Please enter the longitude at the left edge of the domain:\n> '))
    params['lon_max'] = float(raw_input('Please enter the longitude at the right edge of the domain:\n> '))
    params['lat_min'] = float(raw_input('Please enter the latitude at the lower edge of the domain:\n> '))
    params['lat_max'] = float(raw_input('Please enter the latitude at the upper edge of the domain:\n> '))
    dLon = float(raw_input('Please enter the longitude spacing (in degrees) e.g. 0.5:\n> '))
    dLat = float(raw_input('Please enter the latitude spacing (in degrees) e.g. 0.5:\n> '))

  ###################################################################################################
  # Section 6: Select Temporal Regridding Options, e.g. average daily data to monthly.
  ###################################################################################################
  print 'Temporal regridding options: i.e. averaging from daily data -> monthly data'
  print 'The time averaging will be performed on both model and observational data.'
  print '[0] Calculate time mean for full period.'
  print '[1] Calculate annual means'
  print '[2] Calculate monthly means'
  print '[3] Calculate daily means (from sub-daily data)'

  try:
     options['time_regrid'] = int(raw_input('Please make a selection from above:\n> '))
  except:
     options['time_regrid'] = int(raw_input('There was a problem with your selection, please try again:\n> '))

  if options['time_regrid']>3:
    try:
     options['time_regrid'] = int(raw_input('That was not an option, please make a selection from above:\n> '))
    except:
     options['time_regrid'] = int(raw_input('There was a problem with your selection, please try again:\n> '))

  if options['time_regrid']==0:
        options['time_regrid']='full'

  if options['time_regrid']==1:
        options['time_regrid']='annual'

  if options['time_regrid']==2:
        options['time_regrid']='monthly'

  if options['time_regrid']==3:
        options['time_regrid']='daily'

  ###################################################################################################
  # Section 7: Select whether to perform Area-Averaging over masked region
  ###################################################################################################
  options['mask'] = False
  mask['lon_min'] = 0
  mask['lon_max'] = 0
  mask['lat_min'] = 0
  mask['lat_max'] = 0

  choice = raw_input('Do you want to calculate area averages over a masked region of interest? [y/n]\n> ').lower()
  if choice == 'y':
     options['mask'] = True
     print '[0] Load spatial mask from file.'
     print '[1] Enter regular lat/lon box to use as mask.'

     try:
         maskInputChoice = int(raw_input('Please make a selection from above:\n> '))
     except:
         maskInputChoice = int(raw_input('There was a problem with your selection, please try again:\n> '))

     if maskInputChoice>1:
       try:
         maskInputChoice = int(raw_input('That was not an option, please make a selection from above:\n> '))
       except:
         maskInputChoice = int(raw_input('There was a problem with your selection, please try again:\n> '))

     # Section 7a
     # Read mask from file
     if maskInputChoice==0:
        maskFile = raw_input('Please enter the file containing the mask data (including full path):\n> ')
        maskFileVar = raw_input('Please enter variable name of the mask data in the file:\n> ')


     # Section 7b
     # User enters mask region manually
     if maskInputChoice==1:
        mask['lon_min'] = float(raw_input('Please enter the longitude at the left edge of the mask region:\n> '))
        mask['lon_max'] = float(raw_input('Please enter the longitude at the right edge of the mask region:\n> '))
        mask['lat_min'] = float(raw_input('Please enter the latitude at the lower edge of the mask region:\n> '))
        mask['lat_max'] = float(raw_input('Please enter the latitude at the upper edge of the mask region:\n> '))

  ###################################################################################################
  # Section 8: Select whether to calculate seasonal cycle composites
  ###################################################################################################
  options['seasonal_cycle'] = raw_input('Seasonal Cycle: do you want to composite the data to show seasonal cycles? [y/n]\n> ').lower()
  if options['seasonal_cycle'] == 'y':
        options['seasonal_cycle'] = True
  else:
        options['seasonal_cycle'] = False
    
  ###################################################################################################
  # Section 9: Select Peformance Metric
  ###################################################################################################
  print 'Metric options'
  print '[0] Bias: mean bias across full time range'
  print '[1] Mean Absolute Error: across full time range'
  print '[2] Difference: calculated at each time unit'
  print '[3] Anomaly Correlation Timeseries> '
  print '[4] Pattern Correlation Timeseries> '
  print '[5] Probability Distribution Function similarity score'
  print '[6] RMS error'
  print '[7] Coefficient of Efficiency'
  print '[8] Standard deviation'  
  print '[9] new Anomaly Correlation'  
  choice = int(raw_input('Please make a selection from the options above\n> '))
  if choice==0:
      options['metric'] = 'bias'
  if choice==1:
      options['metric'] = 'mae'
  if choice==2:
      options['metric'] = 'difference'
  if choice==3:
      options['metric'] = 'acc'
  if choice==4:
      options['metric'] = 'patcor'
  if choice==5:
      options['metric'] = 'pdf'
  if choice==6:
      options['metric'] = 'rms'
  if choice==7:
      options['metric'] = 'coe'
  if choice==8:
      options['metric'] = 'stddev'
  if choice==9:
      options['metric'] = 'nacc'
   ###################################################################################################
  # Section 11: Select Plot Options
  ###################################################################################################
  modifyPlotOptions = raw_input('Do you want to modify the default plot options? [y/n]\n> ').lower()

  options['plot_title'] = 'default'
  options['plot_filename'] = 'default'

  if modifyPlotOptions=='y':
     options['plot_title'] = raw_input('Please enter the plot title:\n> ')
     options['plot_filename'] = raw_input('Please enter the filename stub to use, without suffix e.g. files will be named <YOUR CHOICE>.png\n> ')

  ###################################################################################################
  # Section 13: Run RCMET, passing in all of the user options
  ###################################################################################################
  print 'Running RCMET....'

  do_rcmes_processing_sub.do_rcmes( settings, params, model, mask, options )



#####################################################################################################
#####################################################################################################
#####################################################################################################

#####################################################################################################
# Actually call the UI function.
#####################################################################################################

rcmet_ui()

