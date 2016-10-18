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

import ocw.data_source.esgf as esgf
from getpass import getpass
import ssl

if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

dataset_id = 'obs4MIPs.CNES.AVISO.zos.mon.v20110829|esgf-data.jpl.nasa.gov'
variable = 'zosStderr'

username = raw_input('Enter your ESGF OpenID:\n')
password = getpass(prompt='Enter your ESGF Password:\n')

# Multiple datasets are returned in a list if the ESGF dataset is
# divided into multiple files.
datasets = esgf.load_dataset(dataset_id,
                             variable,
                             username,
                             password)

# For this example, our dataset is only stored in a single file so
# we only need to look at the 0-th value in the returned list.
ds = datasets[0]

print '\n--------\n'
print 'Variable: ', ds.variable
print 'Shape: ', ds.values.shape
print 'A Value: ', ds.values[100][100][100]
