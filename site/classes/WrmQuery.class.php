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
 * Functions for querying the WRM database.
 * 
 * @author ahart
 * @author cgoodale
 * 
 */
class WrmQuery {
	
	protected $link;	// The connection to the WRM database

	public function __construct($dataProvider) {

		$this->link = $dataProvider;	
	}
	
	public function parameterQuery($datasetId,$parameterId,$latMin,$latMax,$lonMin,$lonMax,$timeStart,$timeEnd) {
	
		// Convert from provided ISO time to MySql datetime (YYYYMMDDTHHMMZ --> YYYY-MM-DD HH:MM)
		$timeStart = self::isoToMySqlDatetime(mysql_real_escape_string($timeStart));
						 
		// Convert from provided ISO time to MySql datetime (YYYYMMDDTHHMMZ --> YYYY-MM-DD HH:MM)
		$timeEnd   = self::isoToMySqlDatetime(mysql_real_escape_string($timeEnd));
		
		// Build the query SQL
		$sql = "SELECT * FROM `dataPoint` dp WHERE "
			.  "dp.dataset_id ="   . mysql_real_escape_string($datasetId) . ' AND '
			.  "dp.latitude  >="   . mysql_real_escape_string($latMin)    . ' AND '
			.  "dp.latitude  <="   . mysql_real_escape_string($latMax)    . ' AND '
			.  "dp.longitude >="   . mysql_real_escape_string($lonMin)    . ' AND '
			.  "dp.longitude <="   . mysql_real_escape_string($lonMax)    . ' AND '
			.  "dp.time      >=    \"{$timeStart}\" AND "
			.  "dp.time      <=    \"{$timeEnd}\"   AND "
			.  "dp.parameter_id="   . mysql_real_escape_string($parameterId);

		$response = $this->link->request($sql,array("format" => "assoc"));
		
		// Return the response from the server
		return $response;
	}
	
	protected static function isoToMySqlDatetime($time) {
		return substr($time,0,4) . '-' . substr($time,4,2) . '-' . substr($time,6,2) . ' '
			   . substr($time,9,2) . ':' . substr($time,11,2) .':00';
	}

	public function translateParameterId($parameterId) {
		
		$sql = "SELECT p.longName from `parameter` p "
			.  "WHERE  p.parameter_id= " . mysql_real_escape_string($parameterId)
			.  " LIMIT 1 ";
			
		$response = $this->link->request($sql,array("format" => "assoc"));
		if ($response->error()) {
			return $response->errorMessage;
		} else {
			return (count($response->data) > 0)
				? "{$response->data[0]['longName']} ({$parameterId})"
				: "Unknown Parameter Id: {$parameterId}";
		}
	}

	public function translateDatasetId($datasetId) {
		
		$sql = "SELECT d.longName, d.shortName from `dataset` d "
			.  "WHERE  d.dataset_id= " . mysql_real_escape_string($datasetId)
			.  " LIMIT 1 ";
		
		$response = $this->link->request($sql,array("format" => "assoc"));
		if ($response->error()) {
			return $response->errorMessage;
		} else {
			return (count($response->data) > 0) 
				? "{$response->data[0]['longName']} ({$response->data[0]['shortName']}) "
				: "Unknown Dataset Id: {$datasetId}";
		}
	}
}