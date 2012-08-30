<?php
?>
<!DOCTYPE html>
<html>
<head>
<title>RCMES Client Toolkit</title>

<!-- Base stylesheets -->
<link rel="stylesheet" type="text/css" href="<?php echo SITE_ROOT?>/static/css/style.css"/>

<!-- Base Javascript -->
<script type="text/javascript" type="text/javascript" src="<?php echo SITE_ROOT?>/static/js/jquery-1.8.0.min.js"></script>

<!-- Dynamically Added Stylesheets -->
<!-- STYLESHEETS -->

<!-- Dynamically Added Javascripts -->
<!-- JAVASCRIPTS -->

<!-- Site specific stylesheet overrides -->
<link rel="stylesheet" type="text/css" href="<?php echo SITE_ROOT .'/static/css/site.css'?>"/>

</head>
<body>
<div id="container" class="rounded-br">
<header>
<p>&nbsp;</p>
<div id="badge-bg" class="rounded-br">
	<div id="badge-bg-inner" class="rounded-br">
		<a href="<?php echo SITE_ROOT?>/">
		<img src="<?php echo SITE_ROOT?>/static/img/wrm-badge.png"/>
		</a>
		<br/><br/>
		<h1>Regional Climate Model Evaluation System</h1>
	</div>
</div>

</header>
<div id="content" role="main">
<h1 class="bigger">Regional Climate Model Evaluation Toolkit (RCMET)
	<span style="font-size:0.62em;color:#686;">beta</span></h1>
<hr/>
<?php echo App::Get()->GetMessages(); ?>
