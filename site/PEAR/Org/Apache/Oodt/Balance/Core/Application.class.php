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
 * Main class for OODT Balance web applications. Contains utility
 * methods and definitions that provide standard functionality across
 * the site.
 * 
 * @author ahart
 * 
 */
class Org_Apache_Oodt_Balance_Core_Application {
	
	public $request;
	
	public $subrequest;
	
	public $authenticationProviderInstance = null;
	
	public $authorizationProviderInstance = null;
	
	public $response;
	
	public $settings;
	
	public $modulesLoaded;
	
	public function __construct($settings) {
		
		// Save the application settings
		$this->settings = $settings;
		
		// Update the PHP include path to include the locations specified in
		// the application configuration .ini file
		if (isset($this->settings['classes_dir']) && is_array($this->settings['classes_dir'])) {
			$customClassPath = implode(';',$this->settings['classes_dirs']);
			set_include_path(get_include_path() . ';' . $customClassPath);
		}
		
		// Initialize a session
		session_start();
		
		// Define the application base url
		define ("SITE_ROOT", ($settings['site_root'] == '/') 
			? '' 
			: $settings['site_root']);
			
	}
	
	
	public function getResponse() {
		
		$this->setAuthenticationProviderInstance();
		$this->setAuthorizationProviderInstance();
		
		// Interpret the request uri of the current request
		$uri = App::Get()->settings['site_root'] != '/'
			? substr($_SERVER['REQUEST_URI'],strlen(App::Get()->settings['site_root']))
			: $_SERVER['REQUEST_URI'];
		$this->request = new Org_Apache_Oodt_Balance_Core_ApplicationRequest(
			$this->settings,$uri);
			
		// Initialize a response object for the request
		$this->response = new Org_Apache_Oodt_Balance_Core_ApplicationResponse(
			$this->settings,$this->request);
			
		// Process the response
		$this->response->process();
			
		// Return the processed response object
		return $this->response;
	}
	
	public function cleanup() {
		
	}
	
	/**
	 * Determine whether the current request maps to resources associated
	 * with an application module. 
	 * 
	 * If a view, script, or static asset is part of an application module,
	 * the path to the file will differ than those for regular application
	 * resources. This function provides a way to determine whether a given
	 * request should be considered part of a module or of the general 
	 * application. 
	 * 
	 * @param $requestURI - The request uri to test
	 * @return boolean    - true indicates the request uri belongs to a module
	 */
	public function isModule($requestURI) {
		// Determine whether a module is being requested
		$filteredURI = $requestURI;
		$filteredURI = ltrim($filteredURI,'/');
		$parts = explode('/',$filteredURI);

        if (is_dir(HOME . "/modules")) {
			$handle = opendir(HOME . "/modules");
			while (false !== ($dir = readdir($handle))) {
				if ( $dir == $parts[0] && $module = $this->loadModule($dir) ) {
					return $module;
				}
			}
		}
		return false;
	}
	
	public function getAuthenticationProvider() {
		return $this->authenticationProviderInstance;
	}
	
	public function setAuthenticationProviderInstance() {
		
		// Check if the user wants authentication for application 
		if ( $this->settings['authentication_class_path'] != null &&
			 $this->settings['authentication_class']      != null   ) {
			 	
			 	require_once $this->settings['authentication_class_path'];
				$authProvider = $this->settings['authentication_class'];
				$this->authenticationProviderInstance = new $authProvider();
		}
	}
	
	public function getAuthorizationProvider() {
		return $this->authorizationProviderInstance;
	}
	
	public function setAuthorizationProviderInstance() {
		
		// Check if the user wants authorization for application 
		if ( $this->settings['authorization_class_path'] != null &&
			 $this->settings['authorization_class']      != null   ) {
			 	
			 	require_once $this->settings['authorization_class_path'];
				$authProvider 		  				 = $this->settings['authorization_class'];
				$this->authorizationProviderInstance = new $authProvider();
		}
	}
	
