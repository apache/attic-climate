<?php
$activeTab = 'publications';
?>
<div class="breadcrumbs">
    <a href="<?php echo SITE_ROOT?>/">Home</a> &nbsp;&rarr;&nbsp;
<a href="<?php echo SITE_ROOT?>/publications">Publications</a> &nbsp;&rarr;&nbsp;
    Reports

</div>

    <?php echo Puny::container()->load('publications.reports');?>
