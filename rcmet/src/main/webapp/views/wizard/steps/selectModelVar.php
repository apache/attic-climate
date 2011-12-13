<?php
// Get the task from the session
require_once(HOME . "/classes/RCMETWizardTask.class.php");
$task = unserialize($_SESSION['wizardTask']);
$task->setStep('selectModelVar');
	
	
if (isset($_POST['save'])) {
	// Store the model parameter that is to be evaluated
	$task->modelParameter   = $_POST['modelParameter'];
	
	// Go to the next step
	$task->nextStep();
	
} else {
	$path = $task->modelFilePaths[0];
	$srvcPath = 'http://localhost:8082/list/vars/"' . $path . '"';
	$data = json_decode(file_get_contents($srvcPath));
}


$task->showPreviousNextLinks('selectModelVar');
?>

<fieldset class="">
	<legend>Select a Model Parameter to Evaluate</legend>
	<form method="POST">
		The following parameter information has been auto-detected from the model input:<hr/>
		<h5>Available Parameters</h5>
		<select name="modelParameter">
			<?php foreach ($data->variables as $var):?>
				<option value="<?php echo $var?>"><?php echo $var?></option>
			<?php endforeach ?>
		</select>
		<span class="note">The variable in the model file that will be used in calculations</span>
		<hr class="space"/>
		<div style="text-align:right;">
		<p>If the information above is correct, please click: 
		<input type="submit" name="save" value="Continue"/>
		</p>
		</div>
	</form>
</fieldset>
