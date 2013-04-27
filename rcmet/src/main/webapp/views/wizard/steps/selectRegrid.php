<?php
// Get the task from the session
require_once(HOME . "/classes/RCMETWizardTask.class.php");
$task = unserialize($_SESSION['wizardTask']);
$task->setStep('selectRegrid');
if (isset($_POST['save'])) {
	$task->spatialRegridOption  = $_POST['spatialRegridOption'];
	$task->temporalRegridOption = $_POST['temporalRegridOption'];

	$task->nextStep();
}
$task->showPreviousNextLinks();
?>
<div class="section">
<div class="row">
<div class="span12">
<h2 class="title">Regridding Properties</h2>
<div class="box">
<div class="box-content">
<fieldset id="variableAssignmentSelector" class="">
	<legend>Specify parameters for spatial and temporal regridding:</legend>
<form method="POST">
	Provide details about the methods to use for regridding the observational and 
	model data in both space and time:<hr/>
	
	<h4>Spatial Regridding Options</h3>
	<select name="spatialRegridOption">
		<option value="-1">Please select an option...</option>
		<option value="obs">Use Observational Data Grid</option>
		<option value="model">Use Model Data Grid</option>
		<option value="regular" disabled="disabled">Define a New Regular lat/lon Grid</option>
	</select>
	<span class="note">Specify the spatial grid to use as a reference when calculating </span>
	
	<h4>Temporal Regridding Options</h3>
	<select name="temporalRegridOption">
		<option value="-1">Please select an option...</option>
		<option value="full">Calculate time mean for full period</option>
		<option value="annual">Calculate annual means</option>
		<option value="monthly">Calculate monthly means</option>
		<option value="daily">Calculate daily means (from sub-daily data)</option>
	</select>
	<span class="note">Specify the temporal gridding options to use when calculating </span>
	

	<br/><br/>
	<div>
	<p>If the information above is correct, please click: 
	<input type="submit" name="save" value="Continue" class="btn btn-primary"/>
	</p>
	</div>	
</form>
</fieldset>
</div>
</div>
</div>
</div>
</div>
