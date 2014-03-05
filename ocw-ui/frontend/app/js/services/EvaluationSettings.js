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

// EvaluationSettings gives controllers access to the user's selected evaluation settings.
App.Services.service('evaluationSettings', function($rootScope, $http) {
    $http.get($rootScope.baseURL + '/processing/metrics/').then(function(data) {
        metrics_data = data['data']['metrics'];
        metrics = [];

        for (var i = 0; i < metrics_data.length; ++i) {
            metrics.push({'name': metrics_data[i], 'select': false});
        }

        settings['metrics'] = metrics;
    });

	var settings = {
        'metrics': [],
		'temporal': {
			'options': ['daily', 'monthly', 'yearly'],
			'selected': 'yearly',
		},
		'spatialSelect': null,
	};

	return {
		getSettings: function() {
			return settings;
		}
	};
});		
