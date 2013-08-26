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
        #start and end time for URL to query database is the beginning and end of start_time and end_time
        self.start_time_for_url = "20020801T0000Z"
        self.end_time_for_url = "20021031T0000Z"
        self.url = "http://rcmes.jpl.nasa.gov/query-api/query.php?"
        self.lats=numpy.arange(50.5, 70, 1)
        self.lons=numpy.arange(1.5, 15, 1)
        #In this parameter, two days of 10/20 and 10/21 have been missed.
        self.times_list=[datetime.datetime(2002, 8, 31) + datetime.timedelta(days=x) for x in range(0, 62)]
        self.times_list.remove(datetime.datetime(2002, 10, 20))
        self.times_list.remove(datetime.datetime(2002, 10, 21))
        self.times = numpy.array(self.times_list)
        self.values = pickle.load( open( "parameters_values.p", "rb" ) )
        self.param_metadata_output = pickle.load( open( "parameters_metadata_output.p", "rb" ) ) 


    def return_text(self, url):
        if url == self.url + "datasetId={0}&parameterId={1}&latMin={2}&latMax={3}&lonMin={4}&lonMax={5}&timeStart=20020801T0000Z&timeEnd=20021031T0000Z"\
                .format(self.dataset_id, self.parameter_id, self.min_lat, self.max_lat, self.min_lon, self.max_lon, self.start_time_for_url, self.end_time_for_url):
            return open("parameter_dataset_text.txt")
        elif url == self.url + "&param_info=yes":
            return open("parameters_metadata_text.txt")
        else:
            raise Exception ("The URL is not acceptable.")


    def test_function_get_parameters_metadata(self):
        rcmed.urllib2.urlopen = self.return_text
        self.assertEqual(rcmed.get_parameters_metadata(), self.param_metadata_output)


    def test_function_parameter_dataset_lats(self):
        rcmed.urllib2.urlopen = self.return_text
        self.assert1DArraysEqual(rcmed.parameter_dataset(self.dataset_id, self.parameter_id, self.min_lat, self.max_lat, self.min_lon, self.max_lon, self.start_time, self.end_time).lats, self.lats)


    def test_function_parameter_dataset_lons(self):
        rcmed.urllib2.urlopen = self.return_text
        self.assert1DArraysEqual(rcmed.parameter_dataset(self.dataset_id, self.parameter_id, self.min_lat, self.max_lat, self.min_lon, self.max_lon, self.start_time, self.end_time).lons, self.lons)


    def test_function_parameter_dataset_times(self):
        rcmed.urllib2.urlopen = self.return_text
        self.assert1DArraysEqual(rcmed.parameter_dataset(self.dataset_id, self.parameter_id, self.min_lat, self.max_lat, self.min_lon, self.max_lon, self.start_time, self.end_time).times, self.times)


    def test_function_parameter_dataset_values(self):
        rcmed.urllib2.urlopen = self.return_text
        self.assert1DArraysEqual(rcmed.parameter_dataset(self.dataset_id, self.parameter_id, self.min_lat, self.max_lat, self.min_lon, self.max_lon, self.start_time, self.end_time).values.flatten(), self.values.flatten())


if __name__ == '__main__':
    unittest.main()