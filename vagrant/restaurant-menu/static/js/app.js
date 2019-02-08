(function (){
  var year = new Date().getFullYear();
  var span = $("#year").text(year);
})();

$(".restaurant-controls").hover(function(){
  $(this).prev().css(
    {
      "background": "rgb(138, 4, 0)",
      "-webkit-box-shadow": "0px 0px 15px -2px rgba(255, 0, 0, 1)",
      "-moz-box-shadow": "0px 0px 15px -2px rgba(255,0,0,1)",
      "box-shadow": "0px 0px 15px -2px rgba(255,0,0,1)"
    }
  )}, function(){
    $(this).prev().css(
      {
        "background": "#616369",
        "-webkit-box-shadow": "0px 0px 15px -2px rgba(255,255,255,1)",
        "-moz-box-shadow": "0px 0px 15px -2px rgba(255,255,255,1)",
        "box-shadow": "0px 0px 15px -2px rgba(255,255,255,1)"
      }
    );
});

$(".restaurant-container").hover(function(){
  $(this).css(
    {
      "background": "rgb(138, 4, 0)",
      "-webkit-box-shadow": "0px 0px 15px -2px rgba(255, 0, 0, 1)",
      "-moz-box-shadow": "0px 0px 15px -2px rgba(255,0,0,1)",
      "box-shadow": "0px 0px 15px -2px rgba(255,0,0,1)"
    }
  );
}, function(){
  $(this).css(
    {
      "background": "#616369",
      "-webkit-box-shadow": "0px 0px 15px -2px rgba(255,255,255,1)",
      "-moz-box-shadow": "0px 0px 15px -2px rgba(255,255,255,1)",
      "box-shadow": "0px 0px 15px -2px rgba(255,255,255,1)"
    }
  );
});
