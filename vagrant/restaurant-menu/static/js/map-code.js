var map;
var position = {lat: 25.8124647, lng: -80.3375188}
var name = ""
function initMap() {
  map = new google.maps.Map(document.getElementById('map'), {
    center: position,
    zoom: 14
  });
  var marker = new google.maps.Marker({
    position: position,
    map: map,
    title: name
  });
}

$(".restaurant-container").on('click', ".show-on-map", function(){
  var lat = $(this).data("lat");
  var lng = $(this).data("lon");
  var restaurant = $(this).data("name");
  position = {lat: lat, lng: lng};
  name = restaurant;
  initMap();
})
