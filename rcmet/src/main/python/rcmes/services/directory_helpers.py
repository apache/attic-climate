#!/usr/bin/env python
"""
    Provides helpers for listing retrieving directory information from the server.
"""

from bottle import request, route
import os
import json

PATH_LEADER = "/usr/local/rcmes"

@route('/getDirInfo/<dirPath:path>')
def getDirectoryInfo(dirPath):
    dirPath = PATH_LEADER + dirPath
    dirPath = dirPath.replace('/../', '/')
    dirPath = dirPath.replace('/./', '/')

    if os.path.isdir(dirPath):
        listing = os.listdir(dirPath)
        listingNoHidden = [f for f in listing if f[0] != '.']
        joinedPaths = [os.path.join(dirPath, f) for f in listingNoHidden]
        joinedPaths = [f + "/" if os.path.isdir(f) else f for f in joinedPaths]
        finalPaths = [p.replace(PATH_LEADER, '') for p in joinedPaths]
        sorted(finalPaths, key=lambda s: s.lower())
        returnJSON = finalPaths
    else:
        returnJSON = []

    returnJSON = json.dumps(returnJSON)
    if request.query.callback:
        return "%s(%s)" % (request.query.callback, returnJSON)
    else:
        return returnJSON

@route('/getPathLeader/')
def getPathLeader():
    returnJSON = {"leader": PATH_LEADER}

    if request.query.callback:
        return "%s(%s)" % (request.query.callback, returnJSON)
    else:
        return returnJSON
