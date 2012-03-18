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
 * Implementation of iApplicationAuthenticationProvider, which extends SingleSignOn.
 * 
 * Note: This class has a dependency on the OODT CAS-SSO package 
 *      (http://oodt.jpl.nasa.gov/repo/framework/cas-sso/trunk/src/php/pear)
 *      
 *      To build this dependency, check out the above project and then:
 *      1) cd into the checked out project (you should see a package.xml file)
 *      2) pear package
 *      3) (sudo) pear install --force Org_Apache...tar.gz
 * 
 * @author s.khudikyan
 * @author ahart
 * 
 */
require("Org/Apache/Oodt/Security/SingleSignOn.php");

class Org_Apache_Oodt_Balance_Providers_Authentication_LDAPAuthenticationProvider
	extends Org_Apache_Oodt_Security_SingleSignOn 
	implements Org_Apache_Oodt_Balance_Interfaces_IApplicationAuthenticationProvider {

	/**
	 * If authentication config file exists, require(file_name) file
	 */
	public function __construct() {
		
		// set LDAP constants
		define("CAS_SECURITY",true);
		define("SSO_LDAP_HOST", App::Get()->settings['ldap_host']);
		define("SSO_LDAP_PORT", App::Get()->settings['ldap_port']);
		define("SSO_BASE_DN", App::Get()->settings['ldap_base_dn']);
		define("SSO_GROUPS_DN", App::Get()->settings['ldap_group_dn']);
		define("SSO_COOKIE_KEY", App::Get()->settings['cookie_key']);
		
	}
	
	public function connect() {
		return parent::connect(func_get_arg(0),func_get_arg(1));
	}
	
	public function disconnect() {
		
	}
	
	public function isLoggedIn() {
		return parent::isLoggedIn();
	}
	
	public function login( $username, $password ) {
		return parent::login( $username, $password );
	}
	
	public function logout() {
		parent::logout();
	}

	public function getCurrentUsername() {
		return parent::getCurrentUsername();
	}
	
	public function changePassword( $newPassword ) {
		if ( App::Get()->settings['authentication_encryption_method'] ) {
			return parent::changePassword( $newPassword, App::Get()->settings['authentication_encryption_method'] );
		}
		return parent::changePassword( $newPassword );
	}
	
	public function validateChangePassword( $newPass, $encryptionMethod = "SHA" ) {
		$isValid = true;
		$messages = array();
		// validate rules from config file
		$rules = App::Get()->settings['security_password_rules'];

		if ( isset($rules) ) {
			foreach( $rules as $rule ){
				
				// Separate the rule from the error message
				list($regularExpression,$errorMessage) = explode('|',$rule,2);
				
				// Test the rule
				$rulePassed = preg_match($regularExpression, $newPass);
				
				// If the rule failed, append the error message
				if (!$rulePassed) {
					$messages[] = $errorMessage;
					$isValid    = false;
				}
			}
		}

		if ($isValid && $this->connect(SSO_LDAP_HOST,SSO_LDAP_PORT)) {
		  $result = $this->changePassword($newPass,$encryptionMethod);
		  return true;
		} else
		  return $messages;
	}
	
	public function retrieveUserAttributes( $username, $attributes ) {
		$rawArray 		= parent::retrieveUserAttributes( $username, $attributes );
		$userAttributes = array();
		
		if ( count($rawArray) > 1 ) {
			$rawArray = $rawArray[0];
			// Get only necessary attributes to return
			foreach ( $rawArray as $key=>$keyValue ) {
				foreach ( $attributes as $value ) {
					if ( $key === $value ) {
						$userAttributes[$key] = $keyValue[0];
					}
				}
			}
		}
		return $userAttributes;
	}
	
	public function addUser($userInfo) {
		$ldapconn = $this->connect(SSO_LDAP_HOST,SSO_LDAP_PORT);
		if ($ldapconn) {
			$user  = "uid={$userInfo[ "uid" ]}," . SSO_BASE_DN;
			return ldap_add($ldapconn,$user,$userInfo);
		}
		// connection failed
		return false;
	}
	
	public function usernameAvailability( $username ) {
		$justthese = array( App::Get()->settings['username_attr'] );
		$profile = $this->retrieveUserAttributes($username, $justthese);
		if (count($profile) > 0) {
			return false;
		} else {
			// available
			return true;
		}
	}
	
	public function updateProfile($newInfo) {

		if ($this->isLoggedIn()) {
			$user  = "uid={$this->getCurrentUsername()}," . SSO_BASE_DN ;
			$ldapconn = $this->connect(SSO_LDAP_HOST,SSO_LDAP_PORT);
			
			if (ldap_mod_replace($ldapconn,$user,$newInfo)) {
				return true;
			} else {
				return false;
			}
		} else {
			return false;
		}
	}
	
}
