<?php
/**
 * NCDump, provides a wrapper around the NCDump utility so that it can be
 * called by PHP scripts. 
 * 
 * The class provides three public functions: load(), describe(), and extract(). 
 * 
 * + Load() accepts as its only argument the full path to the NetCDF file that
 * will be operated on. It inspects the file's header and initializes several
 * data structures that will facilitate data and metadata extraction via 
 * subsequent calls to either extract() or describe().
 * 
 * + Describe() accepts as its only argument the name of the variable (as a 
 * string) for which to extract metadata. It returns metadata as an associative
 * array in the following format:
 * 
 *   array("variable" => "VarName"  // as defined in the netCDF file
 *         "shape"    => "lat lon"	// as defined in the NetCDF file
 *         "dimensions" => array(   // for all dimensions in "shape":
 *         		"lat" => array(all,defined,lat,values),
 *              "lon" => array(all,defined,lon,values)
 *         )
 *   );
 * 
 * + Extract() accepts as its only argument the name of the variable (as a 
 * string) for which to extract data points. It returns the extracted data
 * points as a regular array. This array can be combined with the information
 * returned by describe() to re-generate the full n-dimensional vector that
 * describes this data point.
 * 
 * 
 * 
 * @author ahart
 *
 */
class NCDump {
	
	/*
	 * @var (string) The path to the ncdump executable
	 */
	public $exePath;
	
	/*
	 * @var (string) The path to the NetCDF File
	 */
	public $filePath;
	
	/*
	 * @var (array) The dimensions defined in the NetCDF file
	 */
	public $dimensions = array();
	
	/*
	 * @var (array) The variables defined in the NetCDF file
	 */
	public $variables  = array();
	
	/*
	 * @var (array) The attributes defined in the NetCDF file
	 */
	public $attributes = array();
	
	
	/**
	 * __construct: Initialization
	 * 
	 * @param $exePath	(string) The path to the ncdump executable
	 * @throws Exception
	 * @return NCDump
	 */
	public function __construct($exePath) {
		if (file_exists($exePath)) {
			$this->exePath = escapeshellcmd($exePath);
			
		} else {
			throw new Exception("Invalid path to ncdump executable specified");
		}
	}
	
	/**
	 * Sets up various internal data structures to represent the data contained
	 * in the NetCDF file provided by $path
	 * 
	 * @param string  The complete path to the NetCDF file to load
	 * @throws Exception 
	 * @return void
	 */
	public function load($path) {
		
		// Ensure that the file exists
		if (!file_exists($path)) {
			throw new Exception ("Unable to load file: does not exist.");
		}
		
		// Store the path to the NetCDF file
		$this->filePath = $path;
		
		// Build the ncdump command to get header information from the file
		$ncdumpCommand = $this->exePath . ' -h -x ' . escapeshellcmd($path);
		
		// Execute the ncdump command
		$response = shell_exec($ncdumpCommand);
		
		// Convert the response to simple_xml
		$root = simplexml_load_string($response);
		
		// Extract dimension data
		$dimensionData = $this->simpleArray($root->dimension);
		$this->processDimensionData($dimensionData);
		 
		// Extract attribute data
		$attributeData = $this->simpleArray($root->attribute);
		$this->processAttributeData($attributeData);
		
		// Extract variable data 
		$variableData  = $this->simpleArray($root->variable);
		$this->processVariableData($variableData);
	}
	
	
	
	/**
	 * Computes and returns metadata about the requested variable
	 * @param string  The variable to extract
	 * @return mixed  The metadata array for the variable or boolean false
	 */
	public function describe($variable) {
		// Determine whether information exists for the given variable
		if (isset($this->variables[$variable])) {
			$shape = $this->variables[$variable]['shape'];
			$type  = $this->variables[$variable]['type'];
			$shapeComponents = explode(' ',$shape);

			$meta = array("variable"   => $variable,	// The variable name
						  "type"       => $type,        // The type of data stored
						  "shape"      => $shape,		// The shape as specified
						  "dimensions" => array(),		// The dimensional data
						  "points"     => 1);			// The total # of data points
			
			// Obtain the actual values for each shapeComponent
			foreach ($shapeComponents as $shapeComponent) {
				$meta['dimensions'][$shapeComponent] = $this->extract($shapeComponent);
				$meta['points'] *= count($meta['dimensions'][$shapeComponent]);
			}
			
			// Return the computed metadata
			return $meta;
		} else {
			return false;
		}
	}
	
	
	/**
	 * Extracts and returns the stored data for the requested variable. 
	 * @param string  The variable to extract
	 * @return array  The data points extracted
	 */
	public function extract($variable) {
		if (isset ($this->variables[$variable])) {
			
			// Build the ncdump command for getting data for the variable
			$ncdumpCommand = $this->exePath . ' -v ' . escapeshellcmd($variable) . ' ' . escapeshellcmd($this->filePath);
			
			// Execute the ncdump command
			$response = shell_exec($ncdumpCommand);
			
			// Find the start of the data section (data:)
			$dataStart = strpos($response,"{$variable} =",strpos($response,"data:")) + (strlen($variable) + 2);
			$data = rtrim(substr($response,$dataStart),";}\r\n");
			$data = explode(',',$data);
			$this->clean($data);
			return $data;
		}
	}
	
	/**
	 * Formats and stores dimension data extracted from the file header
	 * 
	 * @param array The dimension data as an associative array
	 * @return void
	 */
	private function processDimensionData($data) {
		foreach ($data as $dim => $dimval) {
			$this->dimensions[$dim] = $dimval['length'];
		}
	}
	
	/**
	 * Formats and stores attribute data extracted from the file header
	 * 
	 * @param array The attributepoint data as an associative array
	 * @return void
	 */
	private function processAttributeData($data) {
		foreach ($data as $attr => $attrval) {
			$this->attributes[$attr] = $attrval['value'];
		}
	}
	
	/**
	 * Formats and stores variable data extracted from the file header
	 * 
	 * @param array The variable data as an associative array
	 * @return void
	 */
	private function processVariableData($data) {
		foreach ($data as $var => $varval) {
			$this->variables[$var] = array("shape" => $varval['shape'],
										   "type"  => $varval['type']);
		}
	}
	
	/**
	 * Cleans up the values of an associative array by running trim() on each. The provided
	 * array will be operated on directly, so no value is returned by this function.
	 * 
	 * @param  array  The array to clean
	 * @return void
	 */
	static $NCD_MISSING_DATA_FLAG = -9999;
	private function clean(&$data) {
		foreach ($data as $d => &$v) {
			$v = trim($v);
			if ($v == '_') { 
				$v = self::$NCD_MISSING_DATA_FLAG;
			}
		}
	}
	
	/**
	 * simpleArray: Takes a collection of simple_xml objects and represents
	 * them as an associative array
	 * 
	 * @param $xmlObjectCollection	(array)	An array of simple_xml objects
	 * @return unknown_type
	 */
	private function simpleArray($xmlObjectCollection) {
		$data = array();
		foreach ($xmlObjectCollection as $xmlObject) {
			$tmp = array();
			foreach ($xmlObject->attributes() as $a) {
				$tmp[$a->getName()] = (string)$a;
			}
			$data[$tmp['name']] = $tmp;
		}
		return $data;
	}
	
} // NCDump