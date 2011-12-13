#!/usr/bin/php -dmemory_limit=500M 
#
# This is both a shell script and a php class definition. Below the 
# class definition are the commands necessary to parse command line 
# arguments and perform the metadata extraction from an input file. 
# 
# Command Line Useage: 
# 
# $~ php TRMMExtractor /path/to/ncdump /path/to/nc/file \
#        /path/to/output/dir param1,param2,...|all [maxDataPointsPerFile]
#
<?php
// Required classes and files
require_once(dirname(__FILE__).'/core/php/Extractor.class.php');
require_once(dirname(__FILE__).'/core/php/CLAP.class.php');
require_once(dirname(__FILE__).'/core/php/NCDump.class.php');

/**
 * TRMMExtractor - Extract metadata from TRMM NetCDF files
 *
 * This class provides methods for creating an OODT CAS compliant
 * metadata file from a TRMM NetCDF file. The class defines
 * one method "extract" which takes as input:
 *
 * 	1) a path for writing CAS-compatible metadata (.met) output
 *
 *  Example:
 *
 *  $extractor = new TRMMExtractor('/usr/bin/ncdump',
 *  					'/path/to/nc/file/','param1,param2,..');
 *  $extractor->extract('/path/to/met/output');
 *
 *
 * @extends Extractor
 *
 * @author ahart
 *
 */
define("TRMM",3);
class TRMMExtractor extends Extractor {

	/**
	 * @var (NCDump)	An instance of the NCDump class
	 */
	protected $ncdump;        // NCDump instance
	protected $parameters;    // The list of parameters of interest in the file
	protected $granuleTime;   // The computed time to use for each data point in the granule

	/**
	 * __construct: Initializes the extractor structures
	 *
	 * @param $pathToNCDumpExe	(string) The path to the ncdump executable
	 * @param $inputFilePath (string) The full path to the NetCDF input file
	 * @param $parameters (string) A comma-separated list of variables to extract
	 * @return unknown_type
	 */
	public function __construct($pathToNCDumpExe='/usr/bin/ncdump',$inputFilePath, $parameters,$maxDataPointsPerFile=0) {
		
		// Call the parent constructor
		parent::__construct($maxDataPointsPerFile);

		// Force runnable from the command line only
		if (!isset($argc) && isset($argv)) {
			Extractor::fatal("This script must be run from the command line");
		}

		// Create an instance of NCDump and attempt to load the input file
		try {
			$this->ncdump = new NCDump($pathToNCDumpExe);
			$this->ncdump->load($inputFilePath);
			$this->inputFilePath = $inputFilePath;
				
		} catch (Exception $e) {
			$this->fatal($e);
		}
		// Store the parameters to extract
		$this->parameters = explode(',',$parameters);
		
		// Extract the time constant from the file name
		$fn = basename($this->inputFilePath);
		// File name is 3B42_daily.YYYY.MM.DD
		$this->granuleTime  = substr($fn,11,4) . substr($fn,16,2) . substr($fn,19,2);
		$this->granuleTime .= "T0000Z";
	}

