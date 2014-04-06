#
#  Licensed to the Apache Software Foundation (ASF) under one or more
#  contributor license agreements.  See the NOTICE file distributed with
#  this work for additional information regarding copyright ownership.
#  The ASF licenses this file to You under the Apache License, Version 2.0
#  (the "License"); you may not use this file except in compliance with
#  the License.  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

''' Services for interacting with NASA JPL's Regional Climate Model Evaluation Database. '''

import ocw.data_source.rcmed as rcmed

from bottle import Bottle, request, response

import requests

rcmed_app = Bottle()

@rcmed_app.route('/datasets/')
def get_observation_dataset_data():
    ''' Return a list of dataset information from JPL's RCMED.

    **Example Return JSON Format**

    .. sourcecode:: javascript

        [
            {
                "dataset_id": "17",
                "shortname": "The dataset's short name",
                "longname": "The dataset's, full name",
                "source": "Where the dataset originated"
            },
            ...
        ]
    '''
    r = requests.get('http://rcmes.jpl.nasa.gov/query-api/datasets.php')

    if (request.query.callback):
        return "%s(%s)" % (request.query.callback, r.text)
    return r.text

@rcmed_app.route('/parameters/')
def get_dataset_parameters():
    ''' Return dataset specific parameter information from JPL's RCMED.

    **Example Call Format**

    .. sourcecode:: javascript

        /parameters/?dataset=<dataset's short name>

    **Example Return JSON Format**

    .. sourcecode:: javascript

        [
            {
                "parameter_id": "80",
                "shortname": "The dataset's short name",
                "datasetshortname": "The dataset's short name again",
                "longname": "The dataset's long name",
                "units": "Units for the dataset's measurements"
            }
        ]

    '''
    url = 'http://rcmes.jpl.nasa.gov/query-api/parameters.php?dataset=' + request.query.dataset
    r = requests.get(url)

    if (request.query.callback):
        return "%s(%s)" % (request.query.callback, r.text)
    return r.text


def extract_bounds(parameter):
    ''' This will take a parameter dictionary and return the spatial and temporal bounds.

    :param parameter: Single parameter that is returned from rcmed.get_parameters_metadata().
    :type parameter: dictionary:

    :returns: parameter_id and bounds dictionary of format
            {
              "start_date": "1901-01-15",
              "end_date": "2009-12-15",
              "lat_max": 89.75,
              "lat_min": -89.75,
              "lon_max": 179.75,
              "lon_min": -179.75
            }
    '''
    bounds_data = {}
    bounds_data['start_date'] = str(parameter['start_date'])
    bounds_data['end_date'] = str(parameter['end_date'])
    spatial_bounds = parameter['bounding_box'].replace('(','').replace(')','')
    spatial_bounds = spatial_bounds.split(',')
    # spatial_bounds is in format:
    # [<lat_max>, <lon_max>, <lat_min>, <lon_max>, <lat_min>, <lon_min>, <lat_max>, <lon_min>]
    # ['49.875', '179.875', '-49.875', '179.875', '-49.875', '-179.875', '49.875', '-179.875']
    bounds_data['lat_max'] = float(spatial_bounds[0])
    bounds_data['lat_min'] = float(spatial_bounds[2])
    bounds_data['lon_max'] = float(spatial_bounds[1])
    bounds_data['lon_min'] = float(spatial_bounds[5])
    param_id =str(parameter['parameter_id'])
    return param_id, bounds_data


@rcmed_app.route('/parameters/bounds/')
@rcmed_app.route('/parameters/bounds')
def get_parameters_bounds():
    ''' Return temporal and spatial bounds metadata for all of JPL's RCMED parameters.

    **Example Call Format**

    .. sourcecode:: javascript

        /parameters/bounds/

    **Example Return JSON Format**

    .. sourcecode:: javascript
        {
          "38": {
            "start_date": "1901-01-15",
            "end_date": "2009-12-15",
            "lat_max": 89.75,
            "lat_min": -89.75,
            "lon_max": 179.75,
            "lon_min": -179.75
          },
          "39": {
            "start_date": "1901-01-15",
            "end_date": "2009-12-15",
            "lat_max": 89.75,
            "lat_min": -89.75,
            "lon_max": 179.75,
            "lon_min": -179.75
          }
        }

    '''
    parameter_bounds = {}
    raw_parameters = rcmed.get_parameters_metadata()
    for parameter in raw_parameters:
        if parameter['bounding_box'] != None:
            param_id, bounds_data = extract_bounds(parameter)
            parameter_bounds[param_id] = bounds_data


    return parameter_bounds


@rcmed_app.hook('after_request')
def enable_cors():
    ''' Allow Cross-Origin Resource Sharing for all URLs. '''
    response.headers['Access-Control-Allow-Origin'] = '*'
