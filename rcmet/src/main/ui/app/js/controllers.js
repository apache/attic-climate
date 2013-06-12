'use strict';

function SettingsCtrl($scope, evaluationSettings) {
	$scope.settings = evaluationSettings.getSettings();
}
