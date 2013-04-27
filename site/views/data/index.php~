<?php
$activeTab = 'data';

require_once("Org/Apache/Oodt/Balance/Providers/Data/MySqlDataProvider.class.php");
$app = App::Get();

$wrmDatabase = new Org_Apache_Oodt_Balance_Providers_Data_MySqlDataProvider();

$wrmDatabase->connect(
	array("server" => $app->settings['wrm_server'],
          "username"   => $app->settings['wrm_user'],
          "password"   => $app->settings['wrm_pass'],
          "database"   => $app->settings['wrm_database']));

$sqlDatasetCount     = "SELECT count(*) as dsCount    FROM `dataset` ";
$sqlParameterCount   = "SELECT count(*) as paramCount FROM `parameter` ";
$sqlParamDatabaseMap = "SELECT `database` from `parameter`";
$sqlDataPointCount   = "SELECT count(*) as dpCount    FROM `dataPoint` ";

$response   = $wrmDatabase->request($sqlDatasetCount,array("format"=>"assoc"));
$dsCount    = $response->data[0]['dsCount'];
$response   = $wrmDatabase->request($sqlParameterCount,array("format"=>"assoc"));
$paramCount = $response->data[0]['paramCount'];
$response   = $wrmDatabase->request($sqlParamDatabaseMap,array("format"=>"assoc"));
$datasets   = $response->data;
$dpCount    = 0;
foreach($datasets as $dataset){
  $databaseName = $dataset['database'];
  $wrmDpDatabase = new Org_Apache_Oodt_Balance_Providers_Data_MySqlDataProvider();
  $wrmDpDatabase->connect(
        array("server"     => $app->settings['wrm_server'],
          "username"   => $app->settings['wrm_user'],
          "password"   => $app->settings['wrm_pass'],
          "database"   => $databaseName));

  $response   = $wrmDpDatabase->request($sqlDataPointCount,array("format"=>"assoc"));
  $dpCount = $dpCount + ((int)$response->data[0]['dpCount']);
}


// Format the data point count so that it is concise
$labels = array("K","M","B","T");
$counts = array(1000,1000000,1000000000,1000000000000);
$temp   = 0;
for ($i = 0; $i < count($labels); $i++) {
	$temp = $dpCount / $counts[$i];
	if ($temp < 1000) {
		$dpCount = round($temp,1);
		$dpLabel = $labels[$i];
		break;
	}
}

?>
<script type="text/javascript">
	$(document).ready(function() {
		$.get('<?php echo SITE_ROOT?>/newsfeeds/channel.do',
			{"channel" : "news" },
			function(data) {
				$('#newsfeed').html(data);
				$('.nf_author').addClass('quiet').prepend('Posted by: ');
		});
		

	});
	
	$(document).ready(function() {
	   $.get('<?php echo SITE_ROOT?>/prodrss/rss.do', 
	      {"channel" : "ALL",
		   "perPage" : 10},
	      function(data){
	         $('#prods').html(data);
	      }
	   );
	});
</script>
	<h2>Welcome to RCMES Data...</h2>
	<h3>About the RCMES Database...</h3>
	<p>The Regional Climate Model Evaluation Database (RCMED) is a scalable data store containing
	tens of billions of observational measurements collected over several decades by a variety 
	of agencies including <a href="http://nasa.gov">NASA</a>, the <a href="http://www.ecmwf.int/">ECMWF</a>, and others. What makes the RCMED 
	special is the fact that all of the data is stored in a common format, making it extremely easy to request
	exactly the data you need to compare against a regional climate model. 
	</p>
	
	
	<h3>At a Glance...</h3>
	<div id="stats" class="clearfix">
		<div class="stat">
			<img src="<?php echo SITE_ROOT?>/static/img/paper-200.jpg" alt="image of bleached paper"/>
			<div class="number"><?php echo $dsCount?></div>
			<p><a href="<?php echo SITE_ROOT?>/rcmed/datasets/">Datasets</a></p>
		</div>
		<div class="stat">
			<img src="<?php echo SITE_ROOT?>/static/img/paper-200.jpg" alt="image of bleached paper"/>
			<div class="number"><?php echo $paramCount?></div>
			<p><a href="<?php echo SITE_ROOT?>/rcmed/parameters">Parameters</a></p>
		</div>
		<div class="stat">
			<img src="<?php echo SITE_ROOT?>/static/img/paper-200.jpg" alt="image of bleached paper"/>
			<div class="number"><?php echo $dpCount . $dpLabel?></div>
			<p><a href="<?php echo SITE_ROOT?>/browse-rcmed/">Data Points</a></p>
		</div>
	</div>
	
	<h3>How the RCMED is Organized...</h3>
	<p>The RCMED is a homogenized collection of billions (and growing) of observational climate measurements
	taken over several decades. The data are made available via a RESTful HTTP web interface which provides a single
	point of entry to the entire collection, making it easy to write scripts in any language that can make an HTTP
	request.</p>
	<p>The RCMED data model uses the notion that every individual observation is a <code>DataPoint</code>, a measurement
	   of a particular physical <code>Parameter</code> (e.g.: surface air temperature) that is anchored in three
	   dimensional space and time. Data points are further linked to the <code>Granule</code> (file) from which they were
	   originally extracted, and the <code>Dataset</code> to which the file belonged. The following diagram provides
	   a visual picture of the RCMED data model:</p>
	   
	   <img class="figure" src="<?php echo SITE_ROOT?>/static/img/figures/rcmed-data-model.png"/>
	   <br/>
	   <p class="caption">RCMED data model diagram</p>
	   
	<h3>Extraction...</h3>
	<p>The RCMED eliminates a serious roadblock to performing model-to-observational data comparisons
	   efficiently: namely the need to first identify and acquire the necessary observational data from
	   its various upstream sources, and then to understand its format and metadata in order to write a parser
	   that will extract the desired data into a usable form. </p>
	<p>The RCMED provides data on <?php echo $paramCount?> physical <a href="<?php echo SITE_ROOT?>/rcmed/parameters">parameters</a>
	   from <?php echo $dsCount?> distinct <a href="<?php echo SITE_ROOT?>/rcmed/datasets">datasets</a>. These
	   data have been extracted from their original upstream files, sorted by parameter, tagged with the appropriate
	   metadata, and then stored and indexed by a master database for querying. The following diagram visualizes the RCMED extraction process:
	   </p>
	   
	   <img class="figure" src="<?php echo SITE_ROOT?>/static/img/figures/rcmed-extraction-process.png" style="width:600px;margin-left:2px;"/>
	   <br/>
	   <p class="caption" style="margin-left:2px;">High-level overview of the RCMED extraction process</p>
	
	<h3>Querying the RCMED...</h3>
	<p>The RCMED provides a RESTful HTTP query interface that allows clients to quickly specify precisely
	   the data they wish to obtain. Because the query interface is implemented over HTTP, clients are 
	   free to interact with RCMED using their language of choice, provided it supports HTTP requests. The
	   diagram below depicts a selection of the use cases supported by the RCMED query interface:
	   </p>
	   
	   <img class="figure" src="<?php echo SITE_ROOT?>/static/img/figures/rcmed-query-api.png" style="width:600px;margin-left:2px;"/>
	   <br/>
	   <p class="caption" style="margin-left:2px;">High-level overview of interacting with RCMED via the query interface</p>  
	

