$(function() {
  $(".choice").click(function() {
    var correct = $("#question").text();
    $(".choice").map(function() {
      if($(this).attr("ques") === correct) {
        $(this).addClass("correct");
      } else {
        $(this).addClass("wrong");
      }
    })
  });   
});
