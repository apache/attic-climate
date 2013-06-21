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

	describe('WorldMapCtrl', function() {
		it('should initialize the updateMap function', function() {
			inject(function($rootScope, $controller) {
				var scope = $rootScope.$new();
				var ctrl = $controller("WorldMapCtrl", {$scope: scope});

				// Set the important attributes for a fake dataset
				scope.datasets.push({shouldDisplay: true, latlonVals: {latMin: 0, latMax: 0, lonMin: 0, lonMax: 0}});
				// Don't try to add the user defined region since we don't have one
				scope.regionParams.areValid = false;
				// We need to fake the map object. The only thing we care about is faking the "addLayer" function
				$rootScope.map = {addLayer: function(){}};
				$rootScope.fillColors = ['#ff0000'];

				expect("rectangleGroup" in $rootScope).toBe(false);
				scope.updateMap();
				expect("rectangleGroup" in $rootScope).toBe(true);
			});
		});
	});
});
