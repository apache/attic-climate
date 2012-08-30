<?php
require_once(HOME . "/classes/RCMETWizardTask.class.php");
if (isset($_POST['init'])) {
	
	// Clear any old task information from the session
	$task = new RCMETWizardTask();
	
	// Go to the first wizard step
	$task->firstStep();
}

?>
<div class="section">
<div class="row">
<div class="span12">
<h2 class="title">Begin a New Evaluation Task</h2>
<div class="box">
<div class="box-content">
<fieldset>
<legend>You will be asked a series of questions to determine what type of plot to generate:</legend>
<div class="alert alert-info">
<strong>Note:</strong> By continuing, any previous task information will be discarded.
</div>
<form method="post">
	<input type="submit" name="init" value="Start" class="btn btn-primary"/>
</form>
</fieldset>
</div>
</div>
</div>
</div>
</div>
