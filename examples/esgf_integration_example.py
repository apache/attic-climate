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

"""
    esgf_integration_example.py

    Use OCW to download an ESGF dataset into the common format of an OCW dataset object.

    In this example:

    1. Download an ESGF (https://esgf.llnl.gov/) dataset and load it into a OCW dataset object.

    OCW modules demonstrated:

    1. datasource/esgf

"""

from __future__ import print_function

import ssl
import sys
from getpass import getpass

import ocw.data_source.esgf as esgf


def main():
    """
    An example of using the OCW ESGF library.  Connects to an ESGF
    server and downloads a dataset.
    """
    if hasattr(ssl, '_create_unverified_context'):
        ssl._create_default_https_context = ssl._create_unverified_context

    dataset_id = 'obs4mips.CNES.AVISO.zos.mon.v20110829|esgf-data.jpl.nasa.gov'
    variable = 'zosStderr'

    if sys.version_info[0] >= 3:
        username = input('Enter your ESGF OpenID:\n')
    else:
        username = raw_input('Enter your ESGF OpenID:\n')

    password = getpass(prompt='Enter your ESGF Password:\n')

    # Multiple datasets are returned in a list if the ESGF dataset is
    # divided into multiple files.
    datasets = esgf.load_dataset(dataset_id, variable, username, password)

    # For this example, our dataset is only stored in a single file so
    # we only need to look at the 0-th value in the returned list.
    dataset = datasets[0]

    print('\n--------\n')
    print('Variable: ', dataset.variable)
    print('Shape: ', dataset.values.shape)
    print('A Value: ', dataset.values[100][100][100])


if __name__ == '__main__':
    main()
