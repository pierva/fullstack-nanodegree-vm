function checkCoordinates(){
  if($("#coordinates").length){
    var inputs = $(this).find('input');
    if(inputs.eq(0).val() !== "" || inputs.eq(0).val() !== "")
    $("#add-restaurant").attr('disabled', false);
  }
}

$('#coordinates input').on('keyup', function(){
  checkCoordinates();
});

checkCoordinates();
