<?php
/*** Display all figures for specified publication ***/

// Get specified publication name
$publication = App::Get()->request->segments[0];

if ( $publication != null || $publication != '' ) {

	// Get files from specified publication directory
	$gallery_url = SITE_ROOT . '/static/resources/papers/'. $publication . '/';
	$gallery_dir = HOME . '/static/resources/papers/' . $publication . '/';
	$metadata_file 	= $gallery_dir . 'pubs.met';

	/********************************************************************
	 * PREPARATION
	 ********************************************************************/
	// Read in the contents of the publication metadata file
	$pubs = unserialize(file_get_contents($metadata_file));
	$gallery_files = array();
	foreach ($pubs as $pub) {
		if (!isset($gallery_files[$pub['file']])) { $gallery_files[$pub['file']] = array(); }
		$gallery_files[$pub['file']] = $pub;
	}
	ksort($gallery_files);
}
?>

<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />

    <!-- Arquivos utilizados pelo jQuery lightBox plugin -->
    <script type="text/javascript" src="<?php echo SITE_ROOT ?>/static/js/jquery.lightbox-0.5.js"></script>
    <link rel="stylesheet" type="text/css" href="<?php echo SITE_ROOT ?>/static/css/jquery.lightbox-0.5.css" media="screen" />
    <!-- / fim dos arquivos utilizados pelo jQuery lightBox plugin -->
    
    <!-- Ativando o jQuery lightBox plugin -->
    <script type="text/javascript">
    $(function() {
        $('#gallery a').lightBox();
    });
    </script>
   	<style type="text/css">
	/* jQuery lightBox plugin - Gallery style */
	#gallery {
		background-color: #444;
		padding: 10px;
		width: auto;
	}
	#gallery ul { list-style: none; }
	#gallery ul li { display: inline-block; }
	#gallery ul img {
		border: 5px solid #3e3e3e;
		border-width: 5px 5px 20px;
	}
	#gallery ul a:hover img {
		border: 5px solid #000;
		border-width: 5px 5px 20px;
	}
	#gallery ul a { color: #A2A2A2; }
	#gallery ul img {
		display: block;
		height: 110px;
	    margin-left: auto;
	    margin-right: auto;
	    width: 90px;
	}
	#gallery div.figure_frame {
		width: 165px;
		text-align: center;
	}
	</style>
</head>

<body>
<div class="breadcrumbs">
    <a href="<?php echo SITE_ROOT?>/">Home</a> &nbsp;&rarr;&nbsp;
	<a href="<?php echo SITE_ROOT?>/publications">Publications</a> &nbsp;&rarr;&nbsp;
	<a href="<?php echo SITE_ROOT?>/publications/papers">Papers</a> &nbsp;&rarr;&nbsp;
    <?php echo $publication?>
</div>
<?php if ( $metadata_file != null ) : ?>
<h2><?php echo $publication?></h2> <br />
<div id="gallery">
	<ul>
	<?php 
		foreach ($gallery_files as $file) {
					echo '<li>
					<div class="figure_frame">
		   				<a href="' . $gallery_url . $file['file'] . '"  title="' . $file['caption'] . '">
		                	<img src="' . $gallery_url . $file['file'] . '" alt="' . $file['title'] . '" />
		            	</a>
	            		<div>
		            		<a href="' . $gallery_url . $file['file'] . '"  title="' . $file['caption'] . '">
			                	<p>' . $file['title'] . '</p>
			            	</a>
		            	</div>
	            	</div>
	        	</li>';
		}
	?>
    </ul>
</div>
<?php else : ?><br />
<h4>No directory named <?php echo $publication?> exists.</h4> <br />
<?php endif; ?>
</body>
</html>