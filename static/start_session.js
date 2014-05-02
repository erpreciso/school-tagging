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
		if (exercise.goal.type == "which_type") {
			var list = exercise.goal.options;
			Chart.initAnswersChart(list);
			Chart.createAnswersLegend(list);
		}
		var studentsCount = $(".student_dashboard").length;
		Chart.initRespondentsChart(studentsCount);
		Chart.createRespondentsChart($("#chartRespondents .chart"));
		$.post("/session/exercise_request", param);
	});
});

var colorsPool = ["green", "red", "blue", "orange"];

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
		updateStudentExercise(data_arrived.content);
	}
}

function updateStudentExercise (data) {
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
			Chart.updateAnswersValues(answer);
			Chart.createAnswersChart($("#chartAnswers .chart"));
			Chart.updateRespondentsValue("waiting", -1);
		}
		var box = $("#" + student + " #answer_" + answer);
		if ($(box).hasClass("raw_box")) {
			$(box).removeClass("raw_box");
			if (answer == correct) {
				Chart.updateRespondentsValue("correct", 1);
				$(box).addClass("correct_box");
			}
			else {
				Chart.updateRespondentsValue("wrong", 1);
				$(box).addClass("wrong_box");
			}
			Chart.createRespondentsChart();
		}
	}
}

var Chart = {
	strAnswersChartId : "answersPieChart",
	strRespondentsChartId: "respondentsBarChart",
	createRespondentsChart : function () {
		$("#" + Chart.strRespondentsChartId).empty();
		var dictChart = Strg.getRespondentsChartValues();
		var studentsCount = $(".student_dashboard").length;
		var series = [];
		var values = [];
		var i = 0;
		for (var attr in dictChart) {
			var serie = {label: attr, color: colorsPool[i]};
			var value = [Number(dictChart[attr])];
			if (value > 0) {
				values.push(value);
				series.push(serie);
			}
			i++;
		}
		var options = {
			stackSeries: true,
			series: series,
			legend: {
				show: true,
				placement: 'outsideGrid'
			},
	        seriesDefaults: {
	            renderer:$.jqplot.BarRenderer,
	            rendererOptions: {
					barDirection: 'horizontal',
					barWidth: 40,
					shadowAlpha: 0
				},
				pointLabels: {show: true }
	        },
	        axesDefaults: {
				showTicks: false,
				showTickMarks: false,
				borderWidth: 0
			},
			axes: {
				xaxis: {
					max: studentsCount
				}
			},
	        grid: {drawGridlines: false}
		    };
		var plot = $.jqplot(Chart.strRespondentsChartId, values, options);
	},
	initRespondentsChart : function (studentsCount) {
		var chartValues = {"correct": 0, "wrong": 0, "waiting": studentsCount};
		Strg.saveRespondentsChartValues(chartValues);
	},
	updateRespondentsValue : function (category, amount) {
		var values = Strg.getRespondentsChartValues();
		values[category] += Number(amount);
		Strg.saveRespondentsChartValues(values);
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
	createAnswersChart : function () {
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
		$("#" + Chart.strAnswersChartId).sparkline(values, param);
	},
	initAnswersChart : function (list) {
		var chartValues = {};
		for (var i = 0; i < list.length; i++) {
			chartValues[list[i]] = 0;
		}
		Strg.saveAnswersChartValues(chartValues);
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
