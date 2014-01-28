# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

''''''

import sys
import datetime as dt

def decode_time_values(dataset, time_var_name):
    ''''''
    # Grab the time data and time unit info
    time_data = dataset.variables[time_var_name]
    time_format = time_data.units

    # NOTE: Could raise ValueError
    time_units = parse_time_units(time_format)

    # NOTE: Could raise ValueError
    time_base = parse_time_base(time_format)

    times = []
    arg = {}
    if time_units == 'months':
        # datetime.timedelta doesn't support a 'months' option. To remedy
        # this, a month == 30 days for our purposes.
        for time_val in time_data:
            num_days = 30 * time_val
            times.append(time_base + dt.timedelta(days=num_days))
    else:
        for time_val in time_data:
            arg[time_units] = time_val
            times.append(time_base + dt.timedelta(**arg))

    return times

def parse_time_units(time_format):
    ''''''
    for unit in ['seconds', 'minutes', 'hours', 'days', 'months', 'years']:
        if unit in time_format:
            return unit
    else:
        cur_frame = sys._getframe().f_code
        err = "{}.{}: Unable to parse valid units from {}".format(
            cur_frame.co_filename,
            cur_frame.co_name,
            time_format
        )
        raise ValueError(err)

def parse_time_base(time_format):
    ''''''
    # NOTE: This could raise an exception. Check below for info on which
    base_time_string = parse_base_time_string(time_format)

    time_format = time_format.strip()

    possible_time_formats = [
        '%Y:%m:%d %H:%M:%S', '%Y-%m-%d %H-%M-%S', '%Y/%m/%d %H/%M/%S',
        '%Y-%m-%d %H:%M:%S', '%Y/%m/%d %H:%M:%S', '%Y%m%d %H:%M:%S',
        '%Y%m%d%H%M%S', '%Y-%m-%d-%H-%M-%S', '%Y/%m/%d/%H/%M/%S',
        '%Y:%m:%d:%H:%M:%S', '%Y-%m-%d-%H:%M:%S', '%Y-%m-%d %H:%M:%S',
        '%Y/%m/%d%H:%M:%S', '%Y-%m-%d %H:%M', '%Y/%m/%d %H:%M',
        '%Y:%m:%d %H:%M', '%Y%m%d %H:%M', '%Y-%m-%d', '%Y/%m/%d',
        '%Y:%m:%d', '%Y%m%d'
    ]

    for time_format in possible_time_formats:
        try:
            stripped_time = dt.datetime.strptime(base_time_string, time_format)
            break
        except ValueError:
            # This exception means that the time format attempted was incorrect.
            # No need to report or raise this, simply try the next one!
            pass
    else:
        cur_frame = sys._getframe().f_code
        err = "{}.{}: Unable to parse valid date from {}".format(
            cur_frame.co_filename,
            cur_frame.co_name,
            base_time_string
        )

        raise ValueError(err)

    return stripped_time

def parse_base_time_string(time_format):
    ''' Retrieve base time string from time data units information.

    :param time_format: The time data units string from the dataset
        being processed. The string should be of the format
        '<units> since <base time date>'
    :type time_format: String

    :returns: The base time string split out of the time units information.

    :raises ValueError: When the time_format parameter is malformed.
    '''
    if 'since' not in time_format:
        cur_frame = sys._getframe().f_code
        err = "{}.{}: Invalid time_format value {} given".format(
            cur_frame.co_filename,
            cur_frame.co_name,
            time_format
        )

        raise ValueError(err)

    return time_format.split('since')[1].strip()
