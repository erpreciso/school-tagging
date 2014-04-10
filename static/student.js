onMessage = function (message) {
	var data_arrived = JSON.parse(message.data);
	if (data_arrived.type == "exercise") {
		build_exercise(data_arrived.message);
	}
}

function build_exercise (exercise) {
	$("#exercise").remove();
	var instructions = "<div id='instructions'>Please click on the correct ";
	instructions += exercise["to find"];
	instructions += "</div>";
	
	var target = "<div id='target'>";
	for (var i=0; i < exercise.words.length; i++) {
		target += "<div class='word' id='" + i;
		target += "'>" + exercise.words[i] + "</div> ";
	}
	target += "</div>";
	
	var exercise = "<div id='exercise'>";
	exercise += instructions;
	exercise += target;
	exercise += "</div>";
	$("#exercise_area").append(exercise);
	$(".word").on("click", function (event) {
		var triggered = event.target.id;
		$("#target").children().css("background-color", "inherit");
		$("#target #" + triggered).css("background-color", "yellow");
		$.post("/exercise/word_clicked", {"word_number": triggered});
	});
}


