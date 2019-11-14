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


import ocw.data_source.podaac_datasource as podaac
import unittest
import os
import datetime as dt
from ocw.dataset import Dataset

@unittest.skip("CLIMATE-959 Remove ocw.tests.test_podaac.TestPodaacDataSource from tests until service is more reliable")
class TestPodaacDataSource(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.datasetId = 'PODAAC-GHCMC-4FM02'
        cls.variable = 'sea_ice_fraction'
        cls.name = 'PO.DAAC_test_dataset'
        cls.file_path = os.path.dirname(os.path.abspath(__file__))
        cls.format = '.nc'
        cls.dataset = podaac.extract_l4_granule(cls.variable, cls.datasetId, cls.name)
        # Currently the PO.DAAC subsetting is only available for Level2 granules,
        # plans are underway to extend this to Level3 and 4 granules and OCW can make use
        # of this when that functionality becomes available. More information about Level2
        # subsetting can be found at https://podaac.jpl.nasa.gov/ws/subset/granule/index.html
        #cls.json = 'subset.json'
        #cls.subset_datasetId = 'PODAAC-GHRAM-4FA01'
        #cls.subset_variable = 'analysed_sst'
        #cls.subset_name = 'GHRSST Level 4 RAMSSA Australian Regional Foundation Sea Surface Temperature Analysis'
        #cls.granule_subset = podaac.subset_granule(
        #    cls.subset_variable,
        #    cls.subset_datasetId,
        #    name=cls.subset_name,
        #    input_file_path=cls.json)

    def test_is_dataset(self):
        print('in test_is_dataset')
        self.assertTrue(isinstance(self.dataset, Dataset))

    def test_dataset_lats(self):
        print('in test_dataset_lats')
        self.assertEquals(len(self.dataset.lats), 901)

    def test_dataset_lons(self):
        print('in test_dataset_lons')
        self.assertEquals(len(self.dataset.lons), 1800)

    def test_dataset_times(self):
        print('in test_dataset_times')
        self.assertEquals(len(self.dataset.times), 1)

    def test_dataset_values(self):
        print('in test_dataset_values')
        self.assertEquals(len(self.dataset.values), 1)

    def test_valid_date_conversion(self):
        print('in test_valid_date_conversion')
        start = dt.datetime(1991, 9, 2, 12)
        self.assertTrue(start == self.dataset.times[0])

    def test_dataset_origin(self):
        print('in test_dataset_origin')
        self.assertEquals(self.dataset.origin['source'], 'NASA JPL PO.DAAC')
        self.assertEquals(self.dataset.origin['url'], 'https://podaac.jpl.nasa.gov')

    def test_custom_name(self):
        print('in test_custom_name')
        self.assertEquals(self.dataset.name, self.name)

    #def test_granule_subset(self):
    #    print('in test_granule_subset')
    #    self.assertEquals(self.granule_subset.name, self.subset_name)

if __name__ == '__main__':
    unittest.main()
