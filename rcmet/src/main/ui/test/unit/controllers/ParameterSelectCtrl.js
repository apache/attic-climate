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

		it('should set the default datepicker settings', function() {
			inject(function($rootScope, $controller) {
				var scope = $rootScope.$new();
				var ctrl = $controller("ParameterSelectCtrl", {$scope: scope});

				// This tests the default values that get passed to the datepicker objects that we
				// initialize with a directive.
				expect(Object.keys(scope.datepickerSettings).length).toBe(2);
				expect(scope.datepickerSettings.changeMonth).toBe(true);
				expect(scope.datepickerSettings.changeYear).toBe(true);
			});
		});

		it('should define the slide "slide" callback functions', function() {
			inject(function($rootScope, $controller) {
				var scope = $rootScope.$new();
				var ctrl = $controller("ParameterSelectCtrl", {$scope: scope});

				expect(scope.latSliderVal).toBe(0);
				expect(scope.lonSliderVal).toBe(0);
				scope.updateLatSliderDisplayValue(1);
				scope.updateLonSliderDisplayValue(2);
				expect(scope.latSliderVal).toBe(1);
				expect(scope.lonSliderVal).toBe(2);
			});
		});

		it('should initialize the control disable function', function() {
			inject(function($rootScope, $controller) {
				var scope = $rootScope.$new();
				var ctrl = $controller("ParameterSelectCtrl", {$scope: scope});

				expect(scope.shouldDisableControls()).toBe(true);
				// Add to dummy values to datasets to make sure the disable function
				// triggers properly.
				scope.datasets.push(1);
				scope.datasets.push(2);
				expect(scope.shouldDisableControls()).toBe(false);
			});
		});

		it('should initialize the disable clear button function', function() {
			inject(function($rootScope, $controller) {
				var scope = $rootScope.$new();
				var ctrl = $controller("ParameterSelectCtrl", {$scope: scope});

				expect(scope.shouldDisableClearButton()).toBe(true);
				scope.datasets.push(1);
				scope.datasets.push(2);
				expect(scope.shouldDisableClearButton()).toBe(false);
			});
		});

		it('should initialize the disable results view function', function() {
			inject(function($rootScope, $controller) {
				$rootScope.evalResults = "";
				var scope = $rootScope.$new();
				var ctrl = $controller("ParameterSelectCtrl", {$rootScope: $rootScope, $scope: scope});

				expect(scope.shouldDisableResultsView()).toBe(true);

				// Set evalResults to something other than the default value
				$rootScope.evalResults = "this is not an empty string";

				expect(scope.shouldDisableResultsView()).toBe(false);
			});
		});

		it('should initialize the clear datasets function', function() {
			inject(function($rootScope, $controller) {
				var scope = $rootScope.$new();
				var ctrl = $controller("ParameterSelectCtrl", {$rootScope: $rootScope, $scope: scope});

				scope.datasets.push(1);
				expect(scope.datasets.length).toBe(1);
				scope.clearDatasets();
				expect(scope.datasets.length).toBe(0);
			});
		});

		it('should initialize the check parameters function', function() {
			inject(function($rootScope, $controller) {
				var scope = $rootScope.$new();
				var ctrl = $controller("ParameterSelectCtrl", {$scope: scope});

				// Set the displayParams values to be "out of bounds" values so checkParams 
				// adjusts them properly.
				scope.displayParams.latMin = "-95";
				scope.displayParams.latMax = "95";
				scope.displayParams.lonMin = "-185";
				scope.displayParams.lonMax = "185";
				scope.displayParams.start = "1980-00-00 00:00:00";
				scope.displayParams.end = "2031-01-01 00:00:00";

				// If we don't remove the watch on datasets we end up with displayParam values 
				// all being undefined (but only during testing, which is odd...)
				scope.unwatchDatasets();
				scope.checkParameters();

				expect(scope.displayParams.latMin).toBe(-90);
				expect(scope.displayParams.latMax).toBe(90);
				expect(scope.displayParams.lonMin).toBe(-180);
				expect(scope.displayParams.lonMax).toBe(180);
				expect(scope.displayParams.start).toBe('1980-01-01 00:00:00');
				expect(scope.displayParams.end).toBe('2030-01-01 00:00:00');
			});
		});
	});
});
