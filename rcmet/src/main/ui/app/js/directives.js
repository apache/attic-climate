'use strict';

angular.module('rcmes').
    directive('sap', function() {
    return {
        restrict: 'E',
        replace: true,
        template: '<div></div>',
        link: function(scope, element, attrs) {
            var map = L.map(attrs.id, {
                center: [40, -86],
                zoom: 2
            });
            //create a CloudMade tile layer and add it to the map
            L.tileLayer('http://{s}.tile.cloudmade.com/57cbb6ca8cac418dbb1a402586df4528/997/256/{z}/{x}/{y}.png', {
                maxZoom: 18
            }).addTo(map);
        }
    };
});
