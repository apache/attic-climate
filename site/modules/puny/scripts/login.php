<?php

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




