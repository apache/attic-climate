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

import ocw.dataset as ds
import ocw.data_source.local as local
import ocw.dataset_processor as dsp
import ocw.plotter as plotter

import numpy as np
import numpy.ma as ma


''' data source: https://dx.doi.org/10.6084/m9.figshare.3753321.v1
    AOD_monthly_2000-Mar_2016-FEB_from_MISR_L3_JOINT.nc is publicly available.'''
dataset = local.load_file('AOD_monthly_2000-MAR_2016-FEB_from_MISR_L3_JOINT.nc',
                          'nonabsorbing_ave')
''' Subset the data for East Asia'''
Bounds = ds.Bounds(lat_min=20, lat_max=57.7, lon_min=90, lon_max=150)
dataset = dsp.subset(dataset, Bounds)

'''The original dataset includes nonabsorbing AOD values between March 2000 and February 2015. 
dsp.temporal_subset will extract data in September-October-November.'''
dataset_SON = dsp.temporal_subset(
    dataset, month_start=9, month_end=11, average_each_year=True)

ny, nx = dataset_SON.values.shape[1:]

# multi-year mean aod
clim_aod = ma.zeros([3, ny, nx])

clim_aod[0, :] = ma.mean(dataset_SON.values, axis=0)  # 16-year mean
clim_aod[1, :] = ma.mean(dataset_SON.values[-5:, :],
                         axis=0)  # the last 5-year mean
clim_aod[2, :] = dataset_SON.values[-1, :]  # the last year's value

# plot clim_aod (3 subplots)
plotter.draw_contour_map(clim_aod, dataset_SON.lats, dataset_SON.lons,
                         fname='nonabsorbing_AOD_clim_East_Asia_Sep-Nov',
                         gridshape=[1, 3], subtitles=['2000-2015: 16 years', '2011-2015: 5 years', '2015: 1 year'],
                         clevs=np.arange(21) * 0.02)
