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

/*
 * OODT Balance
 * Web Application Base Framework
 *
 * Front-controller
 * This file handles the marshalling of requests to the appropriate
 * application view.
 *
 */
define ("DEBUG", true); // Change this to `false` when no longer debugging

// Application root directory path (should never need to change this)
define ("HOME",  dirname(__FILE__));

/* Set up application environment ***************************************/
require_once("Org/Apache/Oodt/Balance/Boot/bootstrap.php");

/* Initialize the application with the settings from config.ini *********/
$app = $GLOBALS['app'] = App::Create(parse_ini_file(HOME . '/config.ini'));

/* Initialize any globally required modules here ************************/
// Example:
// To load a module 'foo', located at ./modules/foo, on every request:
// App::Get()->loadModule('foo');

/* Generate and send a response to the browser **************************/
$response = $app->getResponse()->send();

/* Clean up after ourselves *********************************************/
$app->cleanup();
