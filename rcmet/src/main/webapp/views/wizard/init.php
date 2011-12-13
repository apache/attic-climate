<?php
require_once(HOME . "/classes/RCMETWizardTask.class.php");
if (isset($_POST['init'])) {
	
	// Clear any old task information from the session
	$task = new RCMETWizardTask();
	
	// Go to the first wizard step
	$task->firstStep();
}

?>
<h1>Begin a New Evaluation Task</h1>
<p>The toolkit will ask you a series of questions to determine what type of plot to generate:
<div class="notice">
<strong>Note:</strong> By continuing, any previous task information will be discarded.
</div>
<hr class="space"/>
<form method="post">
	<input type="submit" name="init" value="OK, Begin"/>
</form>