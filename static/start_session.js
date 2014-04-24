$(document).ready(function () {
	var data;
	$.get("/data/exercises_list");
	
	$(".buttons .exercise_type").on("click", function (event) {
		var exerciseId = event.target.parentNode.parentNode.id;
		var exerciseType = event.target.id;
		var param = {
				"type": exerciseType,
				"id": exerciseId,
			};
		var exercise = Strg.getExercise(exerciseId, exerciseType);
		add_exercise_to_all_students_dashboards(exercise.exercise, exercise.goal);
		$.post("/session/exercise_request", param);
	});
	
});

var Strg = {
	saveExerciseList : function (exerciseList) {
		localStorage.setItem("exercises", JSON.stringify(exerciseList));
	},
	getExercise : function (exerciseId, exerciseType) {
		var exercises = JSON.parse(localStorage.getItem("exercises"));
		var exercise;
		var goal;
		for (var i = 0; i < exercises.length; i++) {
			
			if (exercises[i].id == exerciseId) {
				exercise = exercises[i];
				goals = exercise.goals;
				for (var j = 0; j < goals.length; j++) {
					if (goals[j].type == exerciseType) {
						goal = goals[j];
					}
				}
			}
		}
		return {"exercise": exercise, "goal": goal}
	}
}

onMessage = function (message) {
	var data_arrived = JSON.parse(message.data);
	if (data_arrived.type == "exercises_list") {
		var exerciseList = data_arrived.message;
		Strg.saveExerciseList(exerciseList);
	}
}

function add_exercise_to_all_students_dashboards (exercise, etype) {
	var students_count = $(".student_dashboard").length;
	$(".student_dashboard .sentence").remove();
	for (var i = 0; i < students_count; i++) {
		var sentence = $(document.createElement("div"))
			.attr("class", "sentence");
		for (var j = 0; j < exercise.words.length; j++) {
			var word = $(document.createElement("div"))
				.addClass("word " + j)
				.text(exercise.words[j] + " ");
				if (etype == "type_2" && 
						j == exercise.goal[etype].target) {
					$(word).css("background-color", "#AAF9F4");
				}
			$(sentence).append(word);
		}
		if (etype == "type_2") {
			for (var j in exercise.goal[etype].options) {
				var option = exercise.goal[etype].options[j];
				var choice = $(document.createElement("div"))
					.addClass("box")
					.addClass("raw_box")
					.attr("id", "answer_" + option)
					.text(option);
				$(sentence).append(choice);
			}
		}
		$($(".student_dashboard")[i])
			.children(".exercise_content")
			.append(sentence);
	}
}
