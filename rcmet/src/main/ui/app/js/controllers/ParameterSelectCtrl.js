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

// Controller for dataset parameter selection/modification
App.Controllers.controller('ParameterSelectCtrl', ['$rootScope', '$scope', '$http', '$timeout', 
						   'selectedDatasetInformation', 'regionSelectParams', 'evaluationSettings', 
function($rootScope, $scope, $http, $timeout, selectedDatasetInformation, regionSelectParams, evaluationSettings) {
	$scope.datasets = selectedDatasetInformation.getDatasets();

	// The min/max lat/lon values from the selected datasets
	$scope.latMin = -90;
	$scope.latMax = 90;
	$scope.lonMin = -180;
	$scope.lonMax = 180;
	$scope.start = "1980-01-01 00:00:00";
	$scope.end = "2030-01-01 00:00:00";

	// The min/max lat/lon values that are displayed
	$scope.displayParams = regionSelectParams.getParameters();

	$scope.runningEval = false;

	// Flag for toggling re-grid controls based on whether or not the user has selected a grid
	// base from the selected datasets. By default we have no datasets so we don't need to show
	// the controls!
	$scope.areInUserRegridState = false;

	// Initialization for the lat/lon grid step sliders
	// TODO There has to be a better way of dealing with this. Perhaps a directive??
	$scope.latSliderVal = 0;
	$scope.lonSliderVal = 0;

	$('#latSlider').slider({
		value: 0,
		step: 0.25,
		min: 0.25,
		max: 180,
		slide: function(event, ui) {
			updateLatSliderDisplayValue(ui.value);
		},
	});

	$('#lonSlider').slider({
		value: 0,
		step: 0.25,
		min: 0.25,
		max: 360,
		slide: function(event, ui) {
			updateLonSliderDisplayValue(ui.value);
		},
	});

	var updateLatSliderDisplayValue = function(value) {
		$scope.latSliderVal = value;
		$scope.$apply();
	}

	var updateLonSliderDisplayValue = function(value) {
		$scope.lonSliderVal = value;
		$scope.$apply();
	}

	// Settings for jQuery datepicker directives!
	$scope.datepickerSettings = {
		changeMonth: true,
		changeYear: true,
	};

	$scope.shouldDisableControls = function() {
		return (selectedDatasetInformation.getDatasetCount() < 2);
	}

	$scope.shouldDisableClearButton = function() {
		return (selectedDatasetInformation.getDatasetCount() == 0);
	}

	$scope.shouldDisableResultsView = function() {
		var res = false;

		if ($rootScope.evalResults == "")
			res = true;

		return res;
	}

	$scope.clearDatasets = function() {
		selectedDatasetInformation.clearDatasets();
	}

	$scope.runEvaluation = function() {
		$scope.runningEval = true;

		// TODO
		// Currently this has the 1 model, 1 observation format hard coded in. This shouldn't
		// be the long-term case! This needs to be changed!!!!!!!!
		var obsIndex = -1,
			modelIndex = -1;

		for (var i = 0; i < $scope.datasets.length; i++) {
			if ($scope.datasets[i]['isObs'] == 1)
				obsIndex = i;
			else
				modelIndex = i;
		}

		// TODO At the moment we aren't running all the metrics that the user selected. We're only
		// running the first available metric that the user provides. If the user un-checks all
		// metrics then the default of 'bias' is used.
		var metricToRun = 'bias';
		var settings = evaluationSettings.getSettings().metrics;
		for (var i = 0; i < settings.length; i++) {
			var setting = settings[i];

			if (setting.select) {
				metricToRun = setting.name;
				break;
			}
		};

		// You might wonder why this is using a jQuery ajax call instead of a built
		// in $http.post call. The reason would be that it wasn't working with the 
		// $http.post call but it is with this. So...there you go! This should be
		// changed eventually!!
		$.ajax({
			type: 'POST',
			url: $rootScope.baseURL + '/rcmes/run/', 
			data: { 
				'obsDatasetId'     : $scope.datasets[obsIndex]['id'],
				'obsParameterId'   : $scope.datasets[obsIndex]['param'],
				'startTime'        : $scope.displayParams.start + " 00:00:00",
				'endTime'          : $scope.displayParams.end + " 00:00:00",
				'latMin'           : $scope.displayParams.latMin,
				'latMax'           : $scope.displayParams.latMax,
				'lonMin'           : $scope.displayParams.lonMin,
				'lonMax'           : $scope.displayParams.lonMax,
				'filelist'         : $scope.datasets[modelIndex]['id'],
				'modelVarName'     : $scope.datasets[modelIndex]['param'],
				'modelTimeVarName' : $scope.datasets[modelIndex]['time'],
				'modelLatVarName'  : $scope.datasets[modelIndex]['lat'],
				'modelLonVarName'  : $scope.datasets[modelIndex]['lon'],
				'regridOption'     : 'model',
				'timeRegridOption' : evaluationSettings.getSettings().temporal.selected,
				'metricOption'     : metricToRun,
			},
			success: function(data) {
				var comp = data['comparisonPath'].split('/');
				var model = data['modelPath'].split('/');
				var obs = data['obsPath'].split('/');

				$rootScope.evalResults = {};
				$rootScope.evalResults.comparisonPath = comp[comp.length - 1];
				$rootScope.evalResults.modelPath = model[model.length - 1];
				$rootScope.evalResults.obsPath = obs[obs.length - 1];

				$scope.runningEval = false;

				$timeout(function() {
					$('#evaluationResults').trigger('modalOpen', true, true);
				}, 100);
			},
			error: function(xhr, status, error) {
				$scope.runningEval = false;
			},
		});
	}

	// Check the Parameter selection boxes after the user has changed input to ensure that valid
	// values were entered
	$scope.checkParameters = function() {
		if (parseFloat($scope.displayParams.latMin) < parseFloat($scope.latMin))
			$scope.displayParams.latMin = $scope.latMin;

		if (parseFloat($scope.displayParams.latMax) > parseFloat($scope.latMax))
			$scope.displayParams.latMax = $scope.latMax;

		if (parseFloat($scope.displayParams.lonMin) < parseFloat($scope.lonMin)) 
			$scope.displayParams.lonMin = $scope.lonMin;

		if (parseFloat($scope.displayParams.lonMax) > parseFloat($scope.lonMax)) 
			$scope.displayParams.lonMax = $scope.lonMax;

		if ($scope.displayParams.start < $scope.start) 
			$scope.displayParams.start = $scope.start;

		if ($scope.displayParams.end > $scope.end)
			$scope.displayParams.end = $scope.end;

		$scope.$apply();
		$rootScope.$broadcast('redrawOverlays', []);
	}

	$scope.$watch('datasets', 
		function() { 
			var numDatasets = $scope.datasets.length;
			$scope.displayParams.areValid = false;
			$scope.areInUserRegridState = false;

 			if (numDatasets) {
				var latMin        = -90,
					latMax        = 90,
					lonMin        = -180,
					lonMax        = 180,
					start         = "1980-01-01 00:00:00",
					end           = "2030-01-01 00:00:00",
					datasetRegrid = false;
 				// Get the valid lat/lon range in the selected datasets.
 				for (var i = 0; i < numDatasets; i++) {
 					var curDataset = $scope.datasets[i];
 	
 					latMin = (curDataset['latlonVals']['latMin'] > latMin) ? curDataset['latlonVals']['latMin'] : latMin;
 					latMax = (curDataset['latlonVals']['latMax'] < latMax) ? curDataset['latlonVals']['latMax'] : latMax;
 					lonMin = (curDataset['latlonVals']['lonMin'] > lonMin) ? curDataset['latlonVals']['lonMin'] : lonMin;
 					lonMax = (curDataset['latlonVals']['lonMax'] < lonMax) ? curDataset['latlonVals']['lonMax'] : lonMax;
 					start = (curDataset['timeVals']['start'] > start) ? curDataset['timeVals']['start'] : start;
 					end = (curDataset['timeVals']['end'] < end) ? curDataset['timeVals']['end'] : end;

					datasetRegrid = datasetRegrid || curDataset.regrid;

				}

				$scope.areInUserRegridState = !datasetRegrid
			}

			// Update the display parameters with the new valid overlap that we've found!
			$scope.displayParams.latMin = latMin;
			$scope.displayParams.latMax = latMax;
			$scope.displayParams.lonMin = lonMin;
			$scope.displayParams.lonMax = lonMax;
			$scope.displayParams.start = start.split(" ")[0];
			$scope.displayParams.end = end.split(" ")[0];

			// Update the local store values!
			$scope.latMin = latMin;
			$scope.latMax = latMax;
			$scope.lonMin = lonMin;
			$scope.lonMax = lonMax;
			$scope.start = start.split(" ")[0];
			$scope.end = end.split(" ")[0];

			$scope.displayParams.areValid = true;
			$rootScope.$broadcast('redrawOverlays', []);
		}, true);
}]);
