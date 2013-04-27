<?php
// Get the global application object
$app = $GLOBALS['app'];

// Connect to the WRM MySql catalog
$provider = $app->GetDataProvider('MySqlDataProvider');
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
	$tableWidget = $app->CreateWidget('HtmlTableWidget',array());
	$tableWidget->addColumn('Dataset Name');
	$tableWidget->addColumn('Abbreviation');
	$tableWidget->addColumn('Description');

	foreach ($response->data as $row) {
		$tableWidget->addRow(array(
			"<a href=\"" . SITE_ROOT . "/datasets/{$row['shortName']}\">{$row['longName']}</a>",
		    	"{$row['shortName']}",
			"{$row['description']} ",
			));
	}
?><div class="breadcrumbs">
<a href="<?php echo SITE_ROOT?>/">Home</a>&nbsp;&rarr;&nbsp;
Dataset Index
</div>
<div class="span-7">&nbsp;</div>
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
<a href="<?php echo SITE_ROOT?>/datasets">Dataset Index</a>&nbsp;&rarr;&nbsp;
<?php echo $info['dsLongName'] . " ({$datasetShortName})"?>
</div>
<div class="span-7">&nbsp;</div>
<div class="span-17 last" id="mainSection">
	<h2 class="larger loud"><?php echo $paramLongName?></h2>
	<h3>Parameters provided by <?php echo $info['dsLongName']?></h3>
	<table>
		<thead><tr><th>Parameter Name</th>
				   <th>Description</th>
				   <th>Id</th>
				   </thead>
		<tbody>
	<?php foreach ($response->data as $param):?>
	  <tr><td><a href="<?php echo SITE_ROOT?>/parameters/<?php echo $param['shortName']?>"><?php echo $param['longName']?></a></td>
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
