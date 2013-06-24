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

// We're creating a "global" application object. This allows us to keep module 
// names isolated to a single location as well as simplifying future init code.
var App =  App || {};

App.Services = angular.module('ocw.services', []);
App.Directives = angular.module('ocw.directives', []);
App.Controllers = angular.module('ocw.controllers', []);
App.Filters = angular.module('ocw.filters', []);

angular.module('ocw', ['ocw.services', 'ocw.directives', 'ocw.controllers', 'ocw.filters', 'ui.date']).
	config(['$routeProvider', function($routeProvider) {
		$routeProvider.
			when('/obs', {templateUrl: 'partials/selectObservation.html', controller: 'ObservationSelectCtrl'}).
			when('/rcmed', {templateUrl: 'partials/selectRcmed.html', controller: 'RcmedSelectionCtrl'}).
			otherwise({redirectTo: '/obs'});
	}]).
	run(function($rootScope) {
		$rootScope.evalResults = ""; 
		$rootScope.fillColors = ['#ff0000', '#00c90d', '#cd0074', '#f3fd00'];
		$rootScope.surroundColors = ['#a60000', '#008209', '#8f004b', '#93a400']
		$rootScope.baseURL = 'http://localhost:8082';
	});

