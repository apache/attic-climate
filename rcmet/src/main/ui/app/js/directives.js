'use strict';

// Directive for dealing with the Leaflet map
angular.module('rcmes').
directive('sap', function($rootScope) {
	return {
		restrict: 'E',
		replace: true,
		template: '<div></div>',
		link: function(scope, element, attrs) {
			$rootScope.map = L.map(attrs.id, {
				center: [40, 0],
				zoom: 2,
				scrollWheelZoom: false,
			});
			//create a CloudMade tile layer and add it to the map
			L.tileLayer('http://{s}.tile.cloudmade.com/57cbb6ca8cac418dbb1a402586df4528/997/256/{z}/{x}/{y}.png', {
				maxZoom: 4, minZoom: 2,
			}).addTo($rootScope.map);
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

		openModal = function(event, toggleBackground, toggleKeyboardEscape) {
			// Grab the current modal tag based on the modalId attribute in the bootstrapModal tag
			var modal = $('#' + attrs.modalId);

			// Make all the modal's children of class "close" call the appropriate function for closing!
			$('.close', modal).bind('click', closeModal);

			modal.modal({
				show: true,
				backdrop: toggleBackground,
				keyboard: toggleKeyboardEscape,
			});
		};

		closeModal = function(event) {
			$('#' + attrs.modalId).modal('hide');
			
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
		template: '<div id="{{modalId}}" class="modal hide fade" tabindex="-1"><div ng-transclude></div></div>',
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
			// Enable keyboard closing of modal with escape key.
			var hasKeyboardEscape = (attrs.keyboard === undefined ? true : attrs.keyboard);

			$(elem).bind('click', function() {
				$('#' + attrs.bootstrapModalOpen).trigger('modalOpen', [hasBackground, hasKeyboardEscape]);
			});
		}
	};
}).
// Setup a text input that the user will use to input a path to a local file.
directive('predictiveFileBrowserInput', function() {
	var link = function($scope, $elem, $attrs) {
		$scope.autocomplete = [];
		
		/*
		 * We need a place to dump our auto-completion options
		 */
		$($elem).parent().append('<ul id="autoCompletePath"><ul>');

		// Handle user clicks on auto-complete path options
		$(document).on('click', '#autoCompletePath li span', function(e) {
			// Set the input text box's value to that of the user selected path
			var val = $(e.target).text();
			$($elem).val(val);

			// If the user selected a directory, find more results..
			if (val[val.length - 1] == '/') {
				$scope.fetchFiles($($elem).val());
			// Otherwise, remove the auto-complete options...
			} else {
				$('#autoCompletePath li').remove();
			}
		});

		/*
		 * Handle key-down events on the input box
		 *
		 * We need to ignore <TAB> presses here so we can auto-complete with <TAB>.
		 * If we don't ignore here then <TAB> will move the user to the next field
		 * in the form and our common-prefix-fill won't work later.
		 */
		$($elem).keydown(function(e) {
			var code = e.keyCode || e.which;
			var BACKSPACE = 8,
				TAB = 9;

			if (code == TAB)
				return false;
		});

		/*
		 * Handle key-up events on the input box
		 */
		$($elem).keyup(function(e) {
			var code = e.keyCode || e.which;
			var BACKSPACE = 8,
				TAB = 9,
				FORWARD_SLASH = 191;

			if (code === FORWARD_SLASH) {
				// Fetch new directory information from the server.
				$scope.fetchFiles($(this).val());
			} else if (code === TAB) {
				// Attempt to auto-fill for the user.
				$scope.handleTabPress();
			} else if (code == BACKSPACE) {
				// Need to properly handle the removal of directory information
				// and the displaying of auto-complete options
				$scope.handleBackSpace();
			} else {
				// Filter auto-complete options based on user input..
				$scope.handleMiscKeyPress();
			}

			// This is being used so we can handle backspacing. The user might hold
			// down the backspace key or select a section of text and delete. This allows
			// us to compare the result to its prior state, which makes handling
			// backspaces easier.
			$scope.lastInputContents = $elem.val();
		});

		/*
		 * Grab additional path information from the web-server
		 *
		 * Params:
		 *		path - The path to get a directory listing of.
		 */
		// TODO Make this use $HTTP
		$scope.fetchFiles = function(path) {
			$.get($scope.baseURL + '/getDirInfo/' + path, {},
				 function(data) {
					 $scope.setNewData(data);
					 $scope.updateAutoComplete();
				 }, 'json');
		};

		/*
		 * Grab additional path information from the web-server and filter the
		 * results based on the current input text.
		 *
		 * Params:
		 *		path - The path to get a directory listing of.
		 *
		 * This is needed to handle deletion of selected text. It is possible that
		 * the user will select text and delete only part of a word. The results
		 * need to be filtered based on this partial input.
		 */
		// TODO Why isn't this using $http?!?!?! Because I copy and pasted!!!!
		$scope.fetchFilesAndFilter = function(path) {
			$.get($scope.baseURL + '/getDirInfo/' + path, {},
				 function(data) {
					 $scope.setNewData(data);
					 $scope.filterResults();
					 $scope.updateAutoComplete();
				 }, 'json');
		};

		/*
		 * Handle directory data from the server.
		 *
		 * We store the entire directory information along with the remaining
		 * possible options given the users current input. This lets us avoid
		 * unnecessary calls to the server for directory information every time
		 * the user deletes something.
		 */
		$scope.setNewData = function(data) {
			$scope.autocomplete = data.sort();
			$scope.possibleCompletes = $scope.autocomplete;
		};

		/* 
		 * Handle <TAB> presses.
		 *
		 * Attempt to auto-complete options when the user presses <TAB>.
		 */
		$scope.handleTabPress = function() {
			// If there's only one option available there's no points in trying to
			// find a common prefix! Just set the value!
			if ($scope.possibleCompletes.length === 1) {
				$elem.val($scope.possibleCompletes[0]);

				// Make sure more options are displayed if a directory was selected.
				$scope.checkForMoreOptions();
				$scope.updateAutoComplete();
				return;
			}

			// Find the greatest common prefix amongst the remaining choices and set
			// the input text to it.
			var prefix = $scope.getLargestCommonPrefix($scope.possibleCompletes);
			$elem.val(prefix);
			$scope.updateAutoComplete();
		};

		/*
		 * Handle Backspacing and option displaying.
		 *
		 * The auto-complete options needs to be displayed correctly when the user
		 * removes directory information.
		 */
		$scope.handleBackSpace = function() {
			var curInputVal = $elem.val();

			// If the user deletes everything in the input box all we need to do
			// is make sure that the auto-complete options aren't displayed.
			if (curInputVal.length === 0) {
				$('#autoCompletePath li').remove();
				return;
			}

			// Figure out how much text the user removed from the input box.
			var lengthDiff = $scope.lastInputContents.length - curInputVal.length;
			// Grab the removed text.
			var removedText = $scope.lastInputContents.substr(-lengthDiff);

			// If the user deleted over a directory we need to fetch information on the
			// previous directory for auto-completion.
			if (removedText.indexOf('/') !== -1) {
				var lastSlashIndex = curInputVal.lastIndexOf('/');

				// If the remaining path still contains a directory...
				if (lastSlashIndex !== -1) {
					// Grab the section of the path that points to a valid directory,
					// fetch the listing, and update the results.
					var pathToSearch = curInputVal.slice(0, lastSlashIndex + 1);
					$scope.fetchFilesAndFilter(pathToSearch);
				} else {
					// Delete the old auto-complete information in the case where the user
					// completely removed path information.
					$('#autoCompletePath li').remove();
				}
			} else {
				// Otherwise, we just need to filter results based on the remaining input.
				$scope.filterResults();
				$scope.updateAutoComplete();
			}
		};

		/* 
		 * Handle all other key presses in the input box
		 *
		 * Filter the auto-complete options as the user types to ensure that only options
		 * which are possible given the current input text are still displayed.
		 */
		$scope.handleMiscKeyPress = function() {
			// Safely exit when there are no options available.
			if ($scope.autocomplete === [])
				return;

			// Otherwise, filter the results.
			$scope.filterResults();
			$scope.updateAutoComplete();
		};

		/* 
		 * When a path is auto-completed with <TAB> we need to check to see if it points
		 * to a directory. If it does, we still need to fetch results!
		 */
		$scope.checkForMoreOptions = function() {
			var path = $elem.val();
			if (path[path.length - 1] === '/') {
				$scope.fetchFiles(path);
			}
		};

		/* 
		 * Calculate the greatest common prefix of the passed options.
		 *
		 * Params:
		 *		Options - An array of strings in which the greatest common prefix
		 *				  should be found
		 *
		 * Returns:
		 *		The greatest common prefix of the strings.
		 *
		 *
		 * Note - For us, there will always be a prefix of at least '/' since this can't
		 * possible be called without the users entering a starting directory. As a result,
		 * we don't explicitly handle the case where there is 0 length common prefix.
		 */
		$scope.getLargestCommonPrefix = function(options) {
			var index = 1;
			var shortestString = options.reduce(function(a, b) { return a.length < b.length ? a : b; });
			var longestString = options.reduce(function(a, b) { return a.length > b.length ? a : b; });
			var	substringToCheck = shortestString[0];

			while (longestString.indexOf(substringToCheck) !== -1) {
				substringToCheck = shortestString.slice(0, ++index);
			}

			return longestString.slice(0, index - 1);
		};

		/* 
		 * Filter the auto-complete options based on the current input.
		 */
		$scope.filterResults = function() {
			$scope.possibleCompletes = $scope.autocomplete.filter(function(item, index, array) {
				return (~item.indexOf($($elem).val()));
			});

			$scope.possibleCompletes.sort();
		};

		/*
		 * Update the display of auto-complete options.
		 */
		$scope.updateAutoComplete = function() {
			// Remove all the existing options
			$('#autoCompletePath li').remove();

			// We don't need to show anything if the user has completely selected
			// the only existing option available.
			if ($scope.possibleCompletes.length === 1) {
				if ($scope.possibleCompletes[0] === $elem.val()) {
					return;
				}
			}

			// Display all the possible completes
			$.each($scope.possibleCompletes, function(i, v) {
				$('#autoCompletePath').append($('<li>').html($('<span>').text(v)));
			});
		};
	};

	return {
		link: link,
		scope: true,
		restrict: 'A'
	};
});
