<?php
require_once(HOME . '/classes/WizardTask.class.php');

class RCMETWizardTask extends WizardTask {
	
	public $modelFilePaths = array();
	public $modelVars      = array();
	public $modelBounds    = array();
	
	public $modelParameter = '';
	public $observationalParameter = '';
	public $observationalParameterId = '';
	public $observationalDataset   = '';
	public $observationalDatasetId = '';
	
	// Time Range
	public $rangeStart;
	public $rangeEnd;
	
	// Regrid
	public $spatialRegridOption;
	public $temporalRegridOption;
	
	// Options
	public $computeAreaAverages;
	
	// Metrics
	public $metric;
	
	// Plot Options	
	
	public function dictTemporalRegrid($key) {
		
		$dict = array(
			"full" => "Time mean for full period",
			"annual" => "Annual Means",
			"monthly" => "Monthly Means",
			"daily" => "Daily means (from sub-daily data)"	
		);
		return (isset($dict[$key]))
			? $dict[$key]
			: false;
	}
	
	public function dictSpatialRegrid($key) {
		
		$dict = array(
			"model" => "Use the model data grid",
			"obs" => "Use the observational data grid",
			"regular" => "Monthly Means"	
		);
		return (isset($dict[$key]))
			? $dict[$key]
			: false;
	}
	
	public function dictMetrics($key) {
		$dict = array(
			"bias" => "Bias: mean bias across full time range",
			"mae"  => "Mean Absolute Error: across full time range",
			"difference" => "Difference: calculated at each time unit",
			"acc"  => "Anomaly Correlation",
			"patcor" => "Pattern Correlation",
			"pdf" => "Probability Distribution Function similarity score",
			"rms" => "RMS Error"	
		);
		return (isset($dict[$key]))
			? $dict[$key]
			: false;
	}
	
	public function getTimeRange($observationalDatasetId) {
		$dsTimes = array(
			"1" => array('1989-01-01 00:00:00','2009-12-31 00:00:00'),	// ERA-Interim
			"2" => array('2002-08-31 00:00:00','2010-01-01 00:00:00'),	// AIRS
			"3" => array('1998-01-01 00:00:00','2010-01-01 00:00:00'),	// TRMM
			"4" => array('1948-01-01 00:00:00','2010-01-01 00:00:00'),	// URD
			"5" => array('2000-02-24 00:00:00','2010-05-30 00:00:00'),	// MODIS
			"6" => array('1901-01-01 00:00:00','2006-12-01 00:00:00')); // CRU
		 
		if (isset($dsTimes[$observationalDatasetId]))
			return $dsTimes[$observationalDatasetId];
		else 
			return false;
	}
	
	public function computeOverlap($modelStart,$modelEnd,$obsStart,$obsEnd) {
		$mstart = strtotime($modelStart);
		$mend   = strtotime($modelEnd);
		$ostart = strtotime($obsStart);
		$oend   = strtotime($obsEnd);
		
		// The "later" of the two start times is the beginning of the overlap
		$rangeStart = ($mstart > $ostart) ? $mstart : $ostart;
		
		// The "earlier" of the two end times is the end of the overlap
		$rangeEnd   = ($mend < $oend) ? $mend : $oend;
		
		// Format the return values
		return array(date('Y-m-d H:i:s',$rangeStart),
					 date('Y-m-d H:i:s',$rangeEnd));
	}
	
	
	
	public function __construct () {
		
		parent::__construct();
		
		$this->steps = array(
			//     URL_NAME             HUMAN_READABLE
			array("selectModelFiles",   "Select Model Files"),
			array("selectLatLonVars",   "Select Latitude and Longitude Variables"),
			array("selectTimeVars",     "Select Time Variable"),
			array("selectModelVar",     "Select Model Variable"),
			array("selectObservationalData", "Select Observational Data"),
			array("selectTimeRange",    "Select Time Range for Calculation"),
			array("selectRegrid",       "Select Regridding Options"),
			array("selectOptionalTasks","Select Optional Calculation Tasks"),
			array("selectMetricOptions","Select Metrics"),
			array("selectPlotOptions",  "Select Plot Options"),
			array("generatePlots",      "Generate Plots"),
		);
	}
}