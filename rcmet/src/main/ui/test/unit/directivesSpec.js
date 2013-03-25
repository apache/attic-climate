'use strict';

/* jasmine specs for directives go here */

// This should be testing the Leaflet map directive...
//*
describe('directives', function() {
	beforeEach(module('rcmes'));

	// Testing Leaflet map directive
	/*
	describe('Testing Leaflet map directive', function() {
		it('should create the leaflet dir for proper injection into the page', function() {
			inject(function($compile, $rootScope) {
				var element = $compile('<sap id="map"></sap>')($rootScope);
				expect(element.className).toBe('leaflet-container leaflet-fade-anim');
			})
		});
	});

	//*/
	describe('Testing bootstrap-modal directive', function() {
		it('should create a div element of the correct form', function() {
			inject(function($compile, $rootScope) {
				var element = $compile('<bootstrap-modal modal-id="testmodal"></bootstrap-modal>')($rootScope);
				expect(element.hasClass("modal")).toBeTruthy();
				expect(element.hasClass("hide")).toBeTruthy();
				expect(element.attr("id")).toEqual('{{modalId}}');
			});
		});

		it ('should properly wrap the interior html content' , function() {
			inject(function($compile, $rootScope) {
				var element = $compile('<bootstrap-modal modal-id="testmodal"><h3>Hello</h3></bootstrap-modal>')($rootScope);
				expect(element.html()).toEqual("<div ng-transclude=\"\"><h3 class=\"ng-scope\">Hello</h3></div>");
			})
		});
	});
});
//*/
