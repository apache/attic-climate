<?php
/**
 * Copyright (c) 2010, California Institute of Technology.
 * ALL RIGHTS RESERVED. U.S. Government sponsorship acknowledged.
 * 
 * $Id$
 * 
 * 
 * WRM: Regional Climate Model Evaluation Database API
 * 
 * Configuration file for the WRM database query web service.
 * 
 * @author ahart
 * @author cgoodale
 * 
 */
/**
 * Database Connection Details
 * 
 */
define('WRM_DB_HOST',  'localhost');    // Host machine
define('WRM_DB_USER',  'user');         // Database username
define('WRM_DB_PASS',  'pass');         // Stored password for WRM_DB_USER

// The WRM Master database contains a mapping between parameters
// and the databases that contain actual data points for those
// parameters.
define('WRM_MASTER_DB_NAME',  'db_name'); // Master database name

