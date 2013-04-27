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
 * If no specific parameter has been specified, show all in a table
 ******************************************************************************/
if (empty ($app->request->segments[0])):
	
	// Request the parameter information
	$response = $provider->request("SELECT parameter.*,dataset.longName as dsLongName,dataset.shortName as dsShortName "
								  ."FROM `parameter`,`dataset` "
								  ."WHERE dataset.dataset_id=parameter.dataset_id",
							array("format"   => "assoc"));
	
	// Build the table widget
	$tableWidget = $app->CreateWidget('HtmlTableWidget',array());
	$tableWidget->addColumn('Parameter Name');
	$tableWidget->addColumn('Dataset');
	$tableWidget->addColumn('Id');

	foreach ($response->data as $row) {
		$tableWidget->addRow(array(
			"<a href=\"" . SITE_ROOT . "/parameters/{$row['shortName']}\">{$row['longName']}</a>",
		    "{$row['dsLongName']} ({$row['dsShortName']}) ",
			$row['parameter_id']));
	}
?>
<div class="breadcrumbs">
<a href="<?php echo SITE_ROOT?>/">Home</a>&nbsp;&rarr;&nbsp;
Observational/Model Parameter Index
</div>
<div class="span-7">&nbsp;</div>
<div class="span-17 last" id="mainSection">
	<h2 class="larger loud">Observational/Model Parameter Index..</h2>
	<p>
	This page displays information about the observational and model parameters that are 
	currently represented in the database. Click on a parameter name to get 
	detailed information about the current data holdings for that parameter.
	</p>
	<?php echo $tableWidget->render();?>
</div>
<?php 

/******************************************************************************
 * If a parameter has been specified, show the details for that parameter
 ******************************************************************************/
else: 

$paramShortName = $app->request->segments[0];

$response = $provider->request(
	"SELECT  `parameter`.*,`dataset`.`longName` as dsLongName FROM `parameter`,`dataset` "
	. "WHERE `parameter`.`shortName`='{$paramShortName}' "
	. "AND   `dataset`.`dataset_id`=`parameter`.`dataset_id` ",
	array("format"=>"assoc"));
$info     = $response->data[0];

?>
<div class="breadcrumbs">
<a href="<?php echo SITE_ROOT?>/">Home</a>&nbsp;&rarr;&nbsp;
<a href="<?php echo SITE_ROOT?>/parameters">Parameter Index</a>&nbsp;&rarr;&nbsp;
<?php echo $info['longName']?>
</div>
<div class="span-7">&nbsp;</div>
<div class="span-17 last" id="mainSection">
	<h2 class="larger loud"><?php echo $paramShortName?></h2>
	<h3>Provided By Dataset: <?php echo $info['dsLongName']?></h3>
	<table>
	  <tr><th>Long Name</th><td><?php echo $info['longName']?></td></tr>
	  <tr><th>Description</th><td><?php echo $info['description']?></td></tr>
	  <tr><th>Units</th><td><?php echo $info['units']?></td></tr>
	  <tr><th>Reference URL</th><td><?php echo $info['referenceURL']?></td></tr>
	</table>
	<hr/>
	<h4>Search</h4>
	<form method="GET" action="<?php echo SITE_ROOT?>/parameterQuery.do">
		<input type="hidden" name="datasetId"   value="<?php echo $info['dataset_id']?>" label="datasetId"/>
		<input type="hidden" name="parameterId" value="<?php echo $info['parameter_id']?>" label="parameterId"/>
		<table>
		  <tr><td colspan="4">
		  	    Provide a spatial bound to your search. <br/>
		  	    <span class="quiet">Specify a range of lattitude and longitude values for which to retrieve <?php echo $paramLongName?> data</span>
		  	  </td>
		  </tr>
		  <tr><th>Lat. (min):</th><td><input type="text" name="latMin" alt="latMin"/></td>
		  	  <th>Lat. (max):</th><td><input type="text" name="latMax" alt="latMax"/></td>
		  </tr>
		  <tr><th>Lon. (min):</th><td><input type="text" name="lonMin" alt="lonMin"/></td>
		  	  <th>Lon. (max):</th><td><input type="text" name="lonMax" alt="lonMax"/></td>
		  </tr>
		  <tr>
		    <td colspan="4"><hr/>
		    	Provide a temporal bound to your search. <br/>
		    	<span class="quiet">Dates must be expressed in ISO format: (YYYYMMDD<strong>T</strong>HHMM<strong>Z</strong>)</span>
		    </td>
		  </tr>
		  <tr><th>Start Date:</th><td><input type="text" name="timeStart" alt="timeStart"/></td>
		  	  <th>End Date :</th><td><input type="text" name="timeEnd" alt="timeEnd"/></td>
		  </tr>
		  <tr>
		  	<td colspan="4"><input type="submit" value="Search!" label="Search"/></td>
		  </tr>
		</table>
	
	</form>
			

</div>

<?php 
endif;
$provider->disconnect();
