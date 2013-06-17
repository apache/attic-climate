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

// This directive processes bootstrap-modal-open attributes. This lets the user bind 
// the opening of a specific modal to a button/link. It also lets the user specify
// what features the modal should have. The user can turn off the semi-opaque background
// by having the background attribute set to 'false'. The user can also turn off the
// ability to close the modal with ESC by having the keyboard attribute set to 'false'.
App.Directives.directive('bootstrapModalOpen', function() {
	return {
		restrict: 'A',
		link: function(scope, elem, attrs) {
			// Default to showing the background if the user didn't specify a value for this.
			var hasBackground = (attrs.background === undefined ? true : (attrs.background == "true"));
			// Enable keyboard closing of modal with escape key.
			var hasKeyboardEscape = (attrs.keyboard === undefined ? true : (attrs.keyboard == "true"));

			$(elem).bind('click', function() {
				$('#' + attrs.bootstrapModalOpen).trigger('modalOpen', [hasBackground, hasKeyboardEscape]);
			});
		}
	};
});
