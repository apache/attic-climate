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
	}).
	service('selectedDatasetInformation', function() {
		var datasets = [];

		return {
			getDatasets: function() {
				return datasets;
			},
			getDatasetCount: function() {
				return datasets.length;
			},
			// TODO: Define the structure of the objects that are added with addDataset.
			addDataset: function(dataset) {
				// All datasets need a shouldDisplay attribute that is used when rendering
				// the overlays on the map!
				dataset.shouldDisplay = true;
				// The regrid attribute indicates which dataset should be used for spatial regridding
				dataset.regrid = false;

				datasets.push(dataset);
			},
			removeDataset: function(index) {
				datasets.splice(index, 1);
			},
			clearDatasets: function() {
				datasets.length = 0;
			},
		};
	}).
	service('regionSelectParams', function() {
		var parameters = {
			"latMin": "",
			"latMax": "",
			"lonMin": "",
			"lonMax": "",
			"start" : "",
			"end"   : "",
		};

		return {
			getParameters: function() {
				return parameters;
			},
		};
    }).
	service('evaluationSettings', function() {
		var settings = {
			'metrics': [ 
				{'name': 'bias', 'select': true},
			],
			'temporal': {
				'options': ['daily', 'monthly', 'yearly'],
				'selected': 'monthly',
			},
		};

		return {
			getSettings: function() {
				return settings;
			}
		};
	});	
