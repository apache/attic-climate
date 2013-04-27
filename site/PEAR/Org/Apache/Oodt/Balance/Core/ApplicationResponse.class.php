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
 * ApplicationResponse: Provides functions for dynamically constructing
 * and delivering a response to a resource request.
 * 
 * @author ahart
 * 
 */
class Org_Apache_Oodt_Balance_Core_ApplicationResponse {
	
	protected $config;
	protected $request;
	
	protected $headers;
	
	protected $header;
	protected $view;
	protected $footer;
	
	protected $stylesheets = array();
	protected $javascripts = array();
	
	protected $data;

	const DYN_JS_TAG  = '<!-- JAVASCRIPTS -->';
	const DYN_CSS_TAG = '<!-- STYLESHEETS -->';
	
	/**
	 * Constructor
	 * 
	 * @param array $config
	 * @param Org_Apache_Oodt_Balance_Core_ApplicationRequest $request
	 */
	public function __construct($config, 
		Org_Apache_Oodt_Balance_Core_ApplicationRequest $request) {
		
		$this->config   = $config;
		
		$this->request = $request;
		
		$this->headers  = array();
		
		$this->header   = HOME . "/{$config['header_file_path']}";
		$this->footer   = HOME . "/{$config['footer_file_path']}";
	}
	
	/**
	 * Generates a response by processing the requested view,
	 * including any header and footer views (if needed) as specified
	 * by the application config file.
	 * 
	 * Available options:
	 *   skipHeader: boolean (default = false) If present, omits header processing
	 *   skipFooter: boolean (default = false) If present, omits footer processing
	 *   skipHooks:  boolean (default = false) If present, omits hook processing
	 *
	 * @param array $options
	 */
	public function process($options = array()) {
		
		// Merge defaults with provided options
		$defaults = array(
			'skipHeader' => false,
			'skipFooter' => false,
			'skipHooks'  => false,
		);
		$options += $defaults;
		
		// Preprocessing for a view
		if (!$this->request->isScript) {
			ob_start();	// Start buffering the output
			
			// Include the appropriate hooks.php file
			if (!$options['skipHooks']) {
				include ((App::Get()->request->isModule 
                          ? App::Get()->request->modulePath 
                          : HOME ) . '/hooks.php');
			}
			
			// Check that the requested view exists
			if (file_exists($this->request->viewPath)) {
				
				// Run the beforeView hook
				if (!$options['skipHooks'] && function_exists('hook_before_view')) {
					hook_before_view();
				}
				// Process the view
				include($this->request->viewPath);
			} else { 
				include(HOME . "/views/errors/404.php"); // 404 error page
			}
			
			$this->view = ob_get_contents();
			ob_clean();
			
			// Determine the header view (if any) to include
			if (!$options['skipHeader'] && $this->header && is_file($this->header)) {
				// Run the beforeHeader hook
				if (!$options['skipHooks'] && function_exists('hook_before_header')) {
					hook_before_header();
				}
				
				// Process the header
				if (!empty($this->header)) {include($this->header);}

				$this->header = ob_get_contents();
				ob_clean();
			}
			
			// Determine the footer view (if any) to include
			if (!$options['skipFooter'] && $this->footer && is_file($this->footer)) {
				// Run the beforeFooter hook
				if (!$options['skipHooks'] && function_exists('hook_before_footer')) {
					hook_before_footer();
				}
				
				// Process the footer
				if (!empty($this->footer)) {include($this->footer);}
				
				$this->footer = ob_get_contents();
				ob_clean();
			}

			ob_end_clean();	// Stop buffering the output
		} else {
			require_once( $this->request->scriptPath );
			exit();
		}
	}
	
	/**
	 * Actually sends the response (using 'echo') out to the 
	 * client's browser.
	 */
	public function send() {
		
		if ($this->request->isScript) {	
			if (is_file($this->request->scriptPath)) {
				require_once($this->request->scriptPath);
			} else {
				header("Location: " . SITE_ROOT . "/errors/404");
			}
		} else {
			// Process any dynamically added content
			$this->processDynamicContent();
			
			// Run the beforeSend hook
			if (function_exists('hook_before_send')) {
				hook_before_send();
			}
			foreach ($this->headers as $header) {
				header($header);
			}
			if ($this->header) {
				echo $this->header;
			}
			echo $this->view;
			if ($this->footer) {
				echo $this->footer;
			}
			// Run the afterSend hook
			if (function_exists('hook_after_send')) {
				hook_after_send();
			}
		}
	}

