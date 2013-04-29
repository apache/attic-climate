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

function listDatasets() {
	$sql    = "SELECT dataset_id,shortname,longname,source from dataset";
	$result = pg_query($sql);
	$resultArray = array();
	while ($row = pg_fetch_assoc($result)) {
		$resultArray[] = $row;
	}	
	return $resultArray;
}

$format = isset($_GET['format']) ? $_GET['format'] : 'json';
$data   = listDatasets();
echo    json_encode($data);

pg_close($master_link);
exit();
