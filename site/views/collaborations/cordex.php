<?php
$activeTab = 'collaborations';
?>
<div class="breadcrumbs">
    <a href="<?php echo SITE_ROOT?>/">Home</a> &nbsp;&rarr;&nbsp;
<a href="<?php echo SITE_ROOT?>/collaborations">Collaborations</a> &nbsp;&rarr;&nbsp;
    CORDEX

</div>

    <?php echo Puny::container()->load('collaborations.cordex');?>
