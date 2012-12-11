<?php
// Set the tab
$activeTab = 'data';

// Get the global application object
$app = App::Get();

// Connect to the WRM MySql catalog
require_once("Org/Apache/Oodt/Balance/Providers/Data/MySqlDataProvider.class.php");
$provider = new Org_Apache_Oodt_Balance_Providers_Data_MySqlDataProvider();
$provider->connect(array(
	"username" => $app->settings['wrm_user'],
	"password" => $app->settings['wrm_pass'],
	"server"   => $app->settings['wrm_server'],
	"database" => $app->settings['wrm_database']));

/******************************************************************************
 * If no specific dataset has been specified, show all in a table
 ******************************************************************************/
if (empty ($app->request->segments[0])):
	
	// Request the parameter information
/*
	$response = $provider->request("SELECT dataset.*,count(`parameter`.`parameter_id`) as numParameters "
								  ."FROM `parameter`,`dataset` "
								  ."WHERE dataset.dataset_id=parameter.dataset_id",
							array("format"   => "assoc"));
*/
	$response = $provider->request("SELECT dataset.*  FROM 
`dataset`  WHERE 1",array("format" => "assoc"));	
	// Build the table widget
	require_once(HOME . '/scripts/widgets/HtmlTableWidget.php');
	$tableWidget = new HtmlTableWidget();
	$tableWidget->addColumn('Dataset Name');
	$tableWidget->addColumn('Abbreviation');
	$tableWidget->addColumn('Description');
	$tableWidget->addColumn('Dataset ID');

	foreach ($response->data as $row) {
		$tableWidget->addRow(array(
			"<a href=\"" . SITE_ROOT . "/rcmed/datasets/{$row['shortName']}\">{$row['longName']}</a>",
		    	"{$row['shortName']}",
			"{$row['description']} ",
			"{$row['dataset_id']} ",
			));
	}
?><div class="breadcrumbs">
<a href="<?php echo SITE_ROOT?>/">Home</a>&nbsp;&rarr;&nbsp;
<a href="<?php echo SITE_ROOT?>/data">Data</a>&nbsp;&rarr;&nbsp;
Dataset Index
</div>
<div class="span-17 last" id="mainSection">
	<h2 class="larger loud">Dataset Index..</h2>
	<p>
	This page displays information about the datasets that are 
	currently represented in the database. Click on a dataset name to get 
	detailed information about the current parameters with datapoints in the database.
	</p>
	<?php echo $tableWidget->render();?>
</div>
<?php 

/******************************************************************************
 * If a parameter has been specified, show the details for that parameter
 ******************************************************************************/
else: 

$datasetShortName = $app->request->segments[0];

$response = $provider->request(
	"SELECT  `parameter`.*,`dataset`.`longName` as dsLongName FROM `parameter`,`dataset` "
	. "WHERE `dataset`.`shortName`='{$datasetShortName}' "
	. "AND   `dataset`.`dataset_id`=`parameter`.`dataset_id` ",
	array("format"=>"assoc"));
$info     = $response->data[0];

?>
<div class="breadcrumbs">
<a href="<?php echo SITE_ROOT?>/">Home</a>&nbsp;&rarr;&nbsp;
<a href="<?php echo SITE_ROOT?>/data/">Data</a>&nbsp;&rarr;&nbsp;
<a href="<?php echo SITE_ROOT?>/rcmed/datasets">Dataset Index</a>&nbsp;&rarr;&nbsp;
<?php echo $info['dsLongName'] . " ({$datasetShortName})"?>
</div>
<div class="span-7">&nbsp;</div>
<div class="span-17 last" id="mainSection">
	<h2 class="larger loud">Dataset Index</h2>
	<h3>Parameters for <?php echo $info['dsLongName']?></h3>
	<table>
		<thead><tr><th>Parameter Name</th>
				   <th>Description</th>
				   <th>Id</th>
				   </thead>
		<tbody>
	<?php foreach ($response->data as $param):?>
	  <tr><td><a href="<?php echo SITE_ROOT?>/rcmed/parameters/<?php echo $param['shortName']?>"><?php echo $param['longName']?></a></td>
	  	  <td><?php echo $param['description']?></td>
	  	  <td><?php echo $param['parameter_id']?></td></tr>
	<?php endforeach ?>
		</tbody>
	</table>
	<hr/>

</div>

<?php 
endif;
$provider->disconnect();
