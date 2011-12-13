<?php
// Get the task from the session
require_once(HOME . "/classes/RCMETWizardTask.class.php");
$task = unserialize($_SESSION['wizardTask']);
$task->setStep('selectTimeRange');

if (isset($_POST['save'])) {
	$task->rangeStart = $_POST['rangeStart'] . ' 00:00:00';
	$task->rangeEnd   = $_POST['rangeEnd']   . ' 00:00:00';
	$task->nextStep();
}

// Compute the tiems to show for the observational dataset
list($obsStartTime,$obsEndTime) = $task->getTimeRange($task->observationalDatasetId);

// Compute the times to show for the overlap
list($overlapStart,$overlapEnd) = $task->computeOverlap(
	$task->modelBounds['time']['min'],   // model start
	$task->modelBounds['time']['max'],   // model end
	$obsStartTime,                       // obs start time
	$obsEndTime);                        // obs end time

$task->showPreviousNextLinks();
?>
<link rel="stylesheet" type="text/css" href="<?echo SITE_ROOT?>/static/css/jquery-ui-1.7.1.custom.css"/>
<script type="text/javascript" src="<?php echo SITE_ROOT?>/static/js/jquery-ui-1.7.1.custom.min.js"></script>
<script type="text/javascript">
$(document).ready(function() {
	// Initialize Date Pickers
	$('#overlap-start').datepicker({changeMonth: true, changeYear: true, dateFormat: 'yy-mm-dd'});
	$('#overlap-end').datepicker({changeMonth: true, changeYear: true, dateFormat: 'yy-mm-dd'}); 

});
</script>
<fieldset id="variableAssignmentSelector" class="">
	<legend>Specify a Time Range Over Which to Operate</legend>
<form method="POST">
	The following information has been auto-detected using the model and observational
	data specified in the previous steps:<hr/>
	
	<h3>Model:</h3>
	<label>Range Start:</label>
	<input type="text" disabled="disabled" value="<?php echo substr($task->modelBounds['time']['min'],0,10)?>"/>
	<label>Range End:</label>
	<input type="text" disabled="disabled" value="<?php echo substr($task->modelBounds['time']['max'],0,10)?>"/>
	
	<h3>Observations:</h3>
	<label>Range Start:</label>
	<input type="text" disabled="disabled" value="<?php echo substr($obsStartTime,0,10)?>"/>
	<label>Range End:</label>
	<input type="text" disabled="disabled" value="<?php echo substr($obsEndTime,0,10)?>"/>
	
	
	<h3>Overlap:</h3>
	<label>Range Start:</label>
	<input type="text" id="overlap-start" name="rangeStart" value="<?php echo substr($overlapStart,0,10)?>"/>
	<label>Range End:</label>
	<input type="text" id="overlap-end"   name="rangeEnd" value="<?php echo substr($overlapEnd,0,10)?>"/>
	
	<hr class="space"/>
	<div style="text-align:right;">
	<p>If the information above is correct, please click: 
	<input type="submit" name="save" value="Continue"/>
	</p>
	</div>
	
</form>
</fieldset>