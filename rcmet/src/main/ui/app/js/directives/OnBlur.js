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

// The onBlur directive calls a passed function when a field's "blur" event is called.
// The function should be passed as part of the "on-blur" attribute and be defined in
// the containing scope.
//
// Consider the test function "testFunc". If you wanted this to run on the blur event
// for an input box you would use the following:
//   <input type="text" on-blur="testFunc();" />
angular.module('rcmes').directive('onBlur', function() {
	return {
        restrict: 'A',
        link: function($scope, $elem, $attrs) {
            $elem.bind('blur', function() {
				$scope.$eval($attrs.onBlur);
			});
        },
    };
 });
