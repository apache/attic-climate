<?php
$activeTab = 'tools';
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
</script>
	<h2>Welcome to RCMES Tools...</h2>
	<h3>About the RCMES Toolkit...</h3>
<p>The Regional Climate Model Evaluation Toolkit (RCMET) is a comprehensive suite of algorithms,
    libraries, and interfaces designed to standardize and streamline the process of interacting with 
    large quantities of observational data (such as is provided by the <a href="<?php echo SITE_ROOT?>/data/rcmed">RCMED</a>) 
    and conducting regional climate model evaluations. </p>

<p>RCMET consists of a Python library for common model evaluation tasks (e.g.: area averaging, regridding, bias calculation)
   as well as a set of user-friendly interfaces for quickly configuring a large-scale regional model evaluation task. </p>

   <p>Users can interact with the RCMET either by including the Python library directly in their code, or by way of the 
    flexible, RESTful Application Programmer Interface (API). The API, also implemented in Python, allows RCMET users to
    integrate the capabilities of the toolkit into their workflow regardless of language and environment, provided they
    have the ability to make HTTP requests.</p>

<h3>At a Glance...</h3>
   <p>RCMET is usually packaged as a Virtual Machine image that contains all of the dependencies, libraries, and 
      configuration interfaces needed to quickly get up and running with a model evaluation experiment. The virtual 
      machine packaging dramatically reduces the time required to obtain the necessary environment for experimenting
      with RCMET tools and RCMED data.

   <img class="figure" src="<?php echo SITE_ROOT?>/static/img/figures/rcmet-flow.png" style="width:320px;float:right;"/>
	
<h3>How the RCMET is Organized...</h3>
   <p>The RCMET supports a wide variety of use cases, from simple non-connected tasks like performing re-gridding of 
    model and observational data, to a complete model evaluation workflow from configuration to output plots. Internally
    the RCMET is comprised of a set of components, mostly written in Python, that perform various tasks and can be strung
    together to create more complicated processing workflows. For the common model evaluation use case, a web-based
    interface helps guide users through the entire process of selecting model and observational data to compare, 
    choosing and configuring the processing steps, and customizing the output. </p>
   <p>RCMET is designed to work transparently with the RCMED, making it even easier to work with the large volumes
    of observational data required for full-scale model evaluation tasks. Furthermore, results can be generated in

    <img class="figure" src="<?php echo SITE_ROOT?>/static/img/figures/rcmet-output.png" style="width:320px;float:left;margin-left:0px;margin-right:30px;margin-top:15px;"/>

    a number of output formats, from serialized Python arrays that can be directly injected into Python code, to
    colorful and detailed plots that provide immediate visual feedback on the results of the model evaluation run (see image left).</p>

    <p>For more information on RCMET, please <a href="<?php echo SITE_ROOT?>/about/contact">contact us</a>!</p>
