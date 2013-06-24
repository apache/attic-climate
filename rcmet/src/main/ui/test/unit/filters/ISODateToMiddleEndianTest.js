/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *    http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
**/
'use strict';

describe('OCW Filters', function() {
	beforeEach(module('ocw.filters'));

	describe('ISODateToMiddleEndian', function() {
		it('should replace the ISO Date/Time stamp', function() {
			inject(function($filter) {
				var filter = $filter('ISODateToMiddleEndian');
				expect(filter('2012-01-02T00:00:00')).toEqual('01/02/2012');
			});
		});

		it('should replace the modified ISO Date/Time stamp', function() {
			inject(function($filter) {
				var filter = $filter('ISODateToMiddleEndian');
				expect(filter('2012-01-02 00:00:00')).toEqual('01/02/2012');
			});
		});

		it('should replace the ISO Date stamp', function() {
			inject(function($filter) {
				var filter = $filter('ISODateToMiddleEndian');
				expect(filter('2012-01-02')).toEqual('01/02/2012');
			});
		});

		it('should replace leading and trailing whitespace', function() {
			inject(function($filter) {
				var filter = $filter('ISODateToMiddleEndian');
				expect(filter('      2012-01-02T00:00:00    ')).toEqual('01/02/2012');
			});
		});
	});
});
