<?php

switch (strtoupper($_REQUEST['action'])) {
	
	case "GENERATE":
		$url        = App::Get()->settings['rcmet_service_url_base'] . '/rcmes/run/';
		$postFields = http_build_query($_REQUEST);
		
		$ch = curl_init();
		curl_setopt($ch,CURLOPT_URL,$url);
		curl_setopt($ch,CURLOPT_POST, 1);
		curl_setopt($ch,CURLOPT_POSTFIELDS,$postFields);
		curl_setopt($ch,CURLOPT_RETURNTRANSFER,1);
		#curl_setopt($ch,CURLOPT_HEADER,1);
		echo curl_exec($ch);
		curl_close($ch);
		break;
	default:
		echo "{}";
		break;
	
}

exit();