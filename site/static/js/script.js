$(document).ready(function(){
  /*----------------------------
  Drop Down Navigation Menu
  ----------------------------*/
  $('#site-menu ul li ul').css({
      display: "none",
      left: "auto"
  });
  $('#site-menu ul li').hoverIntent(function() {
      $(this)
        .find('ul').stop(true, true)
        .slideDown('fast');
  }, function() {
      $(this)
        .find('ul')
        .stop(true,true)
        .slideUp('slow')
  });
});
