<?php
// Get the task from the session
require_once(HOME . "/classes/RCMETWizardTask.class.php");
$task = unserialize($_SESSION['wizardTask']);
$task->setStep('selectObservationalData');

	
if (isset($_POST['save'])) {
	// Store the model parameter that is to be evaluated
	$task->observationalDataset   = $_POST['observationalDataset'];
	$task->observationalDatasetId = $_POST['observationalDatasetId'];
	$task->observationalParameter = $_POST['observationalParameter'];
	$task->observationalParameterId = $_POST['observationalParameterId'];

	// Go to the next step
	$task->nextStep();
	
} else {
	$path = App::Get()->settings['rcmed_query_api_url_base'] . "/datasets.php";
	$data = json_decode(file_get_contents($path));
}

$task->showPreviousNextLinks();
?>
<script type="text/javascript">
var parameterServicePath = <?php echo SITE_ROOT?>'/rcmed.do';
$(document).ready(function() {
	$('#observationalDataset').change(function(e) {
		datasetId = $(this).children('option:selected').attr('title');
		$('#obsDatasetId').val(datasetId);
		$.get(parameterServicePath,{'action':'parameters','dataset':$(this).val()},function(data) {
			$paramSelector = $('<select>').attr('name','observationalParameter').addClass('observationalParameter');
			$paramSelector.append($('<option>')
				.attr('value',0)
				.text('Please select a parameter...'));
			$.each(data,function(i,v) {
				$option = $('<option>')
					.attr('title',v.parameter_id)
					.attr('value',v.shortName)
					.text(v.longName);
				$paramSelector.append($option);
			});
			$('#parameterList').html($paramSelector);
		},"json");

	});
	$('.observationalParameter').live('change',function(e) {
		paramId = $(e.target).children('option:selected').attr('title');
		$('#obsParamId').val(paramId);
	});

});
</script>
<fieldset id="modelFileSelector">
	<legend>Select an Observational Dataset from RCMED</legend>
	<p>The following information is pulled automatically from the Regional Climate Model Evaluation Database:
	<form method="post">
		<h3>Available Datasets</h3>
		<input type="hidden" id="obsDatasetId" name="observationalDatasetId" value=""/>
		<input type="hidden" id="obsParamId"   name="observationalParameterId" value=""/>
		<select id="observationalDataset" name="observationalDataset">
			<option value="0" selected="selected">Please select a dataset...</option>
			<?php foreach ($data as $dataset): ?>
				<option value="<?php echo $dataset->shortName?>" title="<?php echo $dataset->dataset_id?>"><?php echo $dataset->longName?> (<?php echo $dataset->shortName?>)</option>
			<?php endforeach ?>
		</select>
		<span id="parameterList"></span>
		<hr class="space"/>
		<div style="text-align:right;">
		<p>If the information above is correct, please click: 
		<input type="submit" name="save" value="Continue"/>
		</p>
		</div>
	</form>
</fieldset>