<?php
/**
 * NewsFeeds
 * 
 * Provides a "framework" for creating and using generic wrappers for technology-
 * specific implementations of a "news feed" concept. Whether the news feed
 * is a local file, a relational database, or a consumable feed published
 * at a third party site, the concept is largely the same and thus the various
 * implementations should be amenable to access via a common interface. 
 * 
 * This class provides convenience functions for invoking data providers and 
 * channel management.
 * 
 * For the purposes of the framework, a "channel" is a collection of newsfeed
 * entries that can be accessed via a common mechanism (say, a single local file).
 * 
 * All "known" channels are defined in <MODULE>/static/channels in a file named
 * 
 *   <channel-name>.<channel-type>
 *   
 * A local YAML text file channel source named 'foo', would be: 
 * 	name:     foo.yml
 *  contents: YAML formatted newsfeed entries         {@link YamlNewsFeedDataProvider}
 * A MySQL database channel source named 'bar', would be:
 *  name:     bar.mysql
 *  contents: connection information for the resource {@link MySqlNewsFeedDataProvider}
 * A Third party atom feed named 'baz' would be:
 *  name:     baz.atom
 *  contents: url information for the remote resource {@link AtomNewsFeedDataProvider}    
 * 
 * @author andrew
 *
 */
class NewsFeeds {
	
	public function __construct() {
		
	}
	
	/**
	 * Gets a list of all the known channels
	 * @return array   basic information about all known channels
	 */
	public function getChannels() {
		$channels = array();
		$handle = opendir(App::Get()->loadModule()->modulePath . "/static/channels");
		while (false !== ($file = readdir($handle))) {
			if (is_dir(HOME . "/modules/{$file}") || $file[0] == '.') {
				continue;
			}
			$info = pathinfo($file);
			// Pre-PHP 5.2 filename detection. 5.2 onwards $info['filename'] is available directly
			$filename = substr($info['basename'],
				0,strlen($info['basename']) - strrpos($info['basename'],".{$info['extension']}"));
			$channels[$filename] = 
				array("label"=>$filename,
					  "type" =>$info['extension']);
		}
		return $channels;
	}
	
	/**
	 * Determines and instantiates a data provider for the specified channel
	 * @param $label  string   The channel label
	 * @return {@link NewsFeedDataProvider} a data provider instance for the channel
	 */
	public function getProviderForChannel($label) {
		$channels = $this->getChannels();
		foreach ($channels as $chanLabel => $chanData) {
			if ($chanLabel == $label) {
				return ($this->getProvider($label,$chanData['type']));
			}
		}
		// Channel label not found
		return false;
	}
	
	/**
	 * Internal helper funtction for determining and instantiating data providers
	 * @param $label  string  The channel label
	 * @param $type   string  The detected channel type
	 * @return {@link NewsFeedDataProvider} a data provider instance for the channel
	 */
	protected function getProvider($label,$type) {
		switch (strtolower($type)) {
			case "yml":
				require_once(App::Get()->loadModule()->modulePath . "/classes/dataProviders/YamlNewsFeedDataProvider.class.php");
				$dp = new YamlNewsFeedDataProvider();
				$dp->connect(array("channel" => $label));
				break;
			default:
				return false;
		}
		// Return the connected data provider
		return $dp;
	}
}
