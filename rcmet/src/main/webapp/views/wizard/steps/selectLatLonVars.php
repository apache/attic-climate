<?php
// Get the task from the session
require_once(HOME . "/classes/RCMETWizardTask.class.php");
$task = unserialize($_SESSION['wizardTask']);
$task->setStep('selectLatLonVars');
	
	
if (isset($_POST['save'])) {
	// Store the model lat/lon variables and bounds
	$task->modelVars['lat']  = $_POST['latname'];
	$task->modelVars['lon']  = $_POST['lonname'];
	$task->modelBounds['lat'] = array("min" => $_POST['latmin'], "max" => $_POST['latmax']);
	$task->modelBounds['lon'] = array("min" => $_POST['lonmin'], "max" => $_POST['lonmax']);
	
	// Go to the next step
	$task->nextStep();
	
} else {
	$path = $task->modelFilePaths[0];
	$srvcPath = 'http://localhost:8082/list/latlon/"' . $path . '"';
	$data = json_decode(file_get_contents($srvcPath));
}

$task->showPreviousNextLinks();
?>

<fieldset id="variableAssignmentSelector" class="">
	<legend>Confirm Latitude and Longitude Selection</legend>
<form method="POST">
	The following information has been auto-detected for latitude and longitude by examining 
	the file specified in the previous step:<hr/>
	<div class="span-7">
	<h5>Latitude</h5>
	<table>
		<tr><th>Var:</th><td id="latVariable"><input type="text" name="latname" value="<?php echo $data->latname?>"/></td><td class="note">The variable in the model file that will be used to represent Latitude</td> </tr>
		<tr><th>Min:</th><td id="latMinValue"><input type="text" name="latmin"  value="<?php echo $data->latMin?>"/></td><td class="note">The minimum Latitude value detected in the model file</td></tr>
		<tr><th>Max:</th><td id="latMaxValue"><input type="text" name="latmax"  value="<?php echo $data->latMax?>"/></td><td class="note">The maximum Latitude value detected in the model file</td></tr>
	</table>
	</div>
	<div class="span-4">
	<h5>Longitude</h5>
	<table>
		<tr><th>Var:</th><td id="lonVariable"><input type="text" name="lonname" value="<?php echo $data->lonname?>"/></td><td class="note">The variable in the model file that will be used to represent Longitude</td></tr>
		<tr><th>Min:</th><td id="lonMinValue"><input type="text" name="lonmin"  value="<?php echo $data->lonMin?>"/></td><td class="note">The minimum Longitude value detected in the model file</td></tr>
		<tr><th>Max:</th><td id="lonMaxValue"><input type="text" name="lonmax"  value="<?php echo $data->lonMax?>"/></td><td class="note">The maximum Longitude value detected in the model file</td></tr>
	</table>
	</div>
	<hr class="space"/>
	<div style="text-align:right;">
	<p>If the information above is correct, please click: 
	<input type="submit" name="save" value="Continue"/>
	</p>
	</div>
</form>
</fieldset>
