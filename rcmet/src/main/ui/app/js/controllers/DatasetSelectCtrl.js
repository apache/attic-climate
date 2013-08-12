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

// Controller for dataset selection/modification
App.Controllers.controller('DatasetSelectCtrl', ['$scope', 'selectedDatasetInformation',
function($scope, selectedDatasetInformation) {

    // Grab a copy of the datasets so we can display a count to the user!
    $scope.datasetCount = selectedDatasetInformation.getDatasets();

    $scope.shouldDisableClearButton = function() {
      return (selectedDatasetInformation.getDatasetCount() == 0);
    }

    $scope.clearDatasets = function() {
      selectedDatasetInformation.clearDatasets();
    }

    $scope.open = function () {
      $scope.datasetSelect = true;
    }

    $scope.close = function () {
      $scope.datasetSelect = false;
    }

    $scope.opts = {
      backdropFade: true,
      dialogFade:true
    };

    $scope.templates =
      [ { title:'Local File', url: 'partials/selectObservation.html'}
      , { title:'RCMED', url: 'partials/selectRcmed.html'}
      , { title:'ESG', disabled: true } ];

    $scope.template = $scope.templates[0];

}]);
