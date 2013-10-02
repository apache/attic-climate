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

import pydap
import requests

def load(url, variable, data_slice=None):
    '''Load a Dataset from an OpenDAP URL

    :param url: The OpenDAP URL for the dataset of interest.
    :type url: String
    :param variable: The name of the variable to read from the dataset.
    :type variable: String
    :param data_slice: A list of slice objects to apply to the variable data
        and lat, lon, and time index lists. If you want to slice one index of
        the data you need to provide valid slices for every index.
    :type data_slice: (Optional) List of slice objects
    '''
    pass
