$(document).ready(function () {
	init.attach_events_to_buttons();
});

var init = {
	attach_events_to_buttons: function () {
		for (var i = 0; i < $(".exercise_type").length; i++) {
			$(".exercise_type:eq(" + i + ")").on("click", {type: i + 1}, function (event) {
				$.get("/dashboard/exercises_list/type_" + event.data.type);
			});	
		}
	}
}

function ask_info(what, data) {
	if (what == "logged") {
		$.get("/dashboard/get_logged");
	}
	else if (what == "exercises_list") {
		$.get("/dashboard/exercises_list/" + data);
	}
}

onMessage = function (message) {
	var data_arrived = JSON.parse(message.data);
	if (data_arrived.type == "exercises_list") {
		var list = data_arrived.message;
		var exercise_type = data_arrived.exercise_type;
		Dashboard.build_exercises_list(list, exercise_type);
	}
	else if (data_arrived.type == "exercise") {
		var exercise = data_arrived.message;
		Dashboard.add_exercise_to_all_students_dashboards(exercise);
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
	build_exercises_list: function (exercises_list, exercise_type) {
		//~ $("#exercises_list").remove();
		var list = $(document.createElement("div"))
			.attr("id", "exercises_list");
		for (var i = 0; i < exercises_list.length; i++) {
			var sentence = $(document.createElement("div"))
				.attr("class", "sentence")
				.attr("id", "sentence_" + i)
				.text(exercises_list[i].sentence);
			$(list).append(sentence);
		}
		var button = $(document.createElement("button"))
			.attr("id", "send_exercise_choosen")
			.text("Send exercise to classroom");
		$("#exercises_menu")
			.append(list)
			.append(button);
		$(list).on("click", Dashboard.choose_element);
		$(button).on("click", {type: exercise_type}, function(event) {
			var chosen = $("#chosen").parent().attr("id").substring(9);
			param = {"exercise_number": chosen, "type": event.data.type}
			$.post("/dashboard/exercise_request/foo", param);
		});
	},
	choose_element: function (event) {
		//~ on click, will highlight the element clicked and add a nested 
		//~ element with id=chosen
		var triggered = $("#" + event.target.id);
		var container = $(triggered).parent();
		$(container).children().css("background-color", "inherit");
		$(triggered).css("background-color", "yellow");
		$("#chosen").remove();
		var chosen = $(document.createElement("div"))
			.attr("id", "chosen")
			.attr("class", "hidden");
		$(triggered).append(chosen);
	},
	add_exercise_to_all_students_dashboards: function (exercise) {
		var students_count = $(".student_dashboard").length;
		$(".student_dashboard .sentence").remove();
		for (var i = 0; i < students_count; i++) {
			var sentence = $(document.createElement("div"))
				.attr("class", "sentence");
			for (var j = 0; j < exercise.words.length; j++) {
				var word = $(document.createElement("div"))
					.addClass("word " + j)
					.text(exercise.words[j] + " "); 
				$(sentence).append(word);
			}
			$($(".student_dashboard")[i])
				.children(".exercise_content")
				.append(sentence);
		}
	},
	update_student_exercise: function (data) {
		var student = data.content.student;
		var choice = data.content.choice;
		$("#" + student + " .word").css("background-color", "inherit");
		var triggered = $("#" + student + " [class='word " + choice + "']");
		triggered.css("background-color", "yellow");
	}
}
