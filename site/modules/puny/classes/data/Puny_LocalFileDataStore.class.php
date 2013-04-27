<?php
/*
 * Licensed to the Apache Software Foundation (ASF) under one or more
 * contributor license agreements.  See the NOTICE file distributed with
 * this work for additional information regarding copyright ownership.
 * The ASF licenses this file to You under the Apache License, Version 2.0
 * (the "License"); you may not use this file except in compliance with
 * the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

// Require the abstract parent class definition
require_once( dirname(__FILE__) . '/Puny_DataStore.class.php');

/**
 * An implementation of the Puny_DataStore class that persists
 * content to ascii text files.
 *
 * @author ahart
 */
class Puny_LocalFileDataStore extends Puny_DataStore {

  protected $dataDirectory;

  public function connect() {
    $this->dataDirectory = App::Get()->settings['puny_datastore_localfile_dir'];

    // Ensure we can write to the directory
    if (!is_writeable($this->dataDirectory)) {
      throw new Exception("Puny can not write to the specified data directory");
    }
  }

  public function disconnect() {
    //noop
  }

  public function load( $resourceId, $version = null ) {

    // The LocalFile data store does not currently support
    // the concept of 'versions'. It could, but is the 
    // added complexity really worth it? This is really 
    // intended as a development tool, with the assumption
    // that one of the more full-featured data store
    // implementations (e.g.: PDO, Mongo) will ultimately
    // be used. 

    // Build the full path from the resourceId
    $path = $this->dataDirectory . '/' . $resourceId . ".txt";

    if (file_exists( $path ) ) {
      $content  = file_get_contents($path);
      $resource = array(
			"resourceId" => $resourceId
			, "content"  => $content
			);
      return new Puny_Resource($resource);
    } else {
      return false;
    }
  }

  public function store ( Puny_Resource $resource ) {

    // Build the full path from the resourceId
    $path = $this->dataDirectory . '/' . $resource->getId() . ".txt";

    // Store the latest content
    file_put_contents($path, $resource->getContent(true)); // raw, unparsed content

  }
}