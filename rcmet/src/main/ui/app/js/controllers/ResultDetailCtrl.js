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

// Controller for result page
App.Controllers.controller('ResultDetailCtrl', ['$rootScope', '$scope', '$http', '$stateParams',
function($rootScope, $scope, $http, $stateParams) {

	// Grab all figures 
	$scope.result = $stateParams.resultId;
	
	$http.jsonp($rootScope.baseURL + '/getResults//' + $scope.result + '?callback=JSON_CALLBACK')
	.success(function(data) {
	  if (data.length < 1){
		$scope.figures = null;
		$scope.alertMessage = "No results found.";
		$scope.alertClass = "alert alert-danger";
	  } else {
		$scope.figures = data;
	  }
	});

}]);