	/**
	 * extract: Begin a metadata extraction session using the input and output
	 * files provided.
	 *
	 * @param $outputDirPath(string) The path (on the filesystem) for the output dir
	 * @return unknown_type
	 */
	public function extract($outputDirPath) {

		// Ensure the output directory is valid
		if ($outputDirPath == '') {
			$this->fatal("No output directory path specified");
		}

		// Store the output directory
		$this->outputDirPath = $outputDirPath;

		// Start writing the output file
		$this->startMetadataFile();

		// Store the dataset information
		$this->writeMetKey("dataset_id",TRMM);
		
		// Store the file information
		$this->writeMetKey('granule_filename',basename($this->inputFilePath));

		// Obtain header stats from the file
		$this->debug("Extracting data from granule: " . basename($this->inputFilePath));
		$this->debug("Found " . count($this->ncdump->dimensions) . " dimension definition(s)");
		$this->debug("Found " . count($this->ncdump->attributes) . " attribute definition(s)");
		$this->debug("Found " . count($this->ncdump->variables)  . " variable definition(s)");
		
		// Has the user specified a list of variables, or should all be processed?
		$bFilterResults = (strtolower($this->parameters[0]) != "all");

		// Obtain data stream for each variable (parameter)
		$totalDataPoints = 0;
		$this->dataPointsThisPart = 0;
		foreach ($this->ncdump->variables as $parameterName => $pdata) {
			if (!$bFilterResults || ($bFilterResults && in_array($parameterName,$this->parameters))) {
				
				// Skip this variable (parameter) if it is actually
				// a dimension definition variable.
				if (array_key_exists($parameterName,$this->ncdump->dimensions)) {
					continue;
				}

				$this->debug("Now processing: {$parameterName}");

				// Extract metadata for the parameter
				$metadata   = $this->ncdump->describe($parameterName);
				
				// Ignore parameters with 'character' data
				if ($metadata['type'] == 'char') {
					continue;
				}

				// Start a new output file if we have passed the specified max points per file
				if ($this->maxDataPointsPerFile > 0 
					&& $this->dataPointsThisPart + $metadata['points'] > $this->maxDataPointsPerFile 
					&& $this->dataPointsThisPart > 0) { 

					$this->startNewMetadataFilePart();
					$this->writeMetKey("dataset_id",TRMM);
					$this->writeMetKey('granule_filename',basename($this->inputFilePath));	
					
					$this->debug("MaxDataPointsPerFile ($this->maxDataPointsPerFile) reached. "
						."Beginning new file *.{$this->outputFilePartCounter}.met");
				}
					
				// Extract the data points from the file
				$data                = $this->ncdump->extract($parameterName);
				$totalDataPoints    += count($data);
				$this->dataPointsThisPart += count($data);
				$points              = array();
				
				// Write the variable definition metadata  (param_*) to the file
				$this->writeMultiValuedMetKey("param_{$parameterName}",$pdata);
				
				// Write the actual data (data_*) to the file
				// Single 2D slice (assumes dimensions are specified x,y)
				if (count($metadata['dimensions']) == 2) {
					$dims = array_keys($metadata['dimensions']);
					$points = $this->populate2DGrid($data,
						0,
						$metadata['dimensions'][$dims[0]],
						$metadata['dimensions'][$dims[1]],0,
						$this->granuleTime);
						
					// Output some statistics
					$this->debug("   Found " . count($points) 
						. " data points for {$parameterName}. Writing... ");
					$this->debug("    * Processing slice at 'level': 0");
						
					// write the data stream to the met file
					$this->writeMultiValuedMetKey("data_{$parameterName}",$points);
				}

				// Multiple 2D slices (assumes dimensions are specified: z,x,y)
				else if (count($metadata['dimensions']) == 3) {
					$dims = array_keys($metadata['dimensions']);
					$gridOffset = count($metadata['dimensions'][$dims[1]])  // x
						* count($metadata['dimensions'][$dims[2]]);         // times y
					$this->debug("   {$parameterName} has " 
						. count($metadata['dimensions'][$dims[0]]) 
						. " slices, each with: {$gridOffset} points");
					$zIter = 0;
						
					// Output some statistics
					$this->debug("   Found " . count($data) 
						. " data points for {$parameterName}. Writing... ");
						
					// Open the key for writing. values will be written in batches
					// to prevent memory exhaustion
					$this->openMultiValuedMetKey("data_{$parameterName}");
						
					// Write values in batches by slice
					foreach ($metadata['dimensions'][$dims[0]] as $zValue) {
						$this->debug("    * Processing slice at 'level': {$zValue}");
						$offset = $zIter * $gridOffset;
						
						// RCMES standardizes its Longitudinal values on a -180 to +180 whereas
						// TRIMM uses 0-360. This converts native TRMM to native RCMES.
						foreach ($metadata['dimensions'][$dims[2]] as &$longitude) {
							if ($longitude > 180) {
								$longitude -= 360;
							}
						}
						
						$points = $this->populate2DGrid($data,
							$offset,
							$metadata['dimensions'][$dims[1]],
							$metadata['dimensions'][$dims[2]],
							$zValue,
							$this->granuleTime);
						// Write this batch of points to the file
						$this->multiWriteMultiValuedMetKey($points);
					}
						
					// All points have been written, so close the key.
					$this->closeMultiValuedMetKey();
				}

				// Anything above 3 dimensions is not supported.
				else {
					$this->fatal("More than 3 dimensions detected for "
						. "{$parameterName}. Max supported dimensions: 3");
				}

				// Unset data about variables that have already been
				// processed, to conserve memory.
				unset($points);
			} 
		}

		// Finish writing to the output file
		$this->debug("Total Data Points for All Variables: " . $totalDataPoints);
		$this->finishMetadataFile();
	}

} // AIRSNetCDFExtractor

/************************************************************************
 * Use the AIRSNetCDFExtractor class defined above to extract metadata
 * from AIRS Level 3 granule files. This script is expecting to be
 * invoked from the command line, and provided with the following
 * arguments, in order:
 *
 *  1) path to ncdump executable on the host machine
 * 	2) path to NetCDF (.nc) file to use as input
 * 	3) path to file which will contain CAS-compatible (.met) metadata
 *  4) comma-separated list of variables to extract or 'all'
 *  5) [optional] max. data points per file. 0 = infinite
 *
 *  Example:
 * 	$~ php ./AIRSNetCDFExtractor.php <input_file_path> <output_file_path>
 *
 * Note: set "DEBUG" to false below to suppress output messages
 *
 */

// Global DEBUG flag. Set to false to suppress debug messages
define('DEBUG',true);

Extractor::debug("PHP Memory Limit: " . ini_get("memory_limit"));
Extractor::debug("PHP Safe Mode:    " . ini_get("safe_mode"));

// Parse command line arguments
$args = CLAP::parse($argv);

if (count($args) < 4 || count($args) > 5) {
	Extractor::fatal("Usage: TRMMExtractor /path/to/ncdump "
		. "/path/to/input/file /path/to/output/dir var1,var2,var3 [maxDataPointsPerFile]");
}

// Create an extractor instance
$extractor = new TRMMExtractor($args[0],$args[1],$args[3],$args[4]);

// Extract metadata from the input file
$extractor->extract($args[2]);

// Cleanup
Extractor::debug('FINISHED.');
exit();