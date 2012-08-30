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
<div class="section">
<div class="row">
<div class="span12">
<h2 class="title">Calculation Metric</h2>
<div class="box">
<div class="box-content">
<fieldset id="variableAssignmentSelector" class="">
	<legend>Specify The Metric to Calculate</legend>
<form method="POST">
	The toolkit can compute results for a number of pre-defined metrics:<hr/>
	
	<h4>Calculation Metric</h4>
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
