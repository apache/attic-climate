# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

import curses
import sys
import os
import numpy as np
import numpy.ma as ma
import getpass
import urllib2
import json

from netCDF4 import Dataset
from datetime import datetime, timedelta

import ocw.metrics as metrics
import ocw.plotter as plotter
import ocw.dataset_processor as dsp
import ocw.evaluation as evaluation
import ocw.data_source.rcmed as rcmed
from ocw.dataset import Bounds
from ocw.data_source.local import load_file
import ocw.utils as utils
import ocw.data_source.esgf as esgf
from example_package import *

#from ocw_config_runner.configuration_writer import export_evaluation_to_config
from configuration_writer import export_evaluation_to_config

import ssl
if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

def ready_screen(page, note=""):
    ''' Generates page borders, header, footer and notification center.

    :param page: Name of current page
    :type page: string
    :param note: Notification that system returns and will be shown
         at the bottom of page
    :type note: string

    :returns: y and x as location of text on screen
    :rtype: integer
    '''

    screen.clear()
    y, x = screen.getmaxyx()
    screen.border(0)
    screen.addstr(0, x/2-len(TITLE)/2, TITLE)
    screen.addstr(y-1, x/2-len(ORGANIZATION)/2, ORGANIZATION)
    screen.addstr(y-3, 1, "Notification:")
    for each in range(1, x-1):
         screen.addstr(y-4, each, "-")
    if page == "main_menu":
         screen.addstr(y-3, x-21, "(NC) = Not complete")
         screen.addstr(y-2, x-21, "(C)  = Complete")
    if page == "settings_screen":
         for i in range(y-5):
              screen.addstr(i+1, x/2-2, ".")
    screen.addstr(y-2, 1, note)

    return y, x


def get_esgf_netCDF_file_name(esgf_dataset_id, esgf_variable):
    dataset_info = esgf._get_file_download_data(esgf_dataset_id, esgf_variable)
    netCDF_name = dataset_info[0][0].split("/")[-1]

    return netCDF_name


##############################################################
#         Manage Model Screen
##############################################################

def load_local_model_screen(header):
    '''Generates screen to be able to load local model file.
    Path to model file (netCDF) and variable name is required.

    :param header: Header of page
    :type header: string

    :returns: Notification
    :rtype: string
    '''

    ready_screen("load_local_model_screen")
    screen.addstr(1, 1, header + " > Load Local Model File ")
    screen.addstr(4, 2, "Enter model path: ")
    model_path = screen.getstr()
    try:
         netCDF_file = Dataset(model_path, 'r')
         all_netcdf_variables = [variable.encode() for variable in netCDF_file.variables.keys()]
         try:
              screen.addstr(6, 2, "Enter model variable name {0}: ".format(all_netcdf_variables))
              variable_name = screen.getstr()
              screen.addstr(7, 4, "{0}".format(netCDF_file.variables[variable_name]))
              screen.addstr(20, 2, "Confirm:")
              screen.addstr(21, 4, "0- No")
              screen.addstr(22, 4, "1- Yes")
              screen.addstr(23, 3, "Would you take this variable:")
              answer = screen.getstr()
              if answer == "0":
                   note = "WARNING: Model file cannot be added."
              elif answer == "1":
                   model_dataset = load_file(model_path, variable_name)
                   model_datasets.append(dsp.normalize_dataset_datetimes(model_dataset, model_dataset.temporal_resolution()))
                   models_info.append({'directory': model_path, 'variable_name': variable_name})
                   note = "Model file successfully added."
              else:
                   note = "WARNING: Model file cannot be added."
         except:
              note = "WARNING: Model file cannot be added. The variable [{0}] is not accepted. Please try again.".format(variable_name)
         netCDF_file.close()
    except:
         note = "WARNING: Model file cannot be read. Please check the file directory or format. Only netCDF format is accepted."

    return note


def load_esgf_model_screen(header):
    '''Generates screen to be able to load ESGF model file.

    :param header: Header of page
    :type header: string

    :returns: Notification
    :rtype: string
    '''

    ready_screen("load_esgf_model_screen")
    screen.addstr(1, 1, header + " > Download ESGF Dataset ")
    screen.addstr(6, 1, "Enter Dataset ID:")
    esgf_dataset_id = screen.getstr()
    screen.addstr(7, 1, "Enter Variable:")
    esgf_variable = screen.getstr()
    screen.addstr(8, 1, "Enter Username:")
    esgf_username = screen.getstr()
    screen.addstr(9, 1, "Enter Password:")
    esgf_password = screen.getstr()
    try:
        solr_url = "http://esg-datanode.jpl.nasa.gov/esg-search/search?id={0}&variable={1}&format=application%2Fsolr%2Bjson".format(esgf_dataset_id, esgf_variable)
        metadata_json = json.load(urllib2.urlopen(solr_url))
        if metadata_json['response']['docs'][0]["product"][0] != "observations":
            screen.addstr(11, 4, "Title: {0}".format(metadata_json['response']['docs'][0]['title']))
            screen.addstr(12, 4, "Start Date: {0}".format(metadata_json['response']['docs'][0]['datetime_start']))
            screen.addstr(13, 4, "End Date: {0}".format(metadata_json['response']['docs'][0]['datetime_stop']))
            screen.addstr(15, 2, "Confirm:")
            screen.addstr(16, 4, "0- No")
            screen.addstr(17, 4, "1- Yes")
            screen.addstr(18, 3, "Would you take this dataset:")
            answer = screen.getstr()
            if answer == "0":
                note = "WARNING: ESGF model file cannot be added."
            elif answer == "1":
                try:
                    screen.addstr(20, 4, "Downloading dataset.....")
                    screen.refresh()
                    datasets = esgf.load_dataset(esgf_dataset_id,
                                                esgf_variable,
                                                esgf_username,
                                                esgf_password)
                    netCDF_name = get_esgf_netCDF_file_name(esgf_dataset_id, esgf_variable)
                    netCDF_path = "/tmp/{0}".format(netCDF_name)
                    model_dataset = load_file(netCDF_path, esgf_variable)
                    model_datasets.append(model_dataset)
                    models_info.append({'directory': netCDF_path, 'variable_name': esgf_variable})
                    note = "Dataset successfully downloaded."
                except:
                    note = "WARNING: Dataset has not been downloaded. Check your ESGF permission."
        else:
            note = "The selected dataset is Observation, please enter model dataset."
    except:
        note = "WARNING: Something went wrong in downloading model dataset from ESGF."

    return  note


def unload_model_screen(header):
    '''Generates screen to be able to unload model file.
    It lists all loaded model with index for each.
    Selection of model with index will remove model from list of models.

    :param header: Header of page
    :type header: string

    :returns: Notification
    :rtype: string
    '''

    ready_screen("unload_model_screen")
    screen.addstr(1, 1, header + " > Unload Model File")
    screen.addstr(6, 1, "List of Model:")
    for i, model in enumerate(models_info):
         screen.addstr(8 + i, 10, "Model Number:[{0}] - Model path:[{1}] - Variables:[{2}]".format(str(i), model['directory'], model['variable_name']))
    screen.addstr(3, 2, "Select the model number to remove (press enter to go back): ")
    try:
         model_remove_index = screen.getstr()
         models_info.pop(int(model_remove_index))
         model_datasets.pop(int(model_remove_index))
         note = "Model file unloaded successfully"
    except:
         note = "WARNING: Model file not unloaded successfully."

    return note


