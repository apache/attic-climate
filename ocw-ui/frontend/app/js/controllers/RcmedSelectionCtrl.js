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
		$http.jsonp($rootScope.baseURL + '/rcmed/datasets/?callback=JSON_CALLBACK').
			success(function(data) {
				$scope.availableObs = data;
				$scope.availableObs.splice(0, 0, {longname: 'Please select an option'});
				$scope.datasetSelection = $scope.availableObs[0];
			}).
			error(function(data) {
				$scope.availableObs = ["Unable to query RCMED"]
			});
	};

    $scope.getObservationBounds = function() {
        $scope.observationBounds = {};

		$http.get($rootScope.baseURL + '/rcmed/parameters/bounds/').
        success(function(data) {
            $scope.observationBounds = data;
            $scope.observationBounds['default'] = {
                'start': '1900-01-01 00:00:00',
                'end': '2050-01-01 00:00:00',
                'latMin': -90,
                'latMax': 89,
                'lonMin': -180,
                'lonMax': 179,
            };
        }).
        error(function(data) {
            $scope.observationBounds['default'] = {
                'start': '1900-01-01 00:00:00',
                'end': '2050-01-01 00:00:00',
                'latMin': -90,
                'latMax': 89,
                'lonMin': -180,
                'lonMax': 179,
            };
        });
    };

    $scope.getBoundsByParameterId = function(parameterId) {
        if (parameterId in $scope.observationBounds) {
            return $scope.observationBounds[parameterId];
        } else {
            return $scope.observationBounds['default'];
        }
    };

	$scope.dataSelectUpdated = function() {
		var urlString = $rootScope.baseURL + '/rcmed/parameters/?dataset=' +
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
		var newDataset = {};

		newDataset['isObs'] = 1;
		// Save the dataset id (the important part) and name (for display purposes)
		newDataset['datasetId'] = $scope.datasetSelection['dataset_id'];
		newDataset['name'] = $scope.datasetSelection['longname'];
		// Save the parameter id (the important part) and name (for display purposes)
		newDataset['id']    = $scope.parameterSelection['parameter_id'];
		newDataset['param'] = $scope.parameterSelection['parameter_id'];
		newDataset['paramName'] = $scope.parameterSelection['longname'];

        bounds = $scope.getBoundsByParameterId(newDataset['id']);
        newDataset['latlonVals'] = {
            'latMin': bounds['lat_min'],
            'latMax': bounds['lat_max'],
            'lonMin': bounds['lon_min'],
            'lonMax': bounds['lon_max'],
        };
        newDataset['timeVals'] = {
            'start': bounds['start_date'],
            'end': bounds['end_date'],
        };

        // Set some defaults for lat/lon/time variable names. This just helps
        // us display stuff later.
		newDataset['lat'] = "N/A";
		newDataset['lon'] = "N/A";
		newDataset['time'] = "N/A";

		selectedDatasetInformation.addDataset(newDataset);

		// Clear the user selections by requery-ing RCMED. This is really hacky, but it works for now...
		$scope.availableObs = [];
		$scope.retrievedObsParams = [];
		$scope.getObservations();

		// Display a confirmation message for a little bit
		$scope.fileAdded = true;
		$timeout(function() {
			$scope.fileAdded = false;
		}, 2000);
	};

    // Grab the available observations from RCMED
    $scope.getObservations();
    $scope.getObservationBounds();
}]);
