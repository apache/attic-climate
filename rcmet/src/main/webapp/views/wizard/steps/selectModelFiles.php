<?php
// Get the task from the session
require_once(HOME . "/classes/RCMETWizardTask.class.php");
$task = unserialize($_SESSION['wizardTask']);
$task->setStep('selectModelFiles');

if (isset($_POST['save'])) {
	if (!$task) { header("Location: " . SITE_ROOT . '/wizard/init'); }
	
	// Store the model file path information
	$task->modelFilePaths[0] = $_POST['txtModelFilePath'];
	
	// Go to the next step
	$task->nextStep('selectModelFiles');
}

?>
<script type="text/javascript">
var autocomplete;
$(document).ready(function() {
	$('#txtModelFilePath').keyup(function(e) {
		var code = (e.keyCode) ? e.keyCode : e.which;
		if (code == 191) {/* forward slash (/) */
			// Load a new set of autocomplete options based
			// on the latest directory path requested
			fetchFiles($(this).val());
			
		} else {
			// Filter the existing autocomplete options based 
			// on the new keypress
		}
	});

	$('#pathAutocomplete li span').live('click',function(e) {
		val = $(e.target).text();
		$('#txtModelFilePath').val($('#txtModelFilePath').val() + val);
		if (val[val.length - 1] == '/')
			fetchFiles($('#txtModelFilePath').val());
	});
});

function fetchFiles(path) {
	$.get('/dirlist.do?path='+path,{},
		function(data) {
			autocomplete = data;
			updateAutocomplete();					
	},'json');
}
function updateAutocomplete() {
	$('#pathAutocomplete li').remove();
	$.each(autocomplete,function(i,v) {
		$('#pathAutocomplete').append($('<li>').html($('<span>').text(v)));
	});
}
</script>
<div class="section">
<div class="row">
<div class="span12">
<h2 class="title">Select a Model File</h2>
<div class="box">
<div class="box-content">
    <fieldset id="modelFileSelector">
    <form method="post">
	    <legend>Please select the file that contains your model data:</legend>
	    <input type="file" id="txtModelFilePath" name="txtModelFilePath" value=""/>
	    <input id="btnLoadModelFile" type="submit" name="save" value="Load" class="btn btn-primary"/>
	    <br/>
	    <p class="hint">Acceptable formats are <strong>NetCDF</strong> (*.nc)</p>
    </form>
    </fieldset>
</div>
</div>
</div>
</div>
</div>
