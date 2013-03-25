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
}
