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
<fieldset id="modelFileSelector" class="span-22 prepend-1 last"	>
<form method="post">
	<legend>To begin, select a model file to work with</legend>
	<input type="text" id="txtModelFilePath" name="txtModelFilePath" value=""/>
	<input id="btnLoadModelFile" type="submit" name="save" value="Load"/>
	<br/>
	<ul id="pathAutocomplete"></ul>
</form>
</fieldset>
<hr/>