def list_model_screen(header):
    '''Generates screen to list all model files.

    :param header: Header of page
    :type header: string
    '''

    ready_screen("list_model_screen")
    screen.addstr(1, 1, header + " > List Model File ")
    screen.addstr(6, 6, "List of model(s): ")
    for i, model in enumerate(models_info):
         screen.addstr(8 + i, 10, "Model Number:[{0}] - Model path:[{1}] - Variables:[{2}]".format(str(i), model['directory'], model['variable_name']))
    screen.addstr(4, 4, "Return to Manage Model (press Enter) :")
    screen.getstr()


def manage_model_screen(header, note=""):
    '''Generates Manage Model screen.

    :param header: Header of page
    :type header: string
    :param note: Notification, defult to empty string.
    :type note: string
    '''

    option = ''
    while option != '0':
         ready_screen("manage_model_screen", note)
         screen.addstr(1, 1, header)
         screen.addstr(4, 4, "1 - Load Local Model File")
         screen.addstr(6, 4, "2 - Load ESGF Model File")
         screen.addstr(8, 4, "3 - Unload Model File")
         screen.addstr(10, 4, "4 - List Model File")
         screen.addstr(12, 4, "0 - Return to Main Menu")
         screen.addstr(14, 2, "Select an option: ")
         screen.refresh()
         option = screen.getstr()

         if option == '1':
              note = load_local_model_screen(header)
         if option == '2':
              note = load_esgf_model_screen(header)
         if option == '3':
              note = unload_model_screen(header)
         if option == '4':
              note = list_model_screen(header)
              note = " "


##############################################################
#     Manage Observation Screen
##############################################################

def select_obs_screen(header):   #TODO: if the observation is already selected, don't select again.
    '''Generates screen to select observation.
    It reterives list of observations from database and make a table from that.
    User has to select observation with dataset_id, parameter_id.
    If the size of terminal screen is small to show whole table, a notification with link to parameter table on website will show up instead.

    :param header: Header of page
    :type header: string

    :returns: Notification
    :rtype: string
    '''

    ready_screen("select_obs_screen")
    screen.addstr(1, 1, header + " > Select Observation ")
    screen.addstr(7, 1, "Observations Table: ")
    screen.addstr(8, 2, "|D-ID| - |P-ID| - |Database")
    screen.addstr(9, 2, "|----| - |----| - |--------")
    all_obs_info = rcmed.get_parameters_metadata()
    new_all_obs_info = []
    for each in all_obs_info:
        if not each['parameter_id'] in ['72', '73', '74', '75', '80', '42', '81', '84', '85', '86', '89', '90', '91', '94', '95', '96', '97', '98', '99', '100', '101', '103', '106']:
            new_all_obs_info.append(each)
    all_obs_info = new_all_obs_info
    del new_all_obs_info
    try:
         for position, obs_info in enumerate(all_obs_info):
            dataset_id = obs_info['dataset_id']
            parameter_id = obs_info['parameter_id']
            database = obs_info['database']
            line = "|{0:>4}| - |{1:>4}| - |{2}".format(dataset_id, parameter_id, database)
            if position <= 25:
                 screen.addstr(10 + position, 2, line)
            elif position > 25 and position <= 50:
                 screen.addstr(8, 50, "|D-ID| - |P-ID| - |Database")
                 screen.addstr(9, 50, "|----| - |----| - |--------")
                 screen.addstr(10 + position - 26, 50, line)
            else:
                 screen.addstr(8, 100, "|D-ID| - |P-ID| - |Database")
                 screen.addstr(9, 100, "|----| - |----| - |--------")
                 screen.addstr(10 + position - 51, 100, line)
    except:
         ready_screen("select_obs_screen")
         screen.addstr(1, 1, header + " > Select Observation ")
         screen.addstr(10, 1, "Observation table cannot be shown due to small screen size. ")
         screen.addstr(11, 1, "Please enlarge your screen and try again or refer to 'https://rcmes.jpl.nasa.gov/content/data-rcmes-database'. ")
    try:
         screen.addstr(2, 1, "More info for observation: https://rcmes.jpl.nasa.gov/content/data-rcmes-database")
         screen.addstr(4, 2, "Enter Dataset ID (D-ID): ")
         dataset_id = screen.getstr()
         screen.addstr(5, 2, "Enter Parameter ID (P-ID): ")
         parameter_id = screen.getstr()

         for obs in all_obs_info:
              if obs['dataset_id'] == dataset_id and obs['parameter_id'] == parameter_id:
                   observations_info.append({
                        'database':obs['database'],
                        'dataset_id':dataset_id,
                        'parameter_id':parameter_id,
                        'start_date':obs['start_date'],
                        'end_date':obs['end_date'],
                        'bounding_box':obs['bounding_box'],
                        'timestep':obs['timestep'],
                        'min_lat':float(eval(obs['bounding_box'].encode())[2][0]) if obs['bounding_box'] else None,
                        'max_lat':float(eval(obs['bounding_box'].encode())[0][0]) if obs['bounding_box'] else None,
                        'min_lon':float(eval(obs['bounding_box'].encode())[2][1]) if obs['bounding_box'] else None,
                        'max_lon':float(eval(obs['bounding_box'].encode())[0][1]) if obs['bounding_box'] else None,
                        'lat_res':float(obs['lat_res'].encode()),
                        'lon_res':float(obs['lon_res'].encode()),
                        'unit':obs['units']
                        })
                   note = "Observation sucessfully selected."
                   break
              else:
                   note = "WARNING: Observation cannot be selected. There is no observation with given info."
    except:
         note = "WARNING: Observation cannot be selected, dataset or parameter id is wrong."

    return  note


