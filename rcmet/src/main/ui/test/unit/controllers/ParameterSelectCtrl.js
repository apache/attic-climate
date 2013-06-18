'use strict';

describe('OCW Controllers', function() {

	beforeEach(module('ocw.controllers'));
	beforeEach(module('ocw.services'));


	describe('ParameterSelectCtrl', function() {
		it('should initialize spatial and temporal range default values properly', function() {
			inject(function($rootScope, $controller) {
				var scope = $rootScope.$new();
				var ctrl = $controller("ParameterSelectCtrl", {$scope: scope});

				expect(scope.latMin).toBe(-90);
				expect(scope.latMax).toBe(90);
				expect(scope.lonMin).toBe(-180);
				expect(scope.lonMax).toBe(180);
				expect(scope.start).toBe("1980-01-01 00:00:00");
				expect(scope.end).toBe("2030-01-01 00:00:00");
			});
		});

		it('should grab the default set of selected datasets from the service', function() {
			inject(function($rootScope, $controller) {
				var scope = $rootScope.$new();
				var ctrl = $controller("ParameterSelectCtrl", {$scope: scope});

				// We should get an object with no keys since the user hasn't selected any
				// datasets by default. Object.keys returns an array of all the user defined
				// keys in the object.
				expect(typeof scope.datasets).toBe('object');
				expect(Object.keys(scope.datasets).length).toBe(0);
			});
		});

		it('should grab the default region select param object from the regionSelectParams service', function() {
			inject(function($rootScope, $controller) {
				var scope = $rootScope.$new();
				var ctrl = $controller("ParameterSelectCtrl", {$scope: scope});

				// The default display values aren't going to be changing any time soon. This test 
				// is a bit of a duplicate since this is really testing functionality of the service.
				// Can't hurt to make sure that we're getting results though!
				expect(typeof scope.displayParams).toBe('object');
				expect(Object.keys(scope.displayParams).length).toBe(7);
			});
		});

		it('should initialize misc. values properly', function() {
			inject(function($rootScope, $controller) {
				var scope = $rootScope.$new();
				var ctrl = $controller("ParameterSelectCtrl", {$scope: scope});
				
				expect(scope.runningEval).toBe(false);
				expect(scope.areInUserRegridState).toBe(false);
				expect(scope.latSliderVal).toBe(0);
				expect(scope.lonSliderVal).toBe(0);
			});
		});
	});
});
