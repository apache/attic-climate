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
 * IApplicationDataProvider defines an interface that should be implemented
 * by all data providers to simplify the process of integrating and accessing
 * multiple heterogeneous data sources. A data source could be a relational
 * SQL-like database, a CAS File Manager, an LDAP server, anything that can
 * be queried for data. 
 * 
 * The interface defines five mandatory functions:
 *    - __construct: Provide any necessary configuration information but do
 *               not actually establish a connection to the underlying data
 *               source.
 *    - connect: This function does the work of actually connecting to the 
 *               underlying data source. Options can be provided either here
 *               or in the constructor arguments (or both), but the connection
 *               to the underlying data source should not be initiated until
 *               this function is invoked.
 *    - disconnect: Disconnect from the underlying data source, performing any
 *               necessary clean up operations in the process.
 *    - request: Satisfy a request for data. The format that this request takes
 *               will likely differ across implementations. An array of further
 *               options may be provided as an optional second argument. As a 
 *               concrete  example, an SQL-like data source may support string 
 *               requests like "SELECT * FROM foo WHERE bar='baz'". The 
 *               response from this call must be an ApplicationDataResponse object
 *               containing the (possibly multidimensional) array of response info. 
 *    - command: Send a command to the underlying data source. As with request,
 *               the format that this command takes will likely differ across
 *               implementations. As a concrete example, an SQL-like data source
 *               may support string commands like "UPDATE foo set bar='baz'". 
 *               Command should not be expected to return a value, other than
 *               possibly true/false to indicate the success of the call.
 *               
 *               
 *   Framework implementations of common data providers can be found in:
 *   {LIB}/classes/dataProviders   and should be named FooDataProvider.class.php.
 *   Framework data providers can be invoked by doing:
 *          $app->GetDataProvider('FooDataProvider');
 *   
 *   Custom data providers should be placed in:
 *   {HOME}/classes/dataProviders  and should be named FooDataProvider.class.php.
 *   Custom data providers can be invoked by doing:
 *          $app->GetDataProvider('foo',true); // true --> custom
 * 
 * @author ahart
 * 
 */
interface Org_Apache_Oodt_Balance_Interfaces_IApplicationDataProvider {
	
	/**
	 * Constructor - Instantiate the provider but do not yet connect
	 * to the underlying data source.
	 * 
	 * @param $options  array   An optional set of configuration values
	 */
	public function __construct($options = array());
	
	/**
	 * Initiate a connection to the underlying data source
	 * 
	 * @param $options  array  An optional set of configuration values
	 * @return boolean         True or false depending on the result
	 */
	public function connect($options = array());
	
	/**
	 * Disconnect from the underlying data source and perform any
	 * cleanup operations necessary.
	 * 
	 * @param $options  array  An optional set of configuration values
	 * @return unknown_type    True or false depending on the result
	 */
	public function disconnect($options = array());
	
	/**
	 * Request data from the underlying data source.
	 * 
	 * @param $request  mixed  The request itself, usually a string. The nature
	 *                         of the request is necessarily implementation 
	 *                         specific and will vary across providers. For a 
	 *                         SQL-like relational provider, this will likely be
	 *                         a "SELECT ..." string.
	 * @param $options  array  An array of options to configure the request.
	 *                         These will be implementation-specific and 
	 *                         therefore will likely differ across providers.
	 * @return ApplicationDataResponse  The resulting data retrieved
	 */
	public function request($request,$options = array());
	
	/**
	 * Send a command to the underlying data source.
	 * 
	 * @param $command mixed   The command itself, usually a string. The nature
	 *                         of the command is necessarily implementation 
	 *                         specific and will vary across providers. For a 
	 *                         SQL-like relational provider, this will likely be
	 *                         a "UPDATE ...", or "CREATE ..." string.
	 * @param $options  array  An array of options to configure the command.
	 *                         These will be implementation-specific and 
	 *                         therefore will likely differ across providers.
	 * @return boolean         True or false depending on the success of the command
	 */
	public function command($command,$options = array());
	
}
