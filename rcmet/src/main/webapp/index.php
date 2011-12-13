<?php
/**
 * Copyright (c) 2010, California Institute of Technology.
 * ALL RIGHTS RESERVED. U.S. Government sponsorship acknowledged.
 * 
 * $Id$
 * 
 * 
 * OODT Balance
 * Web Application Base Framework
 * 
 * Front-controller
 * This file handles the marshalling of requests to the appropriate
 * application view. 
 * 
 * @author ahart
 * 
 */
define ("DEBUG", true); // Change this to `false` when no longer debugging

// Application root directory path (should never need to change this)
define ("HOME",  dirname(__FILE__));

/* Set up application environment ***************************************/
require_once("Gov/Nasa/Jpl/Oodt/Balance/Boot/bootstrap.php");

/* Initialize the application with the settings from config.ini *********/
$app = $GLOBALS['app'] = App::Create(parse_ini_file(HOME . '/config.ini'));

/* Generate and send a response to the browser **************************/
$response = $app->getResponse()->send();

/* Clean up after ourselves *********************************************/
$app->cleanup();