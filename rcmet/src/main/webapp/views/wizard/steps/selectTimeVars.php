<?php
// Get the task from the session
require_once(HOME . "/classes/RCMETWizardTask.class.php");
$task = unserialize($_SESSION['wizardTask']);
$task->setStep('selectTimeVars');
	
	
if (isset($_POST['save'])) {
	// Store the time bounds
	$task->modelVars['time']   = $_POST['timename'];
	$task->modelBounds['time'] = array("min" => $_POST['timeMin'], "max" => $_POST['timeMax']);
	
	// Go to the next step
	$task->nextStep();
	
} else {
	$path = $task->modelFilePaths[0];
	$srvcPath = 'http://localhost:8082/list/time/"' . $path . '"';
	$data = json_decode(file_get_contents($srvcPath));
}

$task->showPreviousNextLinks('selectTimeVars');
?>

<fieldset class="">
	<legend>Confirm Time Variable Selection</legend>
	<form method="POST">
		The following information has been auto-detected for time:<hr/>
		<h5>Time</h5>
		<table>
			<tr><th>Var:</th><td id="timeVariable"><input type="text" name="timename" value="<?php echo $data->timename?>"/></td><td class="note">The variable in the model file that will be used to represent Time</td></tr>
			<tr><th>Min:</th><td id="timeMinValue"><input type="text" name="timeMin"  value="<?php echo $data->start_time?>"/></td><td class="note">The earliest Time value detected in the model file</td></tr>
			<tr><th>Max:</th><td id="timeMaxValue"><input type="text" name="timeMax"  value="<?php echo $data->end_time?>"/></td><td class="note">The most recent Time value detected in the model file</td></tr>
		</table>
		<hr class="space"/>
		<div style="text-align:right;">
		<p>If the information above is correct, please click: 
		<input type="submit" name="save" value="Continue"/>
		</p>
		</div>
	</form>
</fieldset>
