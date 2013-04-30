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
 * @author boustani
 * 
 */
require_once("./api-config.php");


$master_link = pg_connect("host=".WRM_DB_HOST
			  ." dbname=".WRM_MASTER_DB_NAME 
			  ." user=".WRM_DB_USER 
			  ." password=".WRM_DB_PASS) or die("Could not connect: " . pg_last_error());

function boundingBoxQuery($db_link,$latMin,$latMax,$lonMin,$lonMax,$timeStart,$timeEnd) {
	
	// Convert from provided ISO time to Postgres datetime (YYYYMMDDTHHMMZ --> YYYY-MM-DD HH:MM)
	$timeStart = pg_escape_string($timeStart);
	$real_time_start = substr($timeStart,0,4) . '-' . substr($timeStart,4,2) . '-' . substr($timeStart,6,2) . ' '
					 . substr($timeStart,9,2) . ':' . substr($timeStart,11,2) .':00';
	// Convert from provided ISO time to Postgres datetime (YYYYMMDDTHHMMZ --> YYYY-MM-DD HH:MM)
	$timeEnd = pg_escape_string($timeEnd);
	$real_time_end   = substr($timeEnd,0,4) . '-' . substr($timeEnd,4,2) . '-' . substr($timeEnd,6,2) . ' '
					 . substr($timeEnd,9,2) . ':' . substr($timeEnd,11,2) .':00';
	// Build the query SQL

        $sql = "SELECT latitude, longitude, vertical, time, value  FROM datapoint WHERE "
          .  "latitude>="     . pg_escape_string($latMin)    . ' AND '
          .  "latitude<="     . pg_escape_string($latMax)    . ' AND '
          .  "longitude>="    . pg_escape_string($lonMin)    . ' AND '
          .  "longitude<="    . pg_escape_string($lonMax)    . ' AND '
          .  "time>='{$real_time_start}' AND "
          .  "time<='{$real_time_end}'; ";	
    // Return the response from the server
    // var_dump($sql);
	return pg_query($db_link,$sql);
}


function translateParameterId($link,$parameterId) {

        $sql = "SELECT  longname, shortname from parameter  "
                .  "WHERE  parameter_id= " . pg_escape_string($parameterId)
                .  " LIMIT 1 ";
        $r = pg_query($link,$sql);
        if ('' == pg_last_error($link) && pg_num_rows($r) == 1) {
                $result = pg_fetch_row($r);
                return "{$result[1]} ({$result[0]})";
        } else {
          return "Unknown Parameter Id: {$parameterId}" . pg_last_error();
        }
}

function translateDatasetId($link,$datasetId) {

$sql = "SELECT d.longname, d.shortname from dataset d "
                .  "WHERE  d.dataset_id=$datasetId"
                .  " LIMIT 1 ";

        $r = pg_query($link,$sql);
        if ('' == pg_last_error($link) && pg_num_rows($r) == 1) {
                $result = pg_fetch_row($r);

                return $result[0] . " ({$result[1]}) "; #index=0:longname and index=1:shortname
        } else {
                return "Unknown Dataset Id: {$datasetId}";
        }
}

function printQueryMetadata($link) {

        $datasetName   = translateDatasetId($link,$_GET['datasetId']);
        $parameterName = translateParameterId($link,$_GET['parameterId']);
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
  $resp   = pg_query($link,$sql);
  if (pg_num_rows($resp) == 1) {
    $result = pg_fetch_row($resp);
  } else {
    while (false != ($row = pg_fetch_row($resp))) {
      $result[] = $row;
    }
  }
  pg_free_result($resp);
  return $result;
}

