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

''' Endpoints for retrieving directory information from the server. '''

from bottle import Bottle, request, response
import os
import re

from config import WORK_DIR, PATH_LEADER

dir_app = Bottle()

@dir_app.route('/list/')
@dir_app.route('/list/<dir_path:path>')
def get_directory_info(dir_path='/'):
    ''' Return the listing of a supplied path.

    :param dir_path: The directory path to list.
    :type dir_path: String

    :returns: Dictionary containing the directory listing if possible.

    * Example successful JSON return *

    .. sourcecode: javascript

        {
            'listing': [
                '/bar/',
                '/baz.txt',
                '/test.txt'
            ]
        }

    * Example failure JSON return *

    .. sourcecode: javascript

        {'listing': []}
    '''
    dir_info = []

    try:
        clean_path = _get_clean_directory_path(PATH_LEADER, dir_path)
        dir_listing = os.listdir(clean_path)
    except:
        # ValueError - dir_path couldn't be 'cleaned'
        # OSError - clean_path is not a directory
        # Either way, we don't have anything to list for the directory!
        pass
    else:
        for obj in dir_listing:
            # Ignore hidden files
            if obj[0] == '.': continue

            # Create a path to the listed object. If it's a directory add a
            # trailing slash as a visual clue. Then strip out the path leader.
            obj = os.path.join(clean_path, obj)
            if os.path.isdir(obj): obj = obj + '/'
            dir_info.append(obj.replace(PATH_LEADER, ''))

        sorted(dir_info, key=lambda s: s.lower())

    if request.query.callback:
        return "%s(%s)" % (request.query.callback, {'listing': dir_info})
    return {'listing': dir_info}

@dir_app.route('/results/')
def get_result_dir_info():
    ''' Retrieve results directory information.

    The backend's results directory is determined by WORK_DIR. All the 
    directories there are formatted and returned as results. If WORK_DIR does
    not exist, an empty listing will be returned (shown as a 'failure below').

    * Successful JSON Response *

    ..sourcecode: javascript

        {
            'listing': [
                '/bar',
                '/foo'
            ]
        }

    * Failure JSON Response *

    ..sourcecode: javascript

        {
            'listing': []
        }
    '''
    dir_info = []

    try:
        dir_listing = os.listdir(WORK_DIR)
    except OSError:
        # The WORK_DIR hasn't been created, so we don't have any results!
        pass
    else:
        for obj in dir_listing:
            # Ignore hidden files
            if obj[0] == '.': continue

            # Create a path to the listed object and strip the work dir leader.
            # If the result isn't a directory, ignore it.
            obj = os.path.join(WORK_DIR, obj)
            if not os.path.isdir(obj): continue
            dir_info.append(obj.replace(WORK_DIR, ''))

        sorted(dir_info, key=lambda s: s.lower())

    if request.query.callback:
        return "%s(%s)" % (request.query.callback, {'listing': dir_info})
    return {'listing': dir_info}

@dir_app.route('/results/<dir_path:path>')
def get_results(dir_path):
    ''' Retrieve specific result files.

    :param dir_path: The relative results path to list.
    :type dir_path: String

    :returns: Dictionary of the requested result's directory listing.

    * Successful JSON Response *

    ..sourcecode: javascript

        {
            'listing': [
                'file1',
                'file2'
            ]
        }

    * Failure JSON Response *

    ..sourcecode: javascript

        {
            'listing': []
        }
    '''
    dir_info = []

    try:
        clean_path = _get_clean_directory_path(WORK_DIR, dir_path)
        dir_listing = os.listdir(clean_path)
    except:
        # ValueError - dir_path couldn't be 'cleaned'
        # OSError - clean_path is not a directory
        # Either way, we don't have any results to return!
        pass
    else:
        for obj in dir_listing:
            # Ignore hidden files
            if obj[0] == '.': continue

            # Create a path to the listed object and strip out the path leader.
            obj = os.path.join(clean_path, obj)
            dir_info.append(obj.replace(WORK_DIR, ''))

        sorted(dir_info, key=lambda s: s.lower())

    if request.query.callback:
        return "%s(%s)" % (request.query.callback, {'listing': dir_info})
    return {'listing': dir_info}

@dir_app.route('/path_leader/')
def get_path_leader():
    ''' Return the path leader used for clean path creation.

    * Example JSON Response *

    .. sourcecode: javascript

        {'leader': '/usr/local/ocw'}
    '''
    return_json = {'leader': PATH_LEADER}

    if request.query.callback:
        return "%s(%s)" % (request.query.callback, return_json)
    return return_json

@dir_app.hook('after_request')
def enable_cors():
    ''' Allow Cross-Origin Resource Sharing for all URLs. '''
    response.headers['Access-Control-Allow-Origin'] = '*'

def _get_clean_directory_path(path_leader, dir_path):
    ''' Return a cleaned directory path with a defined path prefix.

    'Clean' dir_path to remove any relative path components or duplicate 
    slashes that could cause problems. The final clean path is then the
    path_leader + dir_path.

    :param path_leader: The path prefix that will be prepended to the cleaned
        dir_path.
    :type path_leader: String
    :param dir_path: The path to clean.
    :type path_leader: String
    
    :returns: The cleaned directory path with path_leader prepended.
    '''
    # Strip out any .. or . relative directories and remove duplicate slashes
    dir_path = re.sub('/[\./]*/?', '/', dir_path)
    dir_path = re.sub('//+', '/', dir_path)

    # Prevents the directory path from being a substring of the path leader.
    # os.path.join('/usr/local/ocw', '/usr/local') gives '/usr/local'
    # which could allow access to unacceptable paths. This also means that
    if dir_path[0] == '/': dir_path = dir_path[1:]

    return os.path.join(path_leader, dir_path)
