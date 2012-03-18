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
 * Implementation of IApplicationDataProvider for PEAR MDB2.
 * 
 * @author s.khudikyan
 * @author ahart
 * 
 */
require_once( 'MDB2.php' );

class Org_Apache_Oodt_Balance_Providers_Data_MDB2DataProvider 
	implements Org_Apache_Oodt_Balance_Interfaces_IApplicationDataProvider {
	
	public $link;
	
	public function __construct($options = array()) {
		
	}
	
	public function connect($options = array()) {
		$dsn = 'mysql://'.$options['username'].':'.$options['password'].'@'.$options['server'].'/'.$options['database'];
		$this->link = MDB2::singleton( $dsn );
		
		if ( PEAR::isError($this->link) ) {

			die("There was an error connecting to the database: " . $this->link->getMessage());
		}
	}
	
	public function disconnect($options = array()) {
		if ($this->link) {
			$this->link->disconnect();
		}
	}
	
	public function request($request,$options = array() ) { 
		$data = new Org_Apache_Oodt_Balance_Core_ApplicationDataResponse();
		
		if ($this->link) {
			
			// Handle associative array
			if (isset($options['format']) && 
				strtolower($options['format']) == 'assoc') {
					
					// Execute the request and build a response object
					$result  = $this->link->queryAll($request,null,MDB2_FETCHMODE_ASSOC);
			}

			// Handle numeric array
			else {
				
				// Execute the request and build a response object
				$result  = $this->link->queryAll($request,null,MDB2_FETCHMODE_ORDERED);
			}
			
			if ( PEAR::isError($result) ) {
				
				$data->setError($result->getMessage());
				return $data;
			} else {
				
				// Store the request used to generate the data
				$data->bulkAdd($result);
				
				// Free the request
				$this->link->free();
				
				// Return the requested data
				return $data;
			}
		} else {
			$data->setError("Unable to establish connection to data source");
			return $data;
		}
	}
	
	public function command($command,$options = array()) {
		$data = new Org_Apache_Oodt_Balance_Core_ApplicationDataResponse();
		
		if ($this->link) {
			
			$result = $this->link->exec($command);
			
			if ( PEAR::isError($result) ) {
				
				$data->setError($result->getMessage());
				return $data;
			}
		} else {
			$data->setError("Unable to establish connection to data source");
			return $data;
		}
	}
	
	public function lastInsertedId($options = array()){
		$data = new Org_Apache_Oodt_Balance_Core_ApplicationDataResponse();
		
		if ($this->link) {
			
			$result = $this->link->lastInsertId();
			
			if ( PEAR::isError($result) ) {
				
				$data->setError($result->getMessage());
				return $data;
			} else {
							
				return $result;
				
			}
		} else {
			$data->setError("Unable to establish connection to data source");
			return $data;
		}
	}
	
}
