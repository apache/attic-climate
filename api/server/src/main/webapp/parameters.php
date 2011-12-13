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

$master_link = mysql_connect(WRM_DB_HOST,WRM_DB_USER,WRM_DB_PASS) or die("Could not connect: " . mysql_error());
mysql_select_db(WRM_MASTER_DB_NAME) or die("Could not select db: " . mysql_error());

function listParametersForDataset($shortName) {
	$sql    = "SELECT parameter.parameter_id, parameter.shortName, dataset.shortName as datasetShortName,parameter.longName,parameter.units "
			. "FROM `parameter` "
			. "LEFT JOIN `dataset` USING(dataset_id) WHERE dataset.shortName='"
			. mysql_real_escape_string($shortName) . "' ";
	$result = mysql_query($sql);
	$resultArray = array();
	while ($row = mysql_fetch_assoc($result)) {
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
	
mysql_close($master_link);
exit();