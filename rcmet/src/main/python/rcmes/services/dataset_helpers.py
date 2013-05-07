#!/usr/bin/env python
"""
    Provides Bottle services for interacting with RCMED
"""

from bottle import request, route

import requests
import Nio

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
