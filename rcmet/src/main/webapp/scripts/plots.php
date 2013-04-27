<?php

switch (strtoupper($_REQUEST['action'])) {
	
	case "GENERATE":
		$url        = App::Get()->settings['rcmet_service_url_base'] . '/rcmes/run/';
		$postFields = http_build_query($_REQUEST);
		
		if (isset(App::Get()->settings['rcmet_service_use_curl']) 
		   && App::Get()->settings['rcmet_service_use_curl'] == true) {
		   $ch = curl_init();
		   curl_setopt($ch,CURLOPT_URL,$url);
		   curl_setopt($ch,CURLOPT_POST, 1);
		   curl_setopt($ch,CURLOPT_POSTFIELDS,$postFields);
		   curl_setopt($ch,CURLOPT_RETURNTRANSFER,1);
		   $response = curl_exec($ch);
		   curl_close($ch);
		} else {
		  $params = array('http' => array(
		     'method' => 'POST',
		     'content' => $postFields));
		  $ctx = stream_context_create($params);
		  $fp = @fopen($url, 'rb', false, $ctx);
		  $response = @stream_get_contents($fp);
		}

		echo $response;
		break;
	default:
		echo "{}";
		break;
	
}

exit();