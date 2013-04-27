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

	describe('ObservationSelectCtrl', function() {
		it('should initialize observation variable parameters correctly', function() {
			var scope = {},
				ctrl = new ObservationSelectCtrl(scope);

				expect(scope.params.length).toBe(1);
				expect(scope.lats.length).toBe(1);
				expect(scope.lons.length).toBe(1);
				expect(scope.times.length).toBe(1);

				expect(scope.params[0]).toBe("Please select a file above");
				expect(scope.lats[0]).toBe("Please select a file above");
				expect(scope.lons[0]).toBe("Please select a file above");
				expect(scope.times[0]).toBe("Please select a file above");
		});
	});
});
