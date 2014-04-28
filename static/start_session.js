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
		Strg.saveCurrentExercise(exercise);
		add_exercise_to_all_students_dashboards(exercise.exercise, exercise.goal);
		$.post("/session/exercise_request", param);
	});
	
});

var Strg = {
	saveExerciseList : function (exerciseList) {
		localStorage.setItem("exercises", JSON.stringify(exerciseList));
	},
	saveCurrentExercise : function (exercise) {
		localStorage.setItem("currentExercise", JSON.stringify(exercise));
	},
	getCurrentExercise : function () {
		return JSON.parse(localStorage.getItem("currentExercise"));
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
		return {"exercise": exercise, "goal": goal};
	}
}

onMessage = function (message) {
	var data_arrived = JSON.parse(message.data);
	if (data_arrived.type == "exercises_list") {
		var exerciseList = data_arrived.message;
		Strg.saveExerciseList(exerciseList);
	}
	else if (data_arrived.type == "student_choice") {
		update_student_exercise(data_arrived.content);
	}
}
function update_student_exercise (data) {
	var student = data.student;
	var answer = data.answer;
	var currentExercise = Strg.getCurrentExercise();
	if (currentExercise.goal.type == "find_element") {
		$("#" + student + " .word").css("background-color", "inherit");
		var triggered = $("#" + student + " [class='word " + answer + "']");
		triggered.css("background-color", "yellow");
	}
	else if (currentExercise.goal.type == "which_type") {
		var i = currentExercise.goal.answers[0];
		var correct = currentExercise.goal.options[i];
		$("#" + student + " #answer_" + answer)
			.removeClass("raw_box");
		if (answer == correct) {
			$("#" + student + " #answer_" + answer).addClass("correct_box");
		}
		else {
			$("#" + student + " #answer_" + answer).addClass("wrong_box");
		}
	}
}

function add_exercise_to_all_students_dashboards (exercise, goal) {
	var students_count = $(".student_dashboard").length;
	$(".student_dashboard .sentence").remove();
	for (var i = 0; i < students_count; i++) {
		var sentence = $(document.createElement("div"))
			.attr("class", "sentence");
		for (var j = 0; j < exercise.words.length; j++) {
			var word = $(document.createElement("div"))
				.addClass("word " + j)
				.text(exercise.words[j] + " ");
				if (goal.type == "which_type" && 
						j == goal.target) {
					$(word).css("background-color", "#AAF9F4");
				}
			$(sentence).append(word);
		}
		if (goal.type == "which_type") {
			for (var j in goal.options) {
				var option = goal.options[j];
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
