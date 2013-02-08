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

require_once( dirname(__FILE__) . '/Puny_Container.class.php');
require_once( dirname(__FILE__) . '/Puny_Resource.class.php');

/**
 * Puny
 * 
 * Light-weight content editing for Balance applications. Puny makes it easy
 * to add editable sections of content to your application views and supports
 * real-time, in-place editing.
 * 
 * Puny has been designed so that it is easy to plug in custom back end data
 * stores (MySql, MongoDB, SQLite, etc) and template engines (Markdown, Textile,
 * bbcode, etc). Use what makes sense for your project, and if what you want
 * is not yet supported, writing a Puny driver for a datastore or template 
 * engine is a piece of cake. There are examples of each in the /classes/data and 
 * /classes/parsers directories.
 * 
 * @author ahart
 */

class Puny {
	
	protected static $datastore = null;
	
	protected static $commonResourcesLoaded = false;

	protected static $editorResourcesLoaded = false;
	
	protected static function init() {
		
		// Only if the datastore has not yet been initialized...
		if (!self::$datastore) {
			try {
				// Obtain datastore configuration details
				$datastoreClass = App::Get()->settings['puny_datastore_classname'];
				require_once( App::Get()->settings['puny_datastore_classpath'] );
		
				// Create an instance of the datastore connector
				self::$datastore = new $datastoreClass();
		
				// Connect to the datastore
				self::$datastore->connect();
			} catch ( Exception $e ) {
				throw new Exception("Error instantiating Puny. "
				. "The underlying cause was: " . $e->getMessage());
			}
		}
		
		self::injectCommonResources();
		self::injectEditorResources();
	}
	
	public static function load( $resourceId, $version = null, $parseContent = true ) {

		self::init();
		
		// Load the raw data from the data store...
		if (false !== ($resource = self::$datastore->load( $resourceId, $version ))) {
			
			// If a valid resource was found, return it
			return ($parseContent) ? $resource->parse() : $resource;
			
		} else {
			
			// Otherwise, return an empty resource with the requested id
			return new Puny_Resource( array("resourceId" => $resourceId, "content" => $resourceId) );
		
		}
	}
	
	public static function store (Puny_Resource $resource ) {
		
		self::init();
		
		// Persist the resource to the datastore
		self::$datastore->store( $resource );
		
	}
	
	public static function isEditing() {
		return ( isset($_SESSION['puny']) && $_SESSION['puny']['editing'] === true );
	}
	
	public function initializeEditorSession() {
		$_SESSION['puny'] = array('editing' => true, 'sessionStart' => time());
	}
	
	public static function destroyEditorSession() {
		unset($_SESSION['puny']);
	}
	
	public static function status() {
		if (self::isEditing()) {
			return "<a href='".App::Get()->settings['puny_module_root']."/logout'>Logout</a>";
		} else {
			return "<a href='".App::Get()->settings['puny_module_root']."/login'>Login</a>";
		}
	}
	
	protected static function injectCommonResources() {
	  // Inject the environmental information needed for the javascript libraries
	  // to function as expected...
	  if ( !self::$commonResourcesLoaded ) {
	    $js = "\r\n"
	      . "var puny_module_root   = '" . trim(App::Get()->settings['puny_module_root']) . "'\r\n"
	      . "    puny_module_static = '" . trim(App::Get()->settings['puny_module_static']) ."'\r\n"
	      . "    puny_current_url = '" . $_SERVER['HTTP_REFERER'] ."';\r\n";
	      App::Get()->response->addJavascript( $js, true ); // raw Javascript
	    
	    // Add puny default styles
	    $staticPath = trim(App::Get()->settings['puny_module_static']);
		App::Get()->response->addStylesheet($staticPath . '/css/defaults.css');
		self::$commonResourcesLoaded = true;
	  }
	}

	protected static function injectEditorResources() {
		// Only inject resources if we are editing and they have not already been loaded...
		$segments = App::Get()->request->uri;
		$staticPath = trim(App::Get()->settings['puny_module_static']);
		if ( self::isEditing() && strstr($segments,'edit') != false) {
			
			App::Get()->response->addJavascript($staticPath . '/js/jquery-1.7.2.min.js');
			App::Get()->response->addJavascript($staticPath . '/js/gollum.js');
			App::Get()->response->addJavascript($staticPath . '/js/gollum.dialog.js');
			App::Get()->response->addJavascript($staticPath . '/js/gollum.placeholder.js');
			App::Get()->response->addJavascript($staticPath . '/js/editor/gollum.editor.js');
			
			App::Get()->response->addStylesheet($staticPath . '/css/github.css');
			App::Get()->response->addStylesheet($staticPath . '/css/editor.css');
			App::Get()->response->addStylesheet($staticPath . '/css/dialog.css');
		}
		if ( self::isEditing() && !self::$editorResourcesLoaded ) {
			
			App::Get()->response->addJavascript($staticPath . '/js/puny.js');
			App::Get()->response->addStylesheet($staticPath . '/css/puny.css');
			self::$editorResourcesLoaded = true;
		}
	}
	
	public static function container( $htmlElmt = 'div' , $extra = array()) {
		
		self::init();
		
		// Create a new Puny_Container object according to the provided info
		return new Puny_Container($htmlElmt, $extra);
	}
}