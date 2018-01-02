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
""" OCW UI Backend web services initialization. """

import os
import sys
from bottle import Bottle, response, static_file
from local_file_metadata_extractors import lfme_app
from directory_helpers import dir_app
from rcmed_helpers import rcmed_app
from processing import processing_app


def link_to_frontend():
    """
    The backend expects a link to a directory called frontend at the same level.
    Attempt to create one if it does not exist.
    """
    backend_path = os.path.dirname(os.path.realpath(__file__))
    link_path = backend_path + '/frontend'
    frontend_path = backend_path.replace('backend', 'frontend')

    if not os.path.isdir(link_path):
        print("Expected to find a linked directory to the frontend.")
        print("Checking default location %s." % frontend_path)
        if os.path.isdir(frontend_path):
            print("Attempting to create linked directory to %s." % frontend_path)
            os.symlink(frontend_path, link_path)
        else:
            print("Frontend directory not found in %s." % frontend_path)
            print("Either install the frontend to the default directory "
                  "or manually create a link in the backend directory called "
                  "'frontend' to the directory where the front end is installed.")
            return 1

    return 0


if link_to_frontend():
    sys.exit(1)

app = Bottle()
app.mount('/lfme/', lfme_app)
app.mount('/dir/', dir_app)
app.mount('/rcmed/', rcmed_app)
app.mount('/processing/', processing_app)

@app.route('/')
@app.route('/index.html')
def index():
    return static_file('index.html', root='./frontend/app/')

@app.route('/bower_components/:path#.+#')
def serve_static(path):
    return static_file(path, root='./frontend/bower_components/')

@app.route('/styles/:path#.+#')
def serve_static(path):
    return static_file(path, root='./frontend/app/styles/')

@app.route('/scripts/:path#.+#')
def serve_static(path):
    return static_file(path, root='./frontend/app/scripts/')

@app.route('/views/:path#.+#')
def serve_static(path):
    return static_file(path, root='./frontend/app/views/')

@app.route('/img/:path#.+#')
def server_static(path):
     return static_file(path, root='./frontend/app/img/')

@app.route('/static/eval_results/<file_path:path>')
def get_eval_result_image(file_path):
    ''' Return static file.

    Return static file specified by root + filepath where root defaults to:
        /tmp/ocw

    The 'root' path should coincide with the work directory set used by the
    OCW toolkit for processing.

    :param filepath: The path component that when appended to the 'root' path
        header specifies a file to return.
    :type filepath: string

    :returns: The requested file resource
    '''
    return static_file(file_path, root="/tmp/ocw")

@app.hook('after_request')
def enable_cors():
    ''' Allow Cross-Origin Resource Sharing for all URLs. '''
    response.headers['Access-Control-Allow-Origin'] = '*'

if __name__ == "__main__":
    app.run(host='localhost', port=8082)
