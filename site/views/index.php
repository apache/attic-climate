<?php
	$activeTab='home';
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

	<h2>Welcome to RCMES</h2>
	
	<p>The <strong>R</strong>egional
		   <strong>C</strong>limate
		   <strong>M</strong>odel
		   <strong>E</strong>valuation
		   <strong>S</strong>ystem (RCMES) is empowering the regional climate modeling
		   community by dramatically 
		   simplifying the process of acquiring and utilizing observational data in
		   support of regional climate model evaluation. 
		
	<h3>About this Site</h3>
	<p>This site serves as the public face for both the data and tools provided by the Regional Climate 
	Model Evaluation System. RCMES is composed of two complementary subsystems:
	<dl>
		<dt>RCME<strong>D</strong></dt>
		<dd>Regional Climate Model Evaluation Database. A scalable data store containing decades of observational measurements 
		    from NASA and other sources. You can learn more about RCMED by clicking
		    on the <a href="<?php echo SITE_ROOT?>/data/">Data</a> tab above.</dd>
		<dt>RCME<strong>T</strong></dt>
		<dd>Regional Climate Model Evaluation Toolkit. A comprehensive suite of tools for working with the data and performing 
			common model evaluation tasks. You can learn more about RCMET by clicking
			on the <a href="<?php echo SITE_ROOT?>/tools/">Tools</a> tab above.</dd>
	</dl>
	

	<h3>Background</h3>   
	<p>The project is a collaboration between
		the NASA Jet Propulsion Laboratory (JPL) and the UCLA Joint Institute for 
		Regional Earth System Science and Engineering (JIFRESSE). The project initially
		targeted the water resources management community by supporting efforts at model-
		to-observational data comparisons in the California delta region near Sacramento, CA.
		</p>
	<p>Based largely on the success of that project, the scope of the RCMES has been expanded
	   to support the broader international community of regional climate modelers, and to
	   serve as both a resource and platform for performing data-intensive model evaluation
	   experiments. More information about the project can be found by clicking on the 
	   <a href="<?php echo SITE_ROOT?>/about/">About</a> tab, above.</p> 

	<div class="span-10 colborder">
		<h3 id="latest-news" name="news">Latest News...</h3>
		<div id="newsfeed">
			<span class="quiet">Latest News Loading...</span>
		</div>
		
	</div>
	<div class="span-7 colborder">
	    <h2>Latest Data Products...</h2>
	    <br/>
	    <div id="prods">
	       <span class="quiet">Latest Products Loading...</span>
	    </div>
	</div>
