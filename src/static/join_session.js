onMessage = function (message) {
	var data_arrived = JSON.parse(message.data);
	if (data_arrived.type == "exercise") {
		var exercise = data_arrived.message.exercise;
		var type = data_arrived.message.type;
		Exercise.build(exercise, type);
	}
}

var Exercise = new Object;
Exercise.build = function (exercise, type) {
	$("#exercise").remove();
	var instructions_text = type.description;
	if (type.type == "find_element") {
		instructions_text += " " + type["to find"];
	}
	var instructions = $(document.createElement("div"))
		.attr("class", "instructions")
		.text(instructions_text);
	var target = $(document.createElement("div"))
		.attr("id", "target");
	for (var i=0; i < exercise.words.length; i++) {
		var word = $(document.createElement("div"))
			.addClass("word")
			.attr("id", i)
			.text(exercise.words[i] + " ");
			if (type.type == "which_type" && 
						i == type.target) {
				$(word).css("background-color", "green");
			}
			$(target).append(word);
	}
	var exercise_body = $(document.createElement("div"))
		.attr("id", "exercise")
		.append(instructions)
		.append(target);
	$("#exercise_area").append(exercise_body);
	if (type.type == "find_element") {
		$(".word").on("click", function (event) {
			var triggered = event.target.id;
			$("#target").children().css("background-color", "inherit");
			$("#target #" + triggered).css("background-color", "yellow");
			$.post("/s/answer", {"answer": triggered});
		});
	}
	else {
		var options = type.options;
		for (var i = 0; i < options.length; i++) {
			var button = $(document.createElement("button"))
				.addClass("answer")
				.attr("id", options[i])
				.text(options[i]);
			$(exercise_body).append(button);
			var answer_parameter = {"answer": options[i]};
			$(button).on("click", answer_parameter, function (event) {
				$(event.target).css("background-color", "blue");
				$.post("/s/answer", {"answer": event.data.answer});
				$(".answer").off("click");
			});
		}
	}
}

