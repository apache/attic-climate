<?php

// Require the abstract parent class definition
require_once( dirname(__FILE__) . '/Puny_DataStore.class.php');

/**
 * A MongoDB implementation of the Puny_DataStore class.
 *
 * @author ahart
 */
class Puny_MongoDataStore extends Puny_DataStore {

  protected $collection;

  public function connect() {
    $dbname = App::Get()->settings['puny_datastore_mongo_db'];
    $coll   = App::Get()->settings['puny_datastore_mongo_collection'];
    $this->link = new Mongo();
    $this->dbname = $this->link->selectDB($dbname);
    $this->collection = $this->dbname->$coll;
  }

  public function disconnect() {
    if ($this->link) {
      $this->link->close();
    }
  }

  public function load( $resourceId, $version = null ) {
    // Build criteria for loading...
    $criteria = array("resourceId" => $resourceId);
    
    // If a version is specified...
    if ($version !== null) { 
      $criteria['version'] = $version;
      $doc = $this->collection->findOne( $criteria );
    } 

    // Otherwise...
    else {
      $cursor = $this->collection->find(array("resourceId" => $resourceId));
      $cursor->sort(array('version' => -1));
      $doc = $cursor->getNext();
    }

    // Return whatever was found...
    return ($doc) ? new Puny_Resource( $doc ) : false;
  }

  public function store ( Puny_Resource $resource ) {
    $doc = array(
		 "resourceId" => $resource->getId()
		 , "version"  => time()
		 , "parser"   => $resource->getParser()
		 , "content"  => $resource->getContent( true )); // raw, unparsed content

    $this->collection->insert( $doc );
  }
}