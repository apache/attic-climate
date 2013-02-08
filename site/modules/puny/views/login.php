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

// Parse the Puny config file
$module = App::Get()->loadModule();

App::Get()->response->useHeaderFile(false);
App::Get()->response->useFooterFile(false);

?>
<style type="text/css">
div#login {
	padding:15px;
	width:800px;
	background-color:#dfdfdf;
	margin-bottom:none;
	border:solid 5px #888;
	font-size:1.2em;
	color:#333;
	-webkit-border-radius: 8px;
	-moz-border-radius: 8px;
	border-radius: 8px;
}
form {
	margin:30px;
}
input {
	padding:5px;
	margin-right:5px;
}
label {
	padding-right:5px;
}
</style>
<center>
<p>&nbsp;</p>
<div id="login">
<form method="POST" action="<?php echo $module->moduleRoot?>/login.do">
<label>Username:</label>
<input type="text" alt="username input" name="username"/>
<label>Password:</label>
<input type="password" alt="password input" name="password"/>
<input type="submit" value="Login"/>
</form>
</div>
</center>