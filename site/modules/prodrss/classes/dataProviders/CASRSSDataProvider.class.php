<?php
// Copyright (c) 2010, California Institute of Technology.
// ALL RIGHTS RESERVED. U.S. Government sponsorship acknowledged.
// 
// $Id$

/**
 * 
 * 	@package WRM_DataProviders
 *  @author Chris A. Mattmann
 *  @version $Revision$
 *  @copyright Copyright (c) 2010, California Institute of Technology. 
 *  ALL RIGHTS RESERVED. U.S. Government sponsorship acknowledged.
 *  @version $Id$
 * 
 *  Implements the OODT Balance IApplicationDataProvider interface and 
 *  slurps up CAS product RSS and returns it for use in the WRM webapp.
 * 
 */
class CASRSSDataProvider implements IApplicationDataProvider {

  /**
   * Constructor - Instantiate the provider but do not yet connect
   * to the underlying data source.
   * 
   * @param $options  array   An optional set of configuration values
   */
  public function __construct($options= array()) {

  }

  /**
   * Initiate a connection to the underlying data source
   * 
   * @param $options  array  An optional set of configuration values
   * @return boolean         True or false depending on the result
   */
  public function connect($options= array()) {
    // for us, this method doesn't really do anything
    return true;
  }

  /**
   * Disconnect from the underlying data source and perform any
   * cleanup operations necessary.
   * 
   * @param $options  array  An optional set of configuration values
   * @return unknown_type    True or false depending on the result
   */
  public function disconnect($options= array()) {
    // again, doesn't really do anything
    return true;
  }

  /**
   * Request data from the underlying data source.
   * 
   * @param $request  mixed  The request itself, usually a string. The nature
   *                         of the request is necessarily implementation 
   *                         specific and will vary across providers. For a 
   *                         SQL-like relational provider, this will likely be
   *                         a "SELECT ..." string.
   * @param $options  array  An array of options to configure the request.
   *                         These will be implementation-specific and 
   *                         therefore will likely differ across providers.
   * @return ApplicationDataResponse  The resulting data retrieved
   */
  public function request($request, $options= array()) {
  	$casWsUrl = $GLOBALS['app']->settings['cas_ws_url'];
    $response= new ApplicationDataResponse();
    $response->setRequestString($request);
    $doc= new DOMDocument();
    $doc->load($casWsUrl."viewRecent?channel=".$request);
    $arrFeeds= array();
    foreach($doc->getElementsByTagName('item') as $node) {
      $prodRSS= array('title' => $node->getElementsByTagName('title')->item(0)->nodeValue, 
                      'desc' => $node->getElementsByTagName('description')->item(0)->nodeValue, 
                      'link' => $node->getElementsByTagName('link')->item(0)->nodeValue, 
                      'date' => $node->getElementsByTagName('pubDate')->item(0)->nodeValue);
      array_push($arrFeeds, $prodRSS);
    }

    $response->add("prods", $arrFeeds);
    return $response;
  }

  /**
   * Send a command to the underlying data source.
   * 
   * @param $command mixed   The command itself, usually a string. The nature
   *                         of the command is necessarily implementation 
   *                         specific and will vary across providers. For a 
   *                         SQL-like relational provider, this will likely be
   *                         a "UPDATE ...", or "CREATE ..." string.
   * @param $options  array  An array of options to configure the command.
   *                         These will be implementation-specific and 
   *                         therefore will likely differ across providers.
   * @return boolean         True or false depending on the success of the command
   */
  public function command($command, $options= array()) {
    // always return true
    return true;
  }

}
?>