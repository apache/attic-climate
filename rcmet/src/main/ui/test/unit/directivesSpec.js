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
	beforeEach(module('rcmes'));

	// Testing Leaflet map directive
	/*
	describe('Testing Leaflet map directive', function() {
		it('should create the leaflet dir for proper injection into the page', function() {
			inject(function($compile, $rootScope) {
				var element = $compile('<sap id="map"></sap>')($rootScope);
				expect(element.className).toBe('leaflet-container leaflet-fade-anim');
			})
		});
	});
	//*/
	
	// Testing the Bootstrap Modal directive
	describe('bootstrap-modal directive', function() {
		it('should create a div element of the correct form', function() {
			inject(function($compile, $rootScope) {
				var element = $compile('<bootstrap-modal modal-id="testmodal"></bootstrap-modal>')($rootScope);
				expect(element.hasClass("modal")).toBeTruthy();
				expect(element.hasClass("hide")).toBeTruthy();
				expect(element.attr("id")).toEqual('{{modalId}}');
			});
		});

		it('should properly wrap the interior html content' , function() {
			inject(function($compile, $rootScope) {
				var element = $compile('<bootstrap-modal modal-id="testmodal"><h3>Hello</h3></bootstrap-modal>')($rootScope);
				expect(element.html()).toEqual("<div ng-transclude=\"\"><h3 class=\"ng-scope\">Hello</h3></div>");
			})
		});
	});
});
