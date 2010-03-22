$(function(){
  var setting = {
    colors: [],
    mode: "random", //either of random or ranked.
  },
  colorJSONurl = "http://www.colourlovers.com/api/palettes/top?jsonCallback=?",
  colorrequestargs = {numResults: 4},
  choicemade = function(e) {
    console.log($(".choice"))
  };
  $(".choice").mousedown(function() {
    $(this).addClass("active");
    $(this).mouseup(function() {
      $(this).removeClass("active");
      choicemade(this);
        //handle click event here. (JSON request)
    });
  });
})