	public static function sendFatal($message) {
		// Store the message in the session
		$_SESSION['fail_message'] = $message;
		
		// Clear any old output and restart buffering the output
		ob_clean();
		ob_start();
	
		// Build the 404 error page
		include(LIB . "/views/errors/fail.php");
		
		// Get the contents as a string and flush the buffer
		$content = ob_get_contents();
		
		// Stop buffering output
		ob_end_clean();
		
		// Send the response
		echo $content;
		
		exit();
	}
	
	/**
	 * Replace special tags with their dynamically assigned content. Currently, the only
	 * special tags are for defining an area for CSS and JavaScript imports.
	 * 
	 */
	protected function processDynamicContent() {
		
		// Dynamically insert CSS
		$this->header = str_replace(self::DYN_CSS_TAG,implode("\r\n",$this->stylesheets),$this->header);
		$this->view   = str_replace(self::DYN_CSS_TAG,implode("\r\n",$this->stylesheets),$this->view);
		$this->footer = str_replace(self::DYN_CSS_TAG,implode("\r\n",$this->stylesheets),$this->footer);
		
		// Dynamically insert JS
		$this->header = str_replace(self::DYN_JS_TAG,implode("\r\n",$this->javascripts),$this->header);
		$this->view   = str_replace(self::DYN_JS_TAG,implode("\r\n",$this->javascripts),$this->view);
		$this->footer = str_replace(self::DYN_JS_TAG,implode("\r\n",$this->javascripts),$this->footer);
		
	}
	
	public function useHeaderFile($path) {
		$this->header = $path;
	}
	
	public function useFooterFile($path) {
		$this->footer = $path;
	}
	
	public function sendHeader($headerContent) {
		$this->headers[] = $headerContent;
	}
	
	public function getHeaderContent() {
		return $this->header;
	}
	public function getViewContent() {
		return $this->view;
	}
	public function getFooterContent() {
		return $this->footer;
	}

	public function data($key = null, $value = null) {
	       
		// Return the data store associated with this request
		if ($key == null && $value == null) {
			return $this->data;
		}
					
		// Return the stored value for the provided key
		if ($value == null) {
			return isset($this->data[$key]) 
				? $this->data[$key] 
				: null;
		}
															   
		// Set the stored value for the key to the provided value
		$this->data[$key] = $value;
	}
	
	public function addStylesheet($href,$condition='') {
		// Build the string for the css import
		$str = "<link rel=\"stylesheet\" type=\"text/css\" href=\"{$href}\"/>";
		if (!empty($condition)) {
			$str = "<!--[if {$condition}]>{$str}<![endif]-->";
		}
		$this->stylesheets[] = $str;
	}
	
    /**
     * Add javascript resources to the response
     *
     * This function provides a clean way to programmatically include arbitrary
     * Javascript resources in the response. Depending upon the value
     * provided for 'isRaw', the contents of 'src' will either be interpreted
     * as the 'src' attribute or the body content of the generated <script> block. 
     *
     * @param string src - Either the url to the resource to include (if 
     *                     'isRaw' = false) or a string representing the 
     *                     raw Javascript to include (if 'isRaw' = true)
     * @param boolean isRaw - Controls how 'src' is interpreted. If set to false 
     *                     (default), 'src' will be interpreted as a URL to the
     *                     Javascript resource to include. If set to true, 'src' 
     *                     will be interpreted as a string of raw Javascript.
     */
	public function addJavascript($src, $isRaw = false) {
        if ($isRaw === true) {
            // Build a script container for the raw javascript
            $str = "<script type=\"text/javascript\">{$src}</script>";
            $this->javascripts[] = $str;
        } else {
            // Build the string for the javascript file import
            $str = "<script type=\"text/javascript\" src=\"{$src}\"></script>";
            $this->javascripts[] = $str;
        }
	}
}
