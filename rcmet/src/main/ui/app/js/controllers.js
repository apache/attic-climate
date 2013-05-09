'use strict';

// Controller for the world map
function WorldMapCtrl($rootScope, $scope, selectedDatasetInformation, regionSelectParams) {
	$scope.datasets = selectedDatasetInformation.getDatasets();
	$scope.regionParams = regionSelectParams.getParameters();

	$scope.updateMap = function() {
 		
 		// Clear Group of layers from map if it exists
 		if ("rectangleGroup" in $rootScope) {
 			$rootScope.rectangleGroup.clearLayers();
 		}

		// Don't process if we don't have any datasets added!!
		if ($scope.datasets.length == 0)
			return;
 		
 		if ("map" in $rootScope) {
 			// Create Group to add all rectangles to map
 			$rootScope.rectangleGroup = L.layerGroup();
 			
 			// Loop through datasets and add rectangles to Group 
			var i = 0;
 			angular.forEach($scope.datasets, function(dataset) {
 				// Get bounds from dataset 
 				var maplatlon = dataset.latlonVals;
 				var bounds = [[maplatlon.latMax, maplatlon.lonMin], 
 				              [maplatlon.latMin, maplatlon.lonMax]];
 	
 				var polygon = L.rectangle(bounds,{
					stroke: false,
					fillColor: $rootScope.fillColors[i],
 				    fillOpacity: 0.3
 				});

 				// Add layer to Group
 				$rootScope.rectangleGroup.addLayer(polygon);
				i++;
 			});

			// Draw user selected region
			if ($scope.regionParams.latMin != "" && $scope.regionParams.latMax != "" && 
				$scope.regionParams.lonMin != "" && $scope.regionParams.lonMax != "") {

				var bounds = [[$scope.regionParams.latMax, $scope.regionParams.lonMin],
							  [$scope.regionParams.latMin, $scope.regionParams.lonMax]];

				var polygon = L.rectangle(bounds, {
					color: '#000000',
					opacity: 1.0,
					fill: false,
				});

				$rootScope.rectangleGroup.addLayer(polygon);
			}

 			// Add rectangle Group to map
 			$rootScope.rectangleGroup.addTo($rootScope.map);
 		}
	};

	$scope.$watch('datasets', function() {
		$scope.updateMap();
	}, true);

	$scope.$watch('regionParams', function() {
		$scope.updateMap();
	}, true);
};

