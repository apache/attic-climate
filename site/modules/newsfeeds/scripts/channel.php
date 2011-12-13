<?php
/**
 * Webservice to display data from the requested channel, in the 
 * requested output format.
 * 
 * usage: channel.do?channel=<channel-label>&format=<output-format>
 * usage: channel.do?channel=<channel-label> <-- 'html' format assumed
 */
$module = App::Get()->loadModule();
require_once($module->modulePath . "/classes/NewsFeeds.class.php");


// Determine which channel is requested
$channelWanted = $_GET['channel'];
$outputFormat  = (isset($_GET['format']))
	? $_GET['format']
	: "html";	
	
// Create an instance of the NewsFeeds class
$newsFeeds = new NewsFeeds();

// Get an appropriate data provider for the requested channel
if ($dp = $newsFeeds->getProviderForChannel($channelWanted)) {
	
	// Request the data
	$response = $dp->request("*");
	
	// Provide the appropriate header
	switch ($outputFormat) {
		case "html":
			header("Content Type: text/html");
		default: 
			header("Content Type: text/plain");
	}
	
	// Send the data out in the requested format
	echo $dp->output($response->data['entries'],$outputFormat);
	exit();
	
} else {
	die("Unable to process requested channel '{$channelWanted}'");
}