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

	describe('ObservationSelectCtrl', function() {
		it('should grab the default set of selected datasets from the service', function() {
			inject(function($httpBackend, $rootScope, $controller) {
				$rootScope.baseURL = "http://localhost:8082"
				$httpBackend.expectJSONP($rootScope.baseURL + '/getPathLeader/?callback=JSON_CALLBACK').
					respond(200, {'leader': '/usr/local/rcmes'});

				var scope = $rootScope.$new();
				var ctrl = $controller("ObservationSelectCtrl", {$scope: scope});
				$httpBackend.flush();

				expect(typeof scope.datasetCount).toBe('object');
				expect(Object.keys(scope.datasetCount).length).toBe(0);
			});
		});

		it('should initialize option arrays and default to the first element', function() {
			inject(function($httpBackend, $rootScope, $controller) {
				$rootScope.baseURL = "http://localhost:8082"
				$httpBackend.expectJSONP($rootScope.baseURL + '/getPathLeader/?callback=JSON_CALLBACK').
					respond(200, {'leader': '/usr/local/rcmes'});

				var scope = $rootScope.$new();
				var ctrl = $controller("ObservationSelectCtrl", {$scope: scope});
				$httpBackend.flush();

				expect(scope.params.length).toBe(1);
				expect(scope.lats.length).toBe(1);
				expect(scope.lons.length).toBe(1);
				expect(scope.times.length).toBe(1);

				expect(scope.params[0]).toEqual("Please select a file above");
				expect(scope.lats[0]).toEqual("Please select a file above");
				expect(scope.lons[0]).toEqual("Please select a file above");
				expect(scope.times[0]).toEqual("Please select a file above");
			});
		});

		it('should initialize scope attributes properly', function() {
			inject(function($httpBackend, $rootScope, $controller) {
				$rootScope.baseURL = "http://localhost:8082"
				$httpBackend.expectJSONP($rootScope.baseURL + '/getPathLeader/?callback=JSON_CALLBACK').
					respond(200, {'leader': '/usr/local/rcmes'});

				var scope = $rootScope.$new();
				var ctrl = $controller("ObservationSelectCtrl", {$scope: scope});
				$httpBackend.flush();

				expect(scope.pathLeader).toEqual('/usr/local/rcmes');
				expect(scope.loadingFile).toBe(false);
				expect(scope.fileAdded).toBe(false);
				expect(typeof scope.latLonVals).toEqual('object');
				expect(scope.latLonVals.length).toBe(0);
				expect(typeof scope.timeVals).toEqual('object');
				expect(scope.timeVals.length).toEqual(0);
				expect(typeof scope.localSelectForm).toEqual('object');
				expect(Object.keys(scope.localSelectForm).length).toEqual(0);
			});
		});
	});
});
