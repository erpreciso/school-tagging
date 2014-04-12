$(document).ready(function () {
	$("#pull_exercises_list").on("click", function () {
		$.get("/dashboard/exercises_list");
	});
});

onMessage = function (message) {
	var data_arrived = JSON.parse(message.data);
	if (data_arrived.type == "exercises_list") {
		var list = data_arrived.message;
		var dataToStore = JSON.stringify(list);
		localStorage.setItem("exercises_list", dataToStore);
		Dashboard.build_exercises_list(list);
	}
	else if (data_arrived.type == "exercise") {
		var exercise = data_arrived.message.exercise;
		var etype = data_arrived.message.exercise_type;
		var dataToStore = JSON.stringify({"exercise": exercise, "etype": etype});
		localStorage.setItem("exercise", dataToStore);
		Dashboard.add_exercise_to_all_students_dashboards(exercise, etype);
	}
	else if (data_arrived.type == "connected_user") {
		var student = data_arrived.username;
		Dashboard.add_student_dashboard(student);
	}
	else if (data_arrived.type == "disconnected_user") {
		var student = data_arrived.username;
		Dashboard.remove_student_dashboard(student);
	}
	else if (data_arrived.type == "student_choice") {
		var param = {"action": "update", "content" : data_arrived.content};
		Dashboard.update_student_exercise(param);
	}
}

var Dashboard = {
	add_student_dashboard: function (student) {
		var student_dashboard = $(document.createElement("div"))
			.attr("class", "student_dashboard")
			.attr("id", student);
		var name = $(document.createElement("div"))
			.attr("class", "name")
			.text(student);
		var exercise_content = $(document.createElement("div"))
			.attr("class", "exercise_content");
		var exercise_status = $(document.createElement("div"))
			.attr("class", "exercise_status");
		var response_time = $(document.createElement("div"))
			.attr("class", "response_time");
		$(student_dashboard)
			.append(name)
			.append(exercise_content)
			.append(exercise_status)
			.append(response_time);
		$("#students_data").append(student_dashboard);
	},
	remove_student_dashboard: function (student) {
		$("#" + student).remove();
	},
	build_exercises_list: function (exercises_list) {
		$("#exercises_list").remove();
		var list = $(document.createElement("div"))
			.attr("id", "exercises_list");
		for (var exercise in exercises_list) {
			var sentence = $(document.createElement("div"))
				.attr("class", "sentence")
				.attr("id", exercise);
			var sentence_body = $(document.createElement("div"))
				.addClass("sentence_body")
				.text(exercises_list[exercise].sentence);
			var button_area = $(document.createElement("div"))
				.addClass("button_area");
			$(sentence).append(sentence_body);
			$(sentence).append(button_area);
			$(list).append(sentence);
		}
		$("#exercises_menu").append(list);
		$(".sentence_body").on("click", Dashboard.choose_element);
	},
	choose_element: function (event) {
		//~ yellow the sentence
		var id = event.target.parentElement.id;
		var triggered = $("#" + id);
		var container = $(triggered).parent();
		$(container).children().css("background-color", "inherit");
		$(triggered).css("background-color", "yellow");
		//~ create buttons to send exercise
		$(".exercise_type_choice").remove();
		var exercises_list = JSON.parse(localStorage.getItem("exercises_list"));
		for (var type in exercises_list[id].goal) {
			var button = $(document.createElement("button"))
				.addClass("exercise_type_choice")
				.text(exercises_list[id].goal[type].description);
			$(triggered).append(button);
			var exercise_request_parameters = {
				"id": id,
				"type": type
			};
			$(button).on(
				"click",
				{parameters: exercise_request_parameters},
				function (event) {
					$.post(
						"/dashboard/exercise_request",
						event.data.parameters
						);
			});
			
		}
	},
	add_exercise_to_all_students_dashboards: function (exercise, etype) {
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
	},
	update_student_exercise: function (data) {
		var student = data.content.student;
		var choice = data.content.choice;
		var etype = data.content.etype;
		var localData = JSON.parse(localStorage.getItem("exercise"));
		if (etype == "type_1") {
			$("#" + student + " .word").css("background-color", "inherit");
			var triggered = $("#" + student + " [class='word " + choice + "']");
			triggered.css("background-color", "yellow");
		}
		else {
			var i = localData.exercise.goal[localData.etype].answer;
			var correct = localData.exercise.goal[localData.etype].options[i];
			$("#" + student + " #answer_" + choice)
				.removeClass("raw_box");
			if (choice == correct) {
				$("#" + student + " #answer_" + choice).addClass("correct_box");
			}
			else {
				$("#" + student + " #answer_" + choice).addClass("wrong_box");
			}
		}
	}
}