// Controller for dataset parameter selection/modification
function ParameterSelectCtrl($rootScope, $scope, $http, $timeout, selectedDatasetInformation, regionSelectParams) {
	$scope.datasets = selectedDatasetInformation.getDatasets();

	// The min/max lat/lon values from the selected datasets
	$scope.latMin = -90;
	$scope.latMax = 90;
	$scope.lonMin = -180;
	$scope.lonMax = 180;
	$scope.start = "1980-01-01 00:00:00";
	$scope.end = "2030-01-01 00:00:00";

	// The min/max lat/lon values entered by the user
	$scope.enteredLatMin = "";
	$scope.enteredLatMax = "";
	$scope.enteredLonMin = "";
	$scope.enteredLonMax = "";
	$scope.enteredStart = "";
	$scope.enteredEnd = "";

	// The min/max lat/lon values that are displayed
	$scope.displayParams = regionSelectParams.getParameters();

	$scope.runningEval = false;
	
	var updateDisplayValues = function() {
		// Update the displayed lat/lon values. We give precedence to users entered values assuming
		// they're valid given the current set of datasets selected.
		//
		// If the user has entered a value for latMin
		if ($scope.enteredLatMin != "") {
			// If it's not a valid value...
			if ($scope.enteredLatMin < $scope.latMin) {
				// Reset enteredLatMin to the "unmodified" state and display the correct value.
				$scope.displayParams.latMin = $scope.latMin;
			} else {
				$scope.displayParams.latMin = $scope.enteredLatMin;
			}
		// Otherwise, just display the value.
		} else { 
			$scope.displayParams.latMin = $scope.latMin;
		}
		// Update latMax
		if ($scope.enteredLatMin != "") {
			if ($scope.enteredLatMax > $scope.latMax) {
				$scope.displayParams.latMax = $scope.latMax;
			} else {
				$scope.displayParams.latMax = $scope.enteredLatMax;
			}
		} else { 
			$scope.displayParams.latMax = $scope.latMax;
		}
		// Update lonMin
		if ($scope.enteredLonMin != "") {
			if ($scope.enteredLonMin < $scope.lonMin) {
				$scope.displayParams.lonMin = $scope.lonMin;
			} else {
				$scope.displayParams.lonMin = $scope.enteredLonMin;
			}
		} else { 
			$scope.displayParams.lonMin = $scope.lonMin;
		}
		// Update lonMax
		if ($scope.enteredLonMax != "") {
			if ($scope.enteredLonMax > $scope.lonMax) {
				$scope.displayParams.lonMax = $scope.lonMax;
			} else {
				$scope.displayParams.lonMax = $scope.enteredLonMax;
			}
		} else { 
			$scope.displayParams.lonMax = $scope.lonMax;
		}
		// Update Start time
		if ($scope.enteredStart != "") {
			if ($scope.enteredStart < $scope.start) {
				$scope.displayParams.start = $scope.start;
			} else {
				$scope.displayParams.start = $scope.enteredStart;
			}
		} else {
			$scope.displayParams.start = $scope.start;
		}
		// Update End time
		if ($scope.enteredEnd != "") {
			if ($scope.enteredEnd > $scope.end) {
				$scope.displayParams.end = $scope.end;
			} else {
				$scope.displayParams.end = $scope.enteredEnd;
			}
		} else {
			$scope.displayParams.end = $scope.end;
		}
	}

	$scope.shouldDisableControls = function() {
		return (selectedDatasetInformation.getDatasetCount() < 2);
	}

	$scope.shouldDisableEvaluate = function() {
		return ($scope.shouldDisableControls() || $scope.runningEval);
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

		// You might wonder why this is using a jQuery ajax call instead of a built
		// in $http.post call. The reason would be that it wasn't working with the 
		// $http.post call but it is with this. So...there you go! This should be
		// changed eventually!!
		$.ajax({
			type: "POST",
			url: "http://localhost:8082/rcmes/run/", 
			data: { 
				"obsDatasetId"     : $scope.datasets[obsIndex]['id'],
				"obsParameterId"   : $scope.datasets[obsIndex]['param'],
				"startTime"        : $scope.displayParams.start,
				"endTime"          : $scope.displayParams.end,
				"latMin"           : $scope.displayParams.latMin,
				"latMax"           : $scope.displayParams.latMax,
				"lonMin"           : $scope.displayParams.lonMin,
				"lonMax"           : $scope.displayParams.lonMax,
				"filelist"         : $scope.datasets[modelIndex]['id'],
				"modelVarName"     : $scope.datasets[modelIndex]['param'],
				"modelTimeVarName" : $scope.datasets[modelIndex]['time'],
				"modelLatVarName"  : $scope.datasets[modelIndex]['lat'],
				"modelLonVarName"  : $scope.datasets[modelIndex]['lon'],
				"regridOption"     : "model",
				"timeRegridOption" : "monthly",
				"metricOption"     : "bias",
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

	$scope.updateParameters = function() {
		// Save the user input, even if it isn't valid.
		$scope.enteredLatMin = $scope.displayParams.latMin;
		$scope.enteredLatMax = $scope.displayParams.latMax;
		$scope.enteredLonMin = $scope.displayParams.lonMin;
		$scope.enteredLonMax = $scope.displayParams.lonMax;
		$scope.enteredStart  = $scope.displayParams.start;
		$scope.enteredEnd    = $scope.displayParams.end;

		// Check if the user values are valid and update the display values.
		updateDisplayValues();
	}

	$scope.$watch('datasets', 
		function() { 
			var numDatasets = $scope.datasets.length;

 			if (numDatasets) {
				var latMin = -90,
					latMax = 90,
					lonMin = -180,
					lonMax = 180,
					start  = "1980-01-01 00:00:00",
					end    = "2030-01-01 00:00:00";
 			
 				// Get the valid lat/lon range in the selected datasets.
 				for (var i = 0; i < numDatasets; i++) {
 					var curDataset = $scope.datasets[i];
 	
 					latMin = (curDataset['latlonVals']['latMin'] > latMin) ? curDataset['latlonVals']['latMin'] : latMin;
 					latMax = (curDataset['latlonVals']['latMax'] < latMax) ? curDataset['latlonVals']['latMax'] : latMax;
 					lonMin = (curDataset['latlonVals']['lonMin'] > lonMin) ? curDataset['latlonVals']['lonMin'] : lonMin;
 					lonMax = (curDataset['latlonVals']['lonMax'] < lonMax) ? curDataset['latlonVals']['lonMax'] : lonMax;
 					start = (curDataset['timeVals']['start'] > start) ? curDataset['timeVals']['start'] : start;
 					end = (curDataset['timeVals']['end'] < end) ? curDataset['timeVals']['end'] : end;
				}
			}

			$scope.latMin = latMin;
			$scope.latMax = latMax;
			$scope.lonMin = lonMin;
			$scope.lonMax = lonMax;
			$scope.start = start;
			$scope.end = end;

			updateDisplayValues();
		}, true);
}

// Controller for dataset display
function DatasetDisplayCtrl($rootScope, $scope, selectedDatasetInformation) {
	$scope.datasets = selectedDatasetInformation.getDatasets();

	$scope.removeDataset = function($index) {
		selectedDatasetInformation.removeDataset($index);
	}
}

// Controller for observation selection in modal
function ObservationSelectCtrl($rootScope, $scope, $http, selectedDatasetInformation) {
	// Initalize the option arrays and default to the first element
	$scope.params      = ["Please select a file above"];
	$scope.paramSelect = $scope.params[0];
	$scope.lats        = ["Please select a file above"];
	$scope.latsSelect  = $scope.lats[0];
	$scope.lons        = ["Please select a file above"];
	$scope.lonsSelect  = $scope.lons[0];
	$scope.times       = ["Please select a file above"];
	$scope.timeSelect  = $scope.times[0];

	// TODO: We could probably completely remove these variables...
	$scope.latLonVals = [];
	$scope.timeVals = [];
	$scope.localSelectForm = {};

	$scope.uploadLocalFile = function() {
		// TODO: Need to try to validate the input a bit. At least make sure we're not
		// pointing at a directory perhaps?
		
		// TODO: Two-way binding with ng-model isn't being used here because it fails to update
		// properly with the auto-complete that we're using on the input box. So we're doing
		// it the wrong way temporarily...
		var input = $('#observationFileInput').val();

		// TODO: We're not really handling the case where there is a failure here at all. 
		// Should check for fails and allow the user to make changes.
		//
	    // Get model variables
		$http.jsonp('http://localhost:8082/list/vars/"' + input + '"?callback=JSON_CALLBACK').
			success(function(data) {
				if ("FAIL" in data) {
					$scope.params = ["Unable to find variable(s)"];
				} else {
					$scope.params = data['variables'];
				}

				// Select the first element so the display isn't empty
				$scope.paramSelect = $scope.params[0];
			}).
			error(function(data) {
				$scope.params = ["Unable to find variable(s)"];
				$scope.paramSelect = $scope.params[0];
			});		

		// Get Lat and Lon variables
		$http.jsonp('http://localhost:8082/list/latlon/"' + input + '"?callback=JSON_CALLBACK').
			success(function(data) {
				if (data["success"] == 0) {
					$scope.lats = ["Unable to find variable(s)"];
					$scope.lons = ["Unable to find variable(s)"];
				} else {
					$scope.lats = [data["latname"]];
					$scope.lons = [data["lonname"]];

					var tmpMinsMaxs = [data["latMin"], data["latMax"], data["lonMin"], data["lonMax"]];
					$scope.latLonVals = tmpMinsMaxs.map(parseFloat);
				}

				// Select the first element so the displays aren't empty
				$scope.latsSelect = $scope.lats[0];
				$scope.lonsSelect = $scope.lons[0];
			}).
			error(function(data) {
				$scope.lats = ["Unable to find variable(s)"];
				$scope.lons = ["Unable to find variable(s)"];
				$scope.latsSelect = $scope.lats[0];
				$scope.lonsSelect = $scope.lons[0];
			});		

		// Get Time variables
		$http.jsonp('http://localhost:8082/list/time/"' + input + '"?callback=JSON_CALLBACK').
			success(function(data) {
				if (data["success"] == 0) {
					$scope.times = ["Unable to find variable(s)"];
				} else {
					if (data["timename"] instanceof Array) {
						$scope.times = data["timename"];
					} else {
						$scope.times = [data["timename"]];
					}

					$scope.timeVals = [data["start_time"], data["end_time"]];
				}

				// Select the first element so the display isn't empty
				$scope.timeSelect = $scope.times[0];
			}).
			error(function(data) {
				$scope.times = ["Unable to find variable(s)"];
				$scope.timeSelect = $scope.times[0];
			});		
	};

	$scope.addDataSet = function() {
		// TODO: Need to verify that all the variables selected are correct!!!
		// TODO: We shouldn't allow different parameters to match the same variables!!

		var newDataset = {};
		var input = $('#observationFileInput').val();

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
	}
}

function RcmedSelectionCtrl($rootScope, $scope, $http, selectedDatasetInformation) {
	var getObservations = function() {
		$http.jsonp('http://localhost:8082/getObsDatasets?callback=JSON_CALLBACK').
			success(function(data) {
				$scope.availableObs = data;
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
		var urlString = 'http://localhost:8082/getDatasetParam?dataset=' + 
							$scope.datasetSelection["shortname"] + 
							"&callback=JSON_CALLBACK";
		$http.jsonp(urlString).
			success(function(data) {
				$scope.retrievedObsParams = data;
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
	};

	// Grab the available observations from RCMED
	getObservations();
}
