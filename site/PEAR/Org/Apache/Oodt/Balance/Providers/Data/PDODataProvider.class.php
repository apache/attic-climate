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
 * Implementation of IApplicationDataProvider for PHP PDO.
 * 
 * @author s.khudikyan
 * @author ahart
 * 
 */
class Org_Apache_Oodt_Balance_Providers_Data_PDODataProvider 
	implements Org_Apache_Oodt_Balance_Interfaces_IApplicationDataProvider {
	
	public $link;
	
	public function __construct($options = array()) {
		
	}
	
	public function connect($options = array()) {
		try {
			$dsn = 'mysql:host='.$options['server'].';dbname='.$options['database'];
			$this->link = new PDO( $dsn, $options['username'], $options['password'] );
		} catch (PDOException $e) {
			die("There was an error connecting to the database: " . $e->getMessage());
		}
	}
	
	public function disconnect($options = array()) {
		if ($this->link) {
			/*** close the database connection ***/
    		$this->link = null;
		}
	}
	
	public function request($request,$options = array() ) {
		$data = new Org_Apache_Oodt_Balance_Core_ApplicationDataResponse();
		
		if ($this->link) {
			
			// Handle associative array
			if (isset($options['format']) && 
				strtolower($options['format']) == 'assoc') {
					
					try {
						// fetch into an PDOStatement object
    					$stmt = $this->link->queryAll($request);
    					$result = $stmt->fetch(PDO::FETCH_ASSOC);
					} catch (PDOException $e) {
						
						$data->setError( $e->getMessage() );
						return $data;
					}
			}

			// Handle numeric array
			else {
					try {	
						// fetch into an PDOStatement object
    					$stmt = $this->link->queryAll($request);
    					$result = $stmt->fetch(PDO::FETCH_NUM);
					} catch (PDOException $e) {
						
						$data->setError( $e->getMessage() );
						return $data;
					}
			}
				
			// Store the request used to generate the data
			$data->bulkAdd($result);
			
			// Free the request
			$this->link->free();
			
			// Return the requested data
			return $data;

		} else {
			$data->setError("Unable to establish connection to data source");
			return $data;
		}
	}
	
	public function command($command,$options = array()) {
		$data = new Org_Apache_Oodt_Balance_Core_ApplicationDataResponse();
		
		if ($this->link) {
			
			try {
				
				$result = $this->link->exec( $command );
			} catch (PDOException $e) {
				
				$data->setError( $e->getMessage() );
				return $data;
			}
			
		} else {
			$data->setError( "Unable to establish connection to data source" );
			return $data;
		}
	}
	
	public function lastInsertedId($options = array()){
		$data = new Org_Apache_Oodt_Balance_Core_ApplicationDataResponse();
		
		if ($this->link) {
			
			try {
				$lastId = $this->link->lastInsertId();				
			} catch (PDOException $e) {
				
				$data->setError( $e->getMessage() );
				return $data;
			}
			return $lastId;
			
		} else {
			$data->setError("Unable to establish connection to data source");
			return $data;
		}
	}
	
}