def load_esgf_obs_screen(header):
    '''Generates screen to be able to load ESGF observation file.

    :param header: Header of page
    :type header: string

    :returns: Notification
    :rtype: string
    '''

    ready_screen("load_esgf_obs_screen")
    screen.addstr(1, 1, header + " > Download ESGF Dataset ")
    screen.addstr(6, 1, "Enter Dataset ID:")
    esgf_dataset_id = screen.getstr()
    screen.addstr(7, 1, "Enter Variable:")
    esgf_variable = screen.getstr()
    screen.addstr(8, 1, "Enter Username:")
    esgf_username = screen.getstr()
    screen.addstr(9, 1, "Enter Password:")
    esgf_password = screen.getstr()
    try:
        solr_url = "http://esg-datanode.jpl.nasa.gov/esg-search/search?id={0}&variable={1}&format=application%2Fsolr%2Bjson".format(esgf_dataset_id, esgf_variable)
        metadata_json = json.load(urllib2.urlopen(solr_url))
        all_variables = metadata_json['response']['docs'][0]['variable']
        variable_index = all_variables.index(esgf_variable)
        if metadata_json['response']['docs'][0]["product"][0] == "observations":
            screen.addstr(11, 4, "Variable Long Name: {0}".format(metadata_json['response']['docs'][0]['variable_long_name'][variable_index]))
            screen.addstr(12, 4, "Start Date: {0}".format(metadata_json['response']['docs'][0]['datetime_start']))
            screen.addstr(13, 4, "End Stop: {0}".format(metadata_json['response']['docs'][0]['datetime_stop']))
            screen.addstr(14, 4, "Time Frequency: {0}".format(metadata_json['response']['docs'][0]['time_frequency']))
            screen.addstr(15, 4, "Variable Units: {0}".format(metadata_json['response']['docs'][0]['variable_units'][variable_index]))
            screen.addstr(16, 4, "East Degrees: {0}".format(metadata_json['response']['docs'][0]['east_degrees']))
            screen.addstr(17, 4, "North Degrees: {0}".format(metadata_json['response']['docs'][0]['north_degrees']))
            screen.addstr(18, 4, "South Degrees: {0}".format(metadata_json['response']['docs'][0]['south_degrees']))
            screen.addstr(19, 4, "West Degrees: {0}".format(metadata_json['response']['docs'][0]['west_degrees']))
            screen.addstr(22, 2, "Confirm:")
            screen.addstr(23, 4, "0- No")
            screen.addstr(24, 4, "1- Yes")
            screen.addstr(25, 3, "Would you take this dataset:")
            answer = screen.getstr()
            if answer == "0":
                note = "WARNING: ESGF observation file cannot be added."
            elif answer == "1":
                try:
                    screen.addstr(27, 4, "Downloading dataset.....")
                    screen.refresh()
                    datasets = esgf.load_dataset(esgf_dataset_id,
                                                esgf_variable,
                                                esgf_username,
                                                esgf_password)
                    netCDF_name = get_esgf_netCDF_file_name(esgf_dataset_id, esgf_variable)
                    netCDF_path = "/tmp/{0}".format(netCDF_name)
                    obs_dataset = load_file(netCDF_path, esgf_variable)
                    observations_info.append({
                     'database':"{0}".format(netCDF_path),
                     'dataset_id':"esgf".format(esgf_variable),
                     'parameter_id':"{0}".format(esgf_variable),
                     'start_date': obs_dataset.time_range()[0].strftime("%Y-%m-%d"),
                     'end_date':obs_dataset.time_range()[1].strftime("%Y-%m-%d"),
                     #'bounding_box':obs['bounding_box'],
                     'timestep':"monthly",
                     'min_lat':obs_dataset.spatial_boundaries()[0],
                     'max_lat':obs_dataset.spatial_boundaries()[1],
                     'min_lon':obs_dataset.spatial_boundaries()[2],
                     'max_lon':obs_dataset.spatial_boundaries()[3],
                     'lat_res':obs_dataset.spatial_resolution()[0],
                     'lon_res':obs_dataset.spatial_resolution()[1],
                     'unit':"{0}".format(metadata_json['response']['docs'][0]['variable_units'][1])
                     })
                    note = "Dataset successfully downloaded."
                except:
                    note = "WARNING: Dataset has not been downloaded."
        else:
            note = "The selected dataset is not Observation, please enter observation dataset."
    except:
        note = "WARNING: Something went wrong in downloading observation dataset from ESGF."

    return  note


def unselect_obs_screen(header):
    '''Generates screen to be able to unselect observations.
    Observations can be unselected by entering index allocated to them.

    :param header: Header of page
    :type header: string

    :returns: Notification
    :rtype: string
    '''

    ready_screen("unselect_obs_screen")
    screen.addstr(1, 1, header + " > Unselect Observation ")
    screen.addstr(6, 1, "List Observation(s):")
    for i, obs_info in enumerate(observations_info):
         screen.addstr(8 + i, 10, " [" + str(i) + "] : " + " Dataset ID: " + obs_info['dataset_id'] + " - Parameter ID: "+ obs_info['parameter_id'] + " - Database: "+ obs_info['database'])
    screen.addstr(3, 2, "Select the observation to remove (press enter to go back): ")
    try:
         obs_remove_index = screen.getstr()
         observations_info.pop(int(obs_remove_index))
         note = "Observation sucessfully unselected."
    except:
         note = "WARNING: Unselecting model was not successful."

    return note


def list_obs_screen(header):
    '''Generates screen to list observations.

    :param header: Header of page
    :type header: string
    '''

    ready_screen("list_obs_screen")
    screen.addstr(1, 1, header + " > List Observation ")
    screen.addstr(6, 6, "List of observation(s): ")
    for i, obs_info in enumerate(observations_info):
         screen.addstr(8 + i, 10, " [" + str(i) + "] : " + " Dataset ID: " + obs_info['dataset_id'] + " - Parameter ID: "+ obs_info['parameter_id'] + " - Database: "+ obs_info['database'])
    screen.addstr(4, 4, "Return to Manage Observation (press Enter) :")
    screen.getstr()


def manage_obs_screen(header, note=""):
    '''Generates Manage Observation screen.

    :param header: Header of page
    :type header: string
    :param note: Notification, defult to empty string.
    :type note: string
    '''

    option = ''
    while option != '0':
         ready_screen("manage_obs_screen", note)
         screen.addstr(1, 1, header)
         screen.addstr(4, 4, "1 - Select Observation")
         screen.addstr(6, 4, "2 - Load ESGF Observation")
         screen.addstr(8, 4, "3 - Unselect Observation")
         screen.addstr(10, 4, "4 - List Observation")
         screen.addstr(12, 4, "0 - Return to Main Menu")
         screen.addstr(14, 2, "Select an option: ")
         screen.refresh()

         option = screen.getstr()
         if option == '1':
              note = select_obs_screen(header)
         if option == '2':
              note = load_esgf_obs_screen(header)
         if option == '3':
              note = unselect_obs_screen(header)
         if option == '4':
              list_obs_screen(header)
              note = " "


##############################################################
#     Run Evaluation Screen
##############################################################

