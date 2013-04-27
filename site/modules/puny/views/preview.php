<?php
/*
 * Licensed to the Apache Software Foundation (ASF) under one or more
 * contributor license agreements.  See the NOTICE file distributed with
 * this work for additional information regarding copyright ownership.
 * The ASF licenses this file to You under the Apache License, Version 2.0
 * (the "License"); you may not use this file except in compliance with
 * the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

// Parse the Puny config file
$module = App::Get()->loadModule();

// Include the main Puny class
require_once($module->modulePath . '/classes/Puny.class.php');

// Instantiate Puny
$puny = new Puny();

// Obtain the parameters from the request
$resourceId = App::Get()->request->segments[0];
$versionId  = isset(App::Get()->request->segments[1]) ? App::Get()->request->segments[1] : null;

// Load, parse, and display the requested resource
echo $puny->load($resourceId, $versionId)->getContent();

// we're done :)
?>