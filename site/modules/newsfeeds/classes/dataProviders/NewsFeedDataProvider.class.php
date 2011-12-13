<?php
/**
 * NewsFeedDataProvider
 * 
 * Provides an abstract base class for all NewsFeed data providers. The
 * purpose of a NewsFeed-derived data provider is to wrap the underlying
 * data source (whether it be a local text,yml,xml, or other file, 
 * relational database, or external web service) and provide access
 * via the common IApplicationDataProvider interface.
 * 
 * 
 * This class defines two functions:
 * 
 * - initialize: ready the specified channel for reading. Depending on 
 *   the underlying implementation, this may mean verifying that a 
 *   file exists, or it could mean connecting to a database or remote
 *   web service. 
 *   
 * - output: return the provided data in the format requested by the
 *   $outputFormat parameter. $ata is expected to be an array of 
 *   newsfeed entries. $data will usually be the output of a prior 
 *   call to ::request(). Each newsfeed entry provided in $data should
 *   be an associative array conforming to:
 *   
 *     array(
 *       "date"   => "YYYY-MM-DD HH:II:SS"
 *       "author" => "author name"
 *       "body"   => "article body"
 *     );
 *     
 *   
 * @author ahart
 *
 */
abstract class NewsFeedDataProvider implements 
	Org_Apache_Oodt_Balance_Interfaces_IApplicationDataProvider {
	
	protected $channelDirectory;
	protected $channel;
	
	/**
	 * Ready the specified channel for reading
	 * @param $channel string  the label of the channel to initialize
	 * @param $options array   an optional array of initialization options
	 * @return boolean         true if initialization was successful
	 */
	abstract public function initialize($channel,$options = array());
	
	/**
	 * Format the provided data based on the provided format
	 * @param $data    array   an array of newsfeed entries
	 * @param $outputFormat  string  the output format to use
	 * @return string        the formatted output
	 */
	abstract public function output($data,$outputFormat);
	
	/**
	 * Format the provided data as HTML
	 * @param $data    array   an array of newsfeed entries
	 * @return unknown_type
	 */
	abstract protected function asHtml($data);
	
	/**
	 * Format the provided data as JSON
	 * @param $data    array   an array of newsfeed entries
	 * @return unknown_type
	 */
	abstract protected function asJson($data);
	
	/**
	 * Format the provided data as XML
	 * @param $data    array   an array of newsfeed entries
	 * @return unknown_type
	 */
	abstract protected function asXML($data);
}