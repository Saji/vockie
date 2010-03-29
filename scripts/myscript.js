$(function() {
  var xhrsubpath = '/ajx',
  choicehandler = function() {
    var correctques = $("#question").text(),
    anschoice = $(this).text(),
    correctans = undefined,
    responsehandler = function(got) {
      if(got === "unknown user") {
        $(".unknowndialog").slideDown();
        return;
      }
      if(got === "off sync") {
        $(".offsyncdialog").slideDown();
        return;
      }
      $("#dialog").replaceWith(got);
      $("button.error").click(buttonhandler);
      $(".choice").click(choicehandler);
    };
    $(".choice").map(function() {
      if($(this).attr("ques") === correctques) {
        correctans = $(this).text();
        $(this).addClass("correct");
      } else {
        $(this).addClass("wrong");
      }
    });
    $("#loading").fadeIn();
    $.post(xhrsubpath,
           {ques: correctques, iscorrect: anschoice === correctans},
           responsehandler
          );
  },
  buttonhandler = function() {
    location.reload(true);
  };
  $("a.settings").click(function(e) {
    e.preventDefault();
    $("#settings").slideToggle();
  })
  $("button.error").click(buttonhandler);
  $(".choice").click(choicehandler);   
});
