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
    $("#settings").slideToggle(); //offset requires element visibility
    var colorloversurl = "http://www.colourlovers.com/api/palettes/top?jsonCallback=?";
    $.getJSON(colorloversurl, {numResults: 99}, function(colors) {
      var c , html;
      $("#settings").empty();
      $.each(colors, function(k, v) {
        html = [];
        c = v.colors;
        html.push("<button id='" + k + "' class='colors'>");
        $.each(c, function(l, w) {
          html.push("<span class='color" + l + "' style='background:#" + w + "'>.</span>")
        });
        html.push("</button>");
        $("#settings").append(html.join(""));
      });
      $(".colors").click(function(color) {
        color = $.map(colors[this.id]["colors"], function(v) {
          return "\"#" + v + "\"";
        });
        $.post(xhrsubpath,{iscolorset: 'true', colors: "[" + color.toString() + "]"},function(got) {
          $("style").replaceWith(got);
        });
      });
    });
  });
  $("button.error").click(buttonhandler);
  $(".choice").click(choicehandler);   
});
