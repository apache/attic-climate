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
 * ApplicationRequest: Provides methods for interpreting and processing
 * a resource request.
 * 
 * @author ahart
 * 
 */
class Org_Apache_Oodt_Balance_Core_ApplicationRequest {
	
	public $isScript;
	
	public $config;
	
	public $uri;
	
	public $segments;
	
	public $data;
	
	public $viewPath;
	
	public $scriptPath;
	
	public $isModule;
	
	public $modulePath;	// Filesystem path for module

	public $moduleRoot;	// URL base for module

	public $moduleStatic;	// URL base for  static module assests (images,css,js,etc)

	public function __construct($config,$requestURI) {
		
		// Determine if this request is a script or a view
		$this->isScript = $this->isScript($requestURI);
	
		// Store the config as provided
		$this->config = $config;
		
		// Store the uri as provided
		$this->uri = htmlentities($requestURI);
		
		// Initialize the segments and view path
		$this->segments = array();
		$this->viewPath = false;
		
		// Store data associated with the request
		$this->data = $_GET;
		$this->data = array_merge($this->data,$_POST);
		
		if ($this->isScript) {
			$this->processAsScript();
		} else {
			$this->processAsView();
		}
	} 
	
	protected function processAsView() {
		// Determine the view to use
		list($thePage) = explode('index.php',$this->uri);
		$thePage = ltrim($thePage,'/');

		if ($thePage == '') { $thePage = 'index'; }	
		$parts = explode('/',$thePage);

		// Determine whether a module is being requested
		$module = App::Get()->isModule($thePage);
		
		if ($module) {
			$this->isModule   = true;
			$this->modulePath   = $module->modulePath;
            $this->moduleRoot   = $module->moduleRoot;
            $this->moduleStatic = $module->moduleStatic;
			array_shift($parts);
		}

		// Starting with the full request string, test for the existance of
		// a corresponding view. If none is found in the HOME
		// directory, chop off the last segment and try again. Add the chopped
		// segment to the "segments" array since it is likely a parameter.
		$partCount = count($parts);
		while ($partCount > 0) {
			$testPath    = implode('/',$parts);
			$homeTest    = (($this->isModule) ? "{$this->modulePath}/views" : $this->config['views_dir']) . '/' . $testPath . '.php';
			$homeIdxTest = (($this->isModule) ? "{$this->modulePath}/views" : $this->config['views_dir']) . '/' . $testPath . '/index.php';
			
			
			if (is_file($homeTest)) { 
				$this->viewPath = $homeTest;
				break;
			}
			if (is_file($homeIdxTest)) {
				$this->viewPath = $homeIdxTest;
				break;
			}
			
			// If here, neither is a valid view, so chop the last segment
			$this->segments[] = $parts[$partCount - 1];
			array_pop($parts);
			$partCount--;
		}
		
		// If no view has been found by this point, display a 404 message
		if (!$this->viewPath) {
			$this->viewPath = dirname(dirname(__FILE__)) . "/views/error/404.php";
		}
		
		// Reverse the segments array so that params appear in the proper order
		$this->segments = array_reverse($this->segments);
	}
	
	protected function processAsScript() {
		
		// Determine the desired script
		list($theScript) = explode("_init.php",$this->uri);
		if ($GLOBALS['app']->settings['site_root'] != '/') {
			$theScript   = str_replace($GLOBALS['app']->settings['site_root'],'',$theScript);
		}
		$theScript       = str_replace(".do",".php",$theScript);
		$theScript       = strpos($theScript,'?') 
			? substr($theScript,0,strpos($theScript,'?'))
			: $theScript;
		$theScript       = ltrim($theScript,'/');
		$module          = $GLOBALS['app']->isModule($theScript);
		if ($module) {
			$this->isModule   = true;
			$this->modulePath   = $module->modulePath;
            $this->moduleRoot   = $module->moduleRoot;
            $this->moduleStatic = $module->moduleStatic;
			$theScript        = substr($theScript,strpos($theScript,'/')+1);
			$path             = $module->modulePath . "/scripts/{$theScript}";
		} else {
			$path = HOME . "/scripts/{$theScript}";
		}
		
		$this->scriptPath   = $path;
	}
	
	
	protected function isScript($requestURI) {
		// Is this a script? (does the script filename end in .do?)
		$test = $requestURI;
		if (strpos($test,'?')) {
			$test = substr($test,0,strpos($test,'?'));
		}
		return (substr($test,-3,3) == '.do');
	}
}
