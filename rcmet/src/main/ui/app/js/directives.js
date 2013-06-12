'use strict';

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
