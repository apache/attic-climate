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
interface Org_Apache_Oodt_Balance_Interfaces_IApplicationAuthenticationProvider {
	
	/**
	 * Constructor - Instantiate the provider but do not yet connect
	 * to the underlying system.
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
	 * Disconnect from the underlying system and perform any cleanup 
	 * operations necessary.
	 * 
	 * @return boolean 		      True or false depending on the result
	 */
	public function disconnect();
	
	/**
	 * Check if a valid user has logged in.
	 * 
	 * @return boolean 		      True or false depending on the result
	 */	
	public function isLoggedIn();
	
	/**
	 * Determine whether privileges will be granted to a particular user
	 * using credentials provided.
	 * 
	 * @param $username    mixed  The username is usually a string. 
	 * @param $password    mixed  The password is usually a string. 
	 * @return mixed	          True or false depending on the success of login
	 */
	public function login( $username, $password );
	
	/**
	 * Ending the user's session to the underlying system.
	 * 
	 */
	public function logout();
	
	/**
	 * Get current user's username.
	 * 
	 */
	public function getCurrentUsername();
	
	/**
	 * Change current user's password.
	 * 
	 * @param $newPassword string
	 * @return boolean			   True or false depending on the success of password change
	 */
	public function changePassword( $newPassword );

	/**
	 * Checks if user is logged in. If true, validates rules from config file and uses 
	 * {@link changePassword} to change password.
	 * 
	 * @param $newPass            string  The new password
	 * @param $encryptionMethod   string  The encryption method used
	 */
	public function validateChangePassword( $newPass, $encryptionMethod = "SHA" );
	
	/**
	 * Retrieves the set of attributes from the user's entry 
	 * 
	 * @param $username    string  The user for which attributes will be returned
	 * @param $attributes  array   Attributes to retrieve
	 * @return array               An empty array or requested attributes
	 */
	public function retrieveUserAttributes( $username, $attributes );
	
	/**
	 * Creates a new account with the user information provided
	 * 
	 * @param $userInfo    array  Can include different values depending on provider
	 * 								i.e. username, firstname, lastname, email
	 */
	public function addUser( $userInfo );
	
	/**
	 * Uses {@link retrieveUserAttributes} to retrieve information about the provided 
	 * user. If count of array returned is > 0 then the username is not available.
	 * 
	 * @param $username	   string The username for which a user is checking the 
	 * 								availability of
	 */	
	public function usernameAvailability( $username );
	
	/**
	 * Updates user information with the values of provided attributes
	 * 
	 * @param $newInfo     array  (key, value) based array, where keys are the user's 
 	 * 								entry attribute ids and the values will replace 
 	 * 								the values of those attributes 
	 */
	public function updateProfile( $newInfo );
	
}
