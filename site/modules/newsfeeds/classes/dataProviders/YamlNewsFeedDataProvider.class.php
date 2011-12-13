<?php
require_once(App::Get()->loadModule()->modulePath . "/classes/dataProviders/NewsFeedDataProvider.class.php");
require_once(App::Get()->loadModule()->modulePath . "/classes/thirdparty/spyc-0.4.5/spyc.php");

/**
 * YamlNewsFeedDataProvider
 * 
 * Provides an implementation of {@link NewsFeedDataProvider} that supports reading
 * from and writing to YAML files. This is a great way to handle low-volume,
 * infrequently written feeds, because it has very low overhead and is easy
 * to set up and maintain. The format of each entry in the file should conform
 * to:
 * 
 * - date: YYYY-MM-DD HH:MM:SS
 *   author: Author Name
 *   body: Article Body Text
 *   
 * Note: the leading '-' is important, as it is the yml convention for an
 * array entry. Also remember that whitespace (indentation) is important
 * in YAML. see http://yaml.org for a complete description of YAML.
 * 
 * To create a yml channel 'foo', simply create a file in <MODULE>/static/channels
 * and name it foo.yml. The extension must be .yml for the module to detect
 * and use this particular data provider. Then just add entries to the file
 * according to the format above. See the sample-yaml.yml channel for a working
 * example. 
 * 
 * The easiest way to use this class is to let the NewsFeeds class do all the work:
 * 
 *   $nf = new NewsFeeds();
 *   $yamlNewsFeedDataProvider = $nf->getProviderForChannel('foo');
 *   $response = $yamlNewsFeedDataProvider->request("*");
 *   
 * Responses are standard {@link ApplicationDataResponse} objects, and can be manipulated
 * as such.
 * 
 * To get an HTML-formatted output of your channel, simply call:
 * 
 *  $yamlNewsFeedDataProvider->output($data,'html'); 
 *  
 * Where $data is a collection of newsfeed entries most probably retrieved via a 
 * prior call to {@link request}.
 * 
 * 
 * @author andrew
 *
 */

class YamlNewsFeedDataProvider extends NewsFeedDataProvider {
	
	public function __construct($options = array()) {
		$this->channelDirectory = (isset($options['channelDirectory']))
			? $options['channelDirectory']
			: App::Get()->loadModule()->modulePath . "/static/channels";
	}
	
	public function connect($options = array()) {
		$this->channel = $options['channel'];
	}
	
	public function disconnect($options = array()) {} 
	
	public function request($request,$options = array()) {
		$response = new Org_Apache_Oodt_Balance_Core_ApplicationDataResponse();
		$response->setRequestString($request);
		
		if ($request = "*") {
			$data = spyc_load_file("{$this->channelDirectory}/{$this->channel}.yml");
			$response->add("entries",$data);
		} else {
			$response->setError("Unsupported request string '{$request}'");
		}
		return $response;
	}
	
	public function command($command,$options = array()) {
		switch (strtolower($command)) {
			case "add":
				// Get the data from the options array
				$data   = $options['data'];
				// Format the new data as yml markup
				$str    = "\r\n"
						. "- date: {$data['date']}\r\n"
						. "  author: {$data['author']}\r\n"
						. "  body: ".str_replace("\r\n",'',nl2br(stripslashes($data['body'])))."\r\n\r\n";
				// Write the data to the file		
				file_put_contents("{$this->channelDirectory}/{$this->channel}.yml",$str,FILE_APPEND);
				return true;
				break;
			default:
				die("Unsupported command {$command} requested");
		}
	}
	
	public function initialize($channel,$options = array()) {
		$this->channel = $channel;
		if (is_file("{$this->channelDirectory}/{$channel}.yml")) {
			$this->channel = $channel;
			return true;	
		} else {
			return false;
		}
	}
	
	public function output($data, $outputFormat) {
		switch (strtolower($outputFormat)) {
			case "html":
				return $this->asHtml($data);
			default:
				die("Unsupported output format '{$outputFormat}' requested");
		}
	}
	
	protected function asHtml($data) {
		$r .= "<div class=\"nf_entries\">\r\n";
		foreach ($data as $d) {
			$niceDate = date('F jS, Y \a\t g:i A',strtotime($d['date']));
			$r .= "  <div class=\"nf_entry\">\r\n";
			$r .= "    <div class=\"nf_date\">{$niceDate}</div>\r\n";
			$r .= "    <div class=\"nf_author\">{$d['author']}</div>\r\n";
			$r .= "    <div class=\"nf_body\">{$d['body']}</div>\r\n";
			$r .= "  </div>\r\n";
		}
		$r .= "</div>\r\n";
		return $r;		
	}
	
	protected function asJson($data) { 
		//TODO: Implement This
	}
	
	protected function asXml($data) {
		//TODO: Implement this
	}
}