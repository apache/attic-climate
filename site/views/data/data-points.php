<?php
$activeTab = 'data';
?>
<div class="breadcrumbs">
    <a href="<?php echo SITE_ROOT?>/">Home</a> &nbsp;&rarr;&nbsp;
<a href="<?php echo SITE_ROOT?>/data">Data</a> &nbsp;&rarr;&nbsp;
    Data Points

</div>

    <?php echo Puny::container()->load('data.data-points');?>
