onMessage = function (message) {
	var data_arrived = JSON.parse(message.data);
	if (data_arrived.type == "exercise") {
		Exercise.build(data_arrived.message);
	}
}

var Exercise = new Object;
Exercise.build = function (exercise) {
	if (exercise.type == "type_1") {
		$("#exercise").remove();
		var instructions = $(document.createElement("div"))
			.attr("class", "instructions")
			.text("Please select the correct " + exercise["to find"]);
		var target = $(document.createElement("div"))
			.attr("id", "target");
		for (var i=0; i < exercise.words.length; i++) {
			var word = $(document.createElement("div"))
				.attr("class", "word")
				.attr("id", i)
				.text(exercise.words[i] + " ");
				$(target).append(word);
		}
		var exercise = $(document.createElement("div"))
			.attr("id", "exercise")
			.append(instructions)
			.append(target);
		$("#exercise_area").append(exercise);
		$(".word").on("click", function (event) {
			var triggered = event.target.id;
			$("#target").children().css("background-color", "inherit");
			$("#target #" + triggered).css("background-color", "yellow");
			$.post("/exercise/word_clicked", {"word_number": triggered});
		});
	}
}


