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

$master_link = mysql_connect(WRM_DB_HOST,WRM_DB_USER,WRM_DB_PASS) or die("Could not connect: " . mysql_error());
mysql_select_db(WRM_MASTER_DB_NAME) or die("Could not select db: " . mysql_error());


function boundingBoxQuery($databaseName,$latMin,$latMax,$lonMin,$lonMax,$timeStart,$timeEnd) {
		
	// Convert from provided ISO time to MySql datetime (YYYYMMDDTHHMMZ --> YYYY-MM-DD HH:MM)
	$timeStart = mysql_real_escape_string($timeStart);
	$real_time_start = substr($timeStart,0,4) . '-' . substr($timeStart,4,2) . '-' . substr($timeStart,6,2) . ' '
					 . substr($timeStart,9,2) . ':' . substr($timeStart,11,2) .':00';
					 
	// Convert from provided ISO time to MySql datetime (YYYYMMDDTHHMMZ --> YYYY-MM-DD HH:MM)
	$timeEnd = mysql_real_escape_string($timeEnd);
	$real_time_end   = substr($timeEnd,0,4) . '-' . substr($timeEnd,4,2) . '-' . substr($timeEnd,6,2) . ' '
					 . substr($timeEnd,9,2) . ':' . substr($timeEnd,11,2) .':00';
	
	// Build the query SQL
	$sql = "SELECT * FROM `dataPoint` dp WHERE "
	  .  "dp.latitude>="     . mysql_real_escape_string($latMin)    . ' AND '
	  .  "dp.latitude<="     . mysql_real_escape_string($latMax)    . ' AND '
	  .  "dp.longitude>="    . mysql_real_escape_string($lonMin)    . ' AND '
	  .  "dp.longitude<="    . mysql_real_escape_string($lonMax)    . ' AND '
	  .  "dp.time>=\"{$real_time_start}\" AND "
	  .  "dp.time<=\"{$real_time_end}\"; ";
	
	// Return the response from the server
       	return mysql_query($sql);
}

function translateParameterId($parameterId) {
	global $master_link;
	
	$sql = "SELECT longName, shortName, `database` from `parameter`  "
		.  "WHERE  parameter_id= " . mysql_real_escape_string($parameterId)
		.  " LIMIT 1 ";
	$r = mysql_query($sql,$master_link);
	if ('' == mysql_error($master_link) && mysql_num_rows($r) == 1) {
		$result = mysql_fetch_assoc($r);
		return "{$result['shortName']} ({$result['longName']})";
	} else {
	  return "Unknown Parameter Id: {$parameterId}" . mysql_error();
	}
}

function translateDatasetId($datasetId) {
	global $master_link;
	
	$sql = "SELECT d.longName, d.shortName from `dataset` d "
		.  "WHERE  d.dataset_id= " . mysql_real_escape_string($datasetId)
		.  " LIMIT 1 ";
	$r = mysql_query($sql,$master_link);
	if ('' == mysql_error($master_link) && mysql_num_rows($r) == 1) {
		$result = mysql_fetch_assoc($r);
		return $result['longName'] . " ({$result['shortName']}) ";
	} else {
		return "Unknown Dataset Id: {$datasetId}";
	}
}

function printDatasetMap() {
  global $master_link;
  $query = "SELECT * FROM `dataset` d;";
  $resp  = mysql_query($query,$master_link);
  while (false != ($row = mysql_fetch_assoc($resp))) {
    echo "<tr><td>{$row['longName']}</td><td>{$row['dataset_id']}</td></tr>\r\n";
  }
  mysql_free_result($resp);
}

function printParameterMap() {
	global $master_link;
	$query = "SELECT * FROM `parameter` p;";
	$resp  = mysql_query($query,$master_link);
	while (false !=($row = mysql_fetch_assoc($resp))) {
		echo "<tr><td>{$row['longName']}</td><td>{$row['parameter_id']}</td></tr>\r\n";
	}
	mysql_free_result($resp);
}


function printQueryMetadata() {
	$datasetName   = translateDatasetId($_GET['datasetId']);
	$parameterName = translateParameterId($_GET['parameterId']);
	echo " Dataset: {$datasetName} \r\n";
	echo " Parameter: {$parameterName} (id:{$_GET['parameterId']})\r\n";
	echo " latMin: {$_GET['latMin']}\r\n"
		." latMax: {$_GET['latMax']}\r\n"
		." lonMin: {$_GET['lonMin']}\r\n"
		." lonMax: {$_GET['lonMax']}\r\n"
		." timeStart: {$_GET['timeStart']}\r\n"
		." timeEnd: {$_GET['timeEnd']}\r\n"
		."\r\n";
}

function get_result($sql,$link) {
  $result = array();
  $resp   = mysql_query($sql,$link);
  if (mysql_num_rows($resp) == 1) {
    $result = mysql_fetch_assoc($resp);
  } else {
    while (false != ($row = mysql_fetch_assoc($resp))) {
      $result[] = $row;
    }
  }
  mysql_free_result($resp);
  return $result;
}

