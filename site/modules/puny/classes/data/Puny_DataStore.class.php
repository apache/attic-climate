<?php
/**
 * Puny_DataStore
 * 
 * Base class for Puny data store implementations
 * 
 * @abstract 
 * 
 * @author ahart
 */
abstract class Puny_DataStore {
	
	protected $host;
	protected $username;
	protected $password;
	protected $dbname;
	
	protected $link;
	
	/**
	 * Connect to the data store
	 * 
	 */	
	public abstract function connect();
	
	/**
	 * Disconnect from the data store
	 */
	public abstract function disconnect();
	
	/**
	 * Request a resource from the data store. Optionally
	 * specify a particular version of the resource to fetch.
	 * 
	 * @param string $resourceId The unique id of the resource
	 * @param integer $version   (Optional) the version to retrieve. Default = latest.
	 */
	public abstract function load( $resourceId, $version = null );
	
	/**
	 * Store a new version of a resource. For simplicity, versions are 
	 * immutable. That is, every time a resource is stored, its version is
	 * first incremented and a new record is created. Implemenations should
	 * take care to automatically increment the version number of the
	 * resource before persisting to the datastore.
	 * 
	 * @param string $resourceId The unique id of the resource
	 * @param string $content The content to store 
	 */
	public abstract function store( Puny_Resource $resource );

}