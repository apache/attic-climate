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


import ocw.data_source.podaac
import unittest
import ocw.dataset as Dataset

class TestPodaacDataSource(unittest.TestCase):
	@classmethod
	def setUpClass(self):
		self.datasetId = 'PODAAC-AKASA-XOGD1'
		self.datasetShortName = 'ALTIKA_SARAL_L2_OST_XOGDR'
		self.granuleName = podaac.retreive_granule_name(datasetId, datasetShortName)
    	self.variable =''
    	self.bbox = '45,0,180,90'
    	self.name = 'PO.DAAC_test_dataset'
    	self.file_path = os.path.dirname(os.path.abspath(__file__))
    	self.format = '.nc'
    	self.dataset = load_dataset(variable, datasetId, datasetShortName, bbox, name)	

	def test_is_valid_granule(self):
		length = len(self.granuleName)
		format = self.granuleName[length-3:length]
		self.assertTrue(format, self.format)

	def test_is_Dataset(self):
		self.assertTrue(isinstance(self.dataset, Dataset))
	
	def test_dataset_lats(self):
		self.assertEquals(len(self.dataset.lats), 29)

	def test_dataset_lons(self):
		self.assertEquals(len(self.dataset.lons), 26)

	def test_dataset_times(self):
		self.assertEquals(len(self.dataset.times), 1)

	def test_dataset_origin(self):
		self.assertEquals(self.dataset.origin['source'], 'PO.DAAC')
		self.assertEquals(self.dataset.origin['url'], 'podaac.jpl.nasa.gov/ws')

	def test_custom_name(self):
		self.assertEquals(self.dataset.name, self.name)

	def tearDown(self):
		path = os.path.join(os.path.dirname(__file__), '/'+ self.granuleName)
        os.remove(path)


if __name__ == '__main__':
    unittest.main()
