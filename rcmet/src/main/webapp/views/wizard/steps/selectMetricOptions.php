<?php
// Get the task from the session
require_once(HOME . "/classes/RCMETWizardTask.class.php");
$task = unserialize($_SESSION['wizardTask']);
$task->setStep('selectMetricOptions');

if (isset($_POST['save'])) {
	$task->metric  = $_POST['metric'];
	
	$task->nextStep();
}
$task->showPreviousNextLinks();
?>
<fieldset id="variableAssignmentSelector" class="">
	<legend>Specify The Metric to Calculate</legend>
<form method="POST">
	The toolkit can compute results for a number of pre-defined metrics:<hr/>
	
	<h3>Calculation Metric</h3>
	<select name="metric">
		<option value="-1">Please select an option...</option>
		<option value="bias">Bias: mean bias across full time range</option>
		<option value="mae">Mean Absolute Error: across full time range</option>
		<option value="difference">Difference: calculated at each time unit</option>
		<option value="acc">Anomaly Correlation</option>
		<option value="patcor">Pattern Correlation</option>
		<option value="pdf" disabled="disabled">Probability Distribution Function similarity score</option>
		<option value="rms">RMS Error</option>
	</select>

	<hr class="space"/>
	<div style="text-align:right;">
	<p>If the information above is correct, please click: 
	<input type="submit" name="save" value="Continue"/>
	</p>
	</div>	
</form>
</fieldset>