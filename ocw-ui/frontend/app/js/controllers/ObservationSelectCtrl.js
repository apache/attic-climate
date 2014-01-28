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

// Controller for observation selection in modal
App.Controllers.controller('ObservationSelectCtrl', ['$rootScope', '$scope', '$http', '$q', '$timeout', 'selectedDatasetInformation',
function($rootScope, $scope, $http, $q, $timeout, selectedDatasetInformation) {
	// Grab a copy of the datasets so we can display a count to the user!
	$scope.datasetCount = selectedDatasetInformation.getDatasets();

	// Initalize the option arrays and default to the first element
	$scope.params      = ["Please select a file above"];
	$scope.paramSelect = $scope.params[0];
	$scope.lats        = ["Please select a file above"];
	$scope.latsSelect  = $scope.lats[0];
	$scope.lons        = ["Please select a file above"];
	$scope.lonsSelect  = $scope.lons[0];
	$scope.times       = ["Please select a file above"];
	$scope.timeSelect  = $scope.times[0];

	// Grab the path leader information that the webserver is using to limit directory access.
	$scope.pathLeader = 'False';
	$http.jsonp($rootScope.baseURL + '/getPathLeader/?callback=JSON_CALLBACK').
		success(function(data) {
			$scope.pathLeader = data.leader;
	});

	// Toggle load button view depending on upload state of selected files
	$scope.loadingFile = false;

	// Toggle display of a confirmation when loading a dataset
	$scope.fileAdded = false;

	$scope.latLonVals = [];
	$scope.timeVals = [];
	$scope.localSelectForm = {};

	$scope.uploadLocalFile = function() {
		$scope.loadingFile = true;

		// TODO: Need to try to validate the input a bit. At least make sure we're not
		// pointing at a directory perhaps?
		
		// TODO: Two-way binding with ng-model isn't being used here because it fails to update
		// properly with the auto-complete that we're using on the input box. So we're doing
		// it the wrong way temporarily...
		var input = $('#observationFileInput').val();

		// If the backend is limiting directory access we need to add that leader to our path
		// so it remains valid!
		if ($scope.pathLeader != 'False') {
			input = $scope.pathLeader + input
		}

		// TODO: We're not really handling the case where there is a failure here at all. 
		// Should check for fails and allow the user to make changes.
		//
		// Get model variables
		var varsPromise = $http.jsonp($rootScope.baseURL + '/list/vars/"' + input + '"?callback=JSON_CALLBACK');
		// Get Lat and Lon variables
		var latlonPromise = $http.jsonp($rootScope.baseURL + '/list/latlon/"' + input + '"?callback=JSON_CALLBACK');
		// Get Time variables
		var timesPromise = $http.jsonp($rootScope.baseURL + '/list/time/"' + input + '"?callback=JSON_CALLBACK');

		$q.all([varsPromise, latlonPromise, timesPromise]).then(
			// Handle success fetches!
			function(arrayOfResults) {
				$scope.loadingFile = false;

				// Handle lat/lon results
				var data = arrayOfResults[1].data;
				$scope.lats = [data.latname];
				$scope.lons = [data.lonname];
				$scope.latLonVals = [data.latMin, data.latMax, data.lonMin, data.lonMax];

				// If there is more than one option for the user, tell them they need to pick one!
				if ($scope.lats.length > 1) $scope.lats.splice(0, 0, "Please select an option");
				if ($scope.lons.length > 1) $scope.lons.splice(0, 0, "Please select an option");
				// Default the display to the first available option.
				$scope.latsSelect = $scope.lats[0];
				$scope.lonsSelect = $scope.lons[0];

				// Handle time results
				var data = arrayOfResults[2].data
				$scope.times = [data.timename];
				$scope.timeVals = [data.start_time, data.end_time];

				if ($scope.times.length > 1) $scope.times.splice(0, 0, "Please select an option");
				$scope.timeSelect = $scope.times[0];

				// Handle parameter results
				var data = arrayOfResults[0].data.variables;
				$scope.params = (data instanceof Array) ? data : [data];
				$scope.params = $.grep($scope.params, 
									function(val) {
										return ($.inArray(val, $scope.lats)  != 0 && 
												$.inArray(val, $scope.lons)  != 0 && 
												$.inArray(val, $scope.times) != 0);
									});
				
				if ($scope.params.length > 1) $scope.params.splice(0, 0, "Please select an option");
				$scope.paramSelect = $scope.params[0];
			},
			// Uh oh! AT LEAST on of our fetches failed
			function(arrayOfFailure) {
				$scope.loadingFile = false;

				$scope.params      = ["Unable to load variable(s)"];
				$scope.paramSelect = $scope.params[0];
				$scope.lats        = ["Unable to load variable(s)"];
				$scope.latsSelect  = $scope.lats[0];
				$scope.lons        = ["Unable to load variable(s)"];
				$scope.lonsSelect  = $scope.lons[0];
				$scope.times       = ["Unable to load variable(s)"];
				$scope.timeSelect  = $scope.times[0];
			}
		);
	};

	$scope.addDataSet = function() {
		// TODO: Need to verify that all the variables selected are correct!!!
		// TODO: We shouldn't allow different parameters to match the same variables!!

		var newDataset = {};
		var input = $('#observationFileInput').val();

		// If the backend is limiting directory access we need to add that leader to our path
		// so it remains valid!
		if ($scope.pathLeader != 'False') {
			input = $scope.pathLeader + input
		}

		newDataset['isObs'] = 0;
		// Save the model path. Note that the path is effectively the "id" for the model.
		newDataset['id'] = input;
		// Grab the file name later for display purposes.
		var splitFilePath = input.split('/');
		newDataset['name'] = splitFilePath[splitFilePath.length - 1];
		// Save the model parameter variable. We save it twice for consistency and display convenience.
		newDataset['param'] = $scope.paramSelect;
		newDataset['paramName'] = newDataset['param'];
		// Save the lat/lon information
		newDataset['lat'] = $scope.latsSelect;
		newDataset['lon'] = $scope.lonsSelect;

		newDataset['latlonVals'] = {"latMin": $scope.latLonVals[0], "latMax": $scope.latLonVals[1],
									"lonMin": $scope.latLonVals[2], "lonMax": $scope.latLonVals[3]};
		// Get the time information
		newDataset['time'] = $scope.timeSelect;
		newDataset['timeVals'] = {"start": $scope.timeVals[0], "end": $scope.timeVals[1]};

		selectedDatasetInformation.addDataset(newDataset);

		// Reset all the fields!!
		$scope.params = ["Please select a file above"];
		$scope.paramSelect = $scope.params[0];
		$scope.lats = ["Please select a file above"];
		$scope.latsSelect = $scope.lats[0];
		$scope.lons = ["Please select a file above"];
		$scope.lonsSelect = $scope.lons[0];
		$scope.times = ["Please select a file above"];
		$scope.timeSelect = $scope.times[0];
		$scope.latLonVals = [];
		$scope.timeVals = [];

		// Clear the input box
		$('#observationFileInput').val("");

		// Display a confirmation message for a little bit
		$scope.fileAdded = true;
		$timeout(function() {
			$scope.fileAdded = false;
		}, 2000);
	}

	$scope.shouldDisableLoadButton = function() {
		return $scope.loadingFile;
	}
}]);
