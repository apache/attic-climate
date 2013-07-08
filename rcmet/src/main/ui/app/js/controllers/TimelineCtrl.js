//
// Licensed to the Apache Software Foundation (ASF) under one or more
// contributor license agreements.See the NOTICE file distributed with
// this work for additional information regarding copyright ownership.
// The ASF licenses this file to You under the Apache License, Version 2.0
// (the "License"); you may not use this file except in compliance with
// the License.You may obtain a copy of the License at
// 
// http://www.apache.org/licenses/LICENSE-2.0
// 
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
//

// Controller for the OCW Timeline Widget
App.Controllers.controller('TimelineCtrl', ['$rootScope', '$scope', 'selectedDatasetInformation', 'regionSelectParams',
function($rootScope, $scope, selectedDatasetInformation, regionSelectParams) {
	$scope.datasets = selectedDatasetInformation.getDatasets();
	$scope.regionParams = regionSelectParams.getParameters();

	$scope.updateTimeline = function() {
 		// Clear timeline data if it exists
 		if ("timeline" in $rootScope) {
 			$rootScope.timeline.deleteAllItems();
 		}

		// Don't process if no datasets have been added
		if ($scope.datasets.length == 0 || !("timeline" in $rootScope))
			return;
 		
		// Create DataTable to add data to timeline
		var data = new google.visualization.DataTable();
		data.addColumn('datetime', 'start');
		data.addColumn('datetime', 'end');
		data.addColumn('string', 'content');

		// Loop through datasets and add data to timeline 
		var i = -1;
		angular.forEach($scope.datasets, function(dataset) {

			// Keep track of dataset count for displaying colors
			i++;
			
			/* TODO should "disable overlay" also disable timeline? */

			// Get time bounds from dataset 
			var start = dataset.timeVals.start;
			var end	= dataset.timeVals.end;

			// Add different color to each bar
			var style = 'background-color:' + $rootScope.fillColors[i] +
						'; border-color:' + $rootScope.surroundColors[i] + ';';
			var ocwBar = '<div class="ocw-bar timeline-event-range" style="' + style + '"></div>';
	
			// Add row to DataTable: object with start and end date
			// note: subtract one from month since indexes from 0 to 11
			data.addRow([new Date(start.substr(0,4), start.substr(5,2)-1, start.substr(8,2)), 
						new Date(end.substr(0,4), end.substr(5,2)-1, end.substr(8,2)),
						ocwBar ]);
		});

		// Add user selected bounds to timeline
		if ($scope.regionParams.areValid) {

			var userStart 	= $scope.regionParams.start;
			var userEnd 	= $scope.regionParams.end;

			// Add color to user selected bounds
			var style = 'background-color: #000000; border: 2px solid;';
			var ocwBar = '<div class="ocw-bar timeline-event-range" style="' + style + '"></div>';
			
			// Add row to DataTable: object with start and end date
			// note: subtract one from month since indexes from 0 to 11
			data.addRow([new Date(userStart.substr(0,4), userStart.substr(5,2)-1, userStart.substr(8,2)), 
						new Date(userEnd.substr(0,4), userEnd.substr(5,2)-1, userEnd.substr(8,2)),
						ocwBar ]);
		}
		
		var options = {
				'minHeight': "200px",
				'width':  "99.8%",
				'zoomable': false
		};
		
		// Draw timeline with data (DataTable) and options (a name-value map) 
		$rootScope.timeline.draw(data, options);
	};

	$scope.$on('redrawOverlays', function(event, parameters) {
		$scope.updateTimeline();
	});

	$scope.$watch('datasets', function() {
		$scope.updateTimeline();
	}, true);
}]);
