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
 *  Uses the CASRSSDataProvider object to obtain RSS items and then
 *  spits them out as pretty HTML.
 * 
 *  Usage: rss.do?channel=&lt;channel-label&gt;
 * 
 */

$rssDp = $GLOBALS['app']->getDataProvider('CASRSSDataProvider');
$channel  = $_GET['channel'];
$perPage  = isset($_GET['perPage']) ? $_GET['perPage'] : 20; // Max of 20 (underlying service)
$response = $rssDp->request($channel);


if($response){
  header("Context Type: text/html");
  
  echo "<div class='prod_rss'>\n";
  $count = 0;
  foreach ($response->data['prods'] as $prodItem){
  	 if ($count == $perPage) { break; }
     echo "<div class='prod_item_rss'>\n";
     echo "<a href=\"{$prodItem['link']}\"><img src=\"".SITE_ROOT."/static/img/download-icon.png\"/></a>";
     echo "<div class='prod_item_rss_meta filename'>"
     	. "<a href=\"{$prodItem['link']}\">{$prodItem['title']}</a></div><br/>\n";
     echo "<div class='prod_item_rss_meta description'>dataset: "
     	. "<a href=\"" . SITE_ROOT . "/datasets/{$prodItem['desc']}\">{$prodItem['desc']}</a></div><br/>\n";
     echo "<br style=\"clear:both\">\n";       
     echo "</div>\n";
     $count++;
  }  
  echo "</div>\n";
}
