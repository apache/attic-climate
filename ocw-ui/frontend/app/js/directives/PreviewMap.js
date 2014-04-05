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

App.Directives.directive('previewMap', function($rootScope) {
	return {
		restrict: 'A',
		replace: true,
		scope: {dataset: '=previewMap', index: '=index'},
		template: '<div id="{{dataset.name}}" class="preview-map"></div>',
		replace: true,
		link: function(scope, element, attrs) {

			// Any attribute that contains {{}} interpolation will be set to null in the attrs
			// parameter during the link function since the first $digest since the compilation
			// has yet to run to evaluate it! We can't run a $digest in the middle of compilation,
			// so using an $observe (or $watch) is the best way to get the values.
			attrs.$observe('id', function(newId) {
				var map = L.map(attrs.id, {
					zoom: 0,
					scrollWheelZoom: false,
					zoomControl: false,
					attributionControl: false,
					worldCopyJump: true,
				});

				L.tileLayer('http://{s}.tile.osm.org/{z}/{x}/{y}.png', {}).addTo(map);

				// Zoom the map to the dataset bound regions (or at least try our best to do so)
				var datasetBounds = [[scope.dataset.latlonVals.latMax, scope.dataset.latlonVals.lonMin], 
									 [scope.dataset.latlonVals.latMin, scope.dataset.latlonVals.lonMax]];
				map.fitBounds(datasetBounds, {});

				// Draw a colored overlay on the region of the map
				var maplatlon = scope.dataset.latlonVals;
				var bounds = [[maplatlon.latMax, maplatlon.lonMin], [maplatlon.latMin, maplatlon.lonMax]];

				var polygon = L.rectangle(bounds,{
					stroke: false,
					fillColor: $rootScope.fillColors[1],
					fillOpacity: 0.6
				});

				// Add layer to Group
				var rectangleGroup = L.layerGroup();
				rectangleGroup.addLayer(polygon);

				// Add the overlay to the map
				rectangleGroup.addTo(map);
			});
		}
	};
});
