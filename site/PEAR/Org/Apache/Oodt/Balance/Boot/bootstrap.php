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
 * Bootstrap file to provide all framework base files necessary to 
 * satisfy a resource request.
 * 
 * @author ahart
 * 
 */

define("BALANCE_VERSION", '0.3-SNAPSHOT');

// Include Required Framework Interfaces
include("Org/Apache/Oodt/Balance/Interfaces/IApplicationWidget.php");
include("Org/Apache/Oodt/Balance/Interfaces/IApplicationDataProvider.php");
include("Org/Apache/Oodt/Balance/Interfaces/IApplicationAuthenticationProvider.php");
include("Org/Apache/Oodt/Balance/Interfaces/IApplicationAuthorizationProvider.php");

// Include Required Framework Classes
include("Org/Apache/Oodt/Balance/Core/Application.class.php");
include("Org/Apache/Oodt/Balance/Core/ApplicationRequest.class.php");
include("Org/Apache/Oodt/Balance/Core/ApplicationResponse.class.php");
include("Org/Apache/Oodt/Balance/Core/ApplicationDataResponse.class.php");


class App {
	
	protected static $app = null;
	
	public static function Create($config) {
		if (!self::$app) {
			self::$app = new Org_Apache_Oodt_Balance_Core_Application($config);
		} 
		return self::$app;
	}
	
	public static function Get() {
		return self::$app;
	}
}
