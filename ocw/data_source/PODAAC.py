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

from podaac_data_source import Podaac 
import numpy as np
from ocw.dataset import Dataset
from netCDF4 import Dataset as netcdf_dataset
from netcdftime import utime
import os, urllib
import xml.etree.ElementTree as ET


def _convert_times_to_datetime(time):
    '''Convert the time object's values to datetime objects

    The time values are stored as some unit since an epoch. These need to be
    converted into datetime objects for the OCW Dataset object.

    :param time: The time object's values to convert
    :type time: pydap.model.BaseType

    :returns: list of converted time values as datetime objects
    '''
    units = time.units
    # parse the time units string into a useful object.
    # NOTE: This assumes a 'standard' calendar. It's possible (likely?) that
    # users will want to customize this in the future.
    parsed_time = utime(units)
    return [parsed_time.num2date(x) for x in time[:]]



def load(variable ,datasetId='', datasetShortName='', bbox='', name=''):
	
	# Retrieving the name of granule from datasetId and datasetShortName.
	granuelName = retreive_granule_name(datasetId=datasetId, datasetShortName=datasetShortName)
	path = os.path.dirname(os.path.abspath(__file__))

	# Extracting the granule using podaacpy toolkit's extract_granule service.
	podaac.extract_granule(datasetId=datasetId, shortName=datasetShortName, granuleName=granuleName, bbox=bbox, format='netcdf', path=path)
	
	# Opening the dataset using NETCDF module.
	d = netcdf_dataset(granuleName, mode='r')
	dataset = d[variable]
	temp_dimensions = map(lambda x:x.lower(),dataset.dimensions)
	dataset_dimensions = dataset.dimensions
	time = dataset_dimensions[temp_dimensions.index('time') if 'time' in temp_dimensions else 0]
	lat = dataset_dimensions[temp_dimensions.index('lat') if 'lat' in temp_dimensions else 1]
	lon = dataset_dimensions[temp_dimensions.index('lon') if 'lon' in temp_dimensions else 2]

	# Time is given to us in some units since an epoch. We need to convert
    # these values to datetime objects. Note that we use the main object's
    # time object and not the dataset specific reference to it. We need to
    # grab the 'units' from it and it fails on the dataset specific object.
	times = np.array(_convert_times_to_datetime(d[time]))
	lats = np.array(dataset[lat][:])
	lons = np.array(dataset[lon][:])
	values = np.array(dataset[:])

	# Cleaning up the temporary granule before creating the OCW dataset. 
	d.close()
	path = os.path.join(os.path.dirname(__file__), granuleName)
	os.remove(path)

	origin = {
        'source' : 'PO.DAAC',
        'url' : 'podaac.jpl.nasa.gov/ws'
    }

	return Dataset(lats, lons, times, values, variable,
                  name=name, origin=origin)

def retreive_granule_name(datasetId='', datasetShortName=''):

	# Retrieving the granule saerch results using podaacpy's toolkit and 
	# parsing the xml by creating an xml tree using xml.etree.ElementTree and 
	# fetching the latest granule name in PO.DAAC database of the particular
	# datasetId and datasetShortName. 
	podaac = Podaac()
	startIndex = '1'
	data = podaac.search_granule(datasetId=datasetId, shortName=datasetShortName, startIndex=startIndex)
	root = ET.fromstring(data.encode('utf-8'))
	data = root[12][0].text
	granule = data.split('\t')[3][:-1]

	return granule
