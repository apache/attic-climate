'use strict';

/* Services */


// Demonstrate how to register services
// In this case it is a simple value service.
angular.module('rcmes').service('evaluationSettings', function() {
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
