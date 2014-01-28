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
''' OCW UI Backend web services initialization. '''

from bottle import route, response, run, static_file, hook
import list_vars_in_file
import find_latlon_var
import find_time_var
import decode_model_times as dmt
import run_rcmes_processing
import dataset_helpers
import directory_helpers

@route('/static/evalResults/<filepath:path>')
def get_eval_result_image(filepath):
    ''' Return static file.
    
    Return static file specified by root + filepath where root defaults to:
        /tmp/rcmet

    The 'root' path should coincide with the work directory set used by the
    OCW toolkit for processing.

    :param filepath: The path component that when appended to the 'root' path
        header specifies a file to return.
    :type filepath: string

    :returns: The requested file resource

    '''
    return static_file(filepath, root="/tmp/rcmet")

@hook('after_request')
def enable_cors():
    ''' Allow Cross-Origin Resource Sharing for all URLs. '''
    response.headers['Access-Control-Allow-Origin'] = '*'

if __name__ == "__main__":
    run(host='localhost', port=8082)
