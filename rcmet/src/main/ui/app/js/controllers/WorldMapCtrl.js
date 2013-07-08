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

// Controller for the world map
App.Controllers.controller('WorldMapCtrl', ['$rootScope', '$scope', 'selectedDatasetInformation', 'regionSelectParams',
function($rootScope, $scope, selectedDatasetInformation, regionSelectParams) {
	$scope.datasets = selectedDatasetInformation.getDatasets();
	$scope.regionParams = regionSelectParams.getParameters();

	$scope.updateMap = function() {
 		// Clear Group of layers from map if it exists
 		if ("rectangleGroup" in $rootScope) {
 			$rootScope.rectangleGroup.clearLayers();
 		}

		// Don't process if we don't have any datasets added or if the map doesn't exist!!
		if ($scope.datasets.length == 0 || !("map" in $rootScope))
			return;
 		
		// Create Group to add all rectangles to map
		$rootScope.rectangleGroup = L.layerGroup();
		
		// Loop through datasets and add rectangles to Group 
		var i = -1;
		angular.forEach($scope.datasets, function(dataset) {
			// Keep track of dataset count for displaying colors
			i++;

			// If the user disabled the overlay then get out of here!
			if (!dataset.shouldDisplay)
				return;

			// Get bounds from dataset 
			var maplatlon = dataset.latlonVals;
			var bounds = [[maplatlon.latMax, maplatlon.lonMin], [maplatlon.latMin, maplatlon.lonMax]];

			var polygon = L.rectangle(bounds,{
				stroke: false,
				fillColor: $rootScope.fillColors[i],
				fillOpacity: 0.3
			});

			// Add layer to Group
			$rootScope.rectangleGroup.addLayer(polygon);
		});

		// Draw user selected region
		if ($scope.regionParams.areValid) {

			var bounds = [[$scope.regionParams.latMax, $scope.regionParams.lonMin],
						  [$scope.regionParams.latMin, $scope.regionParams.lonMax]];

			var polygon = L.rectangle(bounds, {
				color: '#000000',
				opacity: 1.0,
				fill: false,
			});

			$rootScope.rectangleGroup.addLayer(polygon);
		}

		// Add rectangle Group to map
		$rootScope.rectangleGroup.addTo($rootScope.map);

		// Calculate the overlap region and set the map to show the new overlap
		var latMin = -90,
			latMax = 90,
			lonMin = -180,
			lonMax = 180;

		// Get the valid lat/lon range in the selected datasets.
		for (var i = 0; i < selectedDatasetInformation.getDatasetCount(); i++) {
			var curDataset = $scope.datasets[i];

			latMin = (curDataset['latlonVals']['latMin'] > latMin) ? curDataset['latlonVals']['latMin'] : latMin;
			latMax = (curDataset['latlonVals']['latMax'] < latMax) ? curDataset['latlonVals']['latMax'] : latMax;
			lonMin = (curDataset['latlonVals']['lonMin'] > lonMin) ? curDataset['latlonVals']['lonMin'] : lonMin;
			lonMax = (curDataset['latlonVals']['lonMax'] < lonMax) ? curDataset['latlonVals']['lonMax'] : lonMax;
		}

		var overlapBounds = [[latMax, lonMin], [latMin, lonMax]];
		$rootScope.map.fitBounds(overlapBounds, {padding: [5, 5]});
	};

	$scope.$on('redrawOverlays', function(event, parameters) {
		$scope.updateMap();
	});

	$scope.$watch('datasets', function() {
		$scope.updateMap();
	}, true);
}]);
