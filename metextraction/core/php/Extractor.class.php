<?php
/**
 * Extractor - Base class for building External CAS Met Extractors in PHP
 * 
 * @author ahart
 *
 */
Class Extractor {
	
	/**
	 * @var (array)		An array of the extracted key/value pairs 
	 */
	protected $metadataKeys;
	
	/**
	 * @var (string)	The path (on the filesystem) of the input file
	 */
	protected $inputFilePath;
	
	/**
	 * @var (string)	The path (on the filesystem) of the output dir
	 */
	protected $outputDirPath;
	
	/**
	 * @var (resource)	A file handle for writing to the output file 
	 */
	protected $outputFileHandle;
	
	/**
	 * @var (integer)   A counter keeping track of the # of met output files 
	 */
	protected $outputFilePartCounter;
	
	/**
	 * @var (integer)  The maximum number of data points for a given met file
	 */
	protected $maxDataPointsPerFile;
	
	/**
	 * @var (integer) The number of data points written to the current file so far
	 */
	protected $dataPointsThisPart;
	
	
	/**
	 * __construct: initializes the base data structures
	 * 
	 * @return unknown_type
	 */
	public function __construct($maxDataPointsPerFile = 0) {
		$this->metadataKeys = array();	
		$this->outputFilePartCounter = 0;
		$this->dataPointsThisPart    = 0;
		$this->maxDataPointsPerFile  = $maxDataPointsPerFile;
		if ($maxDataPointsPerFile > 0) {
			$this->debug("Each .met file will have a maximum of {$maxDataPointsPerFile} data points");
		}
	}
	
	/**
	 * addMetKey: adds a key/value pair to the $metadataKeys array
	 * 
	 * @param $name 	(string) The name of the key
	 * @param $value 	(string) The value for the key	
	 * @return unknown_type
	 */
	protected function addMetKey($name,$value) {
		$this->metadataKeys[$name] = $value;
	}
	
	/**
	 * addMultiValuedMetKey: adds a key/multi-value pair to the $metadataKeys
	 * array
	 * 
	 * @param $name		(string) The name of the key
	 * @param $values	(array)	 An array of values for the key
	 * @return unknown_type
	 */
	protected function addMultiValuedMetKey($name,$values) {
		$valueString = array();
		foreach ($values as $vn => $vv) {
			$valueString[] = "{$vn}|{$vv}";
		}
		$valueString = implode(',',$valueString);
		$this->metadataKeys[$name] = $valueString;
	}
	
	/**
	 * startMetadataFile: opens an output file for writing and 
	 * provides the standard xml prolog. 
	 * 
	 * @return unknown_type
	 */
	public function startMetadataFile() {
		try {
			$this->outputFileHandle = fopen($this->outputDirPath
				."/".basename($this->inputFilePath)
				.".{$this->outputFilePartCounter}.met",'w');
		} catch (Exception $e) {
			$this->fatal($e);
		}
		$r =  '<?xml version="1.0" encoding="UTF-8"?>';
		$r .= '<!-- Generated on ' . date('M. d, Y G:i:s') . "-->\r\n";
		$r .= "<metadata>\r\n";
		fwrite($this->outputFileHandle,$r);
	}
	
	public function startNewMetadataFilePart() {
		// Close the existing metadata file
		$this->finishMetadataFile();
		
		// Increment the part counter
		$this->outputFilePartCounter++;
		
		// Reset data points per part counter
		$this->dataPointsThisPart = 0;
		
		// Open a new metadata file for writing
		$this->startMetadataFile();	
	}
	
	/**
	 * finishMetadataFile: This closes the metadata output file. 
	 * 
	 * @return unknown_type
	 */
	public function finishMetadataFile() {
		$r = "</metadata>\r\n";
		if ($this->outputFileHandle) {
			fwrite($this->outputFileHandle,$r);
			fclose($this->outputFileHandle);
		} else {
			$this->fatal("Extractor::finishMetadataFile(): Output file not yet opened for writing");
		}
	}
	
	/**
	 * writeMetKey: writeMetKey can be used to directly write
	 * a key/value pair to the output file, bypassing the $metadataKeys
	 * array. This can be useful when the input file is so big that
	 * storing all keys before writing would result in memory exhaustion.
	 * Note, however, that ::startMetadataFile() must be called prior to
	 * using this function as it prepares the output file for writing. 
	 * 
	 * @param $name		(string) The name of the key
	 * @param $value	(string) The value for the key
	 * @return unknown_type
	 */
	public function writeMetKey($name,$value) {
		$r = "<keyval>\r\n"
			. "\t<key>{$name}</key>\r\n"
			. "\t<val>{$value}</val>\r\n"
			. "</keyval>\r\n";
		if ($this->outputFileHandle) {
			fwrite($this->outputFileHandle,$r);
		} else {
			$this->fatal("Extractor::writeMetKey(): Output file not yet opened for writing");
		}
		
	}
	
	/**
	 * writeMultiValuedMetKey: writeMultiValuedMetKey can be used to directly
	 * write a key/multi-value pair to the output file, bypassing the $metadataKeys
	 * array. This can be useful when the input file is so big that storing
	 * all keys before writing would result in memory exhaustion. Note,
	 * however, that ::startMetadataFile() must be called prior to using this
	 * function as it prepares the output file for writing.
	 *  
	 * @param $name		(string) The name of the key
	 * @param $values	(array)	 An array of values for the key
	 * @return unknown_type
	 */
	public function writeMultiValuedMetKey($name,$values) {
		if (self::is_assoc($values)) {
			$valueArr = array();
			foreach ($values as $vn => $vv) {
				$valueArr[] = "{$vn}|{$vv}";
			}
		} else {
			$valueArr = $values;
		}			
		$r = '';	
		$r .= "<keyval>\r\n"
			. "\t<key>{$name}</key>\r\n";
		foreach ($valueArr as $v) {
			$r .= "\t<val>{$v}</val>\r\n";
		}
		$r .= "</keyval>\r\n";
		
		if ($this->outputFileHandle) {
			fwrite($this->outputFileHandle,$r);
		} else {
			$this->fatal("Extractor::writeMultiValuedMetKey(): Output file not yet opened for writing");
		}
	}
	
	/**
	 * openMultiValuedMetKey: If a multivalued key is expected to contain more values than can be held
	 * in memory at one time, this function can be used to begin the stanza for the keyval, and values
	 * can be added in batches using multiWriteMultiValuedMetKey(). When all values have been written,
	 * a call to closeMultiValuedMetKey() will finish off the keyval stanza.
	 * 
	 * @param string  The name (key) of the keyval
	 * @return void
	 */
	public function openMultiValuedMetKey($name) {
		$r  = "<keyval>\r\n"
			. "\t<key>{$name}</key>\r\n";
			
		if ($this->outputFileHandle) {
			fwrite($this->outputFileHandle,$r);
		} else {
			$this->fatal("Extractor::writeMultiValuedMetKey(): Output file not yet opened for writing");
		}
	}
	
	/**
	 * multiWriteMultiValuedMetKey: If a multivalued key is expected to conatin more values than can be
	 * held in memory at one time, this function can be used to write values in batches. A call to 
	 * openMultiValuedMetKey should be made first, to open the stanza, and a call to closeMultiValuedMetKey
	 * should be made following the last batch.
	 * 
	 * @param array  The values to write
	 * @return void
	 */
	public function multiWriteMultiValuedMetKey($values) {
		$r = '';
		foreach ($values as $v) {
			$r .= "<val>{$v}</val>\r\n";
		}	
		
		if ($this->outputFileHandle) {
			fwrite($this->outputFileHandle,$r);
		} else {
			$this->fatal("Extractor::writeMultiValuedMetKey(): Output file not yet opened for writing");
		}
	}
	
	/**
	 * closeMultiValuedMetKey: If a multivalued key is expected to conatin more values than can be
	 * held in memory at one time, this function can be used to close the keyval stanza after the last
	 * batch of values has been written using multiWriteMultiValuedMetKey().
	 * 
	 * @param array  The values to write
	 * @return void
	 */
	public function closeMultiValuedMetKey() {
		$r = '';
		$r .= "</keyval>\r\n";
		
		if ($this->outputFileHandle) {
			fwrite($this->outputFileHandle,$r);
		} else {
			$this->fatal("Extractor::writeMultiValuedMetKey(): Output file not yet opened for writing");
		}
	}
	
	
	/**
	 * writeMetadataFile: If 'addMetKey' and 'addMultivaluedMetKey' have been
	 * used to add key/value pairs to the $metadataKeys array, this function can
	 * be called to flush that array to an output file. Note that, for really
	 * big files, it may not be feasible to store all metadata keys before writing
	 * them to a file. If this is the case, use the "write*MetKey" versions of 
	 * these functions. 
	 * 
	 * @return unknown_type
	 */
	public function writeMetadataFile() {
		$r =  '<?xml version="1.0" encoding="UTF-8"?>';
		$r .= '<!-- Generated on ' . date('M. d, Y G:i:s') . "-->\r\n";
		$r .= "<metadata>\r\n";
		foreach ($this->metadataKeys as $mk => $mv) {
			$r .= "\t<keyval>\r\n"
				. "\t\t<key>{$mk}</key>\r\n"
				. "\t\t<val>{$mv}</val>\r\n"
				. "\t</keyval>\r\n";
		}
		$r .= "</metadata>\r\n";
		
		$this->startMetadataFile();
		fwrite($this->outputFileHandle,$r);
		$this->finishMetadataFile();
	}
	
	/**
	 * populate2DGrid: takes an ordered set of observations, a set of x-axis values, 
	 *   y-axis values, and a height constant and returns a vector representation 
	 *   of the observations. 
	 * 
	 * example:
	 *     input: $values = array(100,101,102,103,104);
	 *            $valuesOffset = 1;
	 *            $xCoords= array(30,35,40,45,50);
	 *            $yCoords= array(1,2,3,4,5);
	 *            $heightConstant = 75.3;
	 *            
	 *                    x  y z    v
	 *     output: array("35,2,75.3,101",  // '100' skipped because $valuesOffset = 1
	 *                   "40,3,75.3,102",
	 *                   "45,4,75.3,103",
	 *                   "50,5,75.3,104");
	 * 
	 * 
	 * 
	 * @param array     The set of values to use when populating the grid
	 * @param integer   An offset to start at in the values array
	 * @param integer   The set of values to use as x coordinates of the grid
	 * @param integer   The set of values to use as y coordinates of the grid
	 * @param integer   A scalar value to use as the constant z value of the grid points
	 * @return array    An array of strings of the form "x,y,z,value"
	 */
	public function populate2DGrid(&$values,$valuesOffset,$xCoords,$yCoords,$heightConstant = 0,$timeConstant = '') {
		$grid = array();
		$valuesIterator = $valuesOffset;
		foreach ($xCoords as $x) {
			foreach ($yCoords as $y) {
				$grid[] = "{$x},{$y},{$heightConstant},{$timeConstant},{$values[$valuesIterator++]}";
			}
		}
		return $grid;
	}
	
	
	/**
	 * debug: provides a way to get debug messages to the terminal. Output
	 * can be suppressed by defining 'DEBUG' to 0 or false;
	 * 
	 * @param $message	(string) The message to display to developers
	 * @return unknown_type
	 */
	public static function debug($message) {
		if (DEBUG) {
			echo ">> {$message}\r\n";
		}
	}
	
	/**
	 * fatal: provides a way to die with a message to the terminal. 
	 * 
	 * @param $message	(string) The message to display when terminating.
	 * @return unknown_type
	 */
	public static function fatal($message) {
		echo ">> FATAL: {$message}\r\n";
		die();
	}
	
	public static function is_assoc($arr) {
		if (!is_array($arr) || empty($arr)) { return false; }
		foreach (array_keys($arr) as $k => $v) {
			if ($k !== $v) {
				return true;
			}
		}
		return false;
	}
}