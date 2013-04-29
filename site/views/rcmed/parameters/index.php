<?php 

// Set the tab
$activeTab = 'data';

// Get the global application object
$app = App::Get();

// Connect to the RCMES Postgres catalog
require_once("Org/Apache/Oodt/Balance/Providers/Data/PostgresDataProvider.class.php");
$provider = new Org_Apache_Oodt_Balance_Providers_Data_PostgresDataProvider();
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
	$response = $provider->request("SELECT parameter.shortname, parameter.longname, parameter.parameter_id, parameter.units, parameter.start_date, parameter.end_date"
								.",dataset.longname as dslongname,dataset.shortname as dsshortname "
								."FROM parameter,dataset "
								."WHERE dataset.dataset_id=parameter.dataset_id order by parameter_id;",
								array("format"   => "assoc"));
	// Build the table widget
	require_once(HOME . '/scripts/widgets/HtmlTableWidget.php');
	$tableWidget = new HtmlTableWidget();
	$tableWidget->addColumn('Id');
	$tableWidget->addColumn('Parameter Name');
	$tableWidget->addColumn('Dataset');
	$tableWidget->addColumn('Unit');
	$tableWidget->addColumn('Start date');
	$tableWidget->addColumn('End date');

	foreach ($response->data as $row) {
		$tableWidget->addRow(array(
			$row['parameter_id'],
			"<a href=\"" . SITE_ROOT . "/rcmed/parameters/{$row['shortname']}\">{$row['longname']}</a>",
		        "{$row['dslongname']} ({$row['dsshortname']})",
			$row['units'],
			$row['start_date'],
			$row['end_date']
		));
	}
?>

<div class="breadcrumbs">
<a href="<?php echo SITE_ROOT?>/">Home</a>&nbsp;&rarr;&nbsp;
<a href="<?php echo SITE_ROOT?>/data">Data</a>&nbsp;&rarr;&nbsp;
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
	"SELECT  parameter.longname, parameter.description, parameter.units, parameter.referenceurl, parameter.dataset_id, parameter.parameter_id"
	.",dataset.longname as dslongname "
	."FROM parameter,dataset "
	. "WHERE parameter.shortname='{$paramShortName}' "
	. "AND   dataset.dataset_id=parameter.dataset_id ",
	array("format"=>"assoc"));
$info     = $response->data[0];

?>
<div class="breadcrumbs">
<a href="<?php echo SITE_ROOT?>/">Home</a>&nbsp;&rarr;&nbsp;
<a href="<?php echo SITE_ROOT?>/data">Data</a>&nbsp;&rarr;&nbsp;
<a href="<?php echo SITE_ROOT?>/rcmed/parameters">Parameter Index</a>&nbsp;&rarr;&nbsp;
<?php echo $info['longname'] ?>
</div>
<div class="span-7">&nbsp;</div>
<div class="span-17 last" id="mainSection">
	<h2 class="larger loud"><?php echo $paramShortName?></h2>
	<h3>Provided By Dataset: <?php echo $info['dslongname']?></h3>
	<table class="vertical" style="width:100%;">
	  <tr><th>Long Name</th><td><?php echo $info['longname'] ?></td></tr>
	  <tr><th>Description</th><td><?php echo $info['description']?></td></tr>
	  <tr><th>Units</th><td><?php echo $info['units'] ?></td></tr>
	  <tr><th>Reference URL</th><td><?php echo $info['referenceurl']?></td></tr>
	</table>

	<h3>Search for Data...</h3>
	<form method="GET" action="<?php echo SITE_ROOT?>/parameterQuery.do">
		<input type="hidden" name="datasetId"   value="<?php echo $info['dataset_id'] ?>" label="datasetId"/>
		<input type="hidden" name="parameterId" value="<?php echo $info['parameter_id'] ?>" label="parameterId"/>
		<table class="vertical">
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
		    <td colspan="4"><br/>
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
