<?php
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