def run_screen(model_datasets, models_info, observations_info,
               overlap_start_time, overlap_end_time, overlap_min_lat,
               overlap_max_lat, overlap_min_lon, overlap_max_lon,
               temp_grid_setting, spatial_grid_option, spatial_grid_setting, reference_dataset, target_datasets, metric, working_directory, plot_title):
    '''Generates screen to show running evaluation process.

    :param model_datasets: list of model dataset objects
    :type model_datasets: list
    :param models_info: list of dictionaries that contain information for each model
    :type models_info: list
    :param observations_info: list of dictionaries that contain information for each observation
    :type observations_info: list
    :param overlap_start_time: overlap start time between model and obs start time
    :type overlap_start_time: datetime
    :param overlap_end_time: overlap end time between model and obs end time
    :type overlap_end_time: float
    :param overlap_min_lat: overlap minimum lat between model and obs minimum lat
    :type overlap_min_lat: float
    :param overlap_max_lat: overlap maximum lat between model and obs maximum lat
    :type overlap_max_lat: float
    :param overlap_min_lon: overlap minimum lon between model and obs minimum lon
    :type overlap_min_lon: float
    :param overlap_max_lon: overlap maximum lon between model and obs maximum lon
    :type overlap_max_lon: float
    :param temp_grid_setting: temporal grid option such as hourly, daily, monthly and annually
    :type temp_grid_setting: string
    :param spatial_grid_setting:
    :type spatial_grid_setting: string
    :param spatial_grid_setting: user specified spatial resolution for regridding
    :type spatial_grid_setting: float   
    :param reference_dataset: dictionary of reference dataset
    :type reference_dataset: dictionary
    :param target_datasets: dictionary of all target datasets
    :type target_datasets: dictionary
    :param metric: name of selected metric
    :type metric: string
    :param working_directory: path to a directory for storring outputs
    :type working_directory: string
    :param plot_title: Title for plot
    :type plot_title: string
    '''
    try:
        target_datasets_ensemble = []
        new_model_datasets = model_datasets[:]

        option = None
        if option != "0":
             ready_screen("run_evaluation_screen")
             y = screen.getmaxyx()[0]
             screen.addstr(2, 2, "Evaluation started....")
             screen.refresh()

             screen.addstr(4, 4, "Retrieving data...")
             screen.refresh()
             obs_dataset = []
             for i in range(len(observations_info)):
                  if observations_info[i]['dataset_id'] == "esgf":
                      original_dataset = load_file(observations_info[i]['database'], observations_info[i]['parameter_id'])
                      obs_dataset.append(dsp.normalize_dataset_datetimes(original_dataset,original_dataset.temporal_resolution()))
                  else:
                      dataset_id = int(observations_info[i]['dataset_id'])
                      parameter_id = int(observations_info[i]['parameter_id'])
                      original_dataset = rcmed.parameter_dataset(
                          dataset_id,
                          parameter_id,
                          overlap_min_lat,
                          overlap_max_lat,
                          overlap_min_lon,
                          overlap_max_lon,
                          overlap_start_time,
                          overlap_end_time)
                      obs_dataset.append(dsp.normalize_dataset_datetimes(original_dataset,original_dataset.temporal_resolution()))
                          

             screen.addstr(4, 4, "--> Data retrieved.")
             screen.refresh()

             EVAL_BOUNDS = Bounds(overlap_min_lat, overlap_max_lat, overlap_min_lon, overlap_max_lon, overlap_start_time, overlap_end_time)

             screen.addstr(5, 4, "Temporally regridding...")
             screen.refresh()
             if temp_grid_setting.lower() == 'hourly':
                  days = 0.5
             elif temp_grid_setting.lower() == 'daily':
                  days = 1
             elif temp_grid_setting.lower() == 'monthly':
                  days = 31
             else:
                  days = 365
             for i in range(len(obs_dataset)):
                  obs_dataset[i] = dsp.temporal_rebin(obs_dataset[i], timedelta(days))

             for member, each_target_dataset in enumerate(new_model_datasets):
                  new_model_datasets[member] = dsp.temporal_rebin(new_model_datasets[member], timedelta(days))
                  new_model_datasets[member] = dsp.subset(EVAL_BOUNDS, new_model_datasets[member])
             screen.addstr(5, 4, "--> Temporally regridded.")
             screen.refresh()

             screen.addstr(6, 4, "Spatially regridding...")
             screen.refresh()
             if spatial_grid_option == 'Observation':
                 new_lats = obs_dataset[0].lats
                 new_lons = obs_dataset[0].lons
             else:
                 new_lats = np.arange(overlap_min_lat, overlap_max_lat, spatial_grid_setting)
                 new_lons = np.arange(overlap_min_lon, overlap_max_lon, spatial_grid_setting)
                 for i in range(len(obs_dataset)):
                      obs_dataset[i] = dsp.spatial_regrid(obs_dataset[i], new_lats, new_lons)

             for member, each_target_dataset in enumerate(new_model_datasets):
                  new_model_datasets[member] = dsp.spatial_regrid(new_model_datasets[member], new_lats, new_lons)
             screen.addstr(6, 4, "--> Spatially regridded.")
             screen.refresh()

             masked_dataset = dsp.mask_missing_data(obs_dataset + new_model_datasets) 
             obs_dataset = masked_dataset[0:len(obs_dataset)]
             new_model_dataset = masked_dataset[len(obs_dataset):]

             screen.addstr(7, 4, "Calculating multiyears climatology...")
             screen.refresh()
             for i in range(len(obs_dataset)):
                 obs_dataset[i] = dsp.variable_unit_conversion(obs_dataset[i])
                 obs_dataset[i].values = utils.calc_temporal_mean(dsp.temporal_subset(month_start=1, month_end=12, target_dataset=obs_dataset[i]))
                 obs_dataset[i].values = ma.expand_dims(obs_dataset[i].values, axis=0)

             for member, each_target_dataset in enumerate(new_model_datasets):
                 new_model_datasets[member] = dsp.variable_unit_conversion(new_model_datasets[member])
                 new_model_datasets[member].values = utils.calc_temporal_mean(dsp.temporal_subset(month_start=1, month_end=12, target_dataset=new_model_datasets[member]))
                 new_model_datasets[member].values = ma.expand_dims(new_model_datasets[member].values, axis=0) 

             screen.addstr(7, 4, "Multiyears climatology calculated.")
             screen.refresh()

             if not os.path.exists(working_directory):
                 os.makedirs(working_directory)
             screen.addstr(8, 4, "Calculating metrics, "+metric+", and generating a plot")
             screen.refresh()
             if metric == 'bias_of_multiyear_climatology':
                 row = 1
                 column = 2
                 Map_plot_bias_of_multiyear_climatology(obs_dataset[0], 'obs. climatology', new_model_datasets, ['model_bias'],
                                     working_directory+'obs_and_bias_contour', row, column) 
             if metric == 'comparing_spatial_patterns_of_multiyear_climatology':
                 Taylor_diagram_spatial_pattern_of_multiyear_climatology(obs_dataset[0], 'obs.', new_model_datasets, ['model'],
                                      working_directory+'Taylor_diagram_spatial_pattern_of_multiyear_climatology')
             screen.addstr(9, 4, "--> Plots generated.")
             screen.refresh()
             screen.addstr(y-2, 1, "Press 'enter' to Exit: ")
             option = screen.getstr()

        del new_model_datasets
        del obs_dataset
        return "No error"
    except Exception, error:
         return "Error: {0}".format(error[0][:200])


##############################################################
#     Settings Screen
##############################################################

def get_models_temp_bound():
    '''Get models temporal bound.

    :returns: model start and end time
    :rtypes: (datatime, datetime)
    '''

    models_start_time = []
    models_end_time = []
    for model in model_datasets:
         models_start_time.append(model.time_range()[0])
         models_end_time.append(model.time_range()[1])

    return models_start_time, models_end_time


def get_obs_temp_bound():
    '''Get observation temporal bound.

    :returns: observation start and end time
    :rtype: (datetime, datetime)
    '''

    observations_start_time = []
    observations_end_time = []
    for obs in observations_info:
         obs_start_time = datetime.strptime(obs['start_date'], "%Y-%m-%d")
         observations_start_time.append(obs_start_time)
         obs_end_time = datetime.strptime(obs['end_date'], "%Y-%m-%d")
         observations_end_time.append(obs_end_time)

    return observations_start_time, observations_end_time


def get_models_temp_overlap(models_start_time, models_end_time):
    '''Calculate temporal overlap between all the models

    :param models_start_time: models start time
    :type models_start_time: list of datetimes
    :param models_end_time: models end time
    :type models_end_time: list of datetime

    :returns: overlap start and end time between all the models
    :rtype: (datetime, datetime)
    '''

    models_overlap_start_time = max(models_start_time)
    models_overlap_end_time = min(models_end_time)

    #Need to check if all models have temporal overlap, otherwise return
    # to main menu and print a warning as notification.
    if models_overlap_end_time <= models_overlap_start_time:
         main_menu(model_datasets, models_info, observation_datasets, observations_info, note="WARNING: One or more model does not have temporal overlap with others.")

    return models_overlap_start_time, models_overlap_end_time


