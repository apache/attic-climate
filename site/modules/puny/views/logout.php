<?php
// Parse the Puny config file
$module = App::Get()->loadModule();

// Include the main Puny class
require_once($module->modulePath . '/classes/Puny.class.php');

// Instantiate Puny
$puny = new Puny();

// Destroy the editor session
$puny->destroyEditorSession();

// Redirect home
App::Get()->redirect(SITE_ROOT . '/');