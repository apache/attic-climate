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

require_once(dirname(__FILE__) . '/Puny.class.php');

/**
 * Puny_Container
 * 
 * This class provides convenience methods for creating an HTML container
 * around a Puny_Resource. Puny_Container removes the need for developers
 * to manually annotate HTML with the puny="..." attribute (so that the 
 * Puny javascript in-place editor functions on the resource).
 * 
 * @author ahart
 */
class Puny_Container {
	
	protected $htmlElement;
	protected $attributes;
	
	/**
	 * Constructor
	 * 
	 * @param string $elmt  The html element to use as a container (e.g.: 'div','span')
	 * @param array  $attributes (optional) an associative array of attributes to 
	 *                     attach to the html container element. e.g:
	 *                     array("id" => 'foo', "class" => "bar baz");
	 */
	public function __construct( $elmt = 'div', $attributes = array() ) {
		
		$this->htmlElement = $elmt;
		$this->attributes  = $attributes;
	}
	
	/**
	 * Load a resource into this container
	 * 
	 * This function simply calls the Puny::load function and returns
	 * wraps the result in the container html
	 * 
	 * @param string $resourceId The unique id of the resource to load
	 * @param int $version (optional) The version to load (default = latest)
	 * @returns string
	 */
	public function load( $resourceId, $version = null ) {
		return $this->render( Puny::load( $resourceId, $version, false ));
	}
	
	
	/**
	 * Helper function for rendering a resource inside this container
	 * 
	 * @param unknown_type $resource
	 * @access protected
	 */
	protected function render($resource) {
		
		$html = "<{$this->htmlElement}";
		
		foreach ($this->attributes as $k => $v) {
			$html .= " {$k}=\"{$v}\"";
		}
		
		$html .= " puny=\"{$resource->getId()}\">"
			  .  "{$resource->parse()->getContent()}"
			  .  "</{$this->htmlElement}>";
		
		return $html;
	}
}