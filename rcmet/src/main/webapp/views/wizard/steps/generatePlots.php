<?php
// Get the task from the session
require_once(HOME . "/classes/RCMETWizardTask.class.php");
$task = unserialize($_SESSION['wizardTask']);
$task->setStep('generatePlots');

$task->showPreviousNextLinks();
?>
<script type="text/javascript">
	$(document).ready(function() {

		$('#btnBegin').click(function() {
			$('#working').show();

			/** 
			 * All values hardcoded to test webapp <--> Bottle integration
			 **/
			$.post(<?php echo SITE_ROOT?>'/plots.do',{
				"action"        : "GENERATE",

				"obsDatasetId"   : "<?php echo $task->observationalDatasetId?>",
				"obsParameterId" : "<?php echo $task->observationalParameterId?>",
				"startTime"      : "<?php echo $task->rangeStart?>",
				"endTime"        : "<?php echo $task->rangeEnd?>",
				"latMin"         : "<?php echo $task->modelBounds['lat']['min']?>",
				"latMax"         : "<?php echo $task->modelBounds['lat']['max']?>",
				"lonMin"         : "<?php echo $task->modelBounds['lon']['min']?>",
				"lonMax"         : "<?php echo $task->modelBounds['lon']['max']?>",
				"filelist"       : "<?php echo $task->modelFilePaths[0]?>",
				"modelVarName"   : "<?php echo $task->modelParameter?>",
				/*precipFlag*/
				"modelTimeVarName":"<?php echo $task->modelVars['time']?>",
				"modelLatVarName" :"<?php echo $task->modelVars['lat']?>",
				"modelLonVarName" :"<?php echo $task->modelVars['lon']?>",
				"regridOption"    :"<?php echo $task->spatialRegridOption?>",
				"timeRegridOption":"<?php echo $task->temporalRegridOption?>",
				/*seasonalCycleOption*/
				"metricOption"    :"<?php echo $task->metric?>",
				/*titleOption*/
				/*plotFileNameOption*/
				/*maskOption*/
				/*maskLatMin*/
				/*maskLatMax*/
				/*maskLonMin*/
				/*maskLonMax*/
			// Callback
			},function(data) {
				loadResults(data);
			},"json");		
		});
	});

	
	function loadResults(data) {
		// Path to .png server script
		var base = "<?php echo SITE_ROOT?>/plotView.do?path=";
		
		$('#working').hide();
		$('#results').show();
		$('#results')
			.append($('<a>')
				.attr('href',base + data.modelPath)
				.attr('target','new')
				.text('Model Data Plot'));
		$('#results').append('<br/>');
		$('#results')
			.append($('<a>')
				.attr('href',base + data.obsPath)
				.attr('target','new')
				.text('Observational Data Plot'));
		$('#results').append('<br/>');
		$('#results')
			.append($('<a>')
				.attr('href',base + data.comparisonPath)
				.attr('target','new')
				.text('Comparison Plot'))
	}
</script>
<div id="preview">
<h2>Job Summary</h2>
The toolkit is almost ready to generate plots based upon your input. Please take one last look at 
the settings below: 
<fieldset id="modelFileSelector">
<legend>Preview your Job Settings:</legend>
<table class="preview">
<tr><th>Model File:</th>             <td><?php echo $task->modelFilePaths[0]?></td></tr>
<tr><th>Latitude Range (var): </th>  <td><strong>FROM:</strong> <?php echo $task->modelBounds['lat']['min'] . ', <strong>TO:</strong> ' . $task->modelBounds['lat']['max'].", <strong>USING:</strong> \"".$task->modelVars['lat']."\""?></td></tr>
<tr><th>Longitude Range (var):</th>  <td><strong>FROM:</strong> <?php echo $task->modelBounds['lon']['min'] . ', <strong>TO:</strong> ' . $task->modelBounds['lon']['max'].", <strong>USING:</strong> \"".$task->modelVars['lon']."\""?></td></tr>
<tr><th>Time Range (var):</th>       <td><strong>FROM:</strong> <?php echo $task->rangeStart . ', <strong>TO:</strong> ' . $task->rangeEnd.", <strong>USING:</strong> \"".$task->modelVars['time']."\""?></td></tr>
<tr><th>Model Parameter:</th>        <td><?php echo $task->modelParameter?></td></tr>
<tr><th>Observational Dataset:</th>  <td><?php echo $task->observationalDataset?> (id:<?php echo $task->observationalDatasetId?>)</td></tr>
<tr><th>Observational Parameter:</th><td><?php echo $task->observationalParameter?> (id:<?php echo $task->observationalParameterId?>)</td></tr>
<tr><th>Spatial Regrid Option:</th><td><?php echo $task->dictSpatialRegrid($task->spatialRegridOption)?></td></tr>
<tr><th>Temporal Regrid Option:</th><td><?php echo $task->dictTemporalRegrid($task->temporalRegridOption)?></td></tr>
<tr><th>Metric Calculated:</th><td><?php echo $task->dictMetrics($task->metric)?></td></tr>

</table>

<hr class="space"/>
<div style="text-align:right;">
<p>If the information above is correct, please click: 
<input type="button" id="btnBegin" value="Generate Plots"/>
</p>
</div>


<div id="working" style="display:none;">working... (this may take up to 10 minutes)</div>
<div id="results" style="display:none;">
	<h2>Plotted Results</h2>
	<p>Your plotted files are ready. To view, click on a link below. Each link opens
	   in a new window.</p>
	<hr/>
</div>
</fieldset>
</div>