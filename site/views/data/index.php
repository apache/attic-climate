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
	<h2>Welcome to RCMES Data...</h2>
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
	
<?php echo Puny::container()->load('data');?>