	public function loadModule($modName = null) {
		// If the module name is null, a module is requesting that
		// its own context be loaded
		if ($modName === null) {
			return $this->getModuleContext();
		}

		// If the module has been previously loaded, return its context
		if (isset($this->modulesLoaded[$modName])) {
			return $this->modulesLoaded[$modName];
		}

		// check if module path exists before loading module context
		$modulePath = HOME . "/modules/{$modName}";
		if ( is_dir($modulePath) ) {
			
			// create stdClass 
			$modClass = new stdClass();
			$modClass->modulePath   = $modulePath;
			$modClass->moduleRoot   = SITE_ROOT . "/{$modName}";
			$modClass->moduleStatic = SITE_ROOT . "/modules/{$modName}/static";

			$this->modulesLoaded[$modName] = $modClass;

			// Read in the module config file and append to application config
			if (file_exists($modulePath . '/config.ini')) {
			   	// Get the raw contents of the config file
			   	$ini = file_get_contents($modulePath . '/config.ini');
				// Perform environment replacement
				$ini = str_replace('[MODULE_PATH]',  $modClass->modulePath,   $ini);
				$ini = str_replace('[MODULE_ROOT]',  $modClass->moduleRoot,   $ini);
				$ini = str_replace('[MODULE_STATIC]',$modClass->moduleStatic, $ini);
				// Parse the env-replaced content
				$moduleSettings   = parse_ini_string($ini);
				// Append (union) with global settings. += ensures that
				// application settings always override module settings.
				$this->settings  += $moduleSettings;
			}
			
			// Return the configuration object
			return $modClass;
		} else {
			return false;
		}
	}
	
	public function getModuleContext($which = null) {
		
		// If a module is requesting its own context...
		if ( $which === null ) {
			$req = ($this->subrequest != null) 
				? $this->subrequest
				: $this->request;
			$uri = ltrim($req->uri,'/');
			$moduleName = substr($uri,0,strpos($uri,'/'));
							
			return (!empty($moduleName)) 
				? $this->loadModule($moduleName)
				: false;
		} 
				
		// otherwise, return the result of an attempt to load the module
		return $this->loadModule($which);
	}
	
	public static function SetMessage($content,$level = CAS_MSG_INFO) {
		
		switch ($level) {
			case CAS_MSG_WARN:
				$_SESSION['_messages'][] = '<div class="cas_msg warn">'  . $content . '</div>';
				break;
			case CAS_MSG_ERROR:
				$_SESSION['_messages'][] = '<div class="cas_msg error">' . $content . '</div>';
				break;
			default:
				$_SESSION['_messages'][] = '<div class="cas_msg info">'  . $content . '</div>';
				break;
		}
	}
	
	public static function GetMessages() {
		$response = isset($_SESSION['_messages']) 
			? implode('', $_SESSION['_messages'])
			: false;
		unset($_SESSION['_messages']);
		return $response;
	}
	
	public function fatal($message) {
		ApplicationResponse::sendFatal($message);
		exit();
	}
	
	public static function EndUserSession() {
		// Unset all of the session variables.
		$_SESSION = array();
		
		// Finally, destroy the session.
		session_destroy();
	}

	public static function Redirect($newLocation) {
		header("Location: {$newLocation}");
		exit();
	}
	
	/**
	 * Returns an instance of the requested DataProvider class, ensuring
	 * that all necessary prerequisites are correctly loaded. To load a 
	 * custom DataProvider. The framework looks for a matching data
	 * provider according to the following heirarchy, stopping when 
	 * it first finds a matching class: If the request involves a module,
	 * that module's /classes/dataProviders directory is checked, 
	 * otherwise/then the application's classes/dataProviders directory 
	 * is checked, and finally (if no match found yet) the webapp-base
	 * /classes/dataProviders directory is checked.
	 * Data providers must be named <ProviderName>.class.php, and must 
	 * implement the IApplicationDataProvider interface.
	 * 
	 * @param $class        string  The name of the DataProvider class
	 * @param $options      array   optional array of constructor options.
	 * 						These are flowed down to the DataProvider's 
	 * 						constructor function.
	 * @return the data provider (must implement IApplicationDataProvider)
	 * 
	 * Example: to get an instance of a data provider:
	 * 	  $p = $app->GetDataProvider('<ProviderName>');
	 * 
	 * Example 2: to get an instance and pass options to the constructor
	 *    $p = $app->GetDataProvider('<ProviderName>',array('opt1'=>'val1'));
	 *    
	 * Note that this will not attempt to connect to your data provider.
	 * All implementations of IApplicationDataProvider offer a ::connect()
	 * function, which should be invoked on the returned class to initiate
	 * a connection.
	 * 
	 */
	public function getDataProvider($class,$options = array()) {
		require_once( "Org/Apache/Oodt/Balance/Interfaces/IApplicationDataProvider.php");
		$dataProviderPath = "/classes/dataProviders/{$class}.class.php";
		
		// Check for the requested data provider in one of 3 locations. It could be:
		// 1) Part of a module
		if ($this->request->isModule && 
			is_file($this->request->moduleBase . $dataProviderPath)) {
			require_once($this->request->moduleBase . $dataProviderPath);
			
			return new $class($options);
		}
		
		// 2) Part of the application's widget collection
		if (is_file(HOME . $dataProviderPath)) {
			require_once(HOME . $dataProviderPath);
			return new $class($options);
		}
		
		// 3) Part of the webapp-base widget collection
		if (is_file(LIB . $dataProviderPath)) {
			require_once(LIB . $dataProviderPath);
			return new $class($options);
		}
		return false;
	}
	
