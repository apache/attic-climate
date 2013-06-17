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

// Directive for inserting bootstrap modals
App.Directives.directive('bootstrapModal', function($timeout) {
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
});
