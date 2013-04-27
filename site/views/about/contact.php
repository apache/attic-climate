<?php
$activeTab = 'about';
?>
<div class="breadcrumbs">
    <a href="<?php echo SITE_ROOT?>/">Home</a> &nbsp;&rarr;&nbsp;
<a href="<?php echo SITE_ROOT?>/about">About</a> &nbsp;&rarr;&nbsp;
    Contact

</div>

    <?php echo Puny::container()->load('about.contact');?>