def get_obs_temp_overlap(observations_start_time, observations_end_time):
    '''Calculate temporal overlap between all the observations

    :param observations_start_time: observations start time
    :type observations_start_time: list of datetimes
    :param observations_end_time: observations end time
    :type observations_end_time: list of datetime

    :returns: overlap start and end time between all the observations
    :rtype: (datetime, datetime)
    '''

    obs_overlap_start_time = max(observations_start_time)
    obs_overlap_end_time = min(observations_end_time)

    #Need to check if all observations have temporal overlap, otherwise return
    # to main menu and print a warning as notification.
    if obs_overlap_end_time <= obs_overlap_start_time:
         main_menu(model_datasets, models_info, observation_datasets, observations_info, note="WARNING: One or more observation does not have temporal overlap with others.")

    return obs_overlap_start_time, obs_overlap_end_time


def get_all_temp_overlap(models_overlap_start_time, models_overlap_end_time, obs_overlap_start_time, obs_overlap_end_time):
    '''Calculate temporal overlap between given datasets.

    :param models_overlap_start_time: models overlap start time
    :type models_overlap_start_time: list of datetimes
    :param models_overlap_end_time: models overlap end time
    :type models_overlap_end_time: list of datetime
    :param obs_overlap_start_time: obs overlap start time
    :type obs_overlap_start_time: list of datetimes
    :param obs_overlap_end_time: obs overlap end time
    :type obs_overlap_end_time: list of datetimes

    :returns: overlap start and end time between models and observations
    :rtype: (datetime, datetime)
    '''

    all_overlap_start_time = max([models_overlap_start_time, obs_overlap_start_time])
    all_overlap_end_time = min([models_overlap_end_time, obs_overlap_end_time])

    #Need to check if all datasets have temporal overlap, otherwise return
    # to main menu and print a warning as notification.
    if all_overlap_end_time <= all_overlap_start_time:
         main_menu(model_datasets, models_info, observation_datasets, observations_info, note="WARNING: One or more dataset does not have temporal overlap with others.")

    return all_overlap_start_time, all_overlap_end_time


def get_models_spatial_bound():               #TODO: convert longitudes to -180, 180 to match with observation data
    '''Get all models spatial bound.

    :returns: all models spatial boundaries
    :rtype: list
    '''

    models_bound = []
    for model in model_datasets:
         models_bound.append(model.spatial_boundaries())

    return models_bound


def get_models_spatial_overlap(models_bound):
    '''Calculate spatial overlap between all models.

    :param models_bound: all models spatial boundaries information
    :type models_bound: list

    :returns: spatial boundaries overlap between all models
    :rtype: (float, float, float, float)
    '''

    models_overlap_min_lat = max(each[0] for each in models_bound)
    models_overlap_max_lat = min(each[1] for each in models_bound)
    models_overlap_min_lon = max(each[2] for each in models_bound)
    models_overlap_max_lon = min(each[3] for each in models_bound)

    #Need to check if all models have spatial overlap, otherwise return
    # to main menu and print a warning as notification.
    if models_overlap_max_lat <= models_overlap_min_lat or models_overlap_max_lon <= models_overlap_min_lon:
         main_menu(model_datasets, models_info, observation_datasets, observations_info, note="WARNING: One or more model does not have spatial overlap with others.")

    return models_overlap_min_lat, models_overlap_max_lat, models_overlap_min_lon, models_overlap_max_lon


def get_obs_spatial_bound():
    '''Get all observations spatial bound.

    :returns: all observations spatial boundaries
    :rtype: list
    '''

    observations_bound = []
    for obs in observations_info:
         observations_bound.append([obs['min_lat'], obs['max_lat'], obs['min_lon'], obs['max_lon']])

    return observations_bound


def get_obs_spatial_overlap(observations_bound):
    '''Calculate spatial overlap between all observations.

    :param observations_bound: all observations spatial boundaries information
    :type observations_bound: list

    :returns: spatial boundaries overlap between all observations
    :rtype: (float, float, float, float)
    '''

    obs_overlap_min_lat = max(each[0] for each in observations_bound)
    obs_overlap_max_lat = min(each[1] for each in observations_bound)
    obs_overlap_min_lon = max(each[2] for each in observations_bound)
    obs_overlap_max_lon = min(each[3] for each in observations_bound)

    #Need to check if all observations have spatial overlap, otherwise return
    # to main menu and print a warning as notification.
    if obs_overlap_max_lat <= obs_overlap_min_lat or obs_overlap_max_lon <= obs_overlap_min_lon:
         main_menu(model_datasets, models_info, observation_datasets, observations_info, note="WARNING: One or more observation does not have spatial overlap with others.")

    return obs_overlap_min_lat, obs_overlap_max_lat, obs_overlap_min_lon, obs_overlap_max_lon


def get_all_spatial_overlap(models_overlap_min_lat, models_overlap_max_lat, models_overlap_min_lon, models_overlap_max_lon, obs_overlap_min_lat, obs_overlap_max_lat, obs_overlap_min_lon, obs_overlap_max_lon):
    '''Calculate spatial overlap between all models and observations

    :param models_overlap_min_lat: min latitude between all models
    :type models_overlap_min_lat: float
    :param models_overlap_max_lat: max latitude between all models
    :type models_overlap_max_lat: float
    :param models_overlap_min_lon: min longitude between all models
    :type models_overlap_min_lon: float
    :param models_overlap_max_lon: max longitude between all models
    :type models_overlap_max_lon: float
    :param obs_overlap_min_lat: min latitude between all onservations
    :type obs_overlap_min_lat: float
    :param obs_overlap_max_lat: max latitude between all onservations
    :type obs_overlap_max_lat: float
    :param obs_overlap_min_lon: min longitude between all onservations
    :type obs_overlap_min_lon: float
    :param obs_overlap_max_lon: max longitude between all onservations
    :type obs_overlap_max_lon: float

    :returns: spatial boundaries overlap between all models and observations
    :rtype: (float, float, float, float)
    '''

    all_overlap_min_lat = max([models_overlap_min_lat, obs_overlap_min_lat])
    all_overlap_max_lat = min([models_overlap_max_lat, obs_overlap_max_lat])
    all_overlap_min_lon = max([models_overlap_min_lon, obs_overlap_min_lon])
    all_overlap_max_lon = min([models_overlap_max_lon, obs_overlap_max_lon])

    #Need to check if all datasets have spatial overlap, otherwise return
    # to main menu and print a warning as notification.
    if all_overlap_max_lat <= all_overlap_min_lat or all_overlap_max_lon <= all_overlap_min_lon:
         main_menu(model_datasets, models_info, observation_datasets, observations_info, note="WARNING: One or more dataset does not have spatial overlap with others.")

    return all_overlap_min_lat, all_overlap_max_lat, all_overlap_min_lon, all_overlap_max_lon


def get_models_temp_res():
    '''Get models temporal resolution.

    :returns: models resolution
    :rtypes: string
    '''

    models_resolution = []
    for model in model_datasets:
         models_resolution.append(model.temporal_resolution())
    dic = {0:"hourly", 1:"daily", 2:"monthly", 3:"yearly"}
    models_resolution_key = []
    for res in models_resolution:
         for key, value in dic.items():
              if value == res:
                   models_resolution_key.append(key)

    return dic[max(models_resolution_key)]


