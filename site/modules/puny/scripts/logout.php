<?php
// Parse the Puny config file
$module = App::Get()->loadModule();

// Include the main Puny class
require_once(App::Get()->settings['puny_module_path'] . '/classes/Puny.class.php');

// Destroy the editor session
Puny::destroyEditorSession();

// Redirect home
App::Get()->redirect(SITE_ROOT . '/');

exit();

