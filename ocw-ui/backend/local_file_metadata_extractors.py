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

''' Helpers for local model/observation file metadata extraction. '''

import sys
import netCDF4

from bottle import Bottle, request, route

lfme_app = Bottle()

@lfme_app.route('/list_latlon/<file_path:path>')
def list_latlon(file_path):
    ''' Retrieve lat/lon information from given file.
    
    :param file_path: Path to the NetCDF file from which lat/lon information
        should be extracted
    :type file_path: string:

    :returns: Dictionary containing lat/lon information if successful, otherwise
        failure information is returned.

    * Example successful JSON return *

    .. sourcecode: javascript

        {
            'success': true,
            'lat_name': The guessed latitude variable name,
            'lon_name': the guessed longitude variable name,
            'lat_min': The minimum latitude value,
            'lat_max': The maximum latitude value,
            'lon_min': The minimum longitude value,
            'lon_max': The maximum longitude value
        }

    * Example failure JSON return *

    .. sourcecode: javascript

        {
            'success': false,
            'variables': List of all variables present in the NetCDF file
        }
    '''
    in_file = netCDF4.Dataset(file_path, mode='r')

    var_names = set([key.encode().lower() for key in in_file.variables.keys()])
    var_names_list = list(var_names)

    lat_name_guesses = set(['latitude','lat','lats','latitudes'])
    lon_name_guesses = set(['longitude','lon','lons','longitudes'])

    # Attempt to determine the lat name
    found_lat_name = False

    # Find the intersection (if there is one) of the var names with the lat guesses
    lat_guesses = list(var_names & lat_name_guesses)

    if len(lat_guesses) >= 1:
        found_lat_name = True
        lat_name = var_names_list[var_names_list.index(lat_guesses[0])]

        lats = in_file.variables[lat_name][:]

        # Change 0 - 360 degree values to be -180 to 180
        lats[lats > 180] = lats[lats > 180] - 360

        lat_min = lats.min()
        lat_max = lats.max()

    # Attempt to determine the lon name
    found_lon_name = False

    # Find the intersection (if there is one) of the var names with the lon guesses
    lon_guesses = list(var_names & lon_name_guesses)

    if len(lon_guesses) >= 1:
        found_lon_name = True
        lon_name = var_names_list[var_names_list.index(lon_guesses[0])]

        lons = in_file.variables[lon_name][:]

        # Change 0 - 360 degree values to be -180 to 180
        lons[lons > 180] = lons[lons > 180] - 360

        lon_min = lons.min()
        lon_max = lons.max()

    in_file.close()

    success = found_lat_name and found_lon_name
    if success:
        values = [success, lat_name, lon_name, lat_min, lat_max, lon_min, lon_max]
        value_names = ['success', 'lat_name', 'lon_name', 'lat_min', 'lat_max', 'lon_min', 'lon_max']
        output = dict(zip(value_names, values))

        if request.query.callback:
            return "%s(%s)" % (request.query.callback, output)
        return output

    else:
        output = {"success": success, "variables": var_names_list}

        if request.query.callback:
            return "%s(%s)" % (request.query.callback, output)
        return output

