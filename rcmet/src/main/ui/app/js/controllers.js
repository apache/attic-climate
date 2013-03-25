'use strict';

// Controller for the world map
function WorldMapCtrl($scope) {
}

// Controller for dataset parameter selection/modification
function ParameterSelectCtrl($scope) {
	$scope.numberOfDatasets = 0;

	$scope.shouldDisableControls = function() {
		return ($scope.numberOfDatasets < 2);
	}

	$scope.runEvaluation = function() {
	}

	$scope.addDataset = function() {
	}

	$scope.updateParameters = function() {
	}
}

// Controller for observation selection in modal
function ObservationSelectCtrl($scope) {
	$scope.params = ["Please select a file above"];
	$scope.lats = ["Please select a file above"];
	$scope.lons = ["Please select a file above"];
	$scope.times = ["Please select a file above"];

	$scope.uploadLocalFile = function() {
		// Need to make a request to the bottle services
		// Then upload the local bindings
	};

	$scope.addDataSet = function() {
		// Need to add the dataset information to the correct model for the main div
	}
}
