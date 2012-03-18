<?php
/**
 * Puny_Resource
 * 
 * Represents a piece of content being managed by Puny. 
 * 
 * The Puny_Resource class is a wrapper around a piece of editable
 * content (a resource). The class provides a number of convenience 
 * functions for interacting with content.
 * 
 * @author ahart
 */
class Puny_Resource {

	protected $id;						// The unique id for this resource
	protected $version = 0;				// The version number for this resource
	protected $content;					// The resource raw content
	protected $parser  = 'markdown';	// The parser label for this resource
	protected $parsedContent;			// The resource parsed content
	
	/**
	 * Constructor
	 * 
	 * Optionally provide an associative array containing 
	 * the data to use when initializing this object. 
	 * 
	 * @param array $data (optional) data to use when initializing the object
	 */
	public function __construct($data = array()) {
		$this->id      = isset($data['resourceId']) ? $data['resourceId'] : false;
		$this->version = isset($data['version'])    ? $data['version']    : 0;
		$this->content = isset($data['content'])    ? $data['content']    : '';
		$this->parser  = isset($data['parser'])     ? $data['parser']     : 'markdown';
		$this->parsedContent = isset($data['parsedContent']) ? $data['parsedContent'] : '';
	}
	
	/**
	 * Get the unique id for this resource
	 * @returns String
	 */
	public function getId() {
		return $this->id;
	}
	
	/**
	 * Increment the version number for this resource
	 * @returns Puny_Resource
	 */
	public function incrementVersion() {
		$this->version += 1;
		return $this;	// allow method chaining
	}
	
	/**
	 * Return the version number for this resource
	 * @returns int
	 */
	public function getVersion() {
		return $this->version;
	}
	
	/**
	 * Get the parser label for this resource. The parser
	 * label is a text label which should correspond to 
	 * one of the entries in the 'parsers' section of the
	 * Puny module's config.ini file.
	 */
	public function getParser() {
		return $this->parser;
	}
	
	/**
	 * Set the parser label for this resource. 
	 * 
	 * @param string $label The parser label to use
	 */
	public function setParser( $label ) {
		$this->parser = $label;
		return $this;	// allow method chaining
	}
	
	/**
	 * Get either the parsed or raw resource content. 
	 * 
	 * @param boolean $raw (default=false) return raw content?
	 * @returns string
	 */
	public function getContent( $raw = false ) {
		return ($raw) ? $this->content : $this->parsedContent;
	}
	
	/**
	 * set the raw content for this resource.
	 * @param string $val The raw content for this resource
	 * @returns Puny_Resource
	 */
	public function setContent( $val ) {
		$this->content = $val;
		return $this;	// allow method chaining
	}
	
	/**
	 * Parse the raw contents of this resourse
	 * 
	 * This function uses the parser label associated with this
	 * resource to determine the parser to use, instantiates a
	 * parser instance, and parses the raw content. The result
	 * is stored in $this->parsedContent. 
	 * 
	 * @throws Exception
	 * @returns Puny_Resource
	 */
	public function parse() {
		// Determine the parser to use
		$parserLabel = $this->getParser();
			
		// Ensure the appropriate parser has been required
		$parsers = App::Get()->settings['puny_parser'];
		if ( !in_array( $parserLabel, array_keys( $parsers ) ) ) {
			throw new Exception("Error instantiating parser: "
			. "label '{$parserLabel}' not configured. ");
		} else {
			require_once( $parsers[$parserLabel] );
		}
		
		// Load the parser
		$parserClassName = 'Puny_' . ucfirst($parserLabel) . 'Parser';
		$parser = new $parserClassName();
		
		// Expand Balance constants:
		// ([SITE_ROOT], [MODULE_ROOT], [MODULE_PATH], [MODULE_STATIC])
		$content = str_replace('[SITE_ROOT]',SITE_ROOT, $this->content);
		$moduleInfo = App::Get()->loadModule();
		if ($moduleInfo) {
			$content = str_replace('[MODULE_ROOT]',$moduleInfo->moduleRoot, $content);
			$content = str_replace('[MODULE_PATH]',$moduleInfo->modulePath, $content);
			$content = str_replace('[MODULE_STATIC]',$moduleInfo->moduleStatic, $content);
		}
	
		// Store the parsed contents
		$this->parsedContent = $parser->parse( $content );
		
		// Allow method chaining
		return $this;
	}
}