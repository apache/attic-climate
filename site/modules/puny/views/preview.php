<?php

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