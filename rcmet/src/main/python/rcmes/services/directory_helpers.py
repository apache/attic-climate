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

WORK_DIR = "/tmp/rcmet"

@route('/getResultDirInfo')
def getResultDirInfo():
    dirPath = WORK_DIR
    dirPath = dirPath.replace('/../', '/')
    dirPath = dirPath.replace('/./', '/')

    if os.path.isdir(dirPath):
        listing = os.listdir(dirPath)
        directories=[d for d in os.listdir(os.getcwd()) if os.path.isdir(d)]
        listingNoHidden = [f for f in listing if f[0] != '.']
        joinedPaths = [os.path.join(dirPath, f) for f in listingNoHidden]
        onlyDirs = [f for f in joinedPaths if os.path.isdir(f)]
        finalPaths = [p.replace(WORK_DIR, '') for p in onlyDirs]
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
