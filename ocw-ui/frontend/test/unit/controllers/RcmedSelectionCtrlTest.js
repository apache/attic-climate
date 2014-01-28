/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *    http: *www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
**/

'use strict';

describe('OCW Controllers', function() {

	beforeEach(module('ocw.controllers'));
	beforeEach(module('ocw.services'));

	describe('RcmedSelectionCtrl', function() {
		it('should automatically query RCMED on initialization', function() {
			inject(function($rootScope, $controller, $httpBackend) {
				$rootScope.baseURL = "http://localhost:8082"
				$httpBackend.expectJSONP($rootScope.baseURL + '/getObsDatasets?callback=JSON_CALLBACK').
					respond(200, [{longname: 1}, {longname: 2}]);

				var scope = $rootScope.$new();
				var ctrl = $controller("RcmedSelectionCtrl", {$scope: scope});
				$httpBackend.flush();

				expect(scope.availableObs.length).toBe(3);
				expect(scope.availableObs[0]).toEqual({longname: "Please select an option"});
				expect(scope.availableObs[1]).toEqual({longname: 1});
			});
		});

		it('should initialize the getObservations function', function() {
			inject(function($rootScope, $controller, $httpBackend) {
				$rootScope.baseURL = "http://localhost:8082"
				$httpBackend.expectJSONP($rootScope.baseURL + '/getObsDatasets?callback=JSON_CALLBACK').
					respond(200, [{longname: 1}, {longname: 2}]);

				var scope = $rootScope.$new();
				var ctrl = $controller("RcmedSelectionCtrl", {$scope: scope});
				$httpBackend.flush();

				expect(scope.availableObs.length).toBe(3);
				expect(scope.availableObs[0]).toEqual({longname: "Please select an option"});
				expect(scope.availableObs[1]).toEqual({longname: 1});

				// Set up a failed query
				$httpBackend.expectJSONP($rootScope.baseURL + '/getObsDatasets?callback=JSON_CALLBACK').
					respond(404);
				scope.getObservations();
				$httpBackend.flush();

				expect(scope.availableObs.length).toBe(1);
				expect(scope.availableObs[0]).toEqual('Unable to query RCMED');

			});
		});

		it('should initialze the getObservationTimeRange function', function() {
			inject(function($rootScope, $controller, $httpBackend) {
				$rootScope.baseURL = "http://localhost:8082"
				$httpBackend.expectJSONP($rootScope.baseURL + '/getObsDatasets?callback=JSON_CALLBACK').
					respond(200, [{longname: 1}, {longname: 2}]);

				var scope = $rootScope.$new();
				var ctrl = $controller("RcmedSelectionCtrl", {$scope: scope});
				$httpBackend.flush();

				expect(scope.getObservationTimeRange(1)).toEqual({'start' : '1989-01-01 00:00:00',
				                                                    'end' : '2009-12-31 00:00:00'});
				expect(scope.getObservationTimeRange(-1)).toEqual(false);
			});
		});

		it('should initialize dataSelectUpdated function', function() {
			inject(function($rootScope, $controller, $httpBackend) {
				$rootScope.baseURL = "http://localhost:8082"
				$httpBackend.expectJSONP($rootScope.baseURL + '/getObsDatasets?callback=JSON_CALLBACK').
					respond(200, [{longname: 1}, {longname: 2}]);

				var scope = $rootScope.$new();
				var ctrl = $controller("RcmedSelectionCtrl", {$scope: scope});
				$httpBackend.flush();

				// Add the test dataset to our scope
				scope.datasetSelection = {shortname: 'TRMM'}

				// Test return with only single parameter
				$httpBackend.expectJSONP($rootScope.baseURL + '/getDatasetParam?dataset=' + 
										scope.datasetSelection['shortname'] + 
										'&callback=JSON_CALLBACK').
							 respond(200, ['pcp']);
				scope.dataSelectUpdated();
				$httpBackend.flush();

				expect(scope.parameterSelection).toEqual('pcp');

				// Test return with multiple parameters
				$httpBackend.expectJSONP($rootScope.baseURL + '/getDatasetParam?dataset=' + 
										scope.datasetSelection['shortname'] + 
										'&callback=JSON_CALLBACK').
							 respond(200, ['pcp', 'pcp2']);
				scope.dataSelectUpdated();
				$httpBackend.flush();

				expect(scope.parameterSelection).toEqual({shortname: 'Please select a parameter'});
			});
		});

		it('should initialze the addObservation function', function() {
			inject(function($rootScope, $controller, $httpBackend) {
				$rootScope.baseURL = "http://localhost:8082"
				$httpBackend.expectJSONP($rootScope.baseURL + '/getObsDatasets?callback=JSON_CALLBACK').
					respond(200, [{longname: 1}, {longname: 2}]);

				var scope = $rootScope.$new();
				var ctrl = $controller("RcmedSelectionCtrl", {$scope: scope});
				$httpBackend.flush();

				scope.datasetSelection = {
					"dataset_id" : "3",
					"shortname"  : "TRMM",
					"longname"   : "Tropical Rainfall Measuring Mission Dataset",
					"source"     : "Readme for the Tropical Rainfall Measuring Mission (TRMM) Data Set"
				};

				scope.parameterSelection = {
					"parameter_id":"36",
					"shortname":"pcp",
					"datasetshortname":"TRMM",
					"longname":"TRMM v.6 Monthly Precipitation",
					"units":"mm\/day"
				};

				// addObservations does a refresh of the selections with a re-query of the backend
				// so we need to catch that call!
				$httpBackend.expectJSONP($rootScope.baseURL + '/getObsDatasets?callback=JSON_CALLBACK').
					respond(200, [{longname: 1}, {longname: 2}]);

				scope.addObservation();
				$httpBackend.flush();
				
				expect(scope.datasetCount.length).toBe(1);
				// The selection observation should be reset so we shouldn't have
				// any selected observation parameters.
				expect(scope.retrievedObsParams).toEqual([]);
			});
		});
	});
});
