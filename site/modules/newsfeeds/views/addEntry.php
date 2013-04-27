<?php
/**
 * Simple web form for adding a newsfeed entry to a channel. 
 */
$app = $GLOBALS['app'];
require_once(MODULE . "/classes/NewsFeeds.class.php");

// Create an instance of the NewsFeeds class
$newsFeeds = new NewsFeeds();

// Determine the existing channels
$channels = $newsFeeds->getChannels();

?>
<h1>Add Entry to Channel:</h1>
<form method="POST" action="<?php echo MODULE_ROOT?>/addEntry.do">
	<table>
	<tbody>
	<tr><th>Channel:</th>
		<td><select name="channel">
		<?php foreach ($channels as $channel):?>
			<option value="<?php echo $channel['label']?>"><?php echo $channel['label']?></option>
		<?php endforeach;?>
		</select></td>
	</tr>
	<tr><th>Date:</th>
		<td><input type="text" name="date" value="<?php echo date('Y-m-d G:i:s',mktime())?>"/></td>
	</tr>
	<tr><th>Author:</th>
		<td><input type="text" name="author"/></td>
	</tr>
	<tr><th>Body:</th>
		<td><textarea name="body"></textarea></td>
	</tr>
	<tr>
	<td><input type="submit" value="Post!"/></td>
	<td>&nbsp;</td>
	</tr>
	</tbody>
	</table>
</form>