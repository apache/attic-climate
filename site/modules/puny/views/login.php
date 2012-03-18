<?php
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