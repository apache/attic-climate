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

from podaac.podaac import Podaac
from podaac.podaac_utils import PodaacUtils
import numpy as np
from ocw.dataset import Dataset
from netCDF4 import Dataset as netcdf_dataset
from netcdftime import utime
import os


def convert_times_to_datetime(time):
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

def list_available_extract_granule_dataset_ids():
    '''Convenience function which returns an up-to-date \
        list of available granule dataset id's which can be \
        used in the granule extraction service.

    :returns: a comma-seperated list of granule dataset id's.

    '''
    podaac_utils = PodaacUtils()
    return podaac_utils.list_available_extract_granule_dataset_ids()

def subset_granule(input_file_path=''):
    '''Subset Granule service allows users to Submit subset jobs. \
        Use of this service should be preceded by a Granule Search in \
        order to identify and generate a list of granules to be subsetted.

    :param input_file_path: path to a json file which contains the \
        the request that you want to send to PO.DAAC
    :type input_file_path: :mod:`string`

    :returns: a token on successful request reception. This can be \
        further used to check the status of the request.

    '''
    podaac = Podaac()
    status = podaac.subset_status(podaac.granule_subset(input_file_path))
    print("Granule subsetting initiated with request tracking token '%s'." % status)
    while status is not "200":
        print('...')
    return status

def load_level4_granule(variable, datasetId='', name=''):
    '''Loads a Level4 gridded Dataset from PODAAC

    :param variable: The name of the variable to read from the dataset.
    :type variable: :mod:`string`

    :param datasetId: dataset persistent ID. datasetId or \
        shortName is required for a granule search. Example: \
        PODAAC-ASOP2-25X01
    :type datasetId: :mod:`string`

    :param shortName: the shorter name for a dataset. \
        Either shortName or datasetId is required for a \
        granule search. Example: ASCATA-L2-25km
    :type shortName: :mod:`string`

    :param name: (Optional) A name for the loaded dataset.
    :type name: :mod:`string`

    :returns: A :class:`dataset.Dataset` containing the dataset pointed to by
        the OpenDAP URL.

    :raises: ServerError
    '''
    # Downloading the dataset using podaac toolkit
    podaac = Podaac()
    path = os.path.dirname(os.path.abspath(__file__))
    granuleName = podaac.extract_l4_granule(
        dataset_id=datasetId, path=path)
    path = path + '/' + granuleName
    d = netcdf_dataset(path, mode='r')
    dataset = d.variables[variable]

    # By convention, but not by standard, if the dimensions exist, they will be in the order:
    # time (t), altitude (z), latitude (y), longitude (x)
    # but conventions aren't always followed and all dimensions aren't always present so
    # see if we can make some educated deductions before defaulting to just pulling the first three
    # columns.
    temp_dimensions = map(lambda x: x.lower(), dataset.dimensions)
    dataset_dimensions = dataset.dimensions
    time = dataset_dimensions[temp_dimensions.index(
        'time') if 'time' in temp_dimensions else 0]
    lat = dataset_dimensions[temp_dimensions.index(
        'lat') if 'lat' in temp_dimensions else 1]
    lon = dataset_dimensions[temp_dimensions.index(
        'lon') if 'lon' in temp_dimensions else 2]

    # Time is given to us in some units since an epoch. We need to convert
    # these values to datetime objects. Note that we use the main object's
    # time object and not the dataset specific reference to it. We need to
    # grab the 'units' from it and it fails on the dataset specific object.
    times = np.array(convert_times_to_datetime(d[time]))
    lats = np.array(d.variables[lat][:])
    lons = np.array(d.variables[lon][:])
    values = np.array(dataset[:])
    origin = {
        'source': 'PO.DAAC',
        'url': 'podaac.jpl.nasa.gov/ws'
    }

    # Removing the downloaded temporary granule before creating the OCW
    # dataset.
    d.close()
    path = os.path.join(os.path.dirname(__file__), granuleName)
    os.remove(path)

    return Dataset(lats, lons, times, values, variable, name=name, origin=origin)