def get_obs_temp_res():
    '''Get observations temporal resolution.

    :returns: observations resolution
    :rtypes: string
    '''

    obs_resolution = []
    for model in model_datasets:
         obs_resolution.append(model.temporal_resolution())
    dic = {0:"hourly", 1:"daily", 2:"monthly", 3:"yearly"}
    obs_resolution_key = []
    for res in obs_resolution:
         for key, value in dic.items():
              if value == res:
                   obs_resolution_key.append(key)

    return dic[max(obs_resolution_key)]


def get_models_spatial_res():
    '''Get models spatial resolution

    :returns: maximum models latitude and longitude resolution
    :rtypes: float, float
    '''

    models_lat_res = []
    models_lon_res = []
    for model in model_datasets:
         models_lat_res.append(model.spatial_resolution()[0])
         models_lon_res.append(model.spatial_resolution()[1])

    return max(models_lat_res), max(models_lon_res)


def get_obs_spatial_res():
    '''Get observations spatial resolution

    :returns: maximum observations latitude and longitude resolution
    :rtypes: float, float
    '''

    obs_lat_res = []
    obs_lon_res = []
    for obs in observations_info:
         obs_lat_res.append(obs['lat_res'])
         obs_lon_res.append(obs['lon_res'])

    return max(obs_lat_res), max(obs_lon_res)