if (isset($_GET['latMin'])) {

  // Ensure that required datasetId and parameterId were provided
  if (!isset($_GET['datasetId'])) {
    die("'datasetId' is required but was not provided among the query parameters");
  }
  if (!isset($_GET['parameterId'])) {
    die("'parameterId' is required but was not provided among the query parameters");
  }

  // Take the provided datasetId and parameterId values and determine the database to use
  // 
  $datasetId   = $_GET['datasetId'];
  $parameterId = $_GET['parameterId'];
  $sql = "SELECT `parameter`.`database` from `parameter` "
    . "WHERE `dataset_id`={$datasetId} "
    . "AND   `parameter_id`={$parameterId} "
    . "LIMIT 1";
  
  $result = get_result($sql,$master_link);
  
  if (empty($result)) {
    die ("Invalid datasetId or parameterId provided. Please check your values and try again.");
  }


  // Print Query Metadata
  echo "meta:\r\n";
  echo printQueryMetadata();
  echo "data output format: [lat,lon,vertical,time,value]\r\n";



  // Get Data Points
  $databaseName = $result['database'];
  mysql_select_db($databaseName);
  $resp = boundingBoxQuery(
			   $databaseName,
			   $_GET['latMin'],
			   $_GET['latMax'],
			   $_GET['lonMin'],
			   $_GET['lonMax'],
			   $_GET['timeStart'],
			   $_GET['timeEnd']);

  if ('' !== mysql_error()) {
    echo "<strong>Error:</strong>There was a problem with your query. Check your values and try again.";
    echo "You provided: <br/>\r\n";
    echo printQueryMetadata();
    echo "MySQL said: " . mysql_error();
    exit();
  }
	
  // Print Data Points
  echo "data: \r\n";
  while (false != ($row = mysql_fetch_assoc($resp))) {
    // Simply echo to the screen in the form:  lat,lon,z,time,value\r\n 
    echo "{$row['latitude']},{$row['longitude']},{$row['vertical']},{$row['time']},{$row['value']}\r\n";
  }

  // Clean Up
  mysql_close($master_link);
  exit();
}
?>
<html>
<head>
<title>WRM Regional Climate Modeling Database: Query Service</title>
<style type="text/css">
code {
	background-color:#eee;
	border:dashed 3px #ccc;
	padding:10px;
	display:block;
	margin:10px auto;
	
}
</style>
</head>
<body>
<h1>Water Resource Management</h1>
<h2>Regional Climate Model Evaluation Database Query Service</h2>
<h3>Overview</h3>
<p>This service provides a REST-based access to the WRM Regional Climate Model Evaluation database. To request
data, please formulate a query as follows:</p>
<code>
<?php echo "http://{$_SERVER['SERVER_NAME']}{$_SERVER['REQUEST_URI']}";?>?datasetId=#&amp;parameterId=#&amp;latMin=#&amp;latMax=#&amp;lonMin=#&amp;lonMax=#&amp;timeStart=YYYYMMDDTHHMMZ&amp;timeEnd=YYYYMMDDTHHMMZ
</code>
<h3>Query Parameters</h3>
<dl>
  <dt>datasetId</dt>
  <dd>The unique id of the requested dataset. See <a href="#Datasets">Datasets</a> for complete list</dd>
  <dt>parameterId</dt>
  <dd>The parameter (SurfAirTemp_A, etc) to return values for. See <a href="#Parameters">Parameters</a> for complete list</dd>
  <dt>latMin</dt>
  <dd>The latitude of the lower-left corner of the results bounding box (minimum desired latitude)</dd>
  <dt>latMax</dt>
  <dd>The latitude of the upper-right corner of the results bounding box (maximum desired latitude)</dd>
  <dt>lonMin</dt>
  <dd>The longitude of the lower-left corner of the results bounding box (minimum desired longitude)</dd>
  <dt>lonMax</dt>
  <dd>The longitude of the upper-right corner of the results bounding box (maximum desired longitude)</dd>
  <dt>timeStart</dt>
  <dd>The ISO time marking the beginning of the desired time range (Format: YYYYMMDD<strong>T</strong>HHMM<strong>Z</strong>)</dd>
  <dt>timeEnd</dt>
  <dd>The ISO time marking the end of the time range (Format: YYYYMMDD<strong>T</strong>HHMM<strong>Z</strong>)</dd>
</dl>

<a name="Datasets"></a>
<h3>Datasets</h3>
<p>The following is a lookup table which can be used to obtain the correct id for a given dataset</p>
<table border="1" cellpadding="3">
  <tr><th>Dataset</th><th>Id</th></tr>
  <?php printDatasetMap(); ?>
</table>
<a name="Parameters"></a>
<h3>Parameters</h3>
<p>The following is a lookup table which can be used to obtain the correct parameter id of interest for any parameter in the database. </p>
<table border="1" cellpadding="3">
  <tr><th>Parameter</th><th>Id</th></tr>
  <?php printParameterMap(); ?>
</table>
</body>
</html>

<?php 
mysql_close($link);
exit();
