App.Directives.directive('previewMap', function($rootScope) {
	return {
		restrict: 'A',
		replace: true,
		scope: {dataset: '=previewMap'},
		template: '<div id="{{dataset.name}}" class="preview-map"></div>',
		link: function(scope, element, attrs) {
			var map = L.map(attrs.id, {
				center: [40, 0],
				zoom: 0,
				scrollWheelZoom: false,
				zoomControl: false,
				attributionControl: false,
			});

			//create a CloudMade tile layer and add it to the map
			L.tileLayer('http://{s}.tile.cloudmade.com/57cbb6ca8cac418dbb1a402586df4528/997/256/{z}/{x}/{y}.png', {}).addTo(map);
		}
	};
});
