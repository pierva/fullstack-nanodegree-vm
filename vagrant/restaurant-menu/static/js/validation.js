function checkCoordinates(){
  if($(".coordinates").find('input').length === 2){
    var inputs = $(".coordinates").find('input');
    if(inputs.eq(0).val() === "" || inputs.eq(1).val() === ""){
      $("#add-restaurant").attr('disabled', true);
    } else {
      var enteredVal = inputs.eq(0).val() + inputs.eq(1).val()
      var matchLower = enteredVal.search(/[a-z]/g);
      var matchUpper = enteredVal.search(/[A-Z]/g);
      console.log(matchLower + matchUpper);
      if (matchLower + matchUpper <= 0){
        $("#add-restaurant").attr('disabled', false);
      } else {
        $("#add-restaurant").attr('disabled', true);
      }
    }
  }
  else {
  $("#add-restaurant").attr('disabled', true);
  }
}

$('.coordinates input').on('keyup', function(){
  checkCoordinates();
});

checkCoordinates();
