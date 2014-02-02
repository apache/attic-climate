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

from bottle import Bottle, request

import requests

rcmed_app = Bottle()

@rcmed_app.route('/datasets/')
def get_observation_dataset_data():
    ''' Return a list of dataset information from JPL's RCMED.

    * Example Return JSON Format *

    ..sourcecode: javascript

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

    * Example Call Format *

    ..sourcecode: javascript

        /parameters/?dataset=<dataset's short name>

    * Example Return JSON Format *

    ..sourcecode: javascript

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
