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

		// Loop through datasets and find the overlapping start/end time range
		var start = $scope.datasets[0].timeVals.start;
		var end = $scope.datasets[0].timeVals.end;
		for (var i = 0; i < $scope.datasets.length; i++) {
			var possibleNewStart = $scope.datasets[i].timeVals.start;
			var possibleNewEnd = $scope.datasets[i].timeVals.end;

			start = (possibleNewStart > start) ? possibleNewStart : start;
			end = (possibleNewEnd < end) ? possibleNewEnd : end;
		}

		// Set the timeline extent to the overlapping time range
		//
		// NOTE: The month value substring is expected to be 0-based (hence the -1)
		$rootScope.timeline.setVisibleChartRange(new Date(start.substr(0, 4), start.substr(5, 2) - 1, start.substr(8, 2)),
												 new Date(end.substr(0, 4), end.substr(5, 2) - 1, end.substr(8, 2)));

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
				"width": "100%",
				"showCurrentTime": false,
				"zoomable": false,
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
