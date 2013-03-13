'use strict';

/* jasmine specs for controllers go here */

describe('RCMES Controllers', function() {

	describe('ParameterSelectCtrl', function() {
		it('should create a ParameterSelectCtrl with 0 datasets', function() {
			var scope = {},
				ctrl = new ParameterSelectCtrl(scope);

				expect(scope.numberOfDatasets).toBe(0);
		});

		it('should not activate controls unless there are at least 2 datasets', function() {
			var scope = {},
				ctrl = new ParameterSelectCtrl(scope);

				// Test default case of 0 datasets
				expect(scope.shouldDisableControls()).toBe(true);

				// Push up to the minimum number of datasets and test validity
				scope.numberOfDatasets = 2;
				expect(scope.shouldDisableControls()).toBe(false);
		});
	});
});
