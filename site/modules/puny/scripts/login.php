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

// Include the main Puny class
require_once(App::Get()->settings['puny_module_path'] . '/classes/Puny.class.php');

// Get the configured editor username / password
$punyUsername = App::Get()->settings['puny_editor_username'];
$punyPassword = App::Get()->settings['puny_editor_password'];

// Get the provided credentials from the POST request
$username = $_POST['username'];
$password = $_POST['password'];

// Ensure that the editor credentials are properly configured in config.ini
if ( !($punyUsername && $punyPassword) ) {
	$_SESSION['puny_error'] = "Unable to launch Puny because the Puny "
		. "admin credentials are not configured properly.";
	App::Get()->redirect(App::Get()->settings['puny_module_root'] . '/error');
}

// Test the provided values against the configured values
if ( $username == $punyUsername && $password == $punyPassword ) {
	// Login success
	Puny::initializeEditorSession();
	App::get()->redirect(SITE_ROOT . '/');
} else {
	// Login Failure...
	$_SESSION['puny_error'] = "Invalid editor credentials provided...";
	App::Get()->redirect(App::Get()->settings['puny_module_root'] . '/error');
}

exit();




