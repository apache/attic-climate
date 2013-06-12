'use strict';

angular.module('rcmes', ['ui.date']).
	config(['$routeProvider', function($routeProvider) {
		$routeProvider.
			when('/obs', {templateUrl: 'partials/selectObservation.html',   controller: ObservationSelectCtrl}).
			when('/rcmed', {templateUrl: 'partials/selectRcmed.html', controller: RcmedSelectionCtrl}).
			otherwise({redirectTo: '/obs'});
	}]).
	run(function($rootScope) {
		$rootScope.evalResults = ""; 
		$rootScope.fillColors = ['#ff0000', '#00c90d', '#cd0074', '#f3fd00'];
		$rootScope.surroundColors = ['#a60000', '#008209', '#8f004b', '#93a400']
		$rootScope.baseURL = 'http://localhost:8082';
	});

