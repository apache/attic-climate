/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
**/

'use strict';

describe('directives', function() {
	beforeEach(module('ocw'));

	describe('preview-map directive', function() {
		it('should set the proper class', function() {
			inject(function($compile, $rootScope) {
				$rootScope.dataset = {latlonVals: {latMax: 90, lonMax: 90, latMin: -90, lonMin: -90}, name: "TRMM"};

				var element = $compile('<div preview-map="dataset"></div>')($rootScope);

				expect(element.hasClass("preview-map")).toBeTruthy();
			});
		});

		it('should set the id of the template to the name of the dataset', function() {
			inject(function($compile, $rootScope) {
				$rootScope.dataset = {latlonVals: {latMax: 90, lonMax: 90, latMin: -90, lonMin: -90}, name: "TRMM"};

				var element = $compile('<div preview-map="dataset"></div>')($rootScope);

				expect(element.attr('id')).toEqual("{{dataset.name}}");
			});
		});
	});
});
