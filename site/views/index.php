<?php
$activeTab='home';

//App::Get()->response->addJavascript('static/js/slides.jquery.js');
App::Get()->response->addJavascript('https://raw.github.com/twitter/bootstrap/master/js/bootstrap-transition.js');
App::Get()->response->addJavascript('https://raw.github.com/twitter/bootstrap/master/js/bootstrap-carousel.js');
App::Get()->response->addStylesheet('http://twitter.github.com/bootstrap/assets/css/bootstrap.css');


?>
<script type="text/javascript">	
  $(document).ready(function() {
		      //$('#slides').slides();
		      $('.carousel').carousel();
  });
</script>
<style type="text/css">
body {
  background-color:#213452;
  font-size:16px;

}

h1 { 
font-size:30px;
  line-height:18px;
}

#left {
background-color:#eee;
width:280px;
border-right:solid 1px #ccc;
padding:5px;
min-height:320px;
float:left;
}

#right {

width:630px;
margin-left:320px;
}
div.header {
  margin-top:0px;
}

#slides {

}
</style>
<div id="left">
<h2 style="margin-top:10px;">Welcome!</h2>
<?php echo Puny::Container()->load('home.blurb');?>
</div>
<div id="right">
    <div id="carousel" class="carousel">
      <!-- Carousel items -->
      <div class="carousel-inner">

      <div class="active item">
        <a href="<?php echo SITE_ROOT?>/about/overview">
        <img src="<?php echo SITE_ROOT?>/static/img/slides/rcmes-slide-02.jpg"/>
        </a>
        <div class="carousel-caption">
          <h4>Regional Decision Making</h4>
          <p>Observational data from RCMES helps analyze models used by public policy makers at
   local, state, and national levels.
   &nbsp;<a href="<?php echo SITE_ROOT?>/about/project-history">Learn more...</a>
</p>
        </div>
      </div>

   <div class="item">
        <a href="<?php echo SITE_ROOT?>/about/overview">
        <img src="<?php echo SITE_ROOT?>/static/img/slides/rcmes-slide-01.jpg"/>
        </a>
        <div class="carousel-caption">
          <h4>Comparing Models to Observations</h4>
   <p>RCMES provides uniform access to billions of observational measurements, as well as a robust
   set of tools for performing common analysis tasks using the data...
  &nbsp;<a href="<?php echo SITE_ROOT?>/about/overview">Learn more...</a>
</p>
        </div>
      </div>


      <div class="item">
        <a href="<?php echo SITE_ROOT?>/collaborations/exarch">
        <img src="<?php echo SITE_ROOT?>/static/img/slides/rcmes-slide-03.jpg"/>
        </a>
        <div class="carousel-caption">
          <h4>Collaborations with ExArch</h4>
          <p>RCMES is developing connections with the multinational, multi-institutional ExArch project
             to faciliate broader access to RCMES data.
  &nbsp;<a href="<?php echo SITE_ROOT?>/collaborations/exarch">Learn more...</a>
</p>
        </div>
     </div>

 
     <div class="item">
        <a href="<?php echo SITE_ROOT?>/collaborations/cordex">
        <img src="<?php echo SITE_ROOT?>/static/img/slides/rcmes-slide-04.jpg"/>
        </a>
  <div class="carousel-caption">
          <h4>Collaborations with CORDEX/IPCC</h4>
   <p>RCMES is supporting the efforts of the Intergovernmental Panel on Climate Change and the 
      COordinated Regional Downscaling EXperiment. 
   &nbsp;<a href="<?php echo SITE_ROOT?>/collaborations/cordex">Learn more...</a>
   </p>
        </div>
     </div>

<div class="item">
  <a href="<?php echo SITE_ROOT?>/collaborations/narccap">
  <img src="<?php echo SITE_ROOT?>/static/img/slides/rcmes-slide-05.jpg"/>
  </a>
  <div class="carousel-caption">
          <h4>Collaborations with NARCCAP/NCA</h4>
   <p>RCMES is supporting the efforts of the North American Regional Climate Change Assessment Program
      by providing access to data and tools for climate model validation.
      &nbsp;<a href="<?php echo SITE_ROOT?>/collaborations/narccap">Learn More...</a>
      </p>
   </div>
     </div>




    </div>
    <!-- Carousel nav -->
    <a class="carousel-control left" href="#carousel" data-slide="prev">&lsaquo;</a>
    <a class="carousel-control right" href="#carousel" data-slide="next">&rsaquo;</a>
</div>
<!--
<div id="slides">
  <div class="slides_container">
    <div>
     <img src="<?php echo SITE_ROOT?>/static/img/slides/rcmes-slide1.png" style="width:570px;height:270px;padding:5px;"/>
    </div>
    <div>
     <img src="<?php echo SITE_ROOT?>/static/img/slides/rcmes-slide2.png" style="width:570px;height:270px;padding:5px;"/>
    </div>
    <div>

    </div>
    <div>

    </div>
  </div>
<a href="#" class="prev"><img src="<?php echo SITE_ROOT?>/static/img/slides/arrow-prev.png" 
   width="24" height="43" alt="Arrow Prev"></a>
<a href="#" class="next"><img src="<?php echo SITE_ROOT?>/static/img/slides/arrow-next.png" 
   width="24" height="43" alt="Arrow Next"></a>
</div>
<img id="frame" width="739" height="341" alt="Example Frame" src="<?php echo SITE_ROOT?>/static/img/slides/example-frame.png">
-->

</div>
