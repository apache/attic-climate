'use strict';

angular.module('rcmes', []).
	config(['$routeProvider', function($routeProvider) {
	$routeProvider.
		when('/obs', {templateUrl: 'partials/selectObservation.html',   controller: ObservationSelectCtrl}).
		when('/rcmed', {templateUrl: 'partials/selectRcmed.html', controller: ObservationSelectCtrl}).
		otherwise({redirectTo: '/obs'});
}]);
