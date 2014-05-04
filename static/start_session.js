$(document).ready(function () {
	$(".buttons .exercise_type").on("click", function (event) {
		var studentsCount = $(".student_dashboard").length;
		if (studentsCount > 0) {
			var exerciseId = event.target.parentNode.parentNode.id;
			var exerciseType = event.target.id;
			var param = {
					"type": exerciseType,
					"id": exerciseId,
				};
			var exercise = Strg.getExercise(exerciseId, exerciseType);
			Strg.saveCurrentExercise(exercise);
			addExerciseToAllStudentsDashboards(exercise.exercise, exercise.goal);
			if (exercise.goal.type == "which_type") {
				var list = exercise.goal.options;
				Chart.initAnswersChart(list);
			}
			
			Chart.initRespondentsChart(studentsCount);
			Chart.createRespondentsChart($("#chartRespondents .chart"));
			$.post("/session/exercise_request", param);
		}
	});
	$.get("/data/exercises_list");
	$("#askExercises").on("click", function(){
		$.get("/data/exercises_list");
		mylog("exercises asked");
	});
});

var colorsPool = ["#9acd32", "#f08080", "#fffacd", "#40e0d0"];

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
	mylog("Message received: ");
	mylog(message);
	var data_arrived = JSON.parse(message.data);
	if (data_arrived.type == "exercises_list") {
		var exerciseList = data_arrived.message;
		Strg.saveExerciseList(exerciseList);
		$(".buttons .exercise_type").css("background-color", "green");
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
			var value = [Number(dictChart[attr])];
			var serie = {
				label: attr,
				color: colorsPool[i],
				pointLabels: {labels: [value.toString()]}
			};
			
			if (value > 0) {
				values.push(value);
				series.push(serie);
			}
			i++;
		}
		var options = {
			title: "Students responding",
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
					max: studentsCount,
				},
				yaxis: {
					max: 2
				}
			},
	        grid: {
				drawGridlines: false,
				background: "transparent",
				borderWidth: 0,
				shadow: false
			}
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
	updateAnswersValues : function (answer) {
		var values = Strg.getAnswersChartValues();
		values[answer] += 1;
		Strg.saveAnswersChartValues(values);
	},
	createAnswersChart : function () {
		$("#" + Chart.strAnswersChartId).empty();
		var dictChart = Strg.getAnswersChartValues();
		var data = [];
		var i = 0;
		for (var attr in dictChart) {
			var value = Number(dictChart[attr]);
			if (value > 0) {
				data.push([attr, value]);
			}
			i++;
		}
		var options = {
			title: "Answers given",
			legend: {
				show: true,
				location: "e"
			},
	        seriesDefaults: {
	            renderer:$.jqplot.PieRenderer,
	            rendererOptions: {
					showDataLabels: true,
					fill: false
				},
	        },
	        axesDefaults: {
				showTicks: false,
				showTickMarks: false,
				borderWidth: 0
			},
			grid: {
				drawGridlines: false,
				background: "transparent",
				borderWidth: 0,
				shadow: false
			}
	    };
		var plot = $.jqplot(Chart.strAnswersChartId, [data], options);
	},
	initAnswersChart : function (list) {
		var chartValues = {};
		for (var i = 0; i < list.length; i++) {
			chartValues[list[i]] = 0;
		}
		Strg.saveAnswersChartValues(chartValues);
	}
}
	
function addExerciseToAllStudentsDashboards (exercise, goal) {
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
