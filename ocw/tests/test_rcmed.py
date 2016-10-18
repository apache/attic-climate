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

import unittest
import datetime
import numpy
import pickle
import inspect
import os
import test_rcmed  # Import test_rcmed so we can use inspect to get the path
import ocw.data_source.rcmed as rcmed


class CustomAssertions:
    # Custom Assertions to handle Numpy Arrays

    def assert1DArraysEqual(self, array1, array2):
        self.assertSequenceEqual(tuple(array1), tuple(array2))


class test_rcmed(unittest.TestCase, CustomAssertions):

    def setUp(self):
        self.dataset_id = 2
        self.parameter_id = 15
        self.min_lat = 50
        self.max_lat = 70
        self.min_lon = 1
        self.max_lon = 15
        self.start_time = datetime.datetime(2002, 8, 1)
        self.end_time = datetime.datetime(2002, 10, 1)
        # start and end time for URL to query database is the beginning and end
        # of start_time and end_time
        self.start_time_for_url = "20020801T0000Z"
        self.end_time_for_url = "20021001T2359Z"
        self.url = "http://rcmes.jpl.nasa.gov/query-api/query.php?"
        self.lats = numpy.arange(50.5, 70, 1)
        self.lons = numpy.arange(1.5, 15, 1)
        # In this parameter, two days of 10/20 and 10/21 have been missed.
        self.times_list = [datetime.datetime(
            2002, 8, 31) + datetime.timedelta(days=x) for x in range(0, 62)]
        self.times_list.remove(datetime.datetime(2002, 10, 20))
        self.times_list.remove(datetime.datetime(2002, 10, 21))
        self.times = numpy.array(self.times_list)

        # Get the full path to test_rcmed
        self.file_path = os.path.abspath(inspect.getfile(test_rcmed))
        # Remove the end of our path so we're left with the directory in which
        # test_rcmed.py is stored.
        self.file_path = self.file_path.split('test_rcmed')[0]

        # Grab the parameter values file
        params_file = open(os.path.join(
            self.file_path, "parameters_values.p"), "rb")
        self.values = pickle.load(params_file)
        # Grab the parameter metadata file
        meta_file = open(os.path.join(
            self.file_path, "parameters_metadata_output.p"), "rb")
        self.param_metadata_output = pickle.load(meta_file)

    def return_text(self, url):
        if url == self.url + ("datasetId={0}&"
                              "parameterId={1}&"
                              "latMin={2}&"
                              "latMax={3}&"
                              "lonMin={4}&"
                              "lonMax={5}&"
                              "timeStart={6}&"
                              "timeEnd={7}").format(self.dataset_id,
                                                    self.parameter_id,
                                                    self.min_lat,
                                                    self.max_lat,
                                                    self.min_lon,
                                                    self.max_lon,
                                                    self.start_time_for_url,
                                                    self.end_time_for_url):
            return open(os.path.join(self.file_path,
                                     "parameter_dataset_text.txt"))
        elif url == self.url + "&param_info=yes":
            return open(os.path.join(self.file_path,
                                     "parameters_metadata_text.txt"))
        else:
            raise Exception("The URL is not acceptable.")

    def test_function_get_parameters_metadata(self):
        rcmed.urllib2.urlopen = self.return_text
        self.assertEqual(rcmed.get_parameters_metadata(),
                         self.param_metadata_output)

    def test_function_parameter_dataset_lats_monthly(self):
        self.dataset_id = 6
        self.parameter_id = 32
        self.end_time_for_url = "20021031T0000Z"
        rcmed.urllib2.urlopen = self.return_text
        self.assert1DArraysEqual(rcmed.parameter_dataset(self.dataset_id,
                                                         self.parameter_id,
                                                         self.min_lat,
                                                         self.max_lat,
                                                         self.min_lon,
                                                         self.max_lon,
                                                         self.start_time,
                                                         self.end_time).lats,
                                 self.lats)

    def test_function_parameter_dataset_lats(self):
        rcmed.urllib2.urlopen = self.return_text
        self.assert1DArraysEqual(rcmed.parameter_dataset(self.dataset_id,
                                                         self.parameter_id,
                                                         self.min_lat,
                                                         self.max_lat,
                                                         self.min_lon,
                                                         self.max_lon,
                                                         self.start_time,
                                                         self.end_time).lats,
                                 self.lats)

    def test_function_parameter_dataset_lons(self):
        rcmed.urllib2.urlopen = self.return_text
        self.assert1DArraysEqual(rcmed.parameter_dataset(self.dataset_id,
                                                         self.parameter_id,
                                                         self.min_lat,
                                                         self.max_lat,
                                                         self.min_lon,
                                                         self.max_lon,
                                                         self.start_time,
                                                         self.end_time).lons,
                                 self.lons)

    def test_function_parameter_dataset_times(self):
        rcmed.urllib2.urlopen = self.return_text
        self.assert1DArraysEqual(rcmed.parameter_dataset(self.dataset_id,
                                                         self.parameter_id,
                                                         self.min_lat,
                                                         self.max_lat,
                                                         self.min_lon,
                                                         self.max_lon,
                                                         self.start_time,
                                                         self.end_time).times,
                                 self.times)

    def test_function_parameter_dataset_values(self):
        rcmed.urllib2.urlopen = self.return_text
        self.assert1DArraysEqual(rcmed.parameter_dataset(self.dataset_id,
                                                         self.parameter_id,
                                                         self.min_lat,
                                                         self.max_lat,
                                                         self.min_lon,
                                                         self.max_lon,
                                                         self.start_time,
                                                         self.end_time)
                                 .values.flatten(),
                                 self.values.flatten())

    def test_function_parameter_dataset_name(self):
        rcmed.urllib2.urlopen = self.return_text
        ds = rcmed.parameter_dataset(self.dataset_id,
                                     self.parameter_id,
                                     self.min_lat,
                                     self.max_lat,
                                     self.min_lon,
                                     self.max_lon,
                                     self.start_time,
                                     self.end_time,
                                     name='foo')
        self.assertEquals(ds.name, 'foo')

    def test_dataset_origin(self):
        rcmed.urllib2.urlopen = self.return_text
        ds = rcmed.parameter_dataset(self.dataset_id,
                                     self.parameter_id,
                                     self.min_lat,
                                     self.max_lat,
                                     self.min_lon,
                                     self.max_lon,
                                     self.start_time,
                                     self.end_time,
                                     name='foo')

        self.assertEquals(ds.origin['source'], 'rcmed')
        self.assertEquals(ds.origin['dataset_id'], self.dataset_id)
        self.assertEquals(ds.origin['parameter_id'], self.parameter_id)

if __name__ == '__main__':
    unittest.main()
