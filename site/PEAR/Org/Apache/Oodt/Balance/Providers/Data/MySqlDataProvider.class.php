<?php
/*
 * Licensed to the Apache Software Foundation (ASF) under one or more
 * contributor license agreements.  See the NOTICE file distributed with
 * this work for additional information regarding copyright ownership.
 * The ASF licenses this file to You under the Apache License, Version 2.0
 * (the "License"); you may not use this file except in compliance with
 * the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
/**
 * 
 * OODT Balance
 * Web Application Base Framework
 * 
 * Implementation of IApplicationDataProvider for a MySql database.
 * 
 * @author ahart
 * 
 */
class Org_Apache_Oodt_Balance_Providers_Data_MySqlDataProvider 
	implements Org_Apache_Oodt_Balance_Interfaces_IApplicationDataProvider {
	
	public $link;
	
	public function __construct($options = array()) {
		
	}
	
	public function connect($options = array()) {
		$this->link = mysql_connect($options['server'],
			$options['username'],
			$options['password']) or 
			die("Could not connect: " . mysql_error());
			mysql_select_db($options['database'],$this->link) or
			die("Could not select database: " . mysql_error());
	}
	
	public function disconnect($options = array()) {
		if ($this->link) {
			mysql_close($this->link);
		}
	}
	
	public function request($request,$options = array()) {
		if ($this->link) {
			
			// Execute the request and build a response object
			$raw  = mysql_query($request,$this->link);
			$data = new Org_Apache_Oodt_Balance_Core_ApplicationDataResponse();
			
			if ('' != ($errMessage = mysql_error($this->link))) {
				$data->setError($errMessage);
				return $data;
			} else {
			
				// Handle associative array
				if (isset($options['format']) && 
					strtolower($options['format']) == 'assoc') {
					$idx = 0;
					while (false !== $row = mysql_fetch_assoc($raw)) {
						if (isset($options['indexKey'])) {
							$data->add($raw[$options['indexKey']],$row);
						} else {
							$data->add($idx++,$row);
						}
					}
				} 
				
				// Handle numeric array
				else {
					$idx = 0;
					while (false !== $row = mysql_fetch_row($raw)) {
						if (isset($options['indexKey'])) {
							$data->add($raw[$options['indexKey']],$row);
						} else {
							$data->add($idx++,$row);
						}
					}
				}
				
				// Store the request used to generate the data
				$data->setRequestString($request);
				
				// Free the request
				mysql_free_result($raw);
				
				// Return the requested data
				return $data;
			}
		} else {
			$data = new Org_Apache_Oodt_Balance_Core_ApplicationDataResponse();
			$data->setError("Unable to establish connection to data source");
			return $data;
		}
	}
	
	public function command($command,$options = array()) {
		if ($this->link) {
			
			mysql_query($command);
			
		} else {
			$data = Org_Apache_Oodt_Balance_Core_ApplicationDataResponse();
			$data->setError("Unable to establish connection to data source");
			return $data;
		}
	}
	
	public function lastInsertedId($options = array()){
		if ($this->link) {
			
			return mysql_insert_id();
			
		} else {
			$data = Org_Apache_Oodt_Balance_Core_ApplicationDataResponse();
			$data->setError("Unable to establish connection to data source");
			return $data;
		}
	}
}
