<?php

	// Grab the most recent error from the session
	$errorText = $_SESSION['puny_error'];
	unset($_SESSION['puny_error']);
	
	// Don't show a header or footer for this view
	App::Get()->response->useHeaderFile(false);
	App::Get()->response->useFooterFile(false);

?>

<h1>Puny</h1>
<h2>An error has occurred:</h2>
<p><?php echo $errorText;?></p>