def settings_screen(header):
    '''Generates screen for settings before running evaluation.

    :param header: Header of page
    :type header: string
    '''

    note = " "
    models_start_time, models_end_time = get_models_temp_bound()
    models_overlap_start_time, models_overlap_end_time = get_models_temp_overlap(models_start_time, models_end_time)
    observations_start_time, observations_end_time = get_obs_temp_bound()
    obs_overlap_start_time, obs_overlap_end_time = get_obs_temp_overlap(observations_start_time, observations_end_time)
    all_overlap_start_time, all_overlap_end_time = get_all_temp_overlap(models_overlap_start_time, models_overlap_end_time, obs_overlap_start_time, obs_overlap_end_time)
    models_bound = get_models_spatial_bound()
    models_overlap_min_lat, models_overlap_max_lat, models_overlap_min_lon, models_overlap_max_lon = get_models_spatial_overlap(models_bound)
    observations_bound = get_obs_spatial_bound()
    obs_overlap_min_lat, obs_overlap_max_lat, obs_overlap_min_lon, obs_overlap_max_lon = get_obs_spatial_overlap(observations_bound)
    all_overlap_min_lat, all_overlap_max_lat, all_overlap_min_lon, all_overlap_max_lon = get_all_spatial_overlap(models_overlap_min_lat,
                                                                                                                 models_overlap_max_lat,
                                                                                                                 models_overlap_min_lon,
                                                                                                                 models_overlap_max_lon,
                                                                                                                 obs_overlap_min_lat,
                                                                                                                 obs_overlap_max_lat,
                                                                                                                 obs_overlap_min_lon,
                                                                                                                 obs_overlap_max_lon)
    model_temp_res = get_models_temp_res()
    obs_temp_res = get_obs_temp_res()
    model_lat_res, model_lon_res = get_models_spatial_res()
    obs_lat_res, obs_lon_res = get_obs_spatial_res()

    temp_grid_option = "Observation"
    temp_grid_setting = obs_temp_res
    spatial_grid_option = "Observation"
    spatial_grid_setting = obs_lat_res
    models_dict = {}

    for i in enumerate(models_info):
         models_dict['mod{0}'.format(i[0])] = models_info[i[0]]
    obs_dict = {}
    for i in enumerate(observations_info):
         obs_dict['obs{0}'.format(i[0])] = observations_info[i[0]]

    reference_dataset = 'obs0'
    target_datasets = []
    for i in range(len(model_datasets)):
         target_datasets.append('mod{0}'.format(i))
    subregion_path = None
    metrics_dict = {'1':'bias_of_multiyear_climatology', '2':'comparing_spatial_patterns_of_multiyear_climatology'}
    metric = 'bias_of_multiyear_climatology'
    plots = {'bias_of_multiyear_climatology':"contour map", 'comparing_spatial_patterns_of_multiyear_climatology':"Taylor diagram"}
    working_directory = os.getcwd() + "/plots/"  #Default value of working directory set to "plots" folder in current directory
    plot_title = '' #TODO: ask user about plot title or figure out automatically

    fix_min_time = all_overlap_start_time
    fix_max_time = all_overlap_end_time
    fix_min_lat = all_overlap_min_lat
    fix_max_lat = all_overlap_max_lat
    fix_min_lon = all_overlap_min_lon
    fix_max_lon = all_overlap_max_lon

    option = ''
    while option != '0':
         y, x = ready_screen("settings_screen", note)
         screen.addstr(1, 1, header)
         screen.addstr(3, 1, "INFORMATION")
         screen.addstr(4, 1, "===========")
         screen.addstr(6, 2, "Number of model file:   {0}".format(str(len(model_datasets))))
         screen.addstr(7, 2, "Number of observation:  {0}".format(str(len(observations_info))))
         screen.addstr(8, 2, "Temporal Boundaries:")
         screen.addstr(9, 5, "Start time = {0}".format(all_overlap_start_time))
         screen.addstr(10, 5, "End time = {0}".format(all_overlap_end_time))
         screen.addstr(11, 2, "Spatial Boundaries:")
         screen.addstr(12, 5, "min-lat = {0}".format(all_overlap_min_lat))
         screen.addstr(13, 5, "max-lat = {0}".format(all_overlap_max_lat))
         screen.addstr(14, 5, "min-lon = {0}".format(all_overlap_min_lon))
         screen.addstr(15, 5, "max-lon = {0}".format(all_overlap_max_lon))
         screen.addstr(16, 2, "Temporal Resolution:")
         screen.addstr(17, 5, "Model = {0}".format(model_temp_res))
         screen.addstr(18, 5, "Observation = {0}".format(obs_temp_res))
         screen.addstr(19, 2, "Spatial Resolution:")
         screen.addstr(20, 5, "Model:")
         screen.addstr(21, 10, "lat = {0}".format(model_lat_res))
         screen.addstr(22, 10, "lon = {0}".format(model_lon_res))
         screen.addstr(23, 5, "Observation:")
         screen.addstr(24, 10, "lat = {0}".format(obs_lat_res))
         screen.addstr(25, 10, "lon = {0}".format(obs_lon_res))
         screen.addstr(26, 2, "Temporal Grid Option:  {0}".format(temp_grid_option))
         screen.addstr(27, 2, "Spatial Grid Option:   {0}".format(spatial_grid_option))
         screen.addstr(28, 2, "Reference Dataset: {0}".format(reference_dataset))
         screen.addstr(29, 2, "Target Dataset/s: {0}".format([mod for mod in target_datasets]))
         screen.addstr(30, 2, "Working Directory:")
         screen.addstr(31, 5, "{0}".format(working_directory))
         screen.addstr(32, 2, "Metric: {0}".format(metric))
         screen.addstr(33, 2, "Plot: {0}".format(plots[metric]))

         screen.addstr(3, x/2, "MODIFICATION and RUN")
         screen.addstr(4, x/2, "====================")
         screen.addstr(6, x/2, "1 - Change Temporal Boundaries")
         screen.addstr(7, x/2, "2 - Change Spatial Boundaries")
         screen.addstr(8, x/2, "3 - Change Temporal Gridding")
         screen.addstr(9, x/2, "4 - Change Spatial Gridding")
         screen.addstr(10, x/2, "5 - Change Reference dataset")
         screen.addstr(11, x/2, "6 - Change Target dataset/s")
         screen.addstr(12, x/2, "7 - Change Metric")
         screen.addstr(13, x/2, "8 - Change Working Directory")
         #screen.addstr(14, x/2, "9 - Change Plot Title [Coming Soon....]")
         #screen.addstr(15, x/2, "10 - Save the processed data [Coming Soon....]")
         screen.addstr(14, x/2, "9 - Show Temporal Boundaries")
         screen.addstr(15, x/2, "10 - Show Spatial Boundaries")
         screen.addstr(16, x/2, "0 - Return to Main Menu")
         screen.addstr(18, x/2, "r - Run Evaluation")
         screen.addstr(20, x/2, "Select an option: ")

         screen.refresh()
         option = screen.getstr()

         if option == '1':
              screen.addstr(25, x/2, "Enter Start Time [min time: {0}] (Format YYYY-MM-DD):".format(fix_min_time))
              new_start_time = screen.getstr()
              try:
                   new_start_time = datetime.strptime(new_start_time, '%Y-%m-%d')
                   #new_start_time_int = int("{0}{1}".format(new_start_time.year, new_start_time.month))
                   #fix_min_time_int = int("{0}{1}".format(fix_min_time.year, fix_min_time.month))
                   #fix_max_time_int = int("{0}{1}".format(fix_max_time.year, fix_max_time.month))
                   #all_overlap_end_time_int = int("{0}{1}".format(all_overlap_end_time.year, all_overlap_end_time.month))
                   #if new_start_time_int < fix_min_time_int \
                   #or new_start_time_int > fix_max_time_int \
                   #or new_start_time_int > all_overlap_end_time_int:
                   if new_start_time < fix_min_time \
                   or new_start_time > fix_max_time \
                   or new_start_time > all_overlap_end_time:
                        note = "Start time has not changed."
                   else:
                        all_overlap_start_time = new_start_time
                        note = "Start time has changed successfully. "
              except:
                   note = "Start time has not changed."
              screen.addstr(26, x/2, "Enter End Time [max time:{0}] (Format YYYY-MM-DD):".format(fix_max_time))
              new_end_time = screen.getstr()
              try:
                   new_end_time = datetime.strptime(new_end_time, '%Y-%m-%d')
                   #new_end_time_int = int("{0}{1}".format(new_end_time.year, new_end_time.month))
                   #fix_min_time_int = int("{0}{1}".format(fix_min_time.year, fix_min_time.month))
                   #fix_max_time_int = int("{0}{1}".format(fix_max_time.year, fix_max_time.month))
                   #all_overlap_start_time_int = int("{0}{1}".format(all_overlap_start_time.year, all_overlap_start_time.month))
                   #if new_end_time_int > fix_max_time_int \
                   #or new_end_time_int < fix_min_time_int \
                   #or new_end_time_int < all_overlap_start_time_int:
                   if new_end_time > fix_max_time \
                   or new_end_time < fix_min_time \
                   or new_end_time < all_overlap_start_time:
                        note = note + " End time has not changed. "
                   else:
                        all_overlap_end_time = new_end_time
                        note = note + " End time has changed successfully. "
              except:
                   note = note + " End time has not changed. "

         if option == '2':
              screen.addstr(25, x/2, "Enter Minimum Latitude [{0}]:".format(fix_min_lat))
              new_min_lat = screen.getstr()
              try:
                   new_min_lat = float(new_min_lat)
                   if new_min_lat < fix_min_lat or new_min_lat > fix_max_lat or new_min_lat > all_overlap_max_lat:
                        note = "Minimum latitude has not changed. "
                   else:
                        all_overlap_min_lat = new_min_lat
                        note = "Minimum latitude has changed successfully. "
              except:
                   note = "Minimum latitude has not changed. "
              screen.addstr(26, x/2, "Enter Maximum Latitude [{0}]:".format(fix_max_lat))
              new_max_lat = screen.getstr()
              try:
                   new_max_lat = float(new_max_lat)
                   if new_max_lat > fix_max_lat or new_max_lat < fix_min_lat or new_max_lat < all_overlap_min_lat:
                        note = note + " Maximum latitude has not changed. "
                   else:
                        all_overlap_max_lat = new_max_lat
                        note = note + "Maximum latitude has changed successfully. "
              except:
                   note = note + " Maximum latitude has not changed. "
              screen.addstr(27, x/2, "Enter Minimum Longitude [{0}]:".format(fix_min_lon))
              new_min_lon = screen.getstr()
              try:
                   new_min_lon = float(new_min_lon)
                   if new_min_lon < fix_min_lon or new_min_lon > fix_max_lon or new_min_lon > all_overlap_max_lon:
                        note = note + " Minimum longitude has not changed. "
                   else:
                        all_overlap_min_lon = new_min_lon
                        note = note + "Minimum longitude has changed successfully. "
              except:
                   note = note + " Minimum longitude has not changed. "
              screen.addstr(28, x/2, "Enter Maximum Longitude [{0}]:".format(fix_max_lon))
              new_max_lon = screen.getstr()
              try:
                   new_max_lon = float(new_max_lon)
                   if new_max_lon > fix_max_lon or new_max_lon < fix_min_lon or new_max_lon < all_overlap_min_lon:
                        note = note + " Maximum longitude has not changed. "
                   else:
                        all_overlap_max_lon = new_max_lon
                        note = note + "Maximum longitude has changed successfully. "
              except:
                   note = note + " Maximum longitude has not changed. "

         if option == '3':
              screen.addstr(25, x/2, "Enter Temporal Gridding Option [Model or Observation]:")
              new_temp_grid_option = screen.getstr()
              if new_temp_grid_option.lower() == 'model':
                   temp_grid_option = 'Model'
                   temp_grid_setting = model_temp_res
                   note = "Temporal gridding option has changed successfully to {0}".format(temp_grid_option)
              elif new_temp_grid_option.lower() == 'observation':
                   temp_grid_option = 'Observation'
                   temp_grid_setting = obs_temp_res
                   note = "Temporal gridding option has changed successfully to {0}".format(temp_grid_option)
              else:
                   note = "Temporal gridding option has not changed."

         if option == '4':
              screen.addstr(25, x/2, "Enter Spatial Gridding Option [Model, Observation or User]:")
              new_spatial_grid_option = screen.getstr()
              #if new_spatial_grid_option.lower() == 'model':
              #     spatial_grid_option = 'Model'
              #     spatial_grid_setting = model_lat_res
              #     note = "Spatial gridding option has changed successfully to {0}".format(spatial_grid_option)
              if new_spatial_grid_option.lower() == 'observation':
                   spatial_grid_option = 'Observation'
                   spatial_grid_setting = obs_lat_res
                   note = "Spatial gridding option has changed successfully to {0}".format(spatial_grid_option)
              elif new_spatial_grid_option.lower() == 'user':
                   screen.addstr(26, x/2, "Please enter spatial resolution: ")
                   user_res = screen.getstr()
                   try:
                        user_res = float(user_res)
                        spatial_grid_option = 'User: resolution {0}'.format(str(user_res))
                        spatial_grid_setting = user_res
                        note = "Spatial gridding option has changed successfully to {0}".format(spatial_grid_option)
                   except:
                        note = "Spatial gridding option has not changed."
              else:
                   note = "Spatial gridding option has not changed."

         if option == '5':
              screen.addstr(25, x/2, "Model/s:")
              for each in enumerate(models_dict):
                   screen.addstr(26 + each[0], x/2 + 2, "{0}: {1}".format(each[1], models_dict[each[1]]['directory'].split("/")[-1]))
              screen.addstr(26 + len(models_dict), x/2, "Observation/s:")
              for each in enumerate(obs_dict):
                   screen.addstr(27 + len(models_dict) + each[0], x/2 + 2, "{0}: {1} - ({2})".format(each[1], obs_dict[each[1]]['database'], obs_dict[each[1]]['unit']))
              screen.addstr(27 + len(obs_dict) + len(models_dict), x/2, "Please select reference dataset:")
              selected_reference = screen.getstr()
              if selected_reference in models_dict:
                   reference_dataset = selected_reference
                   note = "Reference dataset successfully changed."
              elif selected_reference in obs_dict:
                   reference_dataset = selected_reference
                   note = "Reference dataset successfully changed."
              else:
                   note = "Reference dataset did not change."

         if option == '6':
              screen.addstr(25, x/2, "Model/s:")
              for each in enumerate(models_dict):
                   screen.addstr(26 + each[0], x/2 + 2, "{0}: {1}".format(each[1], models_dict[each[1]]['directory'].split("/")[-1]))
              screen.addstr(26 + len(models_dict), x/2, "Observation/s:")
              for each in enumerate(obs_dict):
                   screen.addstr(27 + len(models_dict) + each[0], x/2 + 2, "{0}: {1} - ({2})".format(each[1], obs_dict[each[1]]['database'], obs_dict[each[1]]['unit']))
              screen.addstr(27 + len(obs_dict) + len(models_dict), x/2, "Please enter target dataset/s (comma separated for multi target):")
              selected_target = screen.getstr()
              selected_target = selected_target.split(",")
              if selected_target != ['']:
                   target_datasets = []
                   for target in selected_target:
                        if target in models_dict:
                             target_datasets.append(target)
                             note = "Target dataset successfully changed."
                        elif target in obs_dict:
                             target_datasets.append(target)
                             note = "Target dataset successfully changed."
                        else:
                             note = "Target dataset did not change."

         if option == '7':
              screen.addstr(25, x/2, "Available metrics:")
              for i in enumerate(sorted(metrics_dict, key=metrics_dict.get)):
                   screen.addstr(26 + i[0], x/2 + 2, "[{0}] - {1}".format(i[1], metrics_dict[i[1]]))
              screen.addstr(26 + len(metrics_dict), x/2, "Please select a metric:")
              metric_id = screen.getstr()
              if metric_id in metrics_dict:
                   metric = metrics_dict[metric_id]
                   note = "Metric sucessfully changed to {0}".format(metric)
              else:
                   note = "Metric has not changes"

         if option == '8':
              screen.addstr(25, x/2, "Please enter working directory path:")
              working_directory = screen.getstr()
              if working_directory:
                   if working_directory[-1] != '/':
                        working_directory = working_directory + "/"
              else:
                   note = "Working directory has not changed"

         if option == '9':
              screen.addstr(25, x/2, "Please enter plot title:")
              plot_title = screen.getstr()

         #if option == '10':
         #     screen.addstr(25, x/2, "Please enter plot title:")
         #     plot_title = screen.getstr()

         if option == '9':
              models_start_time, models_end_time = get_models_temp_bound()
              line = 25
              for i, model in enumerate(model_datasets):
                   mode_name = models_info[i]['directory'].split("/")[-1]
                   line += 1
                   screen.addstr(line, x/2, "{0}".format(mode_name))
                   line += 1
                   screen.addstr(line, x/2 + 3, "Start:{0} - End:{1}".format(models_start_time[i], models_end_time[i]))

              observations_start_time, observations_end_time = get_obs_temp_bound()
              for i, obs in enumerate(observations_info):
                   line += 1
                   screen.addstr(line, x/2, "{0}".format(observations_info[i]['database']))
                   line += 1
                   screen.addstr(line, x/2 + 3, "Start:{0} - End:{1}".format(observations_start_time[i], observations_end_time[i]))
              screen.getstr()

         if option == '10':
              models_bound = get_models_spatial_bound()
              line = 25
              for i, model in enumerate(model_datasets):
                   mode_name = models_info[i]['directory'].split("/")[-1]
                   line += 1
                   screen.addstr(line, x/2, "{0}".format(mode_name))
                   line += 1
                   screen.addstr(line, x/2 + 3, "{0}".format(models_bound[i]))

              observations_bound = get_obs_spatial_bound()
              for i, obs in enumerate(observations_info):
                   line += 1
                   screen.addstr(line, x/2, "{0}".format(observations_info[i]['database']))
                   line += 1
                   screen.addstr(line, x/2 + 3, "{0}".format(observations_bound[i]))
              screen.getstr()

         if option.lower() == 'r':
              note = run_screen(model_datasets, models_info, observations_info, all_overlap_start_time, all_overlap_end_time, \
                         all_overlap_min_lat, all_overlap_max_lat, all_overlap_min_lon, all_overlap_max_lon, \
                         temp_grid_setting, spatial_grid_option, spatial_grid_setting, reference_dataset, target_datasets, metric, working_directory, plot_title)


