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

App.Controllers.controller('RcmedSelectionCtrl', ['$rootScope', '$scope', '$http', '$timeout', 'selectedDatasetInformation', 
function($rootScope, $scope, $http, $timeout, selectedDatasetInformation) {
	// Grab a copy of the datasets so we can display a count to the user!
	$scope.datasetCount = selectedDatasetInformation.getDatasets();
	$scope.fileAdded = false;

	$scope.getObservations = function() {
		$http.jsonp($rootScope.baseURL + '/getObsDatasets?callback=JSON_CALLBACK').
			success(function(data) {
				$scope.availableObs = data;
				$scope.availableObs.splice(0, 0, {longname: 'Please select an option'});
				$scope.datasetSelection = $scope.availableObs[0];
			}).
			error(function(data) {
				$scope.availableObs = ["Unable to query RCMED"]
			});
	};

	var getObservationTimeRange = function(datasetID) {
		var times = {
			'1' : {'start' : '1989-01-01 00:00:00','end' : '2009-12-31 00:00:00'},	// ERA-Interim
			'2' : {'start' : '2002-08-31 00:00:00','end' : '2010-01-01 00:00:00'},	// AIRS
			'3' : {'start' : '1998-01-01 00:00:00','end' : '2010-01-01 00:00:00'},	// TRMM
			'4' : {'start' : '1948-01-01 00:00:00','end' : '2010-01-01 00:00:00'},	// URD
			'5' : {'start' : '2000-02-24 00:00:00','end' : '2010-05-30 00:00:00'},	// MODIS
			'6' : {'start' : '1901-01-01 00:00:00','end' : '2006-12-01 00:00:00'}   // CRU
		};

		return ((datasetID in times) ? times[datasetID] : false);
	};

	$scope.dataSelectUpdated = function() {
		var urlString = $rootScope.baseURL + '/getDatasetParam?dataset=' + 
							$scope.datasetSelection["shortname"] + 
							"&callback=JSON_CALLBACK";
		$http.jsonp(urlString).
			success(function(data) {
				$scope.retrievedObsParams = data;
				if ($scope.retrievedObsParams.length > 1) 
					$scope.retrievedObsParams.splice(0, 0, {shortname: 'Please select a parameter'});
				$scope.parameterSelection = $scope.retrievedObsParams[0];
			});
	};

	$scope.addObservation = function() {
		// This is a horrible hack for temporarily getting a valid time range
		// for the selected observation. Eventually we need to handle this more
		// elegantly than indexing into an array...
		var timeRange = getObservationTimeRange($scope.datasetSelection["dataset_id"]);

		var newDataset = {};

		newDataset['isObs'] = 1;
		// Save the dataset id (the important part) and name (for display purposes)
		newDataset['id'] = $scope.datasetSelection['dataset_id'];
		newDataset['name'] = $scope.datasetSelection['longname'];
		// Save the parameter id (the important part) and name (for display purposes)
		newDataset['param'] = $scope.parameterSelection['parameter_id'];
		newDataset['paramName'] = $scope.parameterSelection['longname'];
		// Save the (fake) lat/lon information. Our datasets cover the entire globe (I think...)
		newDataset['latlonVals'] = {"latMin": -90, "latMax": 90, "lonMin": -180, "lonMax": 180};
		// Set some defaults for lat/lon variable names. This just helps us display stuff later.
		newDataset['lat'] = "N/A";
		newDataset['lon'] = "N/A";
		// Save time range information. If we don't have saved data for this observation then
		// we set the values to extreme values so they'll be ignored when calculating overlaps.
		newDataset['timeVals'] = {"start": (timeRange) ? timeRange['start'] : "1901-01-01 00:00:00",
								  "end": (timeRange) ? timeRange['end'] : "2050-01-01 00:00:00"};
		// Set a default for the time variable names for display convenience.
		newDataset['time'] = "N/A";

		selectedDatasetInformation.addDataset(newDataset);

		// Clear the user selections by requery-ing RCMED. This is really hacky, but it works for now...
		$scope.availableObs = [];
		$scope.retrievedObsParams = [];
		getObservations();

		// Display a confirmation message for a little bit
		$scope.fileAdded = true;
		$timeout(function() {
			$scope.fileAdded = false;
		}, 2000);
	};

	// Grab the available observations from RCMED
	$scope.getObservations();
}]);
