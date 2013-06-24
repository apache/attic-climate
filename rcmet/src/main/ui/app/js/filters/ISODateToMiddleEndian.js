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

'use strict';

// Convert a date in ISO format (or slightly modified such that 'T' is replace by ' ') into
// a 'Middle Endian'/U.S. style date.
App.Filters.filter('ISODateToMiddleEndian', function() {
	return function(input) {
		var original = input;

		// Strip whitespace from the start and end of the string
		input = input.replace(/(^\s+|\s+$)/g,' ');

		// ISO Standard says time is separated from Date with a 'T'. Our timestamps
		// slightly modify that and use a space. We'll check for both here and prefer
		// to split on a 'T' if it's available.
		if (input.indexOf('T') != -1 || input.indexOf(' ') != -1) {
			input = (input.indexOf('T') != -1) ? input.split('T')[0] : input.split(' ')[0];
		} 
		
		// The components of the date should be split with hyphens. If we can't find them
		// then the string is poorly formed.
		if (input.indexOf('-') == -1 || input.split('-').length - 1 != 2) {
			return original;
		}

		// At this point the date is probably valid and we should try to convert it!
		var components = input.split('-');
		return (components[1] + "/" + components[2] + "/" + components[0]);
	};
});
