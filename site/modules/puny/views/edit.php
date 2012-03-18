<?php

// Don't show a header or footer on this view
App::Get()->response->useHeaderFile(false);
App::Get()->response->useFooterFile(false);

// Include the main Puny class
require_once(App::Get()->settings['puny_module_path'] . '/classes/Puny.class.php');

// Load the requested resource
$resource = Puny::load(App::Get()->request->segments[0]);

// Get the raw contents
$content = $resource->getContent(true);

?>

<input type="hidden" name="punyResourceId" value="<?php echo $resource->getId()?>"/>
<table class="punyEditor">
	<tr><td>Resource: </td>
		<td><?php echo $resource->getId();?> 
			(latest version: <?php echo $resource->getVersion();?>, 
			 parser: <?php echo $resource->getParser()?>)</td>
	</tr>
	<!--
	<tr><td>Versions: </td>
		<td><select>
			<option value="3">3: 4 hours ago</option>
		</select></td>
	</tr>
	-->
	<tr><td colspan="2"><textarea name="punyContent" id="punyContent"><?php echo $content ?></textarea></td>
	</tr>
	<tr class="actions">
		<td colspan="2">
			<a class="cancel" href="#">cancel</a> &nbsp;
			<input type="button" class="save" value="Save Changes"/>
	</tr>
</table>