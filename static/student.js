onMessage = function (message) {
	var data_arrived = JSON.parse(message.data);
	if (data_arrived.type == "exercise") {
		var exercise = data_arrived.message.exercise;
		var exercise_type = data_arrived.message.exercise_type;
		Exercise.build(exercise, exercise_type);
	}
}

var Exercise = new Object;
Exercise.build = function (exercise, exercise_type) {
	$("#exercise").remove();
	var instructions = $(document.createElement("div"))
		.attr("class", "instructions")
		.text(exercise.goal[exercise_type].description);
	var target = $(document.createElement("div"))
		.attr("id", "target");
	for (var i=0; i < exercise.words.length; i++) {
		var word = $(document.createElement("div"))
			.addClass("word")
			.attr("id", i)
			.text(exercise.words[i] + " ");
			if (exercise_type == "type_2" && 
						i == exercise.goal[exercise_type].target) {
				$(word).css("background-color", "green");
			}
			$(target).append(word);
	}
	var exercise_body = $(document.createElement("div"))
		.attr("id", "exercise")
		.append(instructions)
		.append(target);
	$("#exercise_area").append(exercise_body);
	if (exercise_type == "type_1") {
		$(".word").on("click", function (event) {
			var triggered = event.target.id;
			$("#target").children().css("background-color", "inherit");
			$("#target #" + triggered).css("background-color", "yellow");
			$.post("/exercise/word_clicked", {"word_number": triggered});
		});
	}
	else {
		var options = exercise.goal[exercise_type].options;
		for (var i = 0; i < options.length; i++) {
			var button = $(document.createElement("button"))
				.addClass("answer")
				.attr("id", options[i])
				.text(options[i]);
			$(exercise_body).append(button);
			var answer_parameter = {"answer": options[i]};
			$(button).on("click", answer_parameter, function (event) {
				$.post("/exercise/type_answer", {"answer": event.data.answer});
			});
		}
	}
}


