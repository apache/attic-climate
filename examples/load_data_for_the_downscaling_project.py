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

import numpy as np

import ocw.data_source.local as local

# data files to read
print 'Loading nuWRF output'
file_path = "<directory name>"
filename_pattern = ["wrfout2d_2006082*"]    # nuWRF B24 simulation results between 08/20 and 08/29/2006

nuWRF_dataset = local.load_files(file_path=file_path, filename_pattern=filename_pattern, 
                                 variable_name="PREC_ACC_C", latitude_range=[35,45], longitude_range=[-110,-90])

print 'Loading geos output'
file_path = "<directory name>"
filename_pattern = ["geos_prcp200612*"]    # geos simulation results in December 2006

geos_dataset = local.load_files(file_path=file_path, filename_pattern=filename_pattern,
                                 variable_name="PRCP", latitude_range=[35,45], longitude_range=[-110,-90])

print 'Loading TRMM 3 hourly output'
file_path = "<directory name>"
filename_pattern = ["3B42.20030331*", "3B42.20030401*"]   # TRMM precipitation on 3/31/2003 and 4/1/2003 

TRMM_dataset = local.load_files(file_path=file_path, filename_pattern=filename_pattern,
                                 variable_name="pcp", latitude_range=[35,45], longitude_range=[-110,-90])
