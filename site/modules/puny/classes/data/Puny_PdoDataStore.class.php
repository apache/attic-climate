<?php

// Require the abstract parent class definition
require_once( dirname(__FILE__) . '/Puny_DataStore.class.php');


/**
 * A PDO implementation of the Puny_DataStore class.
 * 
 * @author ahart
 */
class Puny_PdoDataStore extends Puny_DataStore {
	
	protected $driver      = 'mysql';
	protected $tablePrefix = 'puny_';
	
	/**
	 * (non-PHPdoc)
	 * @see Puny_DataStore::connect()
	 * @throws PDOException
	 */
	public function connect() {
		$this->host = App::Get()->settings['puny_datastore_pdo_host'];
		$this->username = App::Get()->settings['puny_datastore_pdo_username'];
		$this->password = App::Get()->settings['puny_datastore_pdo_password'];
		$this->dbname   = App::Get()->settings['puny_datastore_pdo_dbname'];
		$this->driver   = App::Get()->settings['puny_datastore_pdo_driver'];
		$this->tablePrefix = App::Get()->settings['puny_datastore_pdo_tablePrefix'];
		
		$dsn = $this->driver . ':host=' . $this->host . ';dbname=' . $this->dbname;
		$this->link = new PDO( $dsn, $this->username, $this->password );
	}
	
	/**
	 * (non-PHPdoc)
	 * @see Puny_DataStore::disconnect()
	 */
	public function disconnect() {
		if ($this->link)
			$this->link = null;
	}
	
	public function load( $resourceId, $version = null) {
		
		// Request the specified resource...
		$sql  = "SELECT * FROM `{$this->tablePrefix}resource` WHERE `resourceId`=:resourceId ";
		$data = array('resourceId' => $resourceId); 
		
		// If a version is specified, explicitly request that version...
		if ($version != null) {
			$sql .= " AND `version`=:version ";
			$data['version'] = $version;
		} 
		
		// Otherwise, simply get the latest version...
		else {
			$sql .= " ORDER BY `version` DESC ";
		}
		
		// Limit our results to at most one result...
		$sql .= " LIMIT 1 ";
		
		// Prepare and execute the query using the provided data...
		$stmt = $this->link->prepare( $sql );
		$stmt->execute( $data );

		// Return the single result, or return false if no match...
		if (false != ($resource = $stmt->fetch())) {
			return new Puny_Resource($resource);
		} else {
			return false;
		}
	}
	
	public function store( Puny_Resource $resource ) {
		
		// Increment the resource version id... (see note in Puny_DataStore.class.php)
		$resource->incrementVersion();
		
		// Create sql for storing this new resource version...
		$sql = "INSERT INTO `{$this->tablePrefix}resource` (`resourceId`,`version`,`parser`,`content`) "
			.  "VALUES (:resourceId, :version, :parser, :content) ";
		
		// Prepare and execute the statement using the provided data
		$stmt = $this->link->prepare($sql);
		$stmt->execute ( array (
			'resourceId' => $resource->getId()
			, 'version'  => $resource->getVersion()
			, 'parser'   => $resource->getParser()
			, 'content'  => $resource->getContent(true) // raw, unparsed content
		));
		
	}
	
}