<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html lang="en">
<head>
	<meta http-equiv="content-type" content="text/html; charset=utf-8">
	<title>WRM - Regional Climate Model Evaluation Database</title>
	
	<link rel="stylesheet" href="<?php echo SITE_ROOT ?>/global/static/css/blueprint/screen.css"/>
	<!--[if lt IE 8]><link rel="stylesheet" href="<?php echo SITE_ROOT ?>/global/static/css/blueprint/ie.css" type="text/css" media="screen, projection"><![endif]-->
	<link rel="stylesheet" href="<?php echo SITE_ROOT ?>/static/css/wrm.css" type="text/css">
	<link href="<?php echo SITE_ROOT ?>/static/css/main.css" rel="stylesheet" type="text/css" />
	<link href="<?php echo SITE_ROOT ?>/static/css/print.css" rel="stylesheet" type="text/css" media="print"/>
	<!-- Dynamically added stylesheets appear below -->
	<!-- STYLESHEETS -->
	
	<script type="text/javascript" src="<?php echo SITE_ROOT?>/static/js/jquery-1.4.2.min.js"></script>
	<!-- Dynamically added javascripts appear below -->
	<!-- JAVASCRIPTS -->
	
	<!-- Begin RSS feed -->
	<link rel="alternate" type="application/rss+xml" title="News and features stories" href="http://www.jpl.nasa.gov/multimedia/rss/news.xml"/>
	<link rel="alternate" type="application/rss+xml" title="Podcasts for audio and video" href="http://www.jpl.nasa.gov/multimedia/podcast/podfeed.xml"/>
	<link rel="alternate" type="application/rss+xml" title="Video in High Definition" href="http://www.jpl.nasa.gov/multimedia/rss/podfeed-hd.xml"/>
	<link rel="alternate" type="application/rss+xml" title="JPL Blog" href="http://blogs.jpl.nasa.gov/?feed=rss2"/>
	<link rel="alternate" type="application/rss+xml" title="Slide shows and interactive features" href="http://www.jpl.nasa.gov/multimedia/rss/slideshows.xml"/>
	<link rel="shortcut icon" href="favicon.ico" />
	<!-- End RSS feed -->
</head>
<body>
<div id="wrapper_top">
	<?php include HOME.'/views/common/headerNoNav.php'; ?>
</div>
<!-- end #wrapper_top -->

<div id="page" class="container">
	<div class="header">
		<h1>Regional Climate Model Evaluation System</h1>
		<h2>Connecting Observational Data to Regional Climate Model Evaluation</h2>
	</div>
	<div id="left-nav">
		<img id="rcmes-logo" src="<?php echo SITE_ROOT?>/static/img/rcmes-logo.png" alt="RCMES Logo"/>
		<br/><br/>
		<h4 style="padding-left:20px;">
		<a href="http://twitter.com/intent/user?screen_name=rcmes">
			<img src="<?php echo SITE_ROOT?>/static/img/Twitter_48x48.png" style="width:32px;float:left;margin-left:-15px;margin-right:5px;"/>
		</a>RCMES on Twitter...</h4>
		<script src="http://widgets.twimg.com/j/2/widget.js"></script>
		<script>
		new TWTR.Widget({
		  version: 2,
		  type: 'profile',
		  rpp: 12,
		  interval: 30000,
		  width: 265,
		  height: 400,
		  theme: {
		    shell: {
		      background: '#cccccc',
		      color: '#6b676b'
		    },
		    tweets: {
		      background: '#aaaaaa',
		      color: '#424242',
		      links: '#48693a'
		    }
		  },
		  features: {
		    scrollbar: false,
		    loop: false,
		    live: true,
		    behavior: 'all'
		  }
		}).render().setUser('rcmes').start();
		</script>
	</div>
	<div id="content-container" class="clearfix">
		<div id="site-menu" class="clearfix">
			<ul>
				<li class="<?php echo ($activeTab == 'home') ? 'active' : '';?>"><a href="<?php echo SITE_ROOT . '/'?>">Home</a></li>
				<li class="<?php echo ($activeTab == 'data') ? 'active' : '';?>"><a href="<?php echo SITE_ROOT . '/data/'?>">Data</a></li>
				<li class="<?php echo ($activeTab == 'tools') ? 'active' : '';?>"><a href="<?php echo SITE_ROOT . '/tools/'?>">Tools</a></li>
				<li class="<?php echo ($activeTab == 'resources') ? 'active' : '';?>"><a href="<?php echo SITE_ROOT . '/resources/'?>">Resources</a></li>
				<li class="<?php echo ($activeTab == 'about') ? 'active' : '';?>"><a href="<?php echo SITE_ROOT . '/about/'?>">About</a></li>
			</ul>
		</div>
		<div><a name="bruno"></a></div>
		<div id="content">
		
		
