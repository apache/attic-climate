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

		it('should initialize the uploadLocalFile function', function() {
			inject(function($httpBackend, $rootScope, $controller) {
				$rootScope.baseURL = "http://localhost:8082"
				$httpBackend.expectJSONP($rootScope.baseURL + '/getPathLeader/?callback=JSON_CALLBACK').
					respond(200, {'leader': '/usr/local/rcmes'});

				var scope = $rootScope.$new();
				var ctrl = $controller("ObservationSelectCtrl", {$scope: scope});
				$httpBackend.flush();

				$httpBackend.expectJSONP($rootScope.baseURL + '/list/vars/"/usr/local/rcmesundefined"?callback=JSON_CALLBACK').
					respond(200, {"variables": ["lat", "lon", "prec", "time" ]});
				$httpBackend.expectJSONP($rootScope.baseURL + '/list/latlon/"/usr/local/rcmesundefined"?callback=JSON_CALLBACK').
					respond(200, {'latMax': '75.25', 'success': 1, 'latname': 'lat', 'lonMax': '-29.75', 'lonMin': '-159.75', 'lonname': 'lon', 'latMin': '15.25'});
				$httpBackend.expectJSONP($rootScope.baseURL + '/list/time/"/usr/local/rcmesundefined"?callback=JSON_CALLBACK').
					respond(200, {"start_time": "1980-01-01 00:00:00", "timename": "time", "success": 1, "end_time": "2004-12-01 00:00:00"});

				scope.uploadLocalFile();
				$httpBackend.flush();

				expect(scope.latsSelect).toEqual("lat");
				expect(scope.lonsSelect).toEqual("lon");
				expect(scope.timeSelect).toEqual("time");
				expect(scope.paramSelect).toEqual("prec");

				// Simulate failure on one of the backend calls. Should
				$httpBackend.expectJSONP($rootScope.baseURL + '/list/vars/"/usr/local/rcmesundefined"?callback=JSON_CALLBACK').
					respond(200, {});
				$httpBackend.expectJSONP($rootScope.baseURL + '/list/latlon/"/usr/local/rcmesundefined"?callback=JSON_CALLBACK').
					respond(404, {});
				$httpBackend.expectJSONP($rootScope.baseURL + '/list/time/"/usr/local/rcmesundefined"?callback=JSON_CALLBACK').
					respond(200, {});

				scope.uploadLocalFile();
				$httpBackend.flush();

				expect(scope.paramSelect).toEqual("Unable to load variable(s)");
				expect(scope.params.length).toEqual(1);
				expect(scope.latsSelect).toEqual("Unable to load variable(s)");
				expect(scope.lats.length).toEqual(1);
				expect(scope.lonsSelect).toEqual("Unable to load variable(s)");
				expect(scope.lons.length).toEqual(1);
				expect(scope.timeSelect).toEqual("Unable to load variable(s)");
				expect(scope.times.length).toEqual(1);
			});
		});

		it('should initialize the addDatasets function', function() {
			inject(function($httpBackend, $rootScope, $controller) {
				$rootScope.baseURL = "http://localhost:8082"
				$httpBackend.expectJSONP($rootScope.baseURL + '/getPathLeader/?callback=JSON_CALLBACK').
					respond(200, {'leader': '/usr/local/rcmes'});

				var scope = $rootScope.$new();
				var ctrl = $controller("ObservationSelectCtrl", {$scope: scope});
				$httpBackend.flush();

				// Add a bunch of bogus data as a dataset
				scope.addDataSet();

				expect(scope.datasetCount.length).toBe(1);
			});
		});
	});
});
