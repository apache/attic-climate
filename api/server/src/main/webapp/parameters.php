<?php
/**
 * Copyright (c) 2010, California Institute of Technology.
 * ALL RIGHTS RESERVED. U.S. Government sponsorship acknowledged.
 * 
 * $Id$
 * 
 * 
 * WRM: Regional Climate Model Evaluation Database API
 * 
 * Query API web service for the WRM database.
 * 
 * @author ahart
 * @author cgoodale
 * 
 */
require_once("./api-config.php");
ini_set('display_errors',1);

$master_link = pg_connect("host=".WRM_DB_HOST
                          ." dbname=".WRM_MASTER_DB_NAME
                          ." user=".WRM_DB_USER
                          ." password=".WRM_DB_PASS) or die("Could not connect: " . pg_last_error());

function listParametersForDataset($shortname) {
	$sql    = "SELECT parameter.parameter_id, parameter.shortname, dataset.shortname as datasetshortname, parameter.longname, parameter.units "
			. "FROM parameter "
			. "LEFT JOIN dataset USING(dataset_id) WHERE dataset.shortname='"
			. pg_escape_string($shortname) . "' ";
	$result = pg_query($sql);
	$resultArray = array();
	while ($row = pg_fetch_assoc($result)) {
		$resultArray[] = $row;
	}
	return $resultArray;
}

$dsLabel = isset($_GET['dataset'])? $_GET['dataset']: false;

if ($dsLabel) {

	$format  = isset($_GET['format']) ? $_GET['format'] : 'json';
	$data    = listParametersForDataset($dsLabel);
	echo    json_encode($data);
} else {
	header("HTTP/1.0 404 Not Found");
}
	
pg_close($master_link);
exit();
