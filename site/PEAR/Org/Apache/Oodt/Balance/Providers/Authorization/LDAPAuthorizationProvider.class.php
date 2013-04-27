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
 * IApplicationAuthenticationProvider defines an interface that should be 
 * implemented by all authentication providers to simplify the process of 
 * accessing and retrieving information about the underlying system. 
 * 
 * The interface defines five mandatory functions:
 *    - __construct: Provide any necessary configuration information but do
 *               not actually establish a connection to the underlying system.
 *    - connect: This function does the work of actually connecting to the 
 *               underlying system. Options can be provided either here or in 
 *               the constructor arguments (or both), but the connection to the 
 *               underlying system should not be initiated until this function 
 *               is invoked.
 *    - disconnect: Disconnect from the underlying system, performing any
 *               necessary clean up operations in the process.
 *    - checkLogin: Check if a valid user has logged in.
 *    - login:   Determine the ability to gain access to the underlying system 
 *    			 as a legitimate user. The requirements are a valid username 
 *    			 (or user ID) and password.
 *    - logout:  Ending the user's session to the underlying system.
 *               
 *               
 *   Framework implementations of common authentication providers can be found in:
 *   {LIB}/classes/authenticationProviders   and should be named FooAuthenticationProvider.class.php.
 *   Framework authentication providers can be invoked by doing:
 *          $app->GetAuthenticationProvider('FooAuthenticationProvider');
 *   
 *   Custom authentication providers should be placed in:
 *   {HOME}/classes/authenticationProviders  and should be named FooAuthenticationProvider.class.php.
 *   Custom authentication providers can be invoked by doing:
 *          $app->GetAuthenticationProvider('foo',true); // true --> custom
 * 
 * @author s.khudikyan
 * 
 */

class Org_Apache_Oodt_Balance_Providers_Authorization_LDAPAuthorizationProvider 
	implements Org_Apache_Oodt_Balance_Interfaces_IApplicationAuthorizationProvider {
	
	/**
	 * If authorization config file exists, require(file_name) file
	 */
	public function __construct() {
		// Set LDAP constants
		define("AUTH_BASE_DN",   App::Get()->settings['authorization_ldap_base_dn']);
		define("AUTH_GROUPS_DN", App::Get()->settings['authorization_ldap_group_dn']);
		define("AUTH_LDAP_HOST", App::Get()->settings['authorization_ldap_host']);
		define("AUTH_LDAP_PORT", App::Get()->settings['authorization_ldap_port']);
	}
	
	public function retrieveGroupsForUser($username,$searchDirectory = AUTH_GROUPS_DN) {
		
		// attempt to connect to ldap server 
		$ldapconn = $this->connect(AUTH_LDAP_HOST,AUTH_LDAP_PORT);
		$groups   = array();
		if ($ldapconn) {
			$filter = "(&(objectClass=groupOfUniqueNames)"
				."(uniqueMember=uid={$username}," . AUTH_BASE_DN . "))";
			$result = ldap_search($ldapconn,$searchDirectory,$filter,array('cn'));
			
			if ($result) {
				$entries = ldap_get_entries($ldapconn,$result);
				foreach ($entries as $rawGroup) {
					if (isset($rawGroup['cn'][0]) 
					&& $rawGroup['cn'][0] != '') {
						$groups[] = $rawGroup['cn'][0];
					}
				}
			}
		} 
		return $groups;
	}
			
	public function connect() {
		if ($conn = ldap_connect(func_get_arg(0),func_get_arg(1))) {
			// Connection established
			$this->connectionStatus = 1;
			ldap_set_option($conn, LDAP_OPT_PROTOCOL_VERSION, 3);
			ldap_set_option($conn, LDAP_OPT_DEBUG_LEVEL, 7);
			ldap_set_option($conn, LDAP_OPT_REFERRALS, 0);	
			$this->conn = $conn;
			return $conn;
		} else {
			// Connection failed
			return false;
		}
	}		
}
