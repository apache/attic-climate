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
 * LDAPAuthorizationProvider defines an interface that will determine what level 
 * of access a particular user should have to secured resources. 
 * 
 * The interface defines five mandatory functions:
 *    - __construct: Provide any necessary configuration information 
 *               
 *               
 *   Framework implementations of common authorization providers can be found in:
 *   Balance/Providers/Authorization 
 *   Framework authorization providers can be invoked by doing:
 *          App:Get()->getAuthorizationProvider();
 * 
 * @author s.khudikyan
 * 
 */

interface Org_Apache_Oodt_Balance_Interfaces_IApplicationAuthorizationProvider {
	
	/**
	 * Constructor - Instantiate the provider
	 * 
	 */
	public function __construct();
	
	/**
	 * Initiate a connection to the underlying system.
	 * 
	 * @return boolean            True or false depending on the result
	 */
	public function connect();
	
	/**
	 * Retrieves the set of groups for specified user
	 * 
	 * @param $username    string  The user for which groups will be returned
	 * @return array               An empty array or groups the user belongs to
	 */
	public function retrieveGroupsForUser( $username );
		
}
