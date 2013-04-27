<?php
/**
 * Process a request to add data to a newsfeed channel. Because all supported
 * channel types have a {@link NewsFeedDataProvider}-derived data provider, they
 * all conform to the {@IApplicationDataProvider} interface. Therefore, only one
 * (this) processor is needed, regardless of the ultimate destination of the 
 * data (local file, relational db, etc).
 * 
 * This script uses the NewsFeeds::getProviderForChannel class to determine the
 * appropriate data provider to invoke. 
 * 
 * @author ahart
 */
require_once(App::Get()->loadModule()->modulePath . "/classes/NewsFeeds.class.php");

// Determine the channel
$channelWanted = $_POST['channel'];

// Create an instance of the NewsFeeds class
$newsFeeds = new NewsFeeds();

// Get an appropriate data provider for the requested channel
if ($dp = $newsFeeds->getProviderForChannel($channelWanted)) {
	$data = array("date"   => $_POST['date'],
				  "author" => $_POST['author'],
				  "body"   => $_POST['body']);
	if ($dp->command("add",array("data" => $data))) {
		$app->setMessage("Added entry");
		$app->redirect(App::Get()->loadModule()->moduleRoot . "/addEntry");
	} else {
		$app->setMessage("Could not add entry: command error",CAS_MSG_ERROR);
		$app->redirect(App::Get()->loadModule()->moduleRoot . "/addEntry");
	}
} else {
	$app->setMessage("Could not add entry: data provider error",CAS_MSG_ERROR);
	$app->redirect(App::Get()->loadModule()->moduleRoot . "/addEntry");
}