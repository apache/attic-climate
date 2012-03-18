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
/**
 * 
 * OODT Balance
 * Web Application Base Framework
 * 
 * IApplicationErrorProvider defines an interface that should be implemented
 * by all error providers to simplify the process of formatting and displaying
 * application errors.
 * 
 * 
 * @author ahart
 */
interface Org_Apache_Oodt_Balance_Interfaces_IApplicationErrorProvider {
	
	/**
	 * Causes an error response to be sent to the sender
	 * 
	 * @param integer $httpResponseCode  The HTTP response code to send
	 * @param string  $message           A contextual message to include or log
	 */
	public function error($httpResponseCode,$message = '',$options=array());
}