##############################################################
#     Main Menu Screen
##############################################################

def main_menu(model_datasets, models_info, observation_datasets, observations_info, note=""):
    '''This function Generates main menu page.

    :param model_datasets: list of model dataset objects
    :type model_datasets: list
    :param models_info: list of dictionaries that contain information for each model
    :type models_info: list
    :param observation_datasets: list of observation dataset objects
    :type observation_datasets: list
    :param observations_info: list of dictionaries that contain information for each observation
    :type observations_info: list
    '''

    option = ''
    while option != '0':
         ready_screen("main_menu", note)
         model_status = "NC" if len(model_datasets) == 0 else "C"     #NC (Not Complete), if there is no model added, C (Complete) if model is added
         obs_status = "NC" if len(observations_info) == 0 else "C"    #NC (Not Complete), if there is no observation added, C (Complete) if observation is added
         screen.addstr(1, 1, "Main Menu:")
         screen.addstr(4, 4, "1 - Manage Model ({0})".format(model_status))
         screen.addstr(6, 4, "2 - Manage Observation ({0})".format(obs_status))
         screen.addstr(8, 4, "3 - Run")
         screen.addstr(10, 4, "0 - EXIT")
         screen.addstr(16, 2, "Select an option: ")
         screen.refresh()
         option = screen.getstr()

         if option == '1':
              header = "Main Menu > Manage Model"
              manage_model_screen(header)
         if option == '2':
              header = "Main Menu > Manage Observation"
              manage_obs_screen(header)
         if option == '3':
              if model_status == 'NC' or obs_status == 'NC':
                   main_menu(model_datasets, models_info, observation_datasets, observations_info, note="WARNING: Please complete step 1 and 2 before 3.")
              else:
                   header = "Main Menu > Run"
                   settings_screen(header)
    curses.endwin()
    sys.exit()


if __name__ == '__main__':
     TITLE = "RCMES CLI"
     ORGANIZATION = "JPL/NASA - JIFRESSE/UCLA"
     screen = curses.initscr()
     model_datasets = []           #list of model dataset objects
     models_info = []              #list of dictionaries that contain information for each model
     observation_datasets = []     #list of observation dataset objects
     observations_info = []        #list of dictionaries that contain information for each observation
     main_menu(model_datasets, models_info, observation_datasets, observations_info)
