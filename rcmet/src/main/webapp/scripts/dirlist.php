<?php
if (file_exists($_GET['path'])) {
	echo json_encode(getDirectoryList($_GET['path']));
} else {
	echo json_encode(array());
}

function getDirectoryList ($directory) {
    // create an array to hold directory list
    $results = array();
    // create a handler for the directory
    $handler = opendir($directory);
    // open directory and walk through the filenames
    while ($file = readdir($handler)) {
      // if file isn't this directory or its parent, add it to the results
      if ($file[0] != '.') {
        $results[] = is_dir($directory . '/' . $file) ? "{$file}/" : $file;
      }
    }
    // tidy up: close the handler
    closedir($handler);
    // done!
    sort($results);
    return $results;
}
