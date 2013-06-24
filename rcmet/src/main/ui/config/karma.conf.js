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
basePath = '../';

files = [
  JASMINE,
  JASMINE_ADAPTER,
  'app/js/lib/jquery/jquery-1.10.1.js',
  'app/js/lib/jquery/jquery-ui/jquery-ui-1.10.3.min.js',
  'app/js/lib/bootstrap/bootstrap.js',
  'app/js/lib/angular/angular.js',
  'app/js/lib/angular/angular-*.js',
  'test/lib/angular/angular-mocks.js',
  'app/js/lib/jquery/jquery-ui/datepicker-wrapper/date.js',
  'app/js/lib/leaflet/leaflet-0.5.js',
  'app/js/app.js',
  'app/js/controllers/*.js',
  'app/js/directives/*.js',
  'app/js/services/*.js',
  'app/js/filters/*.js',
  'test/unit/**/*.js'
];

autoWatch = true;

browsers = ['Chrome'];

junitReporter = {
  outputFile: 'test_out/unit.xml',
  suite: 'unit'
};
