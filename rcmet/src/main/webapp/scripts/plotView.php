<?php
/**
 * Serve a .png from the specified path
 */
if (isset($_REQUEST['path'])) {
	
	$im = imagecreatefrompng($_REQUEST['path']);

	header('Content-type: image/png');

	imagepng($im);
	imagedestroy($im);
}