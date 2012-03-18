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
 * ApplicationDataResponse provides a standard response object for use by application
 * data providers. 
 * 
 * The ApplicationDataResponse works off of the idea that the KEY=>VALUE paradigm
 * is more or less universal and suits (or is at least compatible with) a broad array
 * of data sources. By guaranteeing that all data providers will return objects of this type
 * in response to data requests, it is possible to simplify the process of integrating
 * and assimilating data from multiple heterogeneous sources
 * 
 * @author ahart
 * 
 */
class Org_Apache_Oodt_Balance_Core_ApplicationDataResponse {
	
	public $requestString;
	public $data;
	public $errorOccurred;
	public $errorMessage;
	
	public function __construct($seed = array()) {
		$this->data = $seed;
		$this->errorOccurred = false;
	}
	
	public function size() {
		return count($this->data);
	}
	
	public function count() {
		return count($this->data);
	}
	
	public function add($key,$value) {
		$this->data[$key] = $value;
	}
	
	public function bulkAdd($data) {
		$this->data = array_merge($this->data,$data);
	}
	
	public function get($key) {
		return (isset($this->data['key']))
			? $this->data['key']
			: false;
	}
	
	public function setRequestString($request) {
		$this->requestString = $request;
	}
	
	public function error() {
		return ($this->errorOccurred);
	}
	
	public function setError($message) {
		$this->errorOccurred = true;
		$this->errorMessage  = true;
	}
}
