'use strict';

angular.module('rcmes', []).
  config(['$routeProvider', function($routeProvider) {
  $routeProvider.
      when('/modelSelect', {templateUrl: 'partials/modelSelect.html', controller: ModelSelectCtrl}).
      otherwise({redirectTo: '/modelSelect'});
}]);
