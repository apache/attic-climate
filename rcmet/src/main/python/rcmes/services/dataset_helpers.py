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
#!/usr/bin/env python
"""
    Provides Bottle services for interacting with RCMED
"""

from bottle import request, route

import requests

@route('/getObsDatasets')
def getObservationDatasetData():
    r = requests.get('http://rcmes.jpl.nasa.gov/query-api/datasets.php')

    # Handle JSONP requests
    if (request.query.callback):
        return "%s(%s)" % (request.query.callback, r.text)
    # Otherwise, just return JSON
    else:
        return r.text

@route('/getDatasetParam')
def getDatasetParameters():
    url = 'http://rcmes.jpl.nasa.gov/query-api/parameters.php?dataset=' + request.query.dataset
    r = requests.get(url)

    # Handle JSONP requests
    if (request.query.callback):
        return "%s(%s)" % (request.query.callback, r.text)
    # Otherwise, just return JSON
    else:
        return r.text
