'use strict';

// We're creating a "global" application object. This allows us to keep module 
// names isolated to a single location as well as simplifying future init code.
var App =  App || {};

App.Services = angular.module('ocw.services', []);
App.Directives = angular.module('ocw.directives', []);
App.Controllers = angular.module('ocw.controllers', []);

angular.module('ocw', ['ocw.services', 'ocw.directives', 'ocw.controllers', 'ui.date']).
	config(['$routeProvider', function($routeProvider) {
		$routeProvider.
			when('/obs', {templateUrl: 'partials/selectObservation.html', controller: 'ObservationSelectCtrl'}).
			when('/rcmed', {templateUrl: 'partials/selectRcmed.html', controller: 'RcmedSelectionCtrl'}).
			otherwise({redirectTo: '/obs'});
	}]).
	run(function($rootScope) {
		$rootScope.evalResults = ""; 
		$rootScope.fillColors = ['#ff0000', '#00c90d', '#cd0074', '#f3fd00'];
		$rootScope.surroundColors = ['#a60000', '#008209', '#8f004b', '#93a400']
		$rootScope.baseURL = 'http://localhost:8082';
	});

