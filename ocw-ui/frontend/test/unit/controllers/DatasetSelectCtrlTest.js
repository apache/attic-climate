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

	describe('DatasetSelectCtrl', function() {
		it('should initialize the disable clear button function', function() {
			inject(function($rootScope, $controller, selectedDatasetInformation) {
				var scope = $rootScope.$new();
				var ctrl = $controller('DatasetSelectCtrl', {$scope: scope});

				expect(scope.shouldDisableClearButton()).toBe(true);
				selectedDatasetInformation.addDataset({});
				expect(scope.shouldDisableClearButton()).toBe(false);
			});
		});

		it('should initialize the clear datasets function', function() {
			inject(function($rootScope, $controller, selectedDatasetInformation) {
				var scope = $rootScope.$new();
				var ctrl = $controller('DatasetSelectCtrl', {$rootScope: $rootScope, $scope: scope});

				selectedDatasetInformation.addDataset({});
				expect(selectedDatasetInformation.getDatasetCount()).toBe(1);
				scope.clearDatasets();
				expect(selectedDatasetInformation.getDatasetCount()).toBe(0);
			});
		});
	});
});
