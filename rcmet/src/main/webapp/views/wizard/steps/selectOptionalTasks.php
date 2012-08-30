<?php
// Get the task from the session
require_once(HOME . "/classes/RCMETWizardTask.class.php");
$task = unserialize($_SESSION['wizardTask']);
$task->setStep('selectOptionalTasks');

if (isset($_POST['save'])) {
	
	// Nothing to save, yet.
	$task->nextStep();
}
$task->showPreviousNextLinks();
?>
<div class="section">
<div class="row">
<div class="span12">
<h2 class="title">Optional Tasks</h2>
<div class="box">
<div class="box-content">
<fieldset id="variableAssignmentSelector" class="">
	<legend>Specify Optional Processing Steps to Perform</legend>
<form method="POST">
	The toolkit can optionally perform a number of optional processing steps based upon
	preferences specified here:<hr/>
	
	<h4>Spatial Regridding Options</h4>
	<input type="checkbox" name="areaAverages" disabled="disabled" style="vertical-align:middle;"/> Do you wish to calculate area averages over a masked region of interest?
	
	<h4>Seasonal Cycle Option</h4>
	<input type="checkbox" name="seasonalCycle" disabled="disabled" style="vertical-align:middle;"/> Do you wish to composite the data to show seasonal cycles?
	
	
	<br/><br/>
	<div style="text-align:right;">
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
