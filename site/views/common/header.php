<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
<html lang="en">
<head>
	<meta http-equiv="content-type" content="text/html; charset=utf-8">
	<title>Regional Climate Model Evaluation System</title>
	
	<link rel="stylesheet" href="<?php echo SITE_ROOT ?>/global/static/css/blueprint/screen.css"/>
	<!--[if lt IE 8]><link rel="stylesheet" href="<?php echo SITE_ROOT ?>/global/static/css/blueprint/ie.css" type="text/css" media="screen, projection"><![endif]-->
	<link rel="stylesheet" href="<?php echo SITE_ROOT ?>/static/css/wrm.css" type="text/css">
	<link href="<?php echo SITE_ROOT ?>/static/css/main.css" rel="stylesheet" type="text/css" />
	<link href="<?php echo SITE_ROOT ?>/static/css/print.css" rel="stylesheet" type="text/css" media="print"/>
	<!-- Dynamically added stylesheets appear below -->
	<!-- STYLESHEETS -->
	
	<script type="text/javascript" src="<?php echo SITE_ROOT?>/static/js/jquery-1.7.1.min.js"></script>
	<script type="text/javascript" src="<?php echo SITE_ROOT?>/static/js/jquery.hoverIntent.minified.js"></script>
        <script type="text/javascript" src="<?php echo SITE_ROOT?>/static/js/script.js"></script>
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
    <div id="logo">
        <a href="<?php echo SITE_ROOT . '/'?>">
            <img id="rcmes-logo" src="<?php echo SITE_ROOT?>/static/img/rcmes-logo.png" alt="RCMES Logo"/>
        </a>
    </div>
</div>
<!-- end #wrapper_top -->

<div id="page" class="container">
	<div class="header">
		<h1>Regional Climate Model Evaluation System</h1>

<!--
		<h2>Connecting Observational Data to Regional Climate Model Evaluation</h2>
-->
	</div>

<!-- 
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
		  height: 200,
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
-->

	<div id="content-container" class="clearfix">

	    <div id="site-menu" class="clearfix">
	        <ul>
		    <li class="<?php echo ($activeTab == 'about') ? 'active' : '';?>">
                        <a href="<?php echo SITE_ROOT . '/about/'?>">ABOUT</a>
                        <ul id="about">
                            <li><a href="<?php echo SITE_ROOT . '/about/overview'?>">Overview</a></li>
<!--                        <li><a href="<?php echo SITE_ROOT . '/about/project-history'?>">Project History</a></li>-->
                            <li><a href="<?php echo SITE_ROOT . '/about/team'?>">Team</a></li>
                            <li><a href="<?php echo SITE_ROOT . '/about/contact'?>">Contact</a></li>
                        </ul>
                    </li>
		    <li class="<?php echo ($activeTab == 'collaborations') ? 'active' : '';?>">
                        <a href="<?php echo SITE_ROOT . '/collaborations/'?>">COLLABORATIONS</a>
                        <ul id="collab">
                            <li><a href="<?php echo SITE_ROOT . '/collaborations/cordex'?>">CORDEX</a></li>
                            <li><a href="<?php echo SITE_ROOT . '/collaborations/exarch'?>">Ex-Arch</a></li>
                            <li><a href="<?php echo SITE_ROOT . '/collaborations/narccap'?>">NARCCAP</a></li>
                        </ul>
                    </li>
		    <li class="<?php echo ($activeTab == 'publications') ? 'active' : '';?>">
                        <a href="<?php echo SITE_ROOT . '/publications/'?>">PUBLICATIONS</a>
                        <ul id="pubs">
                            <li><a href="<?php echo SITE_ROOT . '/publications/papers'?>">Papers</a></li>
                            <li><a href="<?php echo SITE_ROOT . '/publications/posters'?>">Posters</a></li>
                            <li><a href="<?php echo SITE_ROOT . '/publications/presentations'?>">Presentations</a></li>
                            <li><a href="<?php echo SITE_ROOT . '/publications/reports'?>">Reports</a></li>
                        </ul>
                    </li>
		    <li class="<?php echo ($activeTab == 'data') ? 'active' : '';?>">
                        <a href="<?php echo SITE_ROOT . '/data/'?>">DATA</a>
                        <ul id="data">
                            <li><a href="<?php echo SITE_ROOT . '/data/'?>">Overview</a></li>
                            <li><a href="<?php echo SITE_ROOT . '/rcmed/datasets/'?>">Datasets</a></li>
                            <li><a href="<?php echo SITE_ROOT . '/rcmed/parameters'?>">Parameters</a></li>
                            <li>Data Points
                                <!--  NEED TO FIND THE RIGHT PAGE FOR THIS LINK
                                <a href="<?php echo SITE_ROOT . '/data/data-points'?>">Data Points</a>
                                -->
                            </li>
                        </ul>
                    </li>
		    <li class="<?php echo ($activeTab == 'training') ? 'active' : '';?>">
                        <a href="<?php echo SITE_ROOT . '/training/'?>">TRAINING</a>
                        <ul id="training">
                            <li><a href="<?php echo SITE_ROOT . '/training/rcmet-overview'?>">RCMET Overview</a></li>
                            <li>RCMET User Guide</li>
                            <!--<li><a href="<?php echo SITE_ROOT . '/training/rcmet-user-guide'?>">RCMET User Guide</a></li>-->
                            <li><a href="<?php echo SITE_ROOT . '/training/downloads'?>">RCMET Downloads</a></li>
                            <li><a href="<?php echo SITE_ROOT . '/training/rcmed-api-spec'?>">RCMED API Spec</a></li>
                            <li>Videos</li>
                            <!--<li><a href="<?php echo SITE_ROOT . '/training/videos'?>">Videos</a></li>-->
                        </ul>
                    </li>
		    <li class="<?php echo ($activeTab == 'links') ? 'active' : '';?>">
                        <a href="<?php echo SITE_ROOT . '/links'?>">LINKS</a>
                    </li>
		</ul>
	    </div>
	<div><a name="bruno"></a></div>
		<div id="content">
		
		
