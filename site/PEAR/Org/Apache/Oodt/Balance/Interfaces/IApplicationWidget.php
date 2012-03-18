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
 * Interface for developing widgets (reusable bits of view code) that can
 * be placed on different application pages.
 * 
 * This interface defines two mandatory functions:
 *  - construct : Intialize the widget and provide any necessary 
 *                configuration information
 *  - render    : Build the HTML output that constitutes the widget. This
 *                function does not accept arguments (any config should
 *                be provided either in the controller or via other "set"
 *                functions. This function should return a string composed
 *                of the final HTML output of the widget.
 *        
 * Framework widgets can be found inside the {LIB}/scripts/widgets directory.              
 * 
 * Framework Widgets can be invoked from view code as follows:
 *    // Create an instance of the widget (will transparently call __construct)
 *    $myFooWidget = $app->createWidget('FooWidget',array(..config..))
 *  
 * Custom widgets should be placed inside the {HOME}/scripts/widgets directory and 
 * can be named FooWidget.php. All widgets must implement this interface.
 * 
 * Custom Widgets can be invoked from view code as follows:
 *    // Create an instance of the widget (will transparently call __construct)
 *    $myFooWidget = $app->createWidget('FooWidget',array(..config..),true) // true --> custom
 * 
 * <!-- (all widgets, framework or custom): display widget contents -->
 * <span><?php echo $myFooWidget->render()?></span>
 * 
 * @author ahart
 * 
 */
interface Org_Apache_Oodt_Balance_Interfaces_IApplicationWidget {
	
	public function __construct($options = array());
	
	/**
	 * Build the HTML output that constitutes the widget.
	 * 
	 * @param boolean $bEcho (default = true) If true, the function should
	 *        echo the contents directly. If false, the contents should be
	 *        returned as a string.
	 */
	public function render($bEcho = true);
	
}