	public function getErrorProvider(
		$class = 'Org_Apache_Oodt_Balance_Providers_Error_DefaultErrorProvider',
		$options = array()) {
		
		return new $class;
	}
	
	
	/**
	 * Create an instance of the requested widget class. 
	 * @deprecated
	 * @param unknown_type $class
	 * @param unknown_type $options
	 */
	public function createWidget($class,$options = array()) {
		
		require_once( "Org/Apache/Oodt/Balance/Interfaces/IApplicationWidget.php");
		
		$classPath = "/scripts/widgets/{$class}.php";
		
		// Check for the requested widget in one of 2 locations. It could be:
		// 1) Part of a module
		if ($this->request->isModule && 
			is_file($this->request->moduleBase . $classPath)) {
			require_once($this->request->moduleBase . $classPath);
			return new $class($options);
		}
		
		// 2) Part of the application's widget collection
		if (is_file(HOME . $classPath)) {
			require_once(HOME . $classPath);
			return new $class($options);
		}
		
		// No widget matching $class found...
		return false;
	}
	
	/**
	 * Take any application view and 'widgetize' it. This allows developers to nest
	 * application views, allowing for greater modularity and reuse.
	 * 
	 * As an example: given an application with URIs  /foo/bar and foo/baz (corresponding
	 * to HOME/views/foo/bar.php and HOME/views/foo/baz.php), the content of /foo/baz can
	 * be 'widgetized' (nested) within /foo/bar simply by calling this function from somewhere
	 * within the host view (/foo/bar):
	 * 
	 * <div>
	 *   <?php App::Get()->widgetizeView('/foo/baz');
	 * </div>
	 * 
	 * will produce:
	 * 
	 * <div>
	 *   <div class="bal_widget">...contents of HOME/views/foo/baz.php...</div>
	 * </div>
	 * 
	 * The `cssClasses` parameter allows for specifying any css class definitions that should
	 * be applied to the widget container. For example:
	 * 
	 * App::Get()->widgetizeView('/foo/baz','someClass someOtherClass');
	 * 
	 * will produce:
	 * 
	 * <div>
	 *   <div class="bal_widget someClass someOtherClass">...contents...</div>
	 * </div>
	 * 
	 * @param string $contentPath  The URI to the view to widgetize
	 * @param string $cssClasses   Any css classes to append to the widget's `classes` attribute
	 * @param mixed  $options      An array of options (for the future... none defined yet)
	 */
	public function widgetizeView($contentPath,$cssClasses = '',$options = array()) {
	
		// Create a request object for the content to be widgetized
		$request  = $this->subrequest = new Org_Apache_Oodt_Balance_Core_ApplicationRequest(
			$this->settings,$contentPath);
			
		// Store the application request object prior to processing this nested request
		$parentRequest = $this->request;
		
		// Store the nested request in the application so that it can be accessed as
		// expected via App::Get()->request (for accurate segment processing, for example)
		$this->request = $request; 	
		
		// Generate a response for the nested request
		$response = new Org_Apache_Oodt_Balance_Core_ApplicationResponse(
			$this->settings,$request);
		$response->process(array('skipHeader' => true,'skipFooter' => true,'skipHooks' => true));
		
		//TODO: Process any options (still need to define the options available)
		
		// send the wigitized content
		echo '<div class="bal_widget ' . $cssClasses . '">'
			. $response->getViewContent()
			. '</div>';
			
		// Restore the application request
		$this->request    = $parentRequest;
		$this->subrequest = null;
	}
}
