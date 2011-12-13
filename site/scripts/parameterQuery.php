<?php
// Include the WRM Query API class
require_once(HOME . "/classes/WrmQuery.class.php");

// Get a data provider for the WRM database
$wrmDatabase = $app->getDataProvider('MySqlDataProvider');
$wrmDatabase->connect(
	array("server"     => $app->settings['wrm_server'],
          "username"   => $app->settings['wrm_user'],
          "password"   => $app->settings['wrm_pass'],
          "database"   => $app->settings['wrm_database']));
	
// Create an instance of the WRM Query API	
$queryApi = new WrmQuery($wrmDatabase);

// Process the query parameters and store the response
$response = $queryApi->parameterQuery(
			$_GET['datasetId'],
			$_GET['parameterId'],
			$_GET['latMin'],
			$_GET['latMax'],
			$_GET['lonMin'],
			$_GET['lonMax'],
			$_GET['timeStart'],
			$_GET['timeEnd']);
			
			
// Build an array of query metadata
$meta = array("Dataset"   => $queryApi->translateDatasetId($_GET['datasetId']),
              "Parameter" => $queryApi->translateParameterId($_GET['parameterId']),
              "latMin"    => $_GET['latMin'],
              "latMax"    => $_GET['latMax'],
              "lonMin"    => $_GET['lonMin'],
              "lonMax"    => $_GET['lonMax'],
              "timeStart" => $_GET['timeStart'],
              "timeEnd"   => $_GET['timeEnd']);

// Output the results of the query
header('Content-Type: text/plain');
echo "meta:\r\n";
foreach ($meta as $k => $v) {
	echo "{$k}: {$v}\r\n";
}

echo "data output format: [lat,lon,vertical,time,value]\r\n";
echo "data:\r\n";
foreach ($response->data as $row) {
	echo "{$row['latitude']},{$row['longitude']},{$row['vertical']},{$row['time']},{$row['value']}\r\n";	
}

// Finished
$wrmDatabase->disconnect();
exit();










