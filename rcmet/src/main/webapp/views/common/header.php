<?php
?>
<!DOCTYPE html>
<html>
<head>
<title>RCMES Client Toolkit</title>

<!-- Base stylesheets -->
<link rel="stylesheet" type="text/css" href="<?php echo SITE_ROOT?>/static/bootstrap/css/bootstrap.min.css"/>
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
<header>
    <p>&nbsp;</p>
</header>
<div class="container">
    <div id="content" role="main">
        <h1>Regional Climate Model Evaluation Toolkit (RCMET)
	        <span style="font-size:0.50em;color:#686;">beta</span>
	    </h1>
	    <div class="page">
            <?php echo App::Get()->GetMessages(); ?>
