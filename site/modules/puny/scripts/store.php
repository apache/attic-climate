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
require_once(App::Get()->settings['puny_module_path'] . '/classes/Puny.class.php');

// Get the resource id from the request parameters
$resourceId = $_POST['resourceId'];
$content    = $_POST['content'];

// Load the requested resource and update the content
$resource = Puny::load($resourceId)->setContent($content);

// Store the updated content as a new version
Puny::store($resource);

// we're done :)
echo json_encode(array(
	"status"     => "ok"
	, "resourceId" => $resourceId
	, "version"    => $resource->getVersion()
	, "parsedContent" => $resource->parse()->getContent()));
