<?php
/**
 * RCMET Model Evaluation Toolkit - Wizard
 * 
 * The wizard helps users step through the process of
 * 
 * 1) Selecting locally stored model data output for use in the run
 * 2) Selecting compatible observational data from the RCMED
 * 3) Selecting an operation to perform on the two datasets
 * 4) Selecting an output format and/or visualization style
 * 
 * 
 */


$segments = App::Get()->request->segments;
if (!isset($segments[0])) {
	die("Missing required parameters. Please specify a wizard step in the URL");
}
if (!is_file(HOME . '/views/wizard/steps/' . $segments[0] . '.php')) {
	die("Invalid step requested. See the <a href='./help'>Wizard Help</a> for more information");
} else {
	
	// Widgetize the requested wizard step
	App::Get()->WidgetizeView("/wizard/steps/" . $segments[0]);
}
