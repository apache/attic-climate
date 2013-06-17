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

// Controller for dataset display
App.Controllers.controller('DatasetDisplayCtrl', ['$rootScope', '$scope', 'selectedDatasetInformation', 
function($rootScope, $scope, selectedDatasetInformation) {
	$scope.datasets = selectedDatasetInformation.getDatasets();

	$scope.removeDataset = function($index) {
		selectedDatasetInformation.removeDataset($index);
	}

	$scope.setRegridBase = function(index) {
		for (var i = 0; i < $scope.datasets.length; i++) {
			$scope.datasets[i].regrid = ((i == index) ? $scope.datasets[i].regrid : false);
		}
	}
}]);
