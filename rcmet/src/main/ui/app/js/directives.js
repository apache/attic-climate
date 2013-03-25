'use strict';

// Directive for dealing with the Leaflet map
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
				maxZoom: 4, minZoom: 2
			}).addTo(map);
		}
	};
}).
// Directive for inserting bootstrap modals
directive('bootstrapModal', function($timeout) {
	var link = function(scope, elem, attrs) {
		var escapeEvent;
		var openModal;
		var closeModal;

		escapeEvent = function(e) {
			if (e.which == 27)
				closeModal();
		}

		openModal = function(event, hasBackground, hasEscapeExit) {
			// Grab the current modal tag based on the modalId attribute in the bootstrapModal tag
			var modal = $('#' + attrs.modalId);

			if (hasBackground) {
				// Check if there is a modal-backdrop tag and add it if it doesn't exist
				if (!document.getElementById('modal-backdrop')) {
					$('body').append('<div id="modal-backdrop" class="modal-backdrop"></div>');
				}

				// Show the modal background and bind a click event to the function for closing the modal
				$('#modal-backdrop').
					css({display: 'block'}).
					bind('click', closeModal);
			}

			// Pressing escape should close the modal
			if (hasEscapeExit) {
				$('body').bind('keyup', escapeEvent);
			}

			// Make all the modal's children of class "close" call the appropriate function for closing!
			$('.close', modal).bind('click', closeModal);

			// Display the modal
			modal.css({display: 'block'});
		};

		closeModal = function(event) {
			// Clean up the modal-backdrop by removing the click event and hiding it.
			$('#modal-backdrop').
				unbind('click', closeModal).
				css({display: 'none'});

			// Remove the event for closing the body from the body
			$('body').
				unbind('keyup', escapeEvent)

			// Hide the modal
			$('#' + attrs.modalId).css({display: 'none'});
		};

		// We need to bind the close and open modal events so outside elements can trigger the modal.
		// This has to wait until the template has been fully inserted, so just wait a bit of time
		// before we set them. I'm sure there's a better way of handling this...
		$timeout(function() {
			$('#' + attrs.modalId).
				bind('modalOpen', openModal).
				bind('modalClose', closeModal);
		}, 100);
	};

	return {
		link: link,
		replace: true,
		restrict: 'E',
		scope: {
			modalId: '@' 
		},
		template: '<div id="{{modalId}}" class="modal hide"><div ng-transclude></div></div>',
		transclude: true
	};
}).
// This directive process bootstrap-modal-open attributes. This lets the user bind the opening of a specific modal
// as well as specifying how that modal should open.
directive('bootstrapModalOpen', function() {
	return {
		restrict: 'A',
		link: function(scope, elem, attrs) {
			// Default to showing the background if the user didn't specify a value for this.
			var hasBackground = (attrs.background === undefined ? true : attrs.background);
			// Default to allowing an exit on escape if the user didn't provide a value for this.
			var hasEscapeExit = (attrs.escapeExit === undefined ? true : attrs.escapeExit);

			$(elem).bind('click', function() {
				$('#' + attrs.bootstrapModalOpen).trigger('modalOpen', hasBackground, hasEscapeExit);
			});
		}
	};
});
