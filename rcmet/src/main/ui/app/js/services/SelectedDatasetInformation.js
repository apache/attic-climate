/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *    http: *www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
**/

// Service for giving controllers access to the information on datasets that 
// the user has selected for evaluation.
App.Services.service('selectedDatasetInformation', function() {
	var datasets = [];

	return {
		getDatasets: function() {
			return datasets;
		},
		getDatasetCount: function() {
			return datasets.length;
		},
		// TODO: Define the structure of the objects that are added with addDataset.
		addDataset: function(dataset) {
			// All datasets need a shouldDisplay attribute that is used when rendering
			// the overlays on the map!
			dataset.shouldDisplay = true;
			// The regrid attribute indicates which dataset should be used for spatial regridding
			dataset.regrid = false;

			datasets.push(dataset);
		},
		removeDataset: function(index) {
			datasets.splice(index, 1);
		},
		clearDatasets: function() {
			datasets.length = 0;
		},
	};
});
