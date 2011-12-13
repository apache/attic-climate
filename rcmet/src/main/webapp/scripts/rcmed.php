<?php

/***
 * Fetch various information from the RCMED query API. Serves as a workaround
 * for cross-domain ajax calls.
 */
$action = $_REQUEST['action'];

switch (strtoupper($action)) {
	case "DATASETS":
		echo file_get_contents(
			App::Get()->settings['rcmed_query_api_url_base'] . "/datasets.php");
		break;	
	case "PARAMETERS":
		$dataset = $_REQUEST['dataset'];
		echo file_get_contents(
			App::Get()->settings['rcmed_query_api_url_base'] . '/parameters.php?dataset=' . $dataset);
		break;
	default:
		echo "{}";	
}

exit;