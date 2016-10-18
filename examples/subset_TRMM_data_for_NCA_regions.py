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

# Apache OCW lib immports
import ocw.dataset_processor as dsp
import ocw.utils as utils
from ocw.dataset import Bounds
import ocw.data_source.rcmed as rcmed
import ocw.plotter as plotter

from datetime import datetime
import numpy.ma as ma

import ssl

if hasattr(ssl, '_create_unverified_context'):
    ssl._create_default_https_context = ssl._create_unverified_context

# rectangular boundary
min_lat = 15.75
max_lat = 55.75
min_lon = -125.75
max_lon = -66.75

start_time = datetime(1998, 1, 1)
end_time = datetime(1998, 12, 31)

TRMM_dataset = rcmed.parameter_dataset(3, 36, min_lat, max_lat, min_lon, max_lon,
                                       start_time, end_time)

Cuba_and_Bahamas_bounds = Bounds(
    boundary_type='countries', countries=['Cuba', 'Bahamas'])
# to mask out the data over Mexico and Canada
TRMM_dataset2 = dsp.subset(
    TRMM_dataset, Cuba_and_Bahamas_bounds, extract=False)

plotter.draw_contour_map(ma.mean(TRMM_dataset2.values, axis=0), TRMM_dataset2.lats,
                         TRMM_dataset2.lons, fname='TRMM_without_Cuba_and_Bahamas')

NCA_SW_bounds = Bounds(boundary_type='us_states', us_states=[
                       'CA', 'NV', 'UT', 'AZ', 'NM', 'CO'])
# to mask out the data over Mexico and Canada
TRMM_dataset3 = dsp.subset(TRMM_dataset2, NCA_SW_bounds, extract=True)

plotter.draw_contour_map(ma.mean(TRMM_dataset3.values, axis=0),
                         TRMM_dataset3.lats, TRMM_dataset3.lons, fname='TRMM_NCA_SW')