if (isset($_GET['parameterId'])) {

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
  $sql = "SELECT database, timestep, realm, instrument, start_date, end_date, nx, ny, lon_res, lat_res, units from parameter "
    . "WHERE dataset_id={$datasetId} "
    . "AND   parameter_id={$parameterId} "
    . "LIMIT 1";

  $result = get_result($sql,$master_link);

  if (empty($result)) {
    die ("Invalid datasetId or parameterId provided. Please check your values and try again.");
  }
$info=($_GET['info']);
if($info=="yes"){

$infos= array(
  "database" 	=> $result[0],
  "timestep" 	=> $result[1],
  "realm"   	=> $result[2],
  "instrument"	=> $result[3],
  "start_date"  => $result[4],
  "end_date"    => $result[5],
  "nx"    	=> $result[6],
  "ny"    	=> $result[7],
  "lon_res"    	=> $result[8],
  "lat_res"    	=> $result[9],
  "units"    	=> $result[10]
  );

echo json_encode( $infos );

}else{
  // Print Query Metadata
  echo "meta:\r\n";
  echo printQueryMetadata($master_link);
  echo "data output format: [lat,lon,vertical,time,value]\r\n";


  // Get Data Points
  $databaseName = $result[0];
  $DB_NAME=$databaseName;
  $db_link = pg_connect("host=".WRM_DB_HOST 
			." dbname=$DB_NAME"
			." user=".WRM_DB_USER
			." password=".WRM_DB_PASS) or die("Could not connect: " . pg_last_error());

  $resp = boundingBoxQuery(
			   $db_link,
                           $_GET['latMin'],
                           $_GET['latMax'],
                           $_GET['lonMin'],
                           $_GET['lonMax'],
                           $_GET['timeStart'],
                           $_GET['timeEnd']);

  if ('' !== pg_last_error()) {
    echo "<strong>Error:</strong>There was a problem with your query. Check your values and try again.";
    echo "You provided: <br/>\r\n";
    echo printQueryMetadata();
    echo "Postgres said: " . pg_last_error();
    exit();
  }

  // Print Data Points
  echo "data: \r\n";
  while (false != ($row = pg_fetch_row($resp))) {
    // Simply echo to the screen in the form:  lat,lon,vertical,time,value\r\n 
    echo "{$row[0]},{$row[1]},{$row[2]},{$row[3]},{$row[4]}\r\n";
  }

  // Clean Up
  pg_close($db_link);
}
pg_close($master_link);
exit();
}

/*--------------------------------------------------------------table info-----------------------------------------------------------------------*/

function printDatasetMap_pg() {
	global $master_link;
  $query = "SELECT * FROM dataset;";
  $resp  = pg_query($master_link,$query);
  while (false != ($row = pg_fetch_row($resp))) {
    echo "<tr><td>{$row[1]}</td><td>{$row[0]}</td></tr>\r\n";
  }
  pg_free_result($resp);
}

function printParameterMap_pg() {
	global $master_link;
	$query = "SELECT * FROM parameter;";
	$resp  = pg_query($master_link,$query);
	while (false !=($row = pg_fetch_row($resp))) {
		echo "<tr><td>{$row[1]}</td><td>{$row[0]}</td><td>{$row[10]}</td></tr>\r\n";
	}
	pg_free_result($resp);
}

/*--------------------------------------------------------------HTML-----------------------------------------------------------------------*/

?>
<html>
<head>
<title>Regional Climate Modeling Database: Query Service</title>
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
<h1>Regional Climate Model Evaluation Database Query Service</h1>
<h3>Overview</h3>
<p>This service provides a REST-based access to the Regional Climate Model Evaluation database. To request
data, please formulate a query as follows:</p>
<code>
<?php echo "http://{$_SERVER['SERVER_NAME']}{$_SERVER['REQUEST_URI']}?";?>datasetId=#&amp;parameterId=#&amp;latMin=#&amp;latMax=#&amp;lonMin=#&amp;lonMax=#&amp;timeStart=YYYYMMDDTHHMMZ&amp;timeEnd=YYYYMMDDTHHMMZ&amp;info=yes/no
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
  <dt>info (optional)</dt>
  <dd>The general parameter's information returns by setting this to "yes"</dd>
</dl>

<a name="Datasets"></a>

<h3>Datasets (Postgres)</h3>
<p>The following is a lookup table which can be used to obtain the correct id for a given dataset</p>
<table border="1" cellpadding="3">
  <tr><th>Dataset</th><th>Id</th></tr>
  <?php printDatasetMap_pg(); ?>
</table>
<h3>Parameters (Postgres)</h3>
<p>The following is a lookup table which can be used to obtain the correct parameter id of interest for any parameter in the database. </p>
<table border="1" cellpadding="3">
  <tr><th>Parameter</th><th>Parameter Id</th><th>Dataset Id</th></tr>
  <?php printParameterMap_pg(); ?>
</table>

</body>
</html>

<?php 
pg_close($master_link_pg);
exit();
?>
