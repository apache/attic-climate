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
 * Puny_DataStore
 * 
 * Base class for Puny data store implementations
 * 
 * @abstract 
 * 
 * @author ahart
 */
abstract class Puny_DataStore {
	
	protected $host;
	protected $username;
	protected $password;
	protected $dbname;
	
	protected $link;
	
	/**
	 * Connect to the data store
	 * 
	 */	
	public abstract function connect();
	
	/**
	 * Disconnect from the data store
	 */
	public abstract function disconnect();
	
	/**
	 * Request a resource from the data store. Optionally
	 * specify a particular version of the resource to fetch.
	 * 
	 * @param string $resourceId The unique id of the resource
	 * @param integer $version   (Optional) the version to retrieve. Default = latest.
	 */
	public abstract function load( $resourceId, $version = null );
	
	/**
	 * Store a new version of a resource. For simplicity, versions are 
	 * immutable. That is, every time a resource is stored, its version is
	 * first incremented and a new record is created. Implemenations should
	 * take care to automatically increment the version number of the
	 * resource before persisting to the datastore.
	 * 
	 * @param string $resourceId The unique id of the resource
	 * @param string $content The content to store 
	 */
	public abstract function store( Puny_Resource $resource );

}