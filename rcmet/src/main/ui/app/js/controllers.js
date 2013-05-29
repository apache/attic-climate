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
			var i = -1;
 			angular.forEach($scope.datasets, function(dataset) {
				// Keep track of dataset count for displaying colors
				i++;

				// If the user disabled the overlay then get out of here!
				if (!dataset.shouldDisplay)
					return;

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
function ParameterSelectCtrl($rootScope, $scope, $http, $timeout, selectedDatasetInformation, 
							 regionSelectParams, evaluationSettings) {
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
				'startTime'        : $scope.displayParams.start,
				'endTime'          : $scope.displayParams.end,
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
				'timeRegridOption' : 'monthly',
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

	$scope.setRegridBase = function(index) {
		for (var i = 0; i < $scope.datasets.length; i++) {
			$scope.datasets[i].regrid = ((i == index) ? $scope.datasets[i].regrid : false);
		}
	}
}

// Controller for observation selection in modal
function ObservationSelectCtrl($rootScope, $scope, $http, $q, $timeout, selectedDatasetInformation) {
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
}

function RcmedSelectionCtrl($rootScope, $scope, $http, $timeout, selectedDatasetInformation) {
	// Grab a copy of the datasets so we can display a count to the user!
	$scope.datasetCount = selectedDatasetInformation.getDatasets();
	$scope.fileAdded = false;

	var getObservations = function() {
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
	getObservations();
}

function SettingsCtrl($scope, evaluationSettings) {
	$scope.settings = evaluationSettings.getSettings();
}
