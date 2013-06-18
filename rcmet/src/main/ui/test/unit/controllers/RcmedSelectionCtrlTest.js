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
	});
});
