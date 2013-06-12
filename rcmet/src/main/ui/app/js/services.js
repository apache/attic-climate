'use strict';

/* Services */


// Demonstrate how to register services
// In this case it is a simple value service.
angular.module('rcmes').
	service('regionSelectParams', function() {
		var parameters = {
			"areValid" : true,
			"latMin"   : "",
			"latMax"   : "",
			"lonMin"   : "",
			"lonMax"   : "",
			"start"    : "",
			"end"      : "",
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
