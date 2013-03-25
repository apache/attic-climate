'use strict';

// Directive for dealing with the Leaflet map
angular.module('rcmes', []).
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
directive('bootstrapModal', function($defer) {
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
			var modal = $('#' + attrs.modalID);

			if (hasBackground) {
				// Check if there is a modalBackground tag and add it if it doesn't exist
				if (!document.getElementById('modalBackground')) {
					$('body').append('<div id="modalBackground" class="modalBackground"></div>');
				}

				// Show the modal background and bind a click event to the function for closing the modal
				$('#modalBackground').
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
		}

		closeModal = function(event) {
			// Clean up the modalBackground by removing the click event and hiding it.
			$('#modalBackground').
				unbind('click', closeModal).
				css({diplay: 'none'});

			// Remove the event for closing the body from the body
			$('body').
				unbind('keyup', escapeEvent)

			// Hide the modal
			$('#' + attrs.modalId).css({display: 'hidden'});
		}

		// We need to bind the close and open modal events so outside elements can trigger the modal.
		// This has to wait until the template has been fully inserted, so just wait a bit of time
		// before we set them. I'm sure there's a better way of handling this...
		$defer(function() {
			$('#' + attrs.modalId).
				bind('modalOpen', openModal).
				bind('modalClose', closeModal);
		}, 100);
	};

	return {
		link: link,
		restric: 'E',
		scope: {
			modalId: 'attribute'
		},
		template: '<div id="{{modalId}}" class="modal hide"><div ng-transclude></div></div>',
		transclude: true
	};
});
