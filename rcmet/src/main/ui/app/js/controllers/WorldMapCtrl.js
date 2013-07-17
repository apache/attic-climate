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
 		
		// Create a group that we'll draw overlays to
		$rootScope.rectangleGroup = L.layerGroup();
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
		$rootScope.map.fitBounds(overlapBounds, {padding: [0, 0]});

		// Draw border around overlap region
		var overlapBorder = L.rectangle(overlapBounds, {
			color: '#000000',
			opacity: 1.0,
			fill: false,
			weight: 2,
			dashArray: "10 10",
		});

		$rootScope.rectangleGroup.addLayer(overlapBorder);

		// Draw user selected region
		if ($scope.regionParams.areValid) {

			var bounds = [[$scope.regionParams.latMax, $scope.regionParams.lonMin],
						  [$scope.regionParams.latMin, $scope.regionParams.lonMax]];

			var polygon = L.rectangle(bounds, {
				color: '#000000',
				opacity: .3,
				stroke: false,
				fill: true,
			});

			$rootScope.rectangleGroup.addLayer(polygon);
		}
	};

	$scope.$on('redrawOverlays', function(event, parameters) {
		$scope.updateMap();
	});

	$scope.$watch('datasets', function() {
		$scope.updateMap();
	}, true);
}]);
