/**
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
 */

'use strict';

/**
 * @ngdoc function
 * @name ocwUiApp.controller:ParameterSelectCtrl
 * @description
 * # ParameterSelectCtrl
 * Controller of the ocwUiApp
 */
angular.module('ocwUiApp')
.controller('ParameterSelectCtrl', ['$rootScope', '$scope', '$http', '$timeout',
						   'selectedDatasetInformation', 'regionSelectParams', 'evaluationSettings',
  function($rootScope, $scope, $http, $timeout, selectedDatasetInformation, regionSelectParams, evaluationSettings) {
    $scope.datasets = selectedDatasetInformation.getDatasets();

    // The min/max lat/lon values from the selected datasets
    $scope.latMin = -90;
    $scope.latMax = 90;
    $scope.lonMin = -180;
    $scope.lonMax = 180;
    $scope.start = "1900-01-01 00:00:00";
    $scope.end = "2030-01-01 00:00:00";

    // The min/max lat/lon values that are displayed
    $scope.displayParams = regionSelectParams.getParameters();

    $scope.runningEval = false;

    // Flag for toggling re-grid controls based on whether or not the user has selected a grid
    // base from the selected datasets. By default we have no datasets so we don't need to show
    // the controls!
    $scope.areInUserRegridState = false;

    // Initialization for the lat/lon grid step sliders
    // TODO There has to be a better way of dealing with this. Perhaps a directive??
    $scope.latSliderVal = 0;
    $scope.lonSliderVal = 0;

    // Settings for jQuery datepicker directives!
    $scope.datepickerSettings = {
      changeMonth: true,
      changeYear: true,
    };

    $scope.shouldDisableControls = function() {
      return (selectedDatasetInformation.getDatasetCount() < 2);
    }

    $scope.shouldDisableEvaluateButton = function() {
      return ($scope.shouldDisableControls() || $scope.runningEval);
    }

    $scope.shouldDisableResultsView = function() {
      var res = false;

      if ($rootScope.evalResults == "")
        res = true;

      return res;
    }

    $scope.runEvaluation = function() {
      $scope.runningEval = true;

      var data = {}
      var settings = evaluationSettings.getSettings()

      // Set dataset information

      // Grab the reference dataset information
      var ref_ds = settings.spatialSelect;

      if (ref_ds == null) {
        ref_ds = $scope.datasets[0];
      }

      data['reference_dataset'] = null;
      data['target_datasets'] = [];

      // Parse all the dataset information and generate the necessary objects for the backend
      for (var i = 0; i < $scope.datasets.length; i++) {
        var dataset = {}
        dataset['dataset_info'] = {}

        if ($scope.datasets[i].isObs == 0) {
          dataset['data_source_id'] = 1;
          dataset['dataset_info']['dataset_id'] = $scope.datasets[i]['id'];
          dataset['dataset_info']['var_name'] = $scope.datasets[i]['param'];
          dataset['dataset_info']['lat_name'] = $scope.datasets[i]['lat'];
          dataset['dataset_info']['lon_name'] = $scope.datasets[i]['lon'];
          dataset['dataset_info']['time_name'] = $scope.datasets[i]['time'];
          dataset['dataset_info']['name'] = $scope.datasets[i]['name'];
        } else {
          dataset['data_source_id'] = 2;
          dataset['dataset_info']['dataset_id'] = $scope.datasets[i]['datasetId'];
          dataset['dataset_info']['parameter_id'] = $scope.datasets[i]['param'];
          dataset['dataset_info']['name'] = $scope.datasets[i]['name'];
        }

        if ($scope.datasets[i].id === ref_ds.id) {
          data['reference_dataset'] = dataset;
        } else {
          data['target_datasets'].push(dataset);
        }
      }

      // TODO: These should be use customizable
      // Set the spatial rebin grid steps
      data['spatial_rebin_lat_step'] = 1;
      data['spatial_rebin_lon_step'] = 1;

      // Determine the temporal resolution to use when doing a temporal rebin. The
      // value is used to determine the timedelta in days to use.
      var temporal_res = settings.temporal.selected;

      if (temporal_res == 'daily') {
        data['temporal_resolution'] = 1;
      } else if (temporal_res == 'monthly') {
        data['temporal_resolution'] = 30;
      } else if (temporal_res == 'yearly') {
        data['temporal_resolution'] = 365;
      } else if (temporal_res == 'full') {
        data['temporal_resolution'] = 999;
      } else {
        // Default to monthly just in case
        data['temporal_resolution'] = 30;
      }

      data['temporal_resolution_type'] = temporal_res;

      // Load the Metrics for the evaluation
      data['metrics'] = []
      var metrics = settings.metrics
      for (var i = 0; i < metrics.length; i++) {
        var metric = metrics[i];

        if (metric.select) {
          data['metrics'].push(metric.name)
        }
      }

      // Set the bound values for the evaluation
      data['start_time'] =  $scope.displayParams.start + " 00:00:00",
      data['end_time'] = $scope.displayParams.end + " 00:00:00",
      data['lat_min'] = $scope.displayParams.latMin,
      data['lat_max'] = $scope.displayParams.latMax,
      data['lon_min'] = $scope.displayParams.lonMin,
      data['lon_max'] = $scope.displayParams.lonMax,

      $http.post($rootScope.baseURL + '/processing/run_evaluation/', data).
      success(function(data) {
        var evalWorkDir = data['eval_work_dir'];

        $scope.runningEval = false;

        $timeout(function() {
          if (evalWorkDir !== undefined) {
            window.location = "#/results/" + evalWorkDir;
          } else {
            window.location = "#/results";
          }
        }, 100);

      }).error(function() {
        $scope.runningEval = false;
      });
    };

    // Check the Parameter selection boxes after the user has changed input to ensure that valid
    // values were entered
    $scope.checkParameters = function() {
      if (parseFloat($scope.displayParams.latMin) < parseFloat($scope.latMin))
        $scope.displayParams.latMin = $scope.latMin;

      if (parseFloat($scope.displayParams.latMax) > parseFloat($scope.latMax))
        $scope.displayParams.latMax = $scope.latMax;

      if (parseFloat($scope.displayParams.lonMin) < parseFloat($scope.lonMin))
        $scope.displayParams.lonMin = $scope.lonMin;

      if (parseFloat($scope.displayParams.lonMax) > parseFloat($scope.lonMax))
        $scope.displayParams.lonMax = $scope.lonMax;

      if ($scope.displayParams.start < $scope.start)
        $scope.displayParams.start = $scope.start;

      if ($scope.displayParams.end > $scope.end)
        $scope.displayParams.end = $scope.end;

          $scope.displayParams.latMin = $scope.truncateFloat($scope.displayParams.latMin);
          $scope.displayParams.latMax = $scope.truncateFloat($scope.displayParams.latMax);
          $scope.displayParams.lonMin = $scope.truncateFloat($scope.displayParams.lonMin);
          $scope.displayParams.lonMax = $scope.truncateFloat($scope.displayParams.lonMax);

      $scope.$apply();
      $rootScope.$broadcast('redrawOverlays', []);
    }

    $scope.unwatchDatasets = $scope.$watch('datasets',
      function() {
        var numDatasets = $scope.datasets.length;
        $scope.displayParams.areValid = false;
        $scope.areInUserRegridState = false;

        if (numDatasets) {
          var latMin        = -90,
            latMax        = 90,
            lonMin        = -180,
            lonMax        = 180,
            start         = "1900-01-01 00:00:00",
            end           = "2030-01-01 00:00:00",
            datasetRegrid = false;
          // Get the valid lat/lon range in the selected datasets.
          for (var i = 0; i < numDatasets; i++) {
            var curDataset = $scope.datasets[i];

            latMin = (curDataset['latlonVals']['latMin'] > latMin) ? curDataset['latlonVals']['latMin'] : latMin;
            latMax = (curDataset['latlonVals']['latMax'] < latMax) ? curDataset['latlonVals']['latMax'] : latMax;
            lonMin = (curDataset['latlonVals']['lonMin'] > lonMin) ? curDataset['latlonVals']['lonMin'] : lonMin;
            lonMax = (curDataset['latlonVals']['lonMax'] < lonMax) ? curDataset['latlonVals']['lonMax'] : lonMax;
            start = (curDataset['timeVals']['start'] > start) ? curDataset['timeVals']['start'] : start;
            end = (curDataset['timeVals']['end'] < end) ? curDataset['timeVals']['end'] : end;

            datasetRegrid = datasetRegrid || curDataset.regrid;

          }

          $scope.areInUserRegridState = !datasetRegrid
        }

        // Update the display parameters with the new valid overlap that we've found!
        $scope.displayParams.latMin = $scope.truncateFloat(latMin);
        $scope.displayParams.latMax = $scope.truncateFloat(latMax);
        $scope.displayParams.lonMin = $scope.truncateFloat(lonMin);
        $scope.displayParams.lonMax = $scope.truncateFloat(lonMax);
        $scope.displayParams.start = (typeof start == 'undefined') ? "" : start.split(" ")[0];
        $scope.displayParams.end = (typeof end == 'undefined') ? "" : end.split(" ")[0];

        // Update the local store values!
        $scope.latMin = latMin;
        $scope.latMax = latMax;
        $scope.lonMin = lonMin;
        $scope.lonMax = lonMax;
        $scope.start = (typeof start == 'undefined') ? "" : start.split(" ")[0];
        $scope.end = (typeof end == 'undefined') ? "" : end.split(" ")[0];

        $scope.displayParams.areValid = true;
        $rootScope.$broadcast('redrawOverlays', []);
      }, true);

      $scope.truncateFloat = function(floatVal) {
          if (floatVal > 0) {
              return Math.floor(floatVal);
          } else {
              return Math.ceil(floatVal);
          }
      };
  }]);
