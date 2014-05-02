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
		Classroom.create_dashboard(exercise.exercise, exercise.goal);
		$.post("/session/exercise_request", param);
	});
	
	var studentsCount = $(".student_dashboard").length.toString();
	Chart.initRespondentsChart(studentsCount);
	Chart.createRespondentsChart($("#chartRespondents .chart"));
	
});

var colorsPool = ["red", "green", "blue", "orange"];

var Strg = {
	saveAnswersChartValues : function (chartValues) {
		localStorage.setItem("answersChartValues", JSON.stringify(chartValues));
	},
	saveRespondentsChartValues : function (chartValues) {
		localStorage.setItem("respondentsChartValues", JSON.stringify(chartValues));
	},
	getAnswersChartValues : function () {
		return JSON.parse(localStorage.getItem("answersChartValues"));
	},
	getRespondentsChartValues : function () {
		return JSON.parse(localStorage.getItem("respondentsChartValues"));
	},
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
		if ($("#" + student + " .raw_box").length == $("#" + student + " .box").length) {
			Classroom.add_respondent(1);
			Chart.updateAnswersValues(answer);
			Chart.createAnswersChart($("#chartAnswers .chart"));
		}
		var box = $("#" + student + " #answer_" + answer);
		if ($(box).hasClass("raw_box")) {
			$(box).removeClass("raw_box");
			if (answer == correct) {
				Classroom.add_winner(1);
				$(box).addClass("correct_box");
			}
			else {
				$(box).addClass("wrong_box");
			}
		}
	}
}

var Chart = {
	createRespondentsChart : function (chartElement) {
		var dictChart = Strg.getRespondentsChartValues();
		var values = [[2,6,3]];
		var param = {
			type: "bar",
			width: 80,
			height: 80,
		};
		//~ mylog(param);
		chartElement.sparkline(values, param);
	},
	initRespondentsChart : function (studentsCount) {
		var chartValues = {"correct": 0, "wrong": 0, "waiting": studentsCount};
		Strg.saveRespondentsChartValues(chartValues);
	},
	createAnswersLegend : function (options) {
		for (var i = 0; i < options.length; i++) {
			var option = $(document.createElement("div"))
				.text(options[i])
				.css("color", colorsPool[i]);
			$("#chartAnswers .legend").append(option);
		}
	},
	updateAnswersValues : function (answer) {
		var values = Strg.getAnswersChartValues();
		values[answer] += 1;
		Strg.saveAnswersChartValues(values);
	},
	createAnswersChart : function (chartElement) {
		var dictChart = Strg.getAnswersChartValues();
		var values = [];
		var colors = [];
		var i = 0;
		for (var attr in dictChart) {
			values.push(dictChart[attr]);
			colors.push(colorsPool[i]);
			i++;
		}
		var param = {
			type: "pie",
			width: 80,
			height: 80,
			sliceColors: colors
		};
		//~ mylog(param);
		chartElement.sparkline(values, param);
	},
	initAnswersChart : function (list) {
		var chartValues = {};
		for (var i = 0; i < list.length; i++) {
			chartValues[list[i]] = 0;
		}
		Strg.saveAnswersChartValues(chartValues);
	}
}

var Classroom = {
	create_dashboard : function (exercise, goal) {
		//~ var students_count = $(".student_dashboard").length.toString();
		//~ var exercise_status = document.createElement("div");
		//~ $(exercise_status).attr("id", "exercise_status");
		//~ var students_count_stat = document.createElement("div");
		//~ $(students_count_stat)
			//~ .attr("id", "students_count_stat")
			//~ .text("Students connected: ");
		//~ $(students_count_stat).append('<div id="students_count">' + students_count + '</div>');
		//~ var respondents_count_stat = document.createElement("div");
		//~ $(respondents_count_stat)
			//~ .attr("id", "respondents_count_stat")
			//~ .text("Students responding: ");
		//~ $(respondents_count_stat).append('<div id="respondents_count">0</div>');
		//~ var winners_count_stat = document.createElement("div");
		//~ $(winners_count_stat)
			//~ .attr("id", "winners_count_stat")
			//~ .text("Students correct: ");
		//~ $(winners_count_stat).append('<div id="winners_count">0</div>');
		//~ $(exercise_status)
			//~ .append(students_count_stat)
			//~ .append(respondents_count_stat)
			//~ .append(winners_count_stat);
		//~ $("#classroom_area").append(exercise_status);
		if (goal.type == "which_type") {
			var list = goal.options;
			Chart.initAnswersChart(list);
			Chart.createAnswersLegend(list);
			
			
		}
		
		//~ mylog(exercise);mylog(goal);
		
	},
	add_student : function (n) {
		if ($("#students_count").length > 0) {
			var logged = Number($("#students_count").text());
			logged += n;
			$("#students_count").text(logged);
		}
	},
	add_respondent : function (n) {
		if ($("#respondents_count").length > 0) {
			var respondents = Number($("#respondents_count").text());
			respondents += n;
			$("#respondents_count").text(respondents);
		}
	},
	add_winner : function (n) {
		if ($("#winners_count").length > 0) {
			var winners = Number($("#winners_count").text());
			winners += n;
			$("#winners_count").text(winners,toString());
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
