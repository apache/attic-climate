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

angular.module('ocw', ['ocw.services', 'ocw.directives', 'ocw.controllers', 'ocw.filters', 'ui.date', 'ui.bootstrap', 'ui.compat', 'ui.state'])
.config(
    [        '$stateProvider', '$routeProvider', '$urlRouterProvider',
    function ($stateProvider,   $routeProvider,   $urlRouterProvider) {
      $urlRouterProvider
        .when('/r?id', '/results/:id')
        .otherwise('/');

      $routeProvider
        .when('/evaluation/:id', {
          redirectTo: '/results/:id',
        })
        .when('/', {
          redirectTo: '/evaluate',
        });

      $stateProvider
        .state('main',{
          url: '/evaluate',
          templateUrl: 'partials/main.html',
        })
        .state('results', {
          url: '/results',
          abstract: true,
          templateUrl: 'partials/results.html',
          controller: 'ResultCtrl'
        })
        .state('results.list', {
          // parent: 'results',
          url: '',
          templateUrl: 'partials/results.list.html',
        })
        .state('results.detail', {
          // parent: 'results',
          url: '/{resultId}',
          views: {
            '': {
              templateUrl: 'partials/results.detail.html',
              controller: 'ResultDetailCtrl'
            },
            'menu': {
              templateProvider:
                [ '$stateParams',
                function ($stateParams){
                  return '<hr><small class="muted">result ID: ' + $stateParams.resultId + '</small>';
                }],
            },
          },
        });
    }])
.run(
    [        '$rootScope', '$state', '$stateParams',
    function ($rootScope,   $state,   $stateParams) {
      $rootScope.$state = $state;
      $rootScope.$stateParams = $stateParams;
      $rootScope.evalResults = ""; 
      $rootScope.fillColors = ['#ff0000', '#00c90d', '#cd0074', '#f3fd00'];
      $rootScope.surroundColors = ['#a60000', '#008209', '#8f004b', '#93a400']
      $rootScope.baseURL = 'http://localhost:8082';
}]